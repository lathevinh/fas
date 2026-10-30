"""Full DINO-Reg reconstruction with detached, verified final-CLS attention."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/paper327"))
from objective import attack_tail_ranking

UPSTREAM = Path.home()/".cache/fas/upstream/dinov2-7764ea0"
REVISION = "7764ea0f912e53c92e82eb78a2a1631e92725fc8"
CHECKPOINT = Path.home()/".cache/fas/source-pilot295-v1/checkpoints/dino_reg.pth"


def configure(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    # DINO's antialiased positional interpolation has no deterministic CUDA backward.
    torch.use_deterministic_algorithms(False)


def attention_weights(qkv: torch.Tensor, heads: int = 12, registers: int = 4) -> torch.Tensor:
    if qkv.ndim != 3 or qkv.shape[1:] != (261, 2304) or heads != 12 or registers != 4:
        raise ValueError("DINO-Reg B14 RGB224 requires CLS+4registers+256patches and12heads")
    with torch.no_grad():
        q, k, _ = qkv.detach().reshape(len(qkv), 261, 3, heads, 64).unbind(2)
        logits = torch.einsum("bhd,bnhd->bhn", q[:, 0], k)*(.125)
        # Normalize per head over all tokens first, exactly as the attention backend.
        probabilities = logits.softmax(-1)[..., 1+registers:].mean(1)
        weights = probabilities/probabilities.sum(-1, keepdim=True)
        if not torch.isfinite(weights).all() or (weights < 0).any():
            raise ValueError("finite normalized patch attention required")
        return weights


class Reference(nn.Module):
    def __init__(self, *, initialize: bool = True) -> None:
        super().__init__()
        sys.path.insert(0, str(ROOT/"src"))
        from fas.environment import verify_source_checkout
        verify_source_checkout(UPSTREAM, REVISION)
        sys.path.insert(0, str(UPSTREAM))
        from dinov2.hub import backbones
        self.backbone = backbones.dinov2_vitb14_reg(pretrained=False)
        if initialize:
            self.backbone.load_state_dict(
                torch.load(CHECKPOINT, map_location="cpu", weights_only=True), strict=True)
        self.global_head = nn.Linear(768, 2)
        self.patch_head = nn.Linear(768, 2)
        self.weights = None
        if self.backbone.blocks[-1].attn.attn_drop != 0:
            raise ValueError("zero attention dropout required for exact detached attention readback")
        self.backbone.blocks[-1].attn.qkv.register_forward_hook(self.capture)

    def capture(self, module, inputs, output) -> None:
        self.weights = attention_weights(output)

    def forward(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if images.ndim != 4 or images.shape[1:] != (3, 224, 224):
            raise ValueError("RGB224 input required")
        self.weights = None
        features = self.backbone.forward_features(images)
        if self.weights is None or features["x_norm_patchtokens"].shape[1:] != (256, 768):
            raise RuntimeError("actual final-block attention and256 patch tokens required")
        return (self.global_head(features["x_norm_clstoken"]),
                self.patch_head(F.normalize(features["x_norm_patchtokens"], dim=-1)*16),
                self.weights)


def tensor_images(images: np.ndarray, device: str) -> torch.Tensor:
    if images.ndim != 4 or images.shape[1:] != (224, 224, 3) or images.dtype != np.uint8:
        raise ValueError("uint8 RGB224 batch required")
    tensor = torch.from_numpy(images.copy()).to(device=device, dtype=torch.float32).permute(0, 3, 1, 2)/255
    mean = tensor.new_tensor([.485, .456, .406])[None, :, None, None]
    std = tensor.new_tensor([.229, .224, .225])[None, :, None, None]
    return (tensor-mean)/std


def balanced_mean(values: torch.Tensor, labels: torch.Tensor, domains: torch.Tensor) -> torch.Tensor:
    terms = []
    for domain in torch.unique(domains, sorted=True):
        for label in (0, 1):
            mask = (domains == domain) & (labels == label)
            if not mask.any():
                raise ValueError("both post-augmentation classes in every source required")
            terms.append(values[mask].mean())
    return torch.stack(terms).mean()


def losses(outputs, labels: torch.Tensor, domains: torch.Tensor, patch_labels: torch.Tensor,
           *, tail: bool) -> dict[str, torch.Tensor]:
    global_logits, patch_logits, weights = outputs
    if (patch_labels.shape != (len(labels), 256)
            or not ((patch_labels == 0) | (patch_labels == 1)).all()
            or weights.requires_grad or weights.shape != patch_labels.shape
            or (weights < 0).any()
            or not torch.allclose(weights.sum(1), torch.ones_like(weights[:, 0]), atol=1e-6)):
        raise ValueError("binary patch targets and detached normalized attention required")
    global_loss = balanced_mean(F.cross_entropy(global_logits, labels, reduction="none"), labels, domains)
    patches = F.cross_entropy(patch_logits.transpose(1, 2), patch_labels, reduction="none")
    apl = balanced_mean((patches*weights).sum(1), labels, domains)
    # Compute and log the fixed candidate in both arms; only its multiplier differs.
    hardest = attack_tail_ranking(global_logits[:, 1]-global_logits[:, 0], labels, domains)
    total = global_loss+apl+(.1*hardest if tail else 0)
    values = {"global": global_loss, "APL": apl, "hardest_attack": hardest, "total": total}
    if any(not torch.isfinite(value) for value in values.values()):
        raise ValueError("nonfinite reference or hardest-attack loss")
    return values


def optimizer_for(model: nn.Module) -> torch.optim.Optimizer:
    groups = {}
    for name, parameter in model.named_parameters():
        lr = 5e-6 if name.startswith("backbone.") else 5e-5
        decay = .05 if parameter.ndim > 1 and not name.endswith(".bias") else 0.
        groups.setdefault((lr, decay), []).append(parameter)
    return torch.optim.AdamW([{"params": params, "lr": lr, "weight_decay": decay}
                              for (lr, decay), params in groups.items()],
                             betas=(.9, .999), eps=1e-8)


def check_gradients(model: nn.Module) -> None:
    for name, parameter in model.named_parameters():
        if parameter.grad is None:
            if name != "backbone.mask_token":
                raise ValueError(f"missing gradient: {name}")
        elif not torch.isfinite(parameter.grad).all():
            raise ValueError(f"nonfinite gradient: {name}")
    first = model.backbone.blocks[0].attn.qkv.weight.grad
    if first is None or first.abs().sum() == 0:
        raise ValueError("nonzero first-block gradient required")
