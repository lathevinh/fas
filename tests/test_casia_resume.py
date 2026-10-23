"""Partial reuse, exact153 staging and native-count receipt readback regressions."""

from contextlib import ExitStack, nullcontext
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import resume_casia289 as job
import test_casia_preprocessing as fixtures
import casia_budget289 as budget


class ResumeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "existing FFmpeg required")
    def test_budgeted_real_probe_replay_png_and_saved_readback_preserve_rgb(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            source = root / "synthetic.avi"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "testsrc2=size=64x64:rate=25:duration=1", "-c:v", "mpeg4",
                            "-bf", "2", "-g", "12", "-threads", "1", str(source)],
                           check=True, capture_output=True)
            for module, name in (
                (job.previous, "OUTPUT"), (job.prior, "OUTPUT"), (job.prior.shared, "OUTPUT"),
                (job.previous.probe, "measured"), (job.previous.probe.diagnosis, "enforce"),
                (job.prior.shared, "write_immutable_record"), (job.prior.shared, "write_png"),
                (job.previous.probe, "capture"), (job.previous, "strict_replay"),
            ):
                stack.enter_context(patch.object(module, name, getattr(module, name)))
            stack.enter_context(patch.object(job, "OUTPUT", root))
            stack.enter_context(patch.object(job, "enforce"))
            controls, binding = root / "control", {"synthetic": True}
            budget.initialize(controls, binding)
            budget.scan_once([root], controls, binding, job.prior.shared.retained.tree_bytes)
            client = budget.Client(controls, binding,
                                   lambda group: job.prior.shared.usage(group, root / ".unused"), lambda value: None)
            job.configure(client)
            prefix = root / "probe/0000"
            media = job.previous.probe.probe_video(source, prefix)
            self.assertEqual(media["decode_status"], "decoded", media)
            self.assertEqual(media["frame_count"], 25)
            media.update(media_sha256=job.prior.sha(source), byte_size=source.stat().st_size,
                         probe_evidence_sha256={file.relative_to(root).as_posix(): job.prior.sha(file)
                                                for file in prefix.iterdir()})
            job.prior.write(root / "media/0000.json", media)
            self.assertEqual(job.verify_probe(0)["decoded_rgb_sequence_sha256"], media["decoded_rgb_sequence_sha256"])
            selected, frames = (media["frame_count"] - 1) // 2, []
            job.previous.strict_replay(source, media, lambda order, rgb: frames.append(rgb.copy())
                                       if order == selected else None, root / "replay/0000")
            asset = job.prior.shared.write_png("frames/0000.png", frames[0])
            self.assertEqual(asset["RGB_sha256"], media["frame_index"][selected]["rgb_sha256"])
            budget.scan_once([root], controls, binding, job.prior.shared.retained.tree_bytes)
            self.assertGreaterEqual(client.measure(os.getpgrp())["output_bytes"],
                                    job.prior.shared.retained.tree_bytes(root))
            state = budget.read_control(controls / "writes.json", binding)
            self.assertEqual(state["reserved"], state["completed"])

    def test_exact153_gate_rejects_restarting_retained_or_dropping_originals(self):
        plan = {"videos": [None] * 600, "remaining_indices": list(range(447, 600))}
        job.check_remaining(plan)
        for indices in (list(range(600)), list(range(448, 600)), [447] * 153):
            with self.subTest(indices=len(indices)), self.assertRaises(ValueError):
                job.check_remaining({**plan, "remaining_indices": indices})

    def test_real_copy_keeps_source_immutable_and_rejects_wrong_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.write_bytes(b"retained RGB evidence")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            identity = job.prior.shared.identity(source)
            job.copy_file(source, root / "copied", digest)
            self.assertEqual((root / "copied").read_bytes(), source.read_bytes())
            self.assertEqual(job.prior.shared.identity(source), identity)
            with self.assertRaisesRegex(ValueError, "retained source drift"):
                job.copy_file(source, root / "wrong", "0" * 64)

    def test_native_count_is_hashed_but_not_misread_as_a_subprocess_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "probe/0000"
            folder.mkdir(parents=True)
            (folder / "original-metadata.stdout").write_text("{}")
            (folder / "original-metadata.stderr").write_bytes(b"")
            command = {"returncode": 0, "stdout_bytes": 2, "stderr_bytes": 0,
                       "stdout_sha256": job.prior.sha(folder / "original-metadata.stdout"),
                       "stderr_sha256": job.prior.sha(folder / "original-metadata.stderr")}
            (folder / "original-metadata.json").write_text(json.dumps(command))
            (folder / "native-count.json").write_text('{"decoded_pictures":131}')
            (folder / "probe_result.json").write_text("{}")
            media = {"decode_status": "decoded", "probe_evidence_sha256": {
                file.relative_to(root).as_posix(): job.prior.sha(file) for file in folder.iterdir()}}
            with patch.object(job, "OUTPUT", root):
                job.verify_commands(folder, media)
                (folder / "native-count.json").write_text('{"decoded_pictures":132}')
                with self.assertRaisesRegex(ValueError, "evidence drift"):
                    job.verify_commands(folder, media)

    @unittest.skipUnless(fixtures.EXTRACTOR, "existing bsdtar not available")
    def test_actual_extractor_stages_only153_members_not_the600_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "old", root / "new"
            source.mkdir()
            output.mkdir()
            archive = root / "release.rar"
            videos, entries, pins = [], [], {}
            for index in range(600):
                name, payload = f"train_release/{index:04d}.avi", f"payload-{index}".encode()
                videos.append({"media_relpath": name, "byte_size": len(payload)})
                entries.append((name, payload, False))
                pins[name] = {"sha256": hashlib.sha256(payload).hexdigest(), "byte_size": len(payload),
                              "crc32": zlib.crc32(payload)}
            archive.write_bytes(fixtures.stored_rar(entries))
            job.prior.write(source / "release_integrity.json", {"video_payload_pins": pins})
            plan = {"videos": videos, "remaining_indices": list(range(447, 600)),
                    "headers": [], "crc_headers": [], "deadline_unix_seconds": __import__("time").time() + 30}
            client = Mock()
            client.reserve.side_effect = lambda size: nullcontext()
            with (patch.object(job, "SOURCE", source), patch.object(job, "OUTPUT", output),
                  patch.object(job.prior, "ARCHIVE", archive), patch.object(job.prior, "EXTRACTOR", Path(fixtures.EXTRACTOR)),
                  patch.object(job.prior, "guard"), patch.object(job.prior, "list_headers", return_value=[]),
                  patch.object(job.prior, "read_file_headers", return_value=[]), patch.object(job, "enforce")):
                job.stage_remaining(plan, client)
            actual = {file.relative_to(output / "temporary").as_posix()
                      for file in (output / "temporary").rglob("*") if file.is_file()}
            self.assertEqual(actual, {row["media_relpath"] for row in videos[447:]})
            self.assertEqual(job.prior.read(output / "selective_staging.json")["new_extracted_videos"], 153)

    def run_worker(self, output, *, systemic=False):
        videos, _, _ = fixtures.CasiaPreprocessingTest().population()
        plan = {"videos": videos, "remaining_indices": list(range(447, 600))}
        retained = [{"video_id": row["video_id"], "frame_count": 3, "byte_size": row["byte_size"]}
                    for row in videos[:447]]
        called = []

        def produce(plan, index, original, session):
            called.append(index)
            media = {"video_id": original["video_id"], "frame_count": 0 if systemic else 3,
                     "byte_size": original["byte_size"], "failure_reason": "specific" if systemic else None}
            if systemic:
                media["probe_failure"] = {"stage": "native_clock", "reason": "specific"}
            return {"role": original["role"], "detector_status": "not_run" if systemic else "success"}, media

        ort = types.SimpleNamespace(SessionOptions=lambda: types.SimpleNamespace(),
                                    InferenceSession=lambda *args, **kwargs:
                                    types.SimpleNamespace(get_providers=lambda: ["CPUExecutionProvider"]))
        client = Mock()
        with (patch.object(job, "OUTPUT", output), patch.object(job, "reuse", return_value=retained) as reuse,
              patch.object(job, "stage_remaining") as stage, patch.object(job, "enforce"),
              patch.object(job.previous, "produce_unit", side_effect=produce),
              patch.object(job.prior.shared, "exact_checks", return_value=[]),
              patch.object(job.prior, "cleanup"), patch.dict(sys.modules, {"onnxruntime": ort})):
            if systemic:
                with self.assertRaisesRegex(RuntimeError, "three consecutive"):
                    job.worker(plan, client)
            else:
                job.worker(plan, client)
                self.assertEqual(job.prior.read(output / "worker_completion.json")["retained_without_decode_or_inference"], 447)
            reuse.assert_called_once()
            stage.assert_called_once()
        return called

    def test_worker_never_calls_producer_on_any_of447_retained_units(self):
        with tempfile.TemporaryDirectory() as directory:
            called = self.run_worker(Path(directory))
            self.assertEqual(called, list(range(447, 600)))

    def test_three_same_remaining_failures_stop_without_extra_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            called = self.run_worker(Path(directory), systemic=True)
            self.assertEqual(called, [447, 448, 449])
            self.assertFalse(job.prior.read(Path(directory) / "systemic_stop.json")["automatic_retry"])

    def test_cleanup_uses_final_deadline_not_the_expired_work_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approval = {"deadline_unix_seconds": __import__("time").time() + 5}
            lease = {"parent_pid": os.getppid(), "plan_sha256": "fixed"}
            with (patch.object(job, "OUTPUT", root), patch.object(job, "authority", return_value=approval),
                  patch.object(job.prior, "OUTPUT", job.prior.OUTPUT),
                  patch.object(job.prior.shared, "OUTPUT", job.prior.shared.OUTPUT),
                  patch.object(job.prior, "read", side_effect=[{}, lease]),
                  patch.object(job.prior, "sha", return_value="fixed"),
                  patch.object(job.os, "getsid", return_value=os.getpid()),
                  patch.object(job.prior.shared.retained, "arm_deadline") as arm,
                  patch.object(job.prior, "cleanup") as cleanup,
                  patch.object(sys, "argv", ["resume_casia289.py", "--cleanup"])):
                self.assertEqual(job.main(), 0)
                arm.assert_called_once_with(approval["deadline_unix_seconds"])
                cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
