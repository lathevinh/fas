"""Pinned CC0 ICC profiles; no unlicensed FAS-Aug code or photographs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request

REVISION = "bdd84663061bc4ae95ca70decff54f581e27f702"
BASE = f"https://raw.githubusercontent.com/saucecontrol/Compact-ICC-Profiles/{REVISION}"
DIRECTORY = Path.home()/".cache/fas/paper329-assets-v1"
RGB = ("sRGB-v4.icc", "AdobeCompat-v2.icc", "AppleCompat-v2.icc",
       "ColorMatchCompat-v2.icc", "DCI-P3-v4.icc", "ProPhoto-v4.icc", "Rec2020-v4.icc",
       "Rec601NTSC-v4.icc", "Rec601PAL-v4.icc", "Rec709-v4.icc", "WideGamutCompat-v2.icc")
CMYK = "CGATS001Compat-v2-micro.icc"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acquire() -> None:
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    if (DIRECTORY/"receipt.json").exists():
        verify()
        return
    files = {}
    for name in ("license", *RGB, CMYK):
        path = DIRECTORY/name
        if path.exists():
            raise FileExistsError("partial ICC acquisition requires explicit inspection, not silent reuse")
        url = f"{BASE}/{'profiles/' if name != 'license' else ''}{name}"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read(1024*1024+1)
        if not data or len(data) > 1024*1024:
            raise ValueError("ICC asset acquisition size cap")
        if name == "license" and not data.startswith(b"CC0 1.0 Universal"):
            raise ValueError("expected upstream CC0 dedication")
        with path.open("xb") as stream:
            stream.write(data)
        files[name] = digest(path)
    record = {"revision": REVISION, "license": "CC0-1.0", "files": files}
    with (DIRECTORY/"receipt.json").open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
    verify()


def verify() -> dict:
    record = json.loads((DIRECTORY/"receipt.json").read_text())
    if (record["revision"] != REVISION or record["license"] != "CC0-1.0"
            or set(record["files"]) != {"license", *RGB, CMYK}):
        raise ValueError("fixed ICC asset inventory required")
    for name, expected in record["files"].items():
        if digest(DIRECTORY/name) != expected:
            raise ValueError(f"ICC asset changed: {name}")
    return record


if __name__ == "__main__":
    acquire()
