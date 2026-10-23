"""Keep complete historical storage scans off the strict-probe critical path."""

import json
import os
from pathlib import Path
import tempfile
import threading
import time

import casia_probe287 as probe

MAX_SNAPSHOT_AGE = 30


def publish(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".usage-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


class HistoricalStorage:
    def __init__(self, roots, current, snapshot, binding):
        self.roots = tuple(roots)
        self.current = current
        self.snapshot = snapshot
        self.binding = binding
        if current in self.roots or len(set(self.roots)) != len(self.roots):
            raise ValueError("disjoint historical roots required")
        self.peaks = {str(root): 0 for root in self.roots}
        self.error = None
        self.stop = threading.Event()
        self.thread = None

    def scan(self):
        started = time.monotonic()
        for root in self.roots:
            self.peaks[str(root)] = max(self.peaks[str(root)], probe.prior.shared.retained.tree_bytes(root))
        publish(self.snapshot, {
            "binding": self.binding, "root_peak_bytes": self.peaks,
            "completed_unix_seconds": time.time(), "scan_seconds": time.monotonic() - started,
            "historical_storage_is_conservatively_monotone": True})

    def start(self):
        self.scan()
        self.thread = threading.Thread(target=self._scan_forever, daemon=True)
        self.thread.start()
        return self

    def _scan_forever(self):
        try:
            while not self.stop.wait(0.05):
                self.scan()
        except Exception as error:
            self.error = error

    def measure(self, group):
        if self.error is not None:
            raise RuntimeError("historical storage scan failed") from self.error
        return measured(group, self.current, self.snapshot, self.binding)

    def close(self):
        self.stop.set()
        if self.thread is not None:
            self.thread.join(timeout=MAX_SNAPSHOT_AGE)
            if self.thread.is_alive():
                raise TimeoutError("historical storage scanner failed to stop")
        if self.error is not None:
            raise RuntimeError("historical storage scan failed") from self.error


def measured(group, current, snapshot, binding):
    saved = json.loads(snapshot.read_text())
    if saved["binding"] != binding:
        raise ValueError("historical storage snapshot lease drift")
    age = time.time() - saved["completed_unix_seconds"]
    if not 0 <= age <= MAX_SNAPSHOT_AGE:
        raise TimeoutError("historical storage snapshot stale")
    value = probe.prior.shared.usage(group, current / ".unused")
    value["output_bytes"] = (sum(saved["root_peak_bytes"].values())
                             + probe.prior.shared.retained.tree_bytes(current)
                             + value["temporary_bytes"])
    return value
