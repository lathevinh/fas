"""Immutable, independently resumable native feature shards."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from .frozen_features import check_feature


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 ** 2), b""):
            value.update(chunk)
    return value.hexdigest()


def payload_digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cache_key(base_key: str, contract: dict) -> str:
    return payload_digest({"base_key": base_key, "extraction_contract": contract})


def load_shard(path: Path, keys: list[str], dimension: int) -> np.ndarray:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"features", "keys"} or data["keys"].tolist() != keys or len(set(keys)) != len(keys):
            raise ValueError("exact unique ordered feature/cache-key join required")
        result = data["features"]
    check_feature(result, len(keys), dimension)
    return result


def save_shard(path: Path, keys: list[str], features: np.ndarray) -> None:
    check_feature(features, len(keys), features.shape[1])
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate shard keys")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            np.savez(handle, features=features, keys=np.asarray(keys))
            handle.flush()
            os.fsync(handle.fileno())
        if not np.array_equal(features, load_shard(temporary, keys, features.shape[1])):
            raise ValueError("atomic feature shard exact readback failed")
        os.link(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)
