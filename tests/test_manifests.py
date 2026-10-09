from __future__ import annotations

import hashlib
import json
import importlib.util
import io
import sys
import tempfile
import unittest
import csv
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.manifests import VIDEO_FIELDS, canonicalize_inventory, propose_source_roles
from fas import manifests


class CanonicalManifestTest(unittest.TestCase):
    def inventory(self, dataset="MSU-MFSD"):
        mapping = {"id": "synthetic", "version": 1, "model_boundary": {"bona_fide": 0, "attack": 1}}
        mapping_hash = hashlib.sha256(json.dumps(mapping, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        row = {field: "unknown" for field in VIDEO_FIELDS}
        row.update(dataset=dataset, release_id="synthetic-release", source_record_id="video-1", video_id="video-1",
                   subject_id=None if dataset == "SiW-Mv2" else "subject-001", official_split="train",
                   binary_label="bona_fide", attack_family="none", media_relpath="safe/video-1.mp4",
                   label_mapping_version=1, label_mapping_hash=mapping_hash, media_sha256=None,
                   duration_ms=None, fps=None, frame_count=None, decode_status="not_probed")
        row.update(source_eligible=True, outer_target_eligible=False)
        return {"dataset": dataset, "label_mapping": mapping, "label_mapping_hash": mapping_hash, "videos": [row]}

    def canonicalize(self, inventory):
        payload = json.dumps(inventory).encode()
        with patch.dict(manifests.MAPPING_HASHES, {inventory["dataset"]: inventory["label_mapping_hash"]}):
            return canonicalize_inventory(payload, hashlib.sha256(payload).hexdigest(), inventory["dataset"])

    def test_known_and_unknown_subject_groups_preserve_fields_and_unverified_media(self):
        for dataset in ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"):
            inventory = self.inventory(dataset)
            result = self.canonicalize(inventory)
            row = result["videos"][0]
            self.assertTrue(set(VIDEO_FIELDS).issubset(row))
            self.assertEqual(row["group_id"], row["video_id"] if dataset == "SiW-Mv2" else row["subject_id"])
            self.assertFalse(result["scientific_readiness"])
            self.assertFalse(result["roles_assigned"])
            self.assertIsNone(row["media_sha256"])

    def test_changed_bytes_and_duplicate_identity_fail_closed(self):
        inventory = self.inventory()
        payload = json.dumps(inventory).encode()
        with self.assertRaises(ValueError):
            canonicalize_inventory(payload + b"\n", hashlib.sha256(payload).hexdigest(), "MSU-MFSD")
        inventory["videos"].append(dict(inventory["videos"][0]))
        with self.assertRaises(ValueError):
            self.canonicalize(inventory)


class SourceRoleProposalTest(unittest.TestCase):
    def policy(self):
        return json.loads((ROOT / "configs/role_policy_proposal_v1.yaml").read_text())

    def canonical(self, dataset="MSU-MFSD", groups=15):
        fixture = CanonicalManifestTest()
        inventory = fixture.inventory(dataset)
        inventory["videos"] = []
        for subject in range(groups):
            for label in ("bona_fide", "attack"):
                row = fixture.inventory(dataset)["videos"][0]
                video = f"video-{subject}-{label}"
                row.update(video_id=video, source_record_id=video, media_relpath=f"safe/{video}.mp4", subject_id=None if dataset == "SiW-Mv2" else f"subject-{subject}", binary_label=label, attack_family="print" if label == "attack" else "none", source_eligible=True)
                inventory["videos"].append(row)
        return fixture.canonicalize(inventory)

    def test_deterministic_group_integrity_and_input_order_independence(self):
        canonical = self.canonical()
        result = propose_source_roles(canonical, self.policy())
        reversed_input = deepcopy(canonical)
        reversed_input["videos"].reverse()
        self.assertEqual(result, propose_source_roles(reversed_input, self.policy()))
        self.assertTrue(result["metadata_class_feasible"])
        self.assertFalse(result["roles_frozen_for_execution"])
        assigned = {}
        for row in result["videos"]:
            self.assertEqual(assigned.setdefault(row["group_id"], row["role"]), row["role"])
        self.assertTrue(all(row["role"] is None for row in canonical["videos"]))

    def test_siw_train_only_null_subject_video_groups(self):
        canonical = self.canonical("SiW-Mv2")
        canonical["videos"][-1].update(official_split="test", source_eligible=False)
        result = propose_source_roles(canonical, self.policy())
        self.assertEqual(len(result["videos"]), len(canonical["videos"]) - 1)
        self.assertTrue(all(row["subject_id"] is None and row["official_split"] == "train" for row in result["videos"]))
        policy = self.policy()
        policy["source_partitions"]["SiW-Mv2"].append("test")
        with self.assertRaises(ValueError):
            propose_source_roles(canonical, policy)

    def test_too_small_population_reports_infeasible_without_retry(self):
        result = propose_source_roles(self.canonical(groups=1), self.policy())
        self.assertFalse(result["metadata_class_feasible"])
        self.assertEqual(len(result["videos"]), 2)

    def test_no_outer_target_optimization_seed_or_hidden_policy_inputs(self):
        for change in ({"outer_target": "OULU-NPU"}, {"training_seed": 20260917}, {"split_seed": True}, {"state": "approved"}, {"initial_role_weights": {"train": 0}}, {"minimum_metadata_class_videos_per_role": 0}):
            policy = {**self.policy(), **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                propose_source_roles(self.canonical(), policy)

    def test_invalid_labels_paths_provenance_subjects_and_roles_fail_closed(self):
        fixture = CanonicalManifestTest()
        for field, value in (("dataset", "other"), ("binary_label", "unknown"), ("video_id", ""), ("media_relpath", "../outside"),
                             ("label_mapping_hash", "b" * 64), ("label_mapping_version", True), ("subject_id", None), ("role", "train")):
            inventory = fixture.inventory()
            inventory["videos"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                fixture.canonicalize(inventory)
        inventory = fixture.inventory("SiW-Mv2")
        inventory["videos"][0]["subject_id"] = "invented"
        with self.assertRaises(ValueError):
            fixture.canonicalize(inventory)

    def test_mapping_body_eligibility_and_partition_group_cuts_rejected(self):
        fixture = CanonicalManifestTest()
        inventory = fixture.inventory()
        inventory["label_mapping"]["model_boundary"]["attack"] = 0
        with self.assertRaises(ValueError):
            fixture.canonicalize(inventory)
        inventory = fixture.inventory("SiW-Mv2")
        inventory["videos"][0]["source_eligible"] = False
        with self.assertRaises(ValueError):
            fixture.canonicalize(inventory)
        canonical = self.canonical()
        canonical["videos"][0]["official_split"] = "development"
        with self.assertRaises(ValueError):
            propose_source_roles(canonical, self.policy())


class ManifestCliTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.sources = self.home / "inputs"
        self.sources.mkdir()
        self.receipts = self.home / "receipts"
        self.receipts.mkdir()
        self.receipt = self.receipts / "pins.json"
        self.output = self.home / "bundle"
        sources = {}
        self.mapping_hashes = {}
        fixture = CanonicalManifestTest()
        role_fixture = SourceRoleProposalTest()
        for dataset in sorted(manifests.CORE_DOMAINS):
            inventory = fixture.inventory(dataset)
            inventory["videos"] = role_fixture.canonical(dataset)["videos"]
            path = self.sources / f"{dataset}.json"
            path.write_text(json.dumps(inventory), encoding="utf-8")
            sources[dataset] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            self.mapping_hashes[dataset] = inventory["label_mapping_hash"]
        self.receipt.write_text(json.dumps({"version": 1, "inventories": sources}), encoding="utf-8")
        spec = importlib.util.spec_from_file_location("manifest_cli", ROOT / "scripts/build_manifests.py")
        self.cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cli)

    def command(self, *extra):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["build_manifests", "--inputs", str(self.receipt), "--policy", str(ROOT / "configs/role_policy_proposal_v1.yaml"), "--out", str(self.output), *extra]), patch.dict(manifests.MAPPING_HASHES, self.mapping_hashes), redirect_stdout(stdout), redirect_stderr(stderr):
            status = self.cli.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_private_json_csv_exports_redaction_and_unapproved_roles(self):
        status, stdout, stderr = self.command()
        self.assertEqual(status, 0, stderr)
        summary = json.loads(stdout)
        self.assertFalse(summary["roles_frozen_for_execution"])
        self.assertFalse(summary["policy_approved"])
        self.assertFalse(summary["scientific_readiness"])
        for private in (str(self.home), "subject-0", "video-0", "synthetic-release"):
            self.assertNotIn(private, stdout + stderr)
        with (self.output / "siw_mv2_metadata.csv").open(newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(tuple(reader.fieldnames), self.cli.SIWMV2_METADATA_COLUMNS)
            self.assertTrue(all(row["subject_id"] == "" for row in reader))
        for dataset, row in summary["datasets"].items():
            slug = dataset.lower().replace("-", "_")
            self.assertEqual(row["metadata_csv_sha256"], hashlib.sha256((self.output / f"{slug}_metadata.csv").read_bytes()).hexdigest())

    def test_immutable_existing_output_and_new_path_identical_rerun(self):
        self.assertEqual(self.command()[0], 0)
        first = {path.name: path.read_bytes() for path in self.output.iterdir()}
        self.assertEqual(self.command()[0], 2)
        second = self.home / "rerun"
        self.assertEqual(self.command("--out", str(second))[0], 0)
        self.assertEqual(first, {path.name: path.read_bytes() for path in second.iterdir()})

    def test_changed_or_missing_source_pins_fail_before_any_output(self):
        receipt = json.loads(self.receipt.read_bytes())
        path = Path(receipt["inventories"]["MSU-MFSD"]["path"])
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertEqual(self.command()[0], 2)
        self.assertFalse(self.output.exists())
        del receipt["inventories"]["MSU-MFSD"]
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.assertEqual(self.command()[0], 2)

    def test_private_boundaries_and_symlink_loops_rejected(self):
        for target in (ROOT / "manifests/private/forbidden", self.sources / "bundle", self.receipts / "bundle"):
            self.assertEqual(self.command("--out", str(target))[0], 2)
        link = self.home / "loop"
        link.symlink_to(link)
        status, stdout, stderr = self.command("--out", str(link))
        self.assertEqual(status, 2)
        self.assertNotIn(str(self.home), stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)
        link.unlink()
        link.symlink_to(self.home / "not-created")
        self.assertEqual(self.command("--out", str(link))[0], 2)

    def test_input_symlink_and_policy_errors_rejected(self):
        alias = self.home / "receipt-alias.json"
        alias.symlink_to(self.receipt)
        self.assertEqual(self.command("--inputs", str(alias))[0], 2)
        policy = self.home / "bad-policy.json"
        policy.write_text(json.dumps({"outer_target": "MSU-MFSD"}), encoding="utf-8")
        self.assertEqual(self.command("--policy", str(policy))[0], 2)

    def test_partial_output_failure_never_publishes_completion_marker(self):
        with patch.object(self.cli, "write_csv", side_effect=OSError("private write failure")):
            status, stdout, stderr = self.command()
        self.assertEqual(status, 2)
        self.assertFalse((self.output / "bundle_summary.json").exists())
        self.assertNotIn("private write failure", stdout + stderr)