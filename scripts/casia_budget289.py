"""Asynchronous storage snapshots plus conservative single-writer reservations."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from casia_resource287 import publish

SCAN_INTERVAL = 30
MAX_SNAPSHOT_AGE = 90
CONTROL_RESERVE = 256 * 1024 ** 2
MAX_CONTROL_BYTES = 1024 ** 2


class BudgetError(RuntimeError):
    pass


def read_control(path, binding):
    with path.open("rb") as stream:
        payload = stream.read(MAX_CONTROL_BYTES + 1)
    if len(payload) > MAX_CONTROL_BYTES:
        raise BudgetError("observer control byte cap")
    value = json.loads(payload)
    if value["binding"] != binding:
        raise BudgetError("observer lease/plan binding drift")
    return value


def initialize(directory, binding):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "writes.json"
    if path.exists():
        raise FileExistsError("write journal already exists")
    publish(path, {"binding": binding, "reserved": 0, "completed": 0})


def scan_once(roots, directory, binding, tree_bytes):
    started = time.time()
    state = read_control(directory / "writes.json", binding)
    if not 0 <= state["completed"] <= state["reserved"]:
        raise BudgetError("invalid write journal")
    total = sum(tree_bytes(root) for root in roots)
    publish(directory / "snapshot.json", {
        "binding": binding, "scan_started": started, "scan_completed": time.time(),
        "output_bytes": total, "completed_credit": state["completed"], "error": None})


def scan_forever(roots, directory, binding, tree_bytes):
    try:
        while True:
            scan_once(roots, directory, binding, tree_bytes)
            time.sleep(SCAN_INTERVAL)
    except Exception as error:
        publish(directory / "snapshot.json", {
            "binding": binding, "error": type(error).__name__ + ": " + str(error)})
        raise


class Client:
    def __init__(self, directory, binding, usage, enforce):
        self.directory, self.binding = directory, binding
        self.usage, self.enforce = usage, enforce
        self.depth = 0

    def measure(self, group):
        snapshot = read_control(self.directory / "snapshot.json", self.binding)
        if snapshot["error"] is not None:
            raise BudgetError("storage scanner failed: " + snapshot["error"])
        age = time.time() - snapshot["scan_started"]
        if not 0 <= age <= MAX_SNAPSHOT_AGE:
            raise BudgetError("storage snapshot stale")
        state = read_control(self.directory / "writes.json", self.binding)
        credit = snapshot["completed_credit"]
        if not 0 <= credit <= state["completed"] <= state["reserved"]:
            raise BudgetError("write reservation/scan credit drift")
        value = self.usage(group)
        value["output_bytes"] = (snapshot["output_bytes"] + state["reserved"] - credit
                                 + CONTROL_RESERVE + value["temporary_bytes"])
        return value

    @contextmanager
    def reserve(self, size):
        if type(size) is not int or size < 0:
            raise BudgetError("nonnegative integer write reservation required")
        path = self.directory / "writes.json"
        state = read_control(path, self.binding)
        if self.depth == 0 and state["completed"] != state["reserved"]:
            raise BudgetError("previous producer left unfinished reservations")
        state["reserved"] += size
        self.depth += 1
        publish(path, state)
        try:
            self.enforce(self.measure(os.getpgrp()))
            yield
            self.enforce(self.measure(os.getpgrp()))
        finally:
            self.depth -= 1
            if self.depth == 0:
                state = read_control(path, self.binding)
                state["completed"] = state["reserved"]
                publish(path, state)


def limited_command(command, maximum_file_bytes):
    bootstrap = ("import os,resource,sys;"
                 "n=int(sys.argv[1]);resource.setrlimit(resource.RLIMIT_FSIZE,(n,n));"
                 "os.execvp(sys.argv[2],sys.argv[2:])")
    import sys
    return [sys.executable, "-c", bootstrap, str(maximum_file_bytes), *command]


def stop_group(process, timeout=0.5):
    if process.poll() is not None:
        process.wait()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=timeout)
