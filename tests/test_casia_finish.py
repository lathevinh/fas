"""Native-filesystem IPC and the explicitly approved136-only continuation."""

from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import Mock, patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import finish_casia289 as job
import test_casia_preprocessing as fixtures


class FinishTests(unittest.TestCase):
    def test_native_control_publication_has_no_missing_or_partial_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "control.json"
            job.base.budget.publish(path, {"serial": 0})
            done, errors = threading.Event(), []

            def read():
                while not done.is_set():
                    try:
                        self.assertIsInstance(json.loads(path.read_bytes())["serial"], int)
                    except Exception as error:
                        errors.append(type(error).__name__)
                        done.set()

            reader = threading.Thread(target=read)
            reader.start()
            try:
                for serial in range(100):
                    job.base.budget.publish(path, {"serial": serial})
            finally:
                done.set()
                reader.join(2)
            self.assertFalse(reader.is_alive())
            self.assertEqual(errors, [])

    @unittest.skipUnless(fixtures.EXTRACTOR, "existing bsdtar not available")
    def test_actual_rar_restage_selects_exactly136_and_never_restarts464(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "release.rar"
            output, handoff = root / "output", root / "handoff"
            (output / "temporary").mkdir(parents=True)
            handoff.mkdir()
            videos, entries, pins = [], [], {}
            for index in range(600):
                name, payload = f"train_release/{index:04d}.avi", f"value-{index}".encode()
                videos.append({"media_relpath": name, "byte_size": len(payload)})
                entries.append((name, payload, False))
                pins[name] = {"byte_size": len(payload), "crc32": zlib.crc32(payload),
                              "sha256": hashlib.sha256(payload).hexdigest()}
            archive.write_bytes(fixtures.stored_rar(entries))
            job.prior.write(output / "release_integrity.json", {"video_payload_pins": pins})
            plan = {"videos": videos, "headers": [], "crc_headers": [],
                    "deadline_unix_seconds": __import__("time").time() + 30}
            client = Mock()
            client.reserve.side_effect = lambda size: nullcontext()
            with (patch.object(job, "OUTPUT", output), patch.object(job, "HANDOFF", handoff),
                  patch.object(job.prior, "ARCHIVE", archive), patch.object(job.prior, "EXTRACTOR", Path(fixtures.EXTRACTOR)),
                  patch.object(job.prior, "guard"), patch.object(job.prior, "list_headers", return_value=[]),
                  patch.object(job.prior, "read_file_headers", return_value=[]), patch.object(job.base, "enforce")):
                with self.assertRaisesRegex(ValueError, "exact136"):
                    job.stage(plan, client, list(range(447, 600)))
                job.stage(plan, client, list(range(464, 600)))
            actual = {file.relative_to(output / "temporary").as_posix()
                      for file in (output / "temporary").rglob("*") if file.is_file()}
            self.assertEqual(actual, {row["media_relpath"] for row in videos[464:]})
            self.assertEqual(job.prior.read(handoff / "restaging.json")["new_extracted_videos"], 136)

    def test_worker_only_produces136_and_preserves_overall153_accounting(self):
        with tempfile.TemporaryDirectory() as directory:
            videos, _, _ = fixtures.CasiaPreprocessingTest().population()
            media = [{"video_id": row["video_id"], "frame_count": 3, "byte_size": row["byte_size"]}
                     for row in videos[:464]]
            called = []

            def produce(plan, index, original, session):
                called.append(index)
                return {"role": original["role"], "detector_status": "success"}, {
                    "video_id": original["video_id"], "frame_count": 3, "byte_size": original["byte_size"],
                    "failure_reason": None}

            ort = types.SimpleNamespace(SessionOptions=lambda: types.SimpleNamespace(),
                                        InferenceSession=lambda *args, **kwargs:
                                        types.SimpleNamespace(get_providers=lambda: ["CPUExecutionProvider"]))
            output = Path(directory)
            with (patch.object(job, "OUTPUT", output), patch.object(job, "retained", return_value=media),
                  patch.object(job, "stage"), patch.object(job.base, "enforce"),
                  patch.object(job.base.previous, "produce_unit", side_effect=produce),
                  patch.object(job.prior.shared, "exact_checks", return_value=[]),
                  patch.object(job.prior, "cleanup"), patch.dict(sys.modules, {"onnxruntime": ort})):
                job.worker({"videos": videos}, {"remaining_indices": list(range(464, 600))}, Mock())
            self.assertEqual(called, list(range(464, 600)))
            completion = job.prior.read(output / "worker_completion.json")
            self.assertEqual(completion["new_attempts"], 153)
            self.assertEqual(completion["handoff_new_attempts"], 136)
            self.assertEqual(completion["transactions"], 600)


if __name__ == "__main__":
    unittest.main()
