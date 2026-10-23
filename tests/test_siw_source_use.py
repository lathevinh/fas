import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import resolve_siw293 as resolve
from fas.source_use import POLICY_PATH, load_source_use, use_binding
from fas.transactions import calibration_fit_rows
from fas.preregistration import _validate_source_use_evidence, _validate_source_dry_run


class SourceUseProposalTests(unittest.TestCase):
    def rows(self):
        result = []
        strata = (
            (("train", "train"), ("train", "branch_calibration")),
            (("train", "train"), ("train", "g_domain")),
            (("test", None), ("train", "train")),
            (("test", None), ("train", "g_domain")),
            (("test", None), ("train", "train")),
            (("train", "train"), ("train", "train")),
        )
        for pair, members in enumerate(strata):
            for split, role in members:
                index = len(result)
                result.append({
                    "index": index, "video_id": f"synthetic_{index}",
                    "official_split": split, "role": role, "binary_label": "attack",
                    "detector_status": "success", "media_sha256": f"{pair:064x}",
                    "decoded_rgb_sequence_sha256": f"{pair + 10:064x}"})
        return result

    def test_five_exclusions_preserve_test_roles_and_original_records(self):
        rows = self.rows()
        before = copy.deepcopy(rows)
        proposal = resolve.propose(rows)
        self.assertEqual(rows, before)
        self.assertEqual([item["excluded_index"] for item in proposal["exclusions"]], [0, 2, 5, 7, 9])
        self.assertEqual(proposal["proposed_active_originals"], 7)
        self.assertEqual(proposal["official_test_originals"], 3)
        self.assertEqual(proposal["historical_exact_groups"]["forbidden_unique_groups"], 5)
        self.assertEqual(proposal["proposed_effective_exact_groups"]["forbidden_unique_groups"], 0)
        self.assertEqual(proposal["proposed_effective_exact_groups"]["within_one_partition_role_class_groups"], 1)
        self.assertFalse(proposal["protocol_use_accepted"])

    def test_priority_not_detector_outcome_controls_retention(self):
        rows = self.rows()
        rows[1]["detector_status"] = "failed"
        proposal = resolve.propose(rows)
        self.assertEqual(proposal["exclusions"][0]["retained_index"], 1)
        self.assertEqual(proposal["proposed_effective_counts"]["branch_calibration"]["detector_failure"], 1)

    def test_class_crossing_is_not_waived(self):
        rows = self.rows()
        rows[0]["binary_label"] = "bona_fide"
        with self.assertRaisesRegex(ValueError, "label conflicts"):
            resolve.propose(rows)

    def test_missing_byte_sequence_corroboration_is_rejected(self):
        rows = self.rows()
        rows[0]["decoded_rgb_sequence_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "corroboration"):
            resolve.propose(rows)

    def test_test_role_or_identity_rewrite_is_rejected(self):
        for key, value in (("role", "train"), ("index", 99)):
            rows = self.rows()
            rows[4][key] = value
            with self.assertRaises(ValueError):
                resolve.propose(rows)


class AdoptedSourceUseTests(unittest.TestCase):
    def bundle(self):
        rows = SourceUseProposalTests().rows()
        transactions = []
        for row in rows:
            txn = {key: row[key] for key in ("index", "video_id", "role", "binary_label", "detector_status")}
            txn.update(technical_status="primary_frame_available", selected_frame={"synthetic": True},
                       model_score=None, classifier_error=None, final_k1_action=None)
            payload = json.dumps(txn).encode()
            transactions.append(payload)
            row["transaction_sha256"] = hashlib.sha256(payload).hexdigest()
        proposal = resolve.propose(rows)
        excluded = [item["excluded_index"] for item in proposal["exclusions"]]
        adoption = {
            "explicit_owner_adoption": True, "selected_answer": "adopt_siw293_source_use_exclusions_v1",
            "policy_id": resolve.POLICY, "private_proposal_sha256": "a" * 64,
            "governing_review_sha256": "b" * 64, "source_excluded_indices": excluded}
        adoption_bytes = json.dumps(adoption).encode()
        identity = {"version": 1, "policy_id": resolve.POLICY, "private_proposal_sha256": "a" * 64,
                    "original_plan_sha256": "c" * 64,
                    "owner_adoption_sha256": hashlib.sha256(adoption_bytes).hexdigest()}
        overlay = {**identity, "exclusions": proposal["exclusions"]}
        manifest = {**identity, "rows": [
            {**row, "dataset": "SiW-Mv2", "source_use_policy_id": resolve.POLICY,
             "source_use_eligible": row["official_split"] == "train" and row["index"] not in excluded}
            for row in rows]}
        policy = {
            **identity, "state": "owner_adopted", "source_role_retention_priority": list(resolve.PRIORITY),
            "official_test_retained": True, "archived_membership_and_roles_unchanged": True,
            "training_authorized": False, "target_evaluation_authorized": False,
            "scientific_readiness": False, "source_excluded_indices": excluded,
            "archived_originals": len(rows), "source_use_originals": proposal["proposed_source_use_originals"],
            "active_originals": proposal["proposed_active_originals"],
            "official_test_originals": proposal["official_test_originals"],
            "effective_role_counts": proposal["proposed_effective_counts"],
            "review292_sha256": "b" * 64,
            "frozen_artifact_sha256": {"siw_mv2_metadata.csv": hashlib.sha256(b"synthetic").hexdigest()}}
        return policy, manifest, overlay, adoption_bytes, transactions

    def encode(self, bundle):
        policy, manifest, overlay, adoption, _ = bundle
        manifest_bytes, overlay_bytes = json.dumps(manifest).encode(), json.dumps(overlay).encode()
        policy["effective_manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
        policy["overlay_sha256"] = hashlib.sha256(overlay_bytes).hexdigest()
        return json.dumps(policy).encode(), manifest_bytes, overlay_bytes, adoption

    def test_all_source_consumers_reject_every_excluded_and_test_row(self):
        bundle = self.bundle()
        context = load_source_use(*self.encode(bundle))
        for purpose in ("fitting", "calibration", "domain_use"):
            for row in context.rows:
                payload = bundle[4][row["index"]]
                if row["source_use_eligible"] and row["role"] == {
                        "fitting": "train", "calibration": "branch_calibration", "domain_use": "g_domain"}[purpose]:
                    bound = context.bind_transaction(payload, purpose)
                    context.require_row(bound, purpose)
                else:
                    with self.assertRaises(ValueError):
                        context.bind_transaction(payload, purpose)
        self.assertEqual(len(context.source_rows("fitting")), 2)
        self.assertEqual(len(context.source_rows("calibration")), 1)
        self.assertEqual(len(context.source_rows("domain_use")), 1)

    def test_calibration_requires_use_context_and_preserves_pending_score_behavior(self):
        bundle = self.bundle()
        context = load_source_use(*self.encode(bundle))
        metadata = context.source_rows("calibration")[0]
        row = context.bind_transaction(bundle[4][metadata["index"]], "calibration")
        with self.assertRaisesRegex(ValueError, "adopted use"):
            calibration_fit_rows([row])
        self.assertEqual(calibration_fit_rows([row], source_use=context), [])
        row["model_score"] = 0.5
        self.assertEqual(calibration_fit_rows([row], source_use=context), [row])
        wrong = dict(context.rows[0])
        with self.assertRaises(ValueError):
            calibration_fit_rows([wrong], source_use=context)
        row["transaction_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            calibration_fit_rows([row], source_use=context)

    def test_rehashed_eligibility_and_partition_tampering_fails(self):
        for mutation in ("excluded_active", "test_role", "crossing"):
            bundle = self.bundle()
            rows = bundle[1]["rows"]
            if mutation == "excluded_active":
                rows[0]["source_use_eligible"] = True
            elif mutation == "test_role":
                rows[4]["role"] = "train"
            else:
                rows[10]["media_sha256"] = rows[1]["media_sha256"]
            with self.assertRaises(ValueError):
                load_source_use(*self.encode(bundle))

    def test_changed_or_missing_adoption_or_transaction_hash_fails(self):
        bundle = self.bundle()
        encoded = self.encode(bundle)
        with self.assertRaisesRegex(ValueError, "SHA256"):
            load_source_use(*encoded[:3], b"{}")
        context = load_source_use(*encoded)
        payload = bundle[4][1] + b" "
        with self.assertRaisesRegex(ValueError, "SHA256"):
            context.bind_transaction(payload, "calibration")

    def test_normal_validator_requires_and_joins_external_use_evidence(self):
        bundle = self.bundle()
        payloads = self.encode(bundle)
        with tempfile.TemporaryDirectory() as temporary:
            root, private = Path(temporary) / "repo", Path(temporary) / "use"
            (root / "configs").mkdir(parents=True)
            private.mkdir()
            (root / POLICY_PATH).write_bytes(payloads[0])
            for name, payload in zip(("effective_use_manifest.json", "overlay.json", "owner_adoption.json"),
                                     payloads[1:], strict=True):
                (private / name).write_bytes(payload)
            rows = bundle[1]["rows"]
            metadata = {"SiW-Mv2": [dict(row) for row in rows]}
            roles = {"SiW-Mv2": [dict(row) for row in rows if row["official_split"] == "train"]}
            datasets = {"SiW-Mv2": {"metadata_source": resolve.POLICY}}
            errors = []
            _validate_source_use_evidence(root, datasets, metadata, roles,
                                         {"siw_mv2_metadata.csv": b"synthetic"}, private, {}, errors)
            self.assertEqual(errors, [])
            _validate_source_use_evidence(root, datasets, metadata, roles, None, None, {}, errors)
            self.assertTrue(any("requires --frozen-root" in item for item in errors))
            errors.clear()
            metadata["SiW-Mv2"][0]["binary_label"] = "bona_fide"
            _validate_source_use_evidence(root, datasets, metadata, roles,
                                         {"siw_mv2_metadata.csv": b"synthetic"}, private, {}, errors)
            self.assertTrue(any("archived label" in item for item in errors))
            errors.clear()
            (root / POLICY_PATH).unlink()
            _validate_source_use_evidence(root, datasets, metadata, roles, None, None, {}, errors)
            self.assertTrue(any("requires the adopted" in item for item in errors))

    def test_dry_run_requires_policy_overlay_manifest_binding_for_every_siw_source_record(self):
        bundle = self.bundle()
        payloads = self.encode(bundle)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "configs").mkdir()
            (root / POLICY_PATH).write_bytes(payloads[0])
            directory = root / "results/source-dry-run"
            directory.mkdir(parents=True)
            artifacts = {name: {"version": 1, "no_target_selection_input": True,
                                "records": [{"source_domains": ["SiW-Mv2"]}]}
                         for name in ("competence.json", "applicability.json")}
            evidence = {"version": 1, "no_target_selection_input": True,
                        "source_policy_path": "configs/source_recipe_v2.yaml"}
            for bound in (False, True):
                if bound:
                    binding = use_binding(payloads[0])
                    evidence["source_use_binding"] = binding
                    for artifact in artifacts.values():
                        artifact["records"][0]["source_use_binding"] = binding
                hashes = {}
                for name, artifact in artifacts.items():
                    payload = json.dumps(artifact).encode()
                    (directory / name).write_bytes(payload)
                    hashes[f"results/source-dry-run/{name}"] = hashlib.sha256(payload).hexdigest()
                evidence["artifact_sha256"] = hashes
                (directory / "evidence.json").write_text(json.dumps(evidence))
                errors = []
                _validate_source_dry_run(root, errors)
                binding_errors = [e for e in errors if "source-use" in e or "source consumer" in e]
                self.assertEqual(bool(binding_errors), not bound)


if __name__ == "__main__":
    unittest.main()
