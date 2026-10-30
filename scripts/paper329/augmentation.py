"""Independent eight-family FAS-Aug reconstruction and addressed paired PDA."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance

import assets

FAMILIES = ("motion", "resolution", "camera_ICC", "reflection", "moire",
            "clustered_halftone", "printer_ICC", "blue_halftone")
SPOOF = frozenset(FAMILIES[3:])


def rng_for(seed: int, epoch: int, step: int, attempt: int) -> np.random.Generator:
    address = f"paper329:data:{seed}:{epoch}:{step}:{attempt}".encode()
    return np.random.default_rng(int.from_bytes(hashlib.sha256(address).digest()[:16], "big"))


@lru_cache(maxsize=90)
def background(index: int) -> np.ndarray:
    rng = np.random.default_rng(329000+index)
    image = Image.new("RGB", (224, 224), tuple(rng.integers(30, 230, 3).tolist()))
    draw = ImageDraw.Draw(image)
    for _ in range(18):
        x, y = rng.integers(0, 190, 2).tolist()
        draw.rectangle((x, y, x+int(rng.integers(10, 60)), y+int(rng.integers(10, 60))),
                       fill=tuple(rng.integers(0, 256, 3).tolist()))
    return np.asarray(image).copy()


@lru_cache(maxsize=16)
def moire(index: int) -> np.ndarray:
    rng = np.random.default_rng(329100+index)
    layout, instance = divmod(index, 10)
    colors = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255]], np.uint8)
    y, x = np.indices((12, 12))
    tile = colors[((x//(1+layout % 3) + (y//(1+layout % 4))*(layout//3)
                    + layout) % (4 if layout >= 12 else 3))]
    image = np.tile(tile, (86, 86, 1))[:1024, :1024].copy()
    corners = np.float32([[0, 0], [1023, 0], [1023, 1023], [0, 1023]])
    for _ in range(instance+1):
        destination = corners+rng.uniform(-102.4, 102.4, (4, 2)).astype(np.float32)
        image = cv2.warpPerspective(image, cv2.getPerspectiveTransform(corners, destination),
                                    (1024, 1024), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REFLECT_101)
    return image


@lru_cache(maxsize=48)
def blue(index: int) -> tuple[np.ndarray, np.ndarray]:
    # Independent spectral blue-noise construction, not the paper's void-and-cluster assets.
    rng = np.random.default_rng(329300+index)
    mode = index//8
    channels = (1, 2, 3, 4, 4, 5)[mode]
    frequencies = np.fft.fftfreq(256)
    radius = np.hypot(frequencies[:, None], frequencies[None, :])
    values = []
    for _ in range(channels):
        filtered = np.fft.ifft2(np.fft.fft2(rng.normal(size=(256, 256)))*radius).real
        order = np.argsort(filtered, axis=None, kind="stable")
        ranks = np.empty(256*256, dtype=np.float32)
        ranks[order] = np.arange(256*256, dtype=np.float32)/(256*256-1)
        values.append(ranks.reshape(256, 256))
    data = np.stack(values, axis=-1)
    alpha = data[..., -1:] if mode in (1, 3, 5) else np.ones((256, 256, 1), np.float32)
    if mode < 2:
        rgb = np.repeat(data[..., :1], 3, axis=-1)
    elif mode < 4:
        rgb = data[..., :3]
    else:
        rgb = (1-data[..., :3])*(1-data[..., 3:4])
    return rgb*255, alpha


class FASAug:
    def __init__(self) -> None:
        assets.verify()
        self.transforms = {}

    def icc(self, image: Image.Image, source: str, destination: str) -> Image.Image:
        key = source, destination
        if key not in self.transforms:
            self.transforms[key] = ImageCms.buildTransform(
                str(assets.DIRECTORY/source), str(assets.DIRECTORY/destination),
                "CMYK" if source == assets.CMYK else "RGB", "RGB")
        return ImageCms.applyTransform(image, self.transforms[key])

    def apply(self, rgb: np.ndarray, label: int, rng: np.random.Generator,
              family: str | None = None) -> tuple[np.ndarray, int, str]:
        if rgb.shape != (224, 224, 3) or rgb.dtype != np.uint8 or label not in (0, 1):
            raise ValueError("RGB224 uint8 and binary attack label required")
        family = family if family is not None else str(rng.choice(FAMILIES))
        if family not in FAMILIES:
            raise ValueError("unknown FAS-Aug family")
        image = Image.fromarray(rgb)
        if family == "motion":
            size = int(rng.integers(3, 17))
            kernel = np.zeros((size, size), np.float32)
            direction = int(rng.integers(4))
            if direction == 0:
                kernel[size//2, :] = 1
            elif direction == 1:
                kernel[:, size//2] = 1
            else:
                kernel = np.eye(size, dtype=np.float32)
                if direction == 3:
                    kernel = kernel[:, ::-1].copy()
            result = cv2.filter2D(rgb, -1, kernel/kernel.sum(), borderType=cv2.BORDER_REFLECT_101)
        elif family == "resolution":
            side = max(1, round(224*float(rng.uniform(1/6, 1))))
            result = np.asarray(image.resize((side, side), Image.Resampling.NEAREST)
                                .resize((224, 224), Image.Resampling.NEAREST)).copy()
        elif family == "camera_ICC":
            source, destination = rng.choice(assets.RGB, 2).tolist()
            result = np.asarray(self.icc(image, source, destination)).copy()
        elif family == "printer_ICC":
            result = np.asarray(self.icc(image.convert("CMYK"), assets.CMYK, str(rng.choice(assets.RGB)))).copy()
        else:
            alpha = 1.
            if family == "reflection":
                texture = background(int(rng.integers(90)))
                strength = rng.uniform(.03, .2)
            elif family == "moire":
                texture = moire(int(rng.integers(190)))
                y, x = rng.integers(0, 801, 2)
                texture = texture[y:y+224, x:x+224]
                strength = rng.uniform(.01, .3)
            elif family == "clustered_halftone":
                small = np.asarray(image.convert("L").resize((75, 75), Image.Resampling.BILINEAR))
                levels = np.rint(small.astype(np.float32)/255*9).astype(int)
                ranks = np.array([[8, 3, 7], [4, 0, 2], [6, 1, 5]])
                dots = (levels[:, :, None, None] > ranks)*255
                texture = dots.transpose(0, 2, 1, 3).reshape(225, 225)[:224, :224, None]
                strength = rng.uniform(.01, .2)
            else:
                texture, alpha = blue(int(rng.integers(48)))
                texture, alpha = texture[:224, :224], alpha[:224, :224]
                strength = rng.uniform(.01, .4)
            blend = strength*alpha
            result = np.clip((1-blend)*rgb+blend*texture, 0, 255).astype(np.uint8)
        return result, 1 if family in SPOOF else label, family


@dataclass
class Batch:
    images: np.ndarray
    labels: np.ndarray
    domains: np.ndarray
    patch_labels: np.ndarray
    trace: dict


def paired_batch(rows: list[dict], load_rgb, augmenter: FASAug, seed: int,
                 epoch: int, step: int, *, attempts: int = 32,
                 fas_probability: float = .2, pda_probability: float = .2) -> Batch:
    if (type(attempts) is not int or not 1 <= attempts <= 32
            or not 0 <= fas_probability <= 1 or not 0 <= pda_probability <= 1):
        raise ValueError("bounded attempts and valid augmentation probabilities required")
    sources = sorted({row["dataset"] for row in rows})
    if len(sources) != 3:
        raise ValueError("exactly three fitting sources required")
    strata = [[i for i, row in enumerate(rows)
               if row["dataset"] == source and (row["binary_label"] == "attack") == bool(label)]
              for source in sources for label in (0, 1)]
    if any(not pool for pool in strata):
        raise ValueError("exhausted fitting source/class or PDA donor pool")
    for attempt in range(attempts):
        rng = rng_for(seed, epoch, step, attempt)
        slots = list(range(6))*5+[(2*step) % 6, (2*step+1) % 6]
        selected = [int(rng.choice(strata[slot])) for slot in slots]
        images, labels, families = [], [], []
        domains = np.array([slot//2 for slot in slots], dtype=np.int64)
        for index in selected:
            row = rows[index]
            image = Image.fromarray(load_rgb(row))
            if rng.random() < .5:
                image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            image = image.rotate(float(rng.uniform(-10, 10)), Image.Resampling.BILINEAR, fillcolor=(0, 0, 0))
            image = ImageEnhance.Brightness(image).enhance(float(rng.uniform(.8, 1.2)))
            rgb = np.asarray(image).copy()
            label, family = int(row["binary_label"] == "attack"), "none"
            if rng.random() < fas_probability:
                rgb, label, family = augmenter.apply(rgb, label, rng)
            images.append(rgb)
            labels.append(label)
            families.append(family)
        labels = np.asarray(labels, dtype=np.int64)
        counts = [[int(np.sum((domains == d) & (labels == y))) for y in (0, 1)] for d in range(3)]
        if any(min(pair) == 0 for pair in counts):
            continue
        images = np.stack(images)
        donors = images.copy()
        patches = np.repeat(labels[:, None], 256, axis=1)
        donor_ids, masks = [-1]*32, np.zeros((32, 256), dtype=bool)
        for i in range(32):
            if labels[i] and rng.random() < pda_probability:
                donor = int(rng.choice(np.flatnonzero((domains == domains[i]) & (labels == 0))))
                mask = rng.random((16, 16)) < .5
                pixel_mask = mask.repeat(14, 0).repeat(14, 1)
                images[i][pixel_mask] = donors[donor][pixel_mask]
                patches[i][mask.ravel()] = 0
                donor_ids[i], masks[i] = selected[donor], mask.ravel()
        trace = {"selected": selected, "families": families, "donors": donor_ids,
                 "mask_sha256": hashlib.sha256(masks.tobytes()).hexdigest(),
                 "redraws": attempt, "post_augmentation_counts": counts}
        trace["batch_sha256"] = hashlib.sha256(
            images.tobytes()+labels.tobytes()+domains.tobytes()+patches.tobytes()).hexdigest()
        return Batch(images, labels, domains, patches, trace)
    raise RuntimeError(f"post-augmentation source/class support exhausted after{attempts} attempts")
