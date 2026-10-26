import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from fas.frozen_features import check_feature, dino_pool, feature_key, mean_cosine_logit, normalize_rgb, parity
import pilot_source295 as pilot


class FrozenFeatureTests(unittest.TestCase):
    def test_normalization_uses_native_rgb_and_never_resizes(self):
        rgb = np.full((224, 224, 3), 255, np.uint8)
        value = normalize_rgb(rgb, 224, (0.5, 0.25, 0), (0.5, 0.25, 1))
        np.testing.assert_array_equal(value[:, 0, 0], np.array([1, 3, 1], np.float32))
        self.assertEqual(value.shape, (3, 224, 224))
        with self.assertRaises(ValueError):
            normalize_rgb(rgb, 518, (0, 0, 0), (1, 1, 1))
        with self.assertRaises(ValueError):
            normalize_rgb(rgb.astype(np.float32), 224, (0, 0, 0), (1, 1, 1))

    def test_pooling_concatenates_cls_and_patch_mean_without_registers(self):
        cls = np.full((1, 768), 2, np.float32)
        patches = np.full((1, 1369, 768), 3, np.float32)
        pooled = dino_pool(cls, patches)
        self.assertEqual(pooled.shape, (1, 1536))
        np.testing.assert_array_equal(pooled[:, :768], cls)
        np.testing.assert_array_equal(pooled[:, 768:], patches.mean(axis=1))
        with self.assertRaises(ValueError):
            dino_pool(cls, np.zeros((1, 1373, 768), np.float32))

    def test_cache_key_is_label_free_and_binds_image_checkpoint_and_recipe(self):
        values = dict(dataset="synthetic", video_id="sample", crop_sha256="a" * 64,
                      checkpoint_sha256="b" * 64, preprocessing_sha256="c" * 64, representation="cls_mean")
        key = feature_key(**values)
        self.assertEqual(key, feature_key(**values))
        for field in ("crop_sha256", "checkpoint_sha256", "preprocessing_sha256"):
            self.assertNotEqual(key, feature_key(**{**values, field: "d" * 64}))
        with self.assertRaises(TypeError):
            feature_key(**values, binary_label="attack")

    def test_parity_enforces_exact_shape_finite_fp32_and_numeric_threshold(self):
        value = np.ones((2, 3), np.float32)
        self.assertEqual(parity(value, value.copy()), 0)
        changed = value.copy()
        changed[0, 0] += 1e-4
        with self.assertRaises(ValueError):
            parity(value, changed)
        for invalid in (value.astype(np.float16), value[:, :2], np.full_like(value, np.nan)):
            with self.assertRaises(ValueError):
                check_feature(invalid, 2, 3)

    def test_prompt_logit_is_mean_cosine_attack_minus_live(self):
        images = np.array([[1, 0], [0, 1]], np.float32)
        text = np.array([[1, 0], [1, 0], [0, 1], [0, 1]], np.float32)
        np.testing.assert_array_equal(mean_cosine_logit(images, text, 2), np.array([-1, 1], np.float32))
        with self.assertRaises(ValueError):
            mean_cosine_logit(np.zeros_like(images), text, 2)

    def test_checkpoint_acquisition_checks_eof_sha_and_rejects_retry(self):
        payload = b"synthetic-checkpoint"
        spec = {"url": "https://example.invalid/fixture", "bytes": len(payload),
                "upstream_sha256": hashlib.sha256(payload).hexdigest()}
        approval = {"work_deadline_unix_seconds": time.time() + 30, "caps": {"output_bytes": 1024 ** 2}}
        with tempfile.TemporaryDirectory() as temporary:
            native, private = Path(temporary) / "native", Path(temporary) / "private"
            native.mkdir()
            private.mkdir()
            response = io.BytesIO(payload)
            response.headers = {"Content-Length": str(len(payload))}
            with patch.object(pilot, "NATIVE", native), patch.object(pilot, "APPROVAL_ROOT", private):
                with patch.object(pilot.urllib.request, "urlopen", return_value=response):
                    result = pilot.acquire("synthetic", spec, approval)
                self.assertEqual(result["sha256"], spec["upstream_sha256"])
                with self.assertRaises(FileExistsError):
                    pilot.acquire("synthetic", spec, approval)

    def test_original_deadline_and_combined_storage_are_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            native, private = Path(temporary) / "native", Path(temporary) / "private"
            native.mkdir()
            private.mkdir()
            (native / "fixture.part").write_bytes(b"123")
            (private / "fixture.json").write_bytes(b"456")
            with patch.object(pilot, "NATIVE", native), patch.object(pilot, "APPROVAL_ROOT", private):
                with self.assertRaises(MemoryError):
                    pilot.enforce({"work_deadline_unix_seconds": time.time() + 30, "caps": {"output_bytes": 5}})
                with self.assertRaises(TimeoutError):
                    pilot.enforce({"work_deadline_unix_seconds": time.time() - 1, "caps": {"output_bytes": 100}})

    def test_wrong_download_hash_is_not_promoted(self):
        payload = b"bad"
        response = io.BytesIO(payload)
        response.headers = {"Content-Length": "3"}
        spec = {"url": "https://example.invalid/fixture", "bytes": 3, "upstream_sha256": "0" * 64}
        approval = {"work_deadline_unix_seconds": time.time() + 30, "caps": {"output_bytes": 1024}}
        with tempfile.TemporaryDirectory() as temporary:
            native, private = Path(temporary) / "native", Path(temporary) / "private"
            native.mkdir()
            private.mkdir()
            with patch.object(pilot, "NATIVE", native), patch.object(pilot, "APPROVAL_ROOT", private):
                with patch.object(pilot.urllib.request, "urlopen", return_value=response):
                    with self.assertRaises(ValueError):
                        pilot.acquire("synthetic", spec, approval)
            self.assertFalse((native / "checkpoints/synthetic.pth").exists())

    def test_worker_failure_retains_explicit_failed_terminal_and_never_retries(self):
        class Child:
            pid = 99999999
            returncode = 1

            def poll(self):
                return self.returncode

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private, native = root / "private", root / "native"
            private.mkdir()
            approval = {
                "started_unix_seconds": time.time(), "work_deadline_unix_seconds": time.time() + 30,
                "deadline_unix_seconds": time.time() + 60,
                "caps": {"output_bytes": 1024 ** 2, "rss_bytes": 1024 ** 3}}
            with patch.object(pilot, "NATIVE", native), patch.object(pilot, "APPROVAL_ROOT", private), \
                    patch.object(pilot, "ROOT", root), patch.object(pilot, "authority", return_value=({}, approval)), \
                    patch.object(pilot, "digest", return_value="a" * 64), \
                    patch.object(pilot.subprocess, "Popen", return_value=Child()) as spawn:
                self.assertEqual(pilot.supervise(), 1)
                self.assertEqual(spawn.call_count, 1)
            result = json.loads((private / "terminal.json").read_bytes())
            self.assertEqual(result["status"], "stopped_no_retry")
            self.assertIn("worker exit1", result["failure"])
            self.assertFalse(result["automatic_retry"])
            self.assertIsNone(result["worker_completion_sha256"])
            self.assertFalse(result["scientific_readiness"])


if __name__ == "__main__":
    unittest.main()
