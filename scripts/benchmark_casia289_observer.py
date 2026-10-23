"""Bounded metadata-only observer benchmark on the actual workspace filesystem."""

import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import threading
import time

import casia_budget289 as budget
import recover_casia287 as recovery


def run():
    prior = recovery.prior
    with tempfile.TemporaryDirectory(prefix=".casia289-benchmark-", dir=prior.ROOT) as directory:
        root = Path(directory)
        populated, controls = root / "populated", root / "control"
        populated.mkdir()
        for index in range(600):
            folder = populated / f"{index:04d}"
            folder.mkdir()
            for slot in range(25):
                (folder / f"{slot:02d}").touch()
        binding = {"synthetic600_tree": True}
        budget.initialize(controls, binding)
        started = time.monotonic()
        budget.scan_once([root], controls, binding, prior.shared.retained.tree_bytes)
        scan_seconds = time.monotonic() - started
        errors = []

        def scan():
            try:
                budget.scan_once([root], controls, binding, prior.shared.retained.tree_bytes)
            except Exception as error:
                errors.append(error)

        scanner = threading.Thread(target=scan)
        scanner.start()
        client = budget.Client(controls, binding,
                               lambda group: prior.shared.usage(group, root / ".unused"), lambda value: None)
        timings, reservation_timings = [], []
        try:
            for index in range(200):
                started = time.monotonic()
                client.measure(os.getpgrp())
                timings.append(time.monotonic() - started)
                if index < 40:
                    started = time.monotonic()
                    with client.reserve(4096):
                        (populated / f"{index:04d}" / "growth").write_bytes(b"g" * 4096)
                    reservation_timings.append(time.monotonic() - started)
            scanner.join(timeout=30)
            if scanner.is_alive():
                raise TimeoutError("bounded synthetic scanner did not finish")
            if errors:
                raise RuntimeError("synthetic scanner failed") from errors[0]
            actual = prior.shared.retained.tree_bytes(root)
            reported = client.measure(os.getpgrp())["output_bytes"]
            if reported < actual:
                raise AssertionError("growth between snapshots was undercounted")
        finally:
            scanner.join(timeout=30)
            if scanner.is_alive():
                raise TimeoutError("synthetic scanner cleanup failed")
        ordered = sorted(timings)
        result = {
            "checkpoint": 289, "synthetic_only": True, "private_media_opened": False,
            "filesystem": "actual workspace filesystem", "populated_original_shaped_directories": 600,
            "initial_synthetic_files": 15000, "growth_files": 40, "measurement_samples": len(timings),
            "full_scan_seconds": scan_seconds, "foreground_median_seconds": statistics.median(timings),
            "foreground_p95_seconds": ordered[int(len(ordered) * 0.95) - 1],
            "foreground_max_seconds": max(timings), "reservation_max_seconds": max(reservation_timings),
            "foreground_p95_threshold_seconds": 0.05, "foreground_max_threshold_seconds": 0.25,
            "growth_conservatively_accounted": True, "snapshot_age_limit_seconds": budget.MAX_SNAPSHOT_AGE,
            "idle_between_complete_scans_seconds": budget.SCAN_INTERVAL,
            "source_sha256": {Path(path).name: prior.sha(Path(path)) for path in (__file__, budget.__file__)},
            "observed_total_bytes": actual, "conservative_reported_bytes": reported}
        if result["foreground_p95_seconds"] >= 0.05 or result["foreground_max_seconds"] >= 0.25:
            raise TimeoutError("populated-tree foreground latency threshold failed: " + json.dumps(result))
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run()
    recovery.prior.write(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
