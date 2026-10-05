"""Read-only validation of the declared Phase-1 runtime environment."""

from __future__ import annotations

import hashlib
import platform
import re
import sys
from collections.abc import Mapping, Sequence
from importlib import metadata
from pathlib import Path
from typing import Any


REQUIRED_PACKAGES = (
    "torch", "torchvision", "open_clip_torch", "transformers", "scikit_learn",
)


def check_environment(
    root: Path,
    config: Mapping[str, Any],
    *,
    python_version: Sequence[int],
    runtime_platform: str,
    installed_packages: Mapping[str, str | None],
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({
            "name": name,
            "status": "pass" if passed else "blocked",
            "detail": detail,
        })

    record("schema_version", config.get("version") == 1, "expected environment schema version 1")
    requirement = config.get("python_requires")
    match = re.fullmatch(r">=(\d+)\.(\d+),<(\d+)\.(\d+)", requirement or "") if isinstance(requirement, str) else None
    compatible = False
    if match:
        lower = (int(match[1]), int(match[2]))
        upper = (int(match[3]), int(match[4]))
        compatible = lower <= tuple(python_version[:2]) < upper
    record("python", compatible, f"observed {'.'.join(map(str, python_version))}; required {requirement}")
    record("platform", runtime_platform == config.get("platform"), f"observed {runtime_platform}; required {config.get('platform')}")
    record("lock_status", config.get("status") == "locked", f"declared status: {config.get('status')}")

    packages = config.get("packages")
    if not isinstance(packages, Mapping):
        packages = {}
    record("package_set", all(name in packages for name in REQUIRED_PACKAGES), "all required model-stack packages must be declared")
    for name in sorted(set(REQUIRED_PACKAGES) | set(packages)):
        expected = packages.get(name)
        actual = installed_packages.get(name)
        exact_pin = isinstance(expected, str) and re.fullmatch(r"\d+(?:\.\d+)+(?:[a-zA-Z0-9.+-]*)", expected) is not None
        record(f"package:{name}", exact_pin and actual == expected, f"installed={actual}; pinned={expected}")

    relative_path = config.get("lockfile")
    digest = config.get("lockfile_sha256")
    lock_matches = False
    detail = "lockfile and its actual SHA-256 are required"
    if isinstance(relative_path, str) and relative_path:
        path = (root / relative_path).resolve()
        if Path(relative_path).is_absolute() or not path.is_relative_to(root.resolve()):
            detail = "lockfile must resolve inside the repository"
        elif not path.is_file():
            detail = f"missing lockfile: {relative_path}"
        else:
            actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lock_matches = isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None and actual_digest == digest
            detail = f"actual SHA-256={actual_digest}; recorded={digest}"
    record("lockfile", lock_matches, detail)

    return {
        "version": 1,
        "status": "ready" if all(check["status"] == "pass" for check in checks) else "blocked",
        "checks": checks,
        "scope": "runtime declarations and lock identity only; not model/GPU/data readiness",
    }


def inspect_environment(root: Path, config: Mapping[str, Any]) -> dict[str, Any]:
    packages = config.get("packages", {})
    names = set(REQUIRED_PACKAGES)
    if isinstance(packages, Mapping):
        names.update(packages)
    installed: dict[str, str | None] = {}
    for name in sorted(names):
        try:
            installed[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed[name] = None
    result = check_environment(
        root,
        config,
        python_version=sys.version_info[:3],
        runtime_platform=f"{sys.platform}_{platform.machine()}",
        installed_packages=installed,
    )
    result["python_executable"] = sys.executable
    return result