from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.oulu import LABEL_MAPPING, LABEL_MAPPING_HASH, encode_label, inventory_archives, parse_protocol, parse_video_id
from fas.media import probe_video
from fas.transactions import calibration_fit_rows, select_primary_frame, technical_population_counts, technical_transaction, validate_transaction_policy


class OuluHumanReviewTest(unittest.TestCase):
    def test_batch07_categorical_import_strict_answers_and_preserved_AI_uncertainty(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch07 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")},
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 66 else "rejected_false_positive"} for rank in module.TARGET_RANKS]
            definition = {"sha256": digest, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch07_categorical_review", "review_definition_sha256": digest,
                     "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True},
                     "reviewed_at_utc": "2026-10-15T10:00:00Z", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [1, False, None]},
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True, "same_or_derived_content": False,
                                "personal_inspection_attested": True, "owner_decision_attested": True, "capture_provenance_certified": False,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [True, None]}} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            self.assertEqual(sum(row["disagreement_with_AI"] for row in rows), 1)
            self.assertEqual(rows[6]["ai_disposition"], "uncertain_insufficient_evidence")
            self.assertEqual(rows[6]["comparison_disposition"], "uncertain_insufficient_evidence")
            self.assertEqual(rows[6]["disposition"], "rejected_false_positive")
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertFalse(row["effective_disposition_activated"] or row["counts_as_accepted_current_effective_disposition"])
                self.assertTrue(row["semantic_acceptance_pending"])
                self.assertNotIn("rationale", row)
            for field, value in (("queue_rank", 60.0), ("queue_rank", True), ("queue_rank", 61), ("packet_sha256", "drift"), ("ai_record_sha256", "drift"),
                                 ("exact_pair_record_sha256", "drift"), ("reviewed_assets_sha256", {}), ("evidence_sufficient", 1), ("same_or_derived_content", 0),
                                 ("same_or_derived_content", None), ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("capture_provenance_certified", 0),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", False),
                                 ("ai_disposition", "rejected_false_positive"), ("semantic_acceptance_pending", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch06_categorical_review"}, {"review_definition_sha256": "drift"},
                            {"review194_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T10:00:00"},
                            {"reviewed_at_utc": "2026-10-15T10:00:00+01:00"}, {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}},
                            {"reviewer": {**human["reviewer"], "id": " "}}, {"pairs": human["pairs"][:-1]}, {"stop_for_prospective_scientific_decision": True}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for changes in ({"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 60.0}, *pairs[1:]]},
                            {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"review194_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}):
                with self.assertRaises(ValueError):
                    module.validate_categorical(human, {**definition, **changes})
            for rule in module.CATEGORICAL_RULES:
                stop = rule["same_or_derived_content"] is True
                changed = {**human["pairs"][6], **rule, "stop_for_prospective_scientific_decision": stop}
                result = module.validate_categorical({**human, "pairs": [*human["pairs"][:6], changed, *human["pairs"][7:]], "stop_for_prospective_scientific_decision": stop}, definition)[6]
                self.assertEqual(result["validated_disposition"], rule["disposition"])
                self.assertEqual(result["stop_for_prospective_scientific_decision"], stop)
                self.assertEqual(result["reconciliation_required"], rule["disposition"] != "uncertain_insufficient_evidence")
                self.assertEqual(result["comparison_disposition"], "uncertain_insufficient_evidence")
                self.assertEqual(result["disposition"], rule["disposition"])
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            self.assertEqual(len(module.validate_categorical({**human, "pairs": list(reversed(human["pairs"]))}, definition)), 10)
            check = {"head_sha": "3f648377a7d273fc1f35202d101692423e4d9d40", "run_id": 38710625142, "job_id": 116340807019,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 197, "review196_sha256": module.REVIEW196_SHA256, "import_authority": module.IMPORT_AUTHORITY,
                         "handoff195_CI": check, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 197.0}, {"review196_sha256": "drift"}, {"import_authority": "prepare_only"}, {"activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"handoff195_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"handoff195_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch07-import", root / "review/overlap"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "preflight.json", review_root=root / "review", human_input=root / "review/input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch07_categorical_handoff_authority_blank_answers_and_uncertainty(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch07 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 66 else "rejected_false_positive",
                      "ai_observations": ["</script>"], "human_review_notice": module.human_notice(rank),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "preflight_sha256": digest, "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "ai_record_sha256:pair.ai_record_sha256", "exact_pair_record_sha256:pair.exact_pair_record_sha256",
                             "review194_sha256:DATA.definition.review194_sha256", "batch07_categorical_review", "oulu-batch07-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "imported_human_record", "review184", "rank47", "batch06_categorical_review"):
                self.assertNotIn(fragment, page)
            for changes in ({"review194_sha256": digest}, {"accepted_AI_report_sha256": digest}, {"preflight_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 60.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_record_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_disposition": "clear"}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            check = {"head_sha": "7f998d71dabd8f629f9f117970ce58acdacf7931", "run_id": 38706506199, "job_id": 116327125698,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 195, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "queue_ranks": list(module.TARGET_RANKS), "source193_CI": check,
                         **{field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 195.0}, {"queue_ranks": list(range(70, 80))}, {"queue_ranks": [60.0, *range(61, 70)]},
                            {"human_input_collection_authorized": True}, {"import_authorized": True}, {"effective_activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"review194_sha256": digest},
                            {"source193_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"source193_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            self.assertIn("underexposure", module.human_notice(66))
            self.assertNotIn("uncertain_insufficient_evidence", module.human_notice(66))
            for rank in (67, 68):
                self.assertIn("correlated", module.human_notice(rank))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch07-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch06_categorical_import_strict_answers_bindings_and_owner_preservation(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch06 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")},
                      "ai_disposition": "rejected_false_positive"} for rank in module.TARGET_RANKS]
            definition = {"sha256": digest, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch06_categorical_review", "review_definition_sha256": digest,
                     "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True},
                     "reviewed_at_utc": "2026-10-15T07:00:00Z", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [1, False, None]},
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True, "same_or_derived_content": False,
                                "personal_inspection_attested": True, "owner_decision_attested": True, "capture_provenance_certified": False,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [True, None]}} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertFalse(row["effective_disposition_activated"] or row["reconciliation_required"])
                self.assertTrue(row["semantic_acceptance_pending"])
                self.assertNotIn("rationale", row)
            for field, value in (("queue_rank", 50.0), ("queue_rank", True), ("queue_rank", 51), ("packet_sha256", "drift"), ("ai_record_sha256", "drift"),
                                 ("exact_pair_record_sha256", "drift"), ("reviewed_assets_sha256", {}), ("evidence_sufficient", 1), ("same_or_derived_content", 0),
                                 ("same_or_derived_content", None), ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("capture_provenance_certified", 0),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", False),
                                 ("ai_disposition", "rejected_false_positive"), ("semantic_acceptance_pending", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch05_targeted_categorical_review"}, {"review_definition_sha256": "drift"},
                            {"review184_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T07:00:00"},
                            {"reviewed_at_utc": "2026-10-15T07:00:00+01:00"}, {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}},
                            {"reviewer": {**human["reviewer"], "id": " "}}, {"pairs": human["pairs"][:-1]}, {"stop_for_prospective_scientific_decision": True}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for changes in ({"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 50.0}, *pairs[1:]]},
                            {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"review184_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}):
                with self.assertRaises(ValueError):
                    module.validate_categorical(human, {**definition, **changes})
            for rule in module.CATEGORICAL_RULES:
                stop = rule["same_or_derived_content"] is True
                changed = {**human["pairs"][0], **rule, "stop_for_prospective_scientific_decision": stop}
                result = module.validate_categorical({**human, "pairs": [changed, *human["pairs"][1:]], "stop_for_prospective_scientific_decision": stop}, definition)[0]
                self.assertEqual(result["validated_disposition"], rule["disposition"])
                self.assertEqual(result["stop_for_prospective_scientific_decision"], stop)
                self.assertEqual(result["reconciliation_required"], rule["disposition"] != "rejected_false_positive")
                self.assertEqual(result["comparison_disposition"], "uncertain_insufficient_evidence" if result["reconciliation_required"] else result["disposition"])
                self.assertEqual(result["disposition"], rule["disposition"])
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            self.assertEqual(len(module.validate_categorical({**human, "pairs": list(reversed(human["pairs"]))}, definition)), 10)
            check = {"head_sha": "ad9d5d7edc86a69e2e48a40f4a0ec13ed1d75a16", "run_id": 38690950258, "job_id": 116276475624,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 187, "review186_sha256": module.REVIEW186_SHA256, "import_authority": module.IMPORT_AUTHORITY,
                         "handoff185_CI": check, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 187.0}, {"review186_sha256": "drift"}, {"import_authority": "prepare_only"}, {"activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, *({"handoff185_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch06-import", root / "review/overlap"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "preflight.json", review_root=root / "review", human_input=root / "review/input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch06_categorical_handoff_exact_authority_blank_answers_and_notices(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch06 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "ai_observations": ["</script>"], "human_review_notice": module.human_notice(rank),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "preflight_sha256": digest, "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "ai_record_sha256:pair.ai_record_sha256", "exact_pair_record_sha256:pair.exact_pair_record_sha256",
                             "review184_sha256:DATA.definition.review184_sha256", "batch06_categorical_review", "oulu-batch06-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "imported_human_record", "governance_sha256", "review168", "rank47", "batch05_targeted"):
                self.assertNotIn(fragment, page)
            for changes in ({"review184_sha256": digest}, {"accepted_AI_report_sha256": digest}, {"preflight_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 50.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_record_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            check = {"head_sha": "38e0263c0e20d0d3a27df431142a6550335d8db6", "run_id": 38683111522, "job_id": 116251844389,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 185, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "queue_ranks": list(module.TARGET_RANKS), "source183_CI": check,
                         **{field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 183}, {"queue_ranks": list(range(60, 70))}, {"queue_ranks": [50.0, *range(51, 60)]},
                            {"human_input_collection_authorized": True}, {"import_authorized": True}, {"effective_activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"review184_sha256": digest},
                            *({"source183_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            self.assertIn("Haze", module.human_notice(54))
            for rank in (56, 58, 59):
                self.assertIn("lower garment", module.human_notice(rank))
            for rank in range(56, 60):
                self.assertIn("correlated", module.human_notice(rank))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch06-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_categorical_import_strict_mapping_bindings_and_preservation(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch05 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "imported_human_record_sha256": "prior",
                      "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive",
                      "prior_human_disposition": "rejected_false_positive", "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"sha256": "definition", "governance_sha256": "governance", "review168_sha256": "review", "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch05_targeted_categorical_review", "review_definition_sha256": "definition", "governance_sha256": "governance", "review168_sha256": "review",
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True}, "reviewed_at_utc": "2026-10-15T00:52:21.261Z", "stop_for_prospective_scientific_decision": False,
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"], "imported_human_record_sha256": "prior", "reviewed_assets_sha256": pair["required_assets_sha256"],
                                "evidence_sufficient": True, "same_or_derived_content": False, "personal_inspection_attested": True, "owner_decision_attested": True,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "capture_provenance_certified": False,
                                "bound_images_identical_to_rank47": pair["queue_rank"] == 48, "identical_evidence_reference_rank": 47 if pair["queue_rank"] == 48 else None, "owner_extra": "preserve"} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertNotIn("rationale", row)
                self.assertFalse(row["effective_disposition_activated"] or row["reconciliation_required"])
            for field, value in (("queue_rank", 40.0), ("queue_rank", 41), ("evidence_sufficient", 1), ("same_or_derived_content", 0), ("same_or_derived_content", None),
                                 ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("packet_sha256", "drift"), ("imported_human_record_sha256", "drift"),
                                 ("reviewed_assets_sha256", {}), ("capture_provenance_certified", True), ("bound_images_identical_to_rank47", 0), ("identical_evidence_reference_rank", 47),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch05_targeted_semantic_clarification"}, {"review_definition_sha256": "drift"},
                            {"governance_sha256": "drift"}, {"review168_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T00:52:21"}, {"stop_for_prospective_scientific_decision": True},
                            {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}, {"pairs": human["pairs"][:-1]}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for rule in module.CATEGORICAL_RULES:
                row = {**human["pairs"][0], **rule, "stop_for_prospective_scientific_decision": rule["same_or_derived_content"] is True}
                candidate = {**human, "pairs": [row, *human["pairs"][1:]], "stop_for_prospective_scientific_decision": row["stop_for_prospective_scientific_decision"]}
                outcome = module.validate_categorical(candidate, definition)[0]
                self.assertEqual(outcome["validated_disposition"], rule["disposition"])
                self.assertEqual(outcome["stop_for_prospective_scientific_decision"], rule["same_or_derived_content"] is True)
                self.assertEqual(outcome["reconciliation_required"], rule["disposition"] != "rejected_false_positive")
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                for output in (folder, ROOT / "results/refused-categorical-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=folder, human_input=folder / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_clarification_import_preserves_foreground_and_dual_bindings(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_clarification_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "imported_scrutiny_record_sha256": "scrutiny",
                      "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive"} for rank in (38, 39)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "human_pair_specific_clarification", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T03:54:29.393Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "imported_human_record_sha256": pair["imported_human_record_sha256"],
                                "imported_scrutiny_record_sha256": "scrutiny", "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "left_visible_foreground_structure": "Owner left",
                                "right_visible_foreground_structure": "Owner right", "haze_veil_limitation": "Owner limitation",
                                "remaining_evidence_sufficient": True, "personally_reviewed": True, "disposition": "rejected_false_positive",
                                "rationale": "Owner comparison", "capture_provenance_certified": False} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            outcomes = module.validate_clarification(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], outcomes, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertNotIn("visible_rendered_structure", row)
                self.assertFalse(row["effective_disposition_activated"])
                self.assertFalse(row["pair_specific_reasoning_semantically_verified"])
            for field, value in (("queue_rank", 38.0), ("queue_rank", 39), ("imported_human_record_sha256", "drift"),
                                 ("imported_scrutiny_record_sha256", "drift"), ("packet_sha256", "drift"), ("reviewed_assets_sha256", {}),
                                 ("left_visible_foreground_structure", ""), ("right_visible_foreground_structure", " "),
                                 ("haze_veil_limitation", None), ("remaining_evidence_sufficient", 1), ("personally_reviewed", False)):
                with self.assertRaises(ValueError):
                    module.validate_clarification({**human, "pairs": [{**human["pairs"][0], field: value}, human["pairs"][1]]}, definition)
            with self.assertRaises(ValueError):
                module.validate_clarification({**human, "record_type": "targeted_human_scrutiny_resolution"}, definition)
            human["pairs"][0].update(disposition="uncertain_insufficient_evidence", remaining_evidence_sufficient=False)
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            with self.assertRaises(ValueError):
                module.validate_clarification(human, definition)
            human["stop_for_prospective_scientific_decision"] = True
            outcomes = module.validate_clarification(human, definition)
            self.assertTrue(outcomes[1]["stop_for_prospective_scientific_decision"])
            self.assertTrue(all(row["comparison_disposition"] == "uncertain_insufficient_evidence" for row in outcomes))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-clarification-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=root, human_input=root / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_pair_specific_clarification_blank_foreground_fields_and_bindings(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_clarification_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "imported_scrutiny_record_sha256": "bound",
                      "ai_observations": ["</script>visible_rendered_structure:'',targeted_human_scrutiny_resolution"]} for rank in (38, 39)]
            definition = {"pairs": pairs, "scrutiny_notice": module.NOTICE}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_clarification(definition, "definition")
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": "definition"})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("left_visible_foreground_structure:''", "right_visible_foreground_structure:''", "haze_veil_limitation:''",
                             "item.left_visible_foreground_structure.trim()", "item.right_visible_foreground_structure.trim()", "item.haze_veil_limitation.trim()",
                             "disposition:''", "rationale:''", "remaining_evidence_sufficient:null", "personally_reviewed:false",
                             "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_scrutiny_record_sha256:pair.imported_scrutiny_record_sha256",
                             "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true", "item.rationale.trim()",
                             "Object.keys(pair.required_assets_sha256)", "human_pair_specific_clarification", "stop_for_prospective_scientific_decision",
                             "oulu-batch04-pair-specific-clarification.json", "temporal panels and trigger", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("details.open", page)
            for altered in (pairs[:1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 38.0}, pairs[1]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, pairs[1]], [{**pairs[0], "imported_scrutiny_record_sha256": ""}, pairs[1]]):
                with self.assertRaises(ValueError):
                    module.render_clarification({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-clarification"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(scrutiny_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_targeted_clarification_requires_blank_fields_and_provenance(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_clarification_batch05 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>disposition:''"],
                      "human_review_notice": module.IDENTICAL_EVIDENCE_NOTICE if rank == 48 else module.VISIBILITY_LIMITS[rank] + module.SCRUTINY_NOTICE,
                      "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "governance_sha256": "governance"}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_clarification(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            self.assertEqual(module.TARGET_RANKS, (40, 41, 42, 43, 48, 49))
            for fragment in ("left_visible_foreground_structure:''", "right_visible_foreground_structure:''", "visibility_limitation:''",
                             "remaining_evidence_sufficient:null", "owner_disposition_is_own_decision:false", "wording_assistance_disclosure:''", "disposition:''", "rationale:''", "personally_reviewed:false",
                             "item.left_visible_foreground_structure.trim()", "item.right_visible_foreground_structure.trim()", "item.visibility_limitation.trim()",
                             "item.owner_disposition_is_own_decision&&item.wording_assistance_disclosure", "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true",
                             "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_human_record_sha256:pair.imported_human_record_sha256", "wording_assistance_disclosure:state[rank].wording_assistance_disclosure",
                             "bound_images_identical_to_rank47:pair.bound_images_identical_to_rank47", "identical_evidence_reference_rank:pair.bound_images_identical_to_rank47?47:null",
                             "governance_sha256:DATA.definition.governance_sha256", "batch05_targeted_semantic_clarification", "stop_for_prospective_scientific_decision",
                             "oulu-batch05-targeted-clarification.json", "['','Select disposition']", "['AI_assisted'", "['cannot_exclude'", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("details.open", page)
            self.assertNotIn("count!==10", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            for altered in (pairs[:-1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, *pairs[1:]], [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]],
                            [*pairs[:4], {**pairs[4], "bound_images_identical_to_rank47": False}, pairs[5]], [{**pairs[0], "bound_images_identical_to_rank47": 0}, *pairs[1:]]):
                with self.assertRaises(ValueError):
                    module.render_clarification({**definition, "pairs": altered}, "bound")
            with self.assertRaises(ValueError):
                module.render_clarification({**definition, "governance_sha256": ""}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch05-clarification"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(import_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_categorical_handoff_removes_prose_and_preserves_scope(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch05 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>"],
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": name for name in ("temporal_a", "temporal_b", "trigger")},
                      "human_review_notice": module.IDENTICAL_EVIDENCE_NOTICE if rank == 48 else module.VISIBILITY_LIMITS[rank] + module.NOTICE,
                      "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "governance_sha256": "governance", "review168_sha256": "review", "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "rule.evidence_sufficient===item.evidence_sufficient", "rule.same_or_derived_content===item.same_or_derived_content",
                             "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "if(item.evidence_sufficient===true)", "state[current].same_or_derived_content=null", "state[current].submitted=false",
                             "details.hidden=true", "state[current].submitted!==true", "if(!exportReady())return", "queue_rank:pair.queue_rank",
                             "capture_provenance_certified:false", "stop_for_prospective_scientific_decision", "rows.some", "bound_images_identical_to_rank47",
                             "batch05_targeted_categorical_review", "oulu-batch05-categorical-review.json", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "wording_assistance_disclosure", "left_visible_foreground_structure", "Select disposition", "count!==10"):
                self.assertNotIn(fragment, page)
            for changes in ({"governance_sha256": ""}, {"review168_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]},
                            {"pairs": [*pairs[:4], {**pairs[4], "bound_images_identical_to_rank47": False}, pairs[5]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-categorical"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_targeted_scrutiny_import_preserves_two_answers_and_stop_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_scrutiny_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "packet_sha256": str(rank),
                      "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive"} for rank in (38, 39)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "targeted_human_scrutiny_resolution", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T03:15:48.951Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "imported_human_record_sha256": str(pair["queue_rank"]),
                                "packet_sha256": pair["packet_sha256"], "reviewed_assets_sha256": pair["required_assets_sha256"],
                                "visible_rendered_structure": "Owner words", "remaining_evidence_sufficient": True,
                                "personally_reviewed": True, "disposition": "rejected_false_positive", "rationale": "Owner reason",
                                "capture_provenance_certified": False} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_scrutiny(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], [38, 39])
            self.assertTrue(all(not row["effective_disposition_activated"] and not row["pair_specific_reasoning_semantically_verified"] for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for field, value in (("queue_rank", 38.0), ("queue_rank", 39), ("imported_human_record_sha256", "drift"),
                                 ("packet_sha256", "drift"), ("reviewed_assets_sha256", {}), ("personally_reviewed", False),
                                 ("visible_rendered_structure", ""), ("rationale", " "), ("remaining_evidence_sufficient", 1),
                                 ("remaining_evidence_sufficient", False), ("capture_provenance_certified", True)):
                with self.assertRaises(ValueError):
                    module.validate_scrutiny({**human, "pairs": [{**human["pairs"][0], field: value}, human["pairs"][1]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:1]}, {**human, "version": True}, {**human, "review_definition_sha256": "drift"},
                            {**human, "reviewed_at_utc": "2026-10-13"}, {**human, "record_type": "ten_pair_review"},
                            {**human, "stop_for_prospective_scientific_decision": 0}, {**human, "reviewer": {}}):
                with self.assertRaises(ValueError):
                    module.validate_scrutiny(altered, definition)
            human["pairs"][0].update(disposition="uncertain_insufficient_evidence", remaining_evidence_sufficient=False)
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            with self.assertRaises(ValueError):
                module.validate_scrutiny(human, definition)
            human["stop_for_prospective_scientific_decision"] = True
            rows = module.validate_scrutiny(human, definition)
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertTrue(all(row["comparison_disposition"] == "uncertain_insufficient_evidence" for row in rows))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-scrutiny-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=root, human_input=root / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_targeted_scrutiny_blank_fields_and_two_original_ranks(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_scrutiny_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>note"]} for rank in (38, 39)]
            definition = {"pairs": pairs, "scrutiny_notice": module.NOTICE}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_scrutiny(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": "bound"})
            for fragment in ("visible_rendered_structure:''", "remaining_evidence_sufficient:null", "disposition:''", "rationale:''",
                             "personally_reviewed:false", "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_human_record_sha256:pair.imported_human_record_sha256",
                             "remaining_evidence_sufficient:state[rank].remaining_evidence_sufficient", "item.visible_rendered_structure.trim()",
                             "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true", "item.rationale.trim()",
                             "item.personally_reviewed", "Object.keys(pair.required_assets_sha256)", "review_definition_sha256:DATA.sha256",
                             "oulu-batch04-scrutiny-resolution.json", "targeted_human_scrutiny_resolution", "stop_for_prospective_scientific_decision",
                             "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("count!==10", page)
            self.assertNotIn("queue_rank:rank,", page)
            self.assertNotIn("details.open", page)
            for altered in (pairs[:1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 38.0}, pairs[1]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, pairs[1]], [{**pair, "queue_rank": pair["queue_rank"] - 30} for pair in pairs]):
                with self.assertRaises(ValueError):
                    module.render_scrutiny({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-scrutiny", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(import_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_human_rank_adapter_preserves_answers_and_conservative_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch04 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(30, 40)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T02:16:39.495Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Original owner rationale", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch04(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(30, 40)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertTrue(all(row["rationale"] == "Original owner rationale" for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            human["pairs"][8]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][9]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch04(human, definition)
            self.assertTrue(rows[8]["disagreement"])
            self.assertEqual(rows[8]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[9]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[9]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(all(not row["effective_disposition_activated"] for row in rows))
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 30.0), ("queue_rank", 31),
                               ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                with self.assertRaises(ValueError):
                    module.validate_batch04({**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:-1]}, {**human, "review_definition_sha256": "drift"},
                            {**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}):
                with self.assertRaises(ValueError):
                    module.validate_batch04(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch04(human, {**definition, "pairs": list(reversed(pairs))})
        finally:
            sys.path.pop(0)

    def test_batch05_handoff_requires_blank_pair_specific_structure_and_neutral_visibility(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch05 as module
            pairs = [{"queue_rank": rank, "ai_observations": ["</script>queue_rank:rank,packet_sha256"],
                      "human_review_notice": module.VISIBILITY_LIMITS[rank] + module.SCRUTINY_NOTICE if rank in module.HEIGHTENED_SCRUTINY_RANKS else ""} for rank in range(40, 50)]
            definition = {"pairs": pairs}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch05(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            for text in ("Batch 05", "oulu-batch05-human-review.json", "disposition:''", "visible_rendered_structure:''", "rationale:''", "personally_reviewed:false",
                         "item.visible_rendered_structure.trim()&&item.rationale.trim()", "Object.keys(pair.required_assets_sha256)",
                         "visibleText.value=item.visible_rendered_structure", "visible_rendered_structure:state[rank].visible_rendered_structure",
                         "queue_rank:pair.queue_rank", "batch05_human_review_with_pair_specific_structure", "review_definition_sha256:DATA.sha256",
                         "['','Select disposition']", "['confirmed_same_content_or_derived_lineage'", "['rejected_false_positive'", "['uncertain_insufficient_evidence'",
                         "stop_for_prospective_scientific_decision:state.some", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(text, page)
            self.assertNotIn("details.open", page)
            self.assertIn("notice.textContent=pair.human_review_notice", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            self.assertEqual(module.HEIGHTENED_SCRUTINY_RANKS, (40, 41, 42, 43, 49))
            for altered in (pairs[:-1], list(reversed(pairs)), [{**pair, "queue_rank": pair["queue_rank"] - 10} for pair in pairs],
                            [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]], [{**pairs[0], "human_review_notice": ""}, *pairs[1:]],
                            [*pairs[:4], {**pairs[4], "human_review_notice": "Reject"}, *pairs[5:]]):
                with self.assertRaises(ValueError):
                    module.render_batch05({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-owner-batch05", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(ai_root=root, packet_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_handoff_preserves_blank_answers_and_visible_scrutiny(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch04 as module
            pairs = [{"queue_rank": rank, "ai_observations": ["</script>observed"],
                      "human_review_notice": module.HEIGHTENED_SCRUTINY_NOTICE if rank in (38, 39) else ""} for rank in range(30, 40)]
            definition = {"pairs": pairs}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch04(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertIn("Batch 04", page)
            self.assertIn("oulu-batch04-human-review.json", page)
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            for text in ("disposition:''", "rationale:''", "personally_reviewed:false", "['','Select disposition']",
                         "item.disposition&&item.rationale.trim()&&item.personally_reviewed", "Object.keys(pair.required_assets_sha256)",
                         "document.createElement('details')", "review_definition_sha256:DATA.sha256", "\\u003c/script>"):
                self.assertIn(text, page)
            self.assertNotIn("details.open", page)
            self.assertIn("notice.textContent=pair.human_review_notice", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            for altered in (pairs[:9], list(reversed(pairs)), [{**pair, "queue_rank": pair["queue_rank"] - 10} for pair in pairs],
                            [{**pairs[0], "queue_rank": 30.0}, *pairs[1:]], [*pairs[:8], {**pairs[8], "human_review_notice": ""}, pairs[9]]):
                with self.assertRaises(ValueError):
                    module.render_batch04({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-owner-batch04", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(ai_root=root, packet_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_human_rank_adapter_preserves_structure_and_pending_semantics(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch05 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(40, 50)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "batch05_human_review_with_pair_specific_structure", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-14T09:47:25Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "visible_rendered_structure": "Observed structure",
                                "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch05(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(40, 50)))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            self.assertTrue(all(row["visible_rendered_structure"] == "Observed structure" and not row["effective_disposition_activated"] and row["pair_specific_semantic_review_pending"] for row in rows))
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            human["stop_for_prospective_scientific_decision"] = True
            human["pairs"][2]["rationale"] = "Same with previous queue"
            rows = module.validate_batch05(human, definition)
            self.assertTrue(rows[0]["disagreement"])
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[2]["reference_only_marker_in_human_text"])
            self.assertEqual(rows[2]["rationale"], "Same with previous queue")
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 40.0), ("queue_rank", 41), ("visible_rendered_structure", " "), ("visible_rendered_structure", None), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {}), ("capture_provenance_certified", True)):
                with self.assertRaises(ValueError):
                    module.validate_batch05({**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:-1]}, {**human, "record_type": "wrong"}, {**human, "stop_for_prospective_scientific_decision": False}, {**human, "stop_for_prospective_scientific_decision": 1}, {**human, "review_definition_sha256": "drift"}, {**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}):
                with self.assertRaises(ValueError):
                    module.validate_batch05(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch05(human, {**definition, "pairs": list(reversed(pairs))})
        finally:
            sys.path.pop(0)

    def test_batch03_human_rank_adapter_preserves_attestations_and_conservative_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch03 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(20, 30)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-12T10:45:39Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch03(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(20, 30)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch03(human, definition)
            self.assertTrue(rows[0]["disagreement"])
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(all(not row["effective_disposition_activated"] for row in rows))
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "pairs": human["pairs"][:-1]}, definition)
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 20.0), ("queue_rank", 21), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                altered = {**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}
                with self.assertRaises(ValueError):
                    module.validate_batch03(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "review_definition_sha256": "drift"}, definition)
            with self.assertRaises(ValueError):
                module.validate_batch03(human, {**definition, "pairs": list(reversed(pairs))})
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}, definition)
        finally:
            sys.path.pop(0)

    def test_batch03_handoff_preserves_original_ranks_and_blank_answers(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch03 as module
            definition = {"pairs": [{"queue_rank": rank, "ai_observations": ["</script>observed"]} for rank in range(20, 30)]}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch03(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            self.assertIn("Batch 03", page)
            self.assertIn("oulu-batch03-human-review.json", page)
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            self.assertIn("disposition:''", page)
            self.assertIn("rationale:''", page)
            self.assertIn("personally_reviewed:false", page)
            self.assertIn("document.createElement('details')", page)
            self.assertNotIn("details.open", page)
            self.assertIn("\\u003c/script>", page)
            self.assertIn("review_definition_sha256:DATA.sha256", page)
            for pairs in (definition["pairs"][:9], list(reversed(definition["pairs"])), [{"queue_rank": rank} for rank in range(10, 20)]):
                with self.assertRaises(ValueError):
                    module.render_batch03({"pairs": pairs}, "bound")
        finally:
            sys.path.pop(0)

    def test_batch07_packet_authority_selection_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch07 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(70)]
            prior = {"activation_checkpoint_review_pending": True, "batch06_accepted_reconciled_disposition_state": False,
                     "accepted_batch06_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 50, "prospective_total_after_acceptance": 60, "batch06_closed": False,
                     "stop_for_prospective_scientific_decision": False}
            acceptance = {"batch06_activation_checkpoint_accepted": True, "batch06_screen_level_review_closed": True,
                          "accepted_current_total": 60, "accepted_batch06_disposition_counts": {"rejected_false_positive": 10}}
            before = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(60, 70)))
            for key, value in (("batch06_activation_checkpoint_accepted", False), ("batch06_screen_level_review_closed", False),
                               ("accepted_current_total", 60.0), ("accepted_batch06_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch06_accepted_reconciled_disposition_state", True),
                               ("accepted_batch06_current_effective_dispositions", 10), ("effective_dispositions_activated", 0),
                               ("current_materialized_disposition_counts", {}), ("accepted_current_total", 60),
                               ("prospective_total_after_acceptance", 50), ("batch06_closed", True), ("stop_for_prospective_scientific_decision", True)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:60], {**records[60], "queue_rank": 60.0}, *records[61:]],
                            [*records[:60], {**records[60], "queue_rank": True}, *records[61:]], [*records[:60], {**records[60], "priority": "other"}, *records[61:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), before)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/190-review-doc189-oulu-batch06-activation.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review190 acceptance", encoding="ascii")
                report = repo / "results/phase1/oulu-batch06-activation-v1.json"
                write_immutable_record(report, prior)
                check = {"head_sha": "a81bd9259478a8a49ad0783fdb777329791a99d5", "run_id": 38696814671,
                         "job_id": 116295204960, "status": "completed", "conclusion": "success",
                         "job_status": "completed", "job_conclusion": "success"}
                authority = {**acceptance, "review190_sha256": module._sha256(review)}
                preflight = {"checkpoint": 191, "acceptance": authority, "activation_CI": check,
                             "packet_preparation_authorized": True, "queue_ranks": list(range(60, 70)),
                             "accepted_prior_report_sha256": module._sha256(report),
                             "accepted_recovery": {"accepted_by_Review178": True}, "protected_snapshots": {}}
                original = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "REVIEW190_SHA256", module._sha256(review)), patch.object(module, "ACCEPTED189_REPORT_SHA256", module._sha256(report)):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "acceptance": None}, {**preflight, "acceptance": {**authority, "review190_sha256": "0" * 64}},
                               {**preflight, "checkpoint": 191.0}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(50, 60))}, {**preflight, "queue_ranks": [60.0, *range(61, 70)]},
                               {**preflight, "accepted_prior_report_sha256": "0" * 64}, {**preflight, "activation_CI": None},
                               {**preflight, "accepted_recovery": None}, {**preflight, "accepted_recovery": {"accepted_by_Review178": False}}]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 38694502603), ("run_id", float(check["run_id"])),
                                       ("job_id", 116287801095), ("status", "in_progress"), ("conclusion", "failure"),
                                       ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "activation_CI": {**check, key: value}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, out_root=root / "never-created")
                        with patch.object(module, "verified_archive_identities", side_effect=AssertionError("must not reach archives")):
                            with self.assertRaises(ValueError):
                                module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    for output in (ROOT / "results/refused-visual-batch07", root, root / "source/refused"):
                        with self.assertRaises(ValueError):
                            module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                frozen_root=root, archive_records=root, activation_root=root, preflight=root / "missing", out_root=output))
                self.assertEqual(json.dumps(preflight, sort_keys=True), original)
        finally:
            sys.path.pop(0)

    def test_batch06_packet_selection_requires_additive_acceptance_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(60)]
            prior = {"activation_checkpoint_review_pending": True, "batch05_accepted_reconciled_disposition_state": False,
                     "accepted_batch05_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 40, "prospective_total_after_acceptance": 50, "batch05_closed": False}
            acceptance = {"batch05_activation_checkpoint_accepted": True, "accepted_current_total": 50,
                          "accepted_batch05_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(50, 60)))
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), original)
            for key, value in (("batch05_activation_checkpoint_accepted", False), ("accepted_current_total", 40), ("accepted_batch05_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch05_accepted_reconciled_disposition_state", True), ("accepted_batch05_current_effective_dispositions", 10), ("effective_dispositions_activated", 0), ("current_materialized_disposition_counts", {}), ("accepted_current_total", 50), ("prospective_total_after_acceptance", 40), ("batch05_closed", True)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:50], {**records[50], "queue_rank": 50.0}, *records[51:]], [*records[:50], {**records[50], "queue_rank": True}, *records[51:]], [*records[:50], {**records[50], "priority": "other"}, *records[51:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-visual-batch06", root, root / "source/refused"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                                 frozen_root=root, archive_records=root, activation_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_packet_selection_requires_additive_acceptance_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch05 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(50)]
            prior = {"activation_checkpoint_review_pending": True, "batch04_accepted_reconciled_disposition_state": False,
                     "accepted_batch04_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 30, "prospective_total_after_acceptance": 40}
            acceptance = {"batch04_activation_checkpoint_accepted": True, "accepted_current_total": 40,
                          "accepted_batch04_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(40, 50)))
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), original)
            for key, value in (("batch04_activation_checkpoint_accepted", False), ("accepted_current_total", 30), ("accepted_batch04_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch04_accepted_reconciled_disposition_state", True), ("accepted_batch04_current_effective_dispositions", 10), ("effective_dispositions_activated", 0), ("current_materialized_disposition_counts", {}), ("accepted_current_total", 40), ("prospective_total_after_acceptance", 30)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:40], {**records[40], "queue_rank": 40.0}, *records[41:]], [*records[:40], {**records[40], "priority": "other"}, *records[41:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-visual-batch05", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                                 frozen_root=root, archive_records=root, activation_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_packet_selection_requires_closed_batch03_and_exact_queue(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch04 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(40)]
            prior = {"batch03_accepted_reconciled_disposition_state": True, "effective_dispositions_activated": 10,
                     "current_effective_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps(records, sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(30, 40)))
            self.assertEqual(json.dumps(records, sort_keys=True), original)
            for altered in ({**prior, "batch03_accepted_reconciled_disposition_state": False}, {**prior, "effective_dispositions_activated": 0}, {**prior, "current_effective_disposition_counts": {"rejected_false_positive": 9}}):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, altered)
            with self.assertRaises(ValueError):
                module.fixed_next_records(records[:39], prior)
            records[30], records[31] = records[31], records[30]
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            records[30], records[31] = records[31], records[30]
            records[30]["priority"] = "cross_role"
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                args = Namespace(activation_root=root, out_root=ROOT / "results/refused-batch04", input_root=root, audit_root=root,
                                 exact_root=root, screen_root=root, frozen_root=root, archive_records=root)
                with self.assertRaises(ValueError):
                    module.prepare(args)
                args.out_root = root
                with self.assertRaises(ValueError):
                    module.prepare(args)
        finally:
            sys.path.pop(0)

    def test_batch03_packet_selection_requires_closed_batch02_and_exact_queue(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch03 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(30)]
            prior = {"batch02_accepted_reconciled_disposition_state": True, "effective_dispositions_activated": 10,
                     "current_effective_disposition_counts": {"rejected_false_positive": 10}}
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(20, 30)))
            for altered in ({**prior, "batch02_accepted_reconciled_disposition_state": False}, {**prior, "effective_dispositions_activated": 0}, {**prior, "current_effective_disposition_counts": {"rejected_false_positive": 9}}):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, altered)
            with self.assertRaises(ValueError):
                module.fixed_next_records(records[:29], prior)
            records[20], records[21] = records[21], records[20]
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            records[20], records[21] = records[21], records[20]
            records[20]["priority"] = "cross_role"
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                args = Namespace(activation_root=root, out_root=ROOT / "results/refused-batch03", input_root=root, audit_root=root,
                                 exact_root=root, screen_root=root, frozen_root=root, archive_records=root)
                with self.assertRaises(ValueError):
                    module.prepare(args)
                args.out_root = root
                with self.assertRaises(ValueError):
                    module.prepare(args)
        finally:
            sys.path.pop(0)

    def test_batch02_human_rank_adapter_preserves_disagreement_and_hard_stop(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch02 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(10, 20)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-10T09:27:15Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps(human, sort_keys=True)
            rows = module.validate_batch02(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(10, 20)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertEqual(json.dumps(human, sort_keys=True), original)
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch02(human, definition)
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            with self.assertRaises(ValueError):
                module.validate_batch02({**human, "pairs": human["pairs"][:-1]}, definition)
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 11), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                altered = {**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}
                with self.assertRaises(ValueError):
                    module.validate_batch02(altered, definition)
        finally:
            sys.path.pop(0)

    def test_batch02_handoff_exports_original_queue_ranks_and_blank_answers(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch02 as module
            definition = {"pairs": [{"queue_rank": rank} for rank in range(10, 20)]}
            page = module.render_batch02(definition, "digest")
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            self.assertIn("disposition:'',rationale:''", page)
            self.assertIn("oulu-batch02-human-review.json", page)
            self.assertIn("'Queue '+pair.queue_rank", page)
            self.assertNotIn("Batch 01", page)
            with self.assertRaises(ValueError):
                module.render_batch02({"pairs": [{"queue_rank": rank} for rank in range(10)]}, "digest")
            escaped = module.render_batch02({**definition, "text": "</script>"}, "digest")
            self.assertIn("\\u003c/script>", escaped)
        finally:
            sys.path.pop(0)

    def test_next_visual_batch_requires_closed_prior_and_exact_order(self) -> None:
        spec = importlib.util.spec_from_file_location("prepare_oulu_visual_batch02", ROOT / "scripts/prepare_oulu_visual_batch02.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(20)]
        prior = {"batch01_accepted_reconciled_disposition_state": True, "current_effective_disposition_counts": {"rejected_false_positive": 10}}
        self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(10, 20)))
        with self.assertRaises(ValueError):
            module.fixed_next_records(records, {**prior, "batch01_accepted_reconciled_disposition_state": False})
        with self.assertRaises(ValueError):
            module.fixed_next_records(records[:19], prior)
        records[10], records[11] = records[11], records[10]
        with self.assertRaises(ValueError):
            module.fixed_next_records(records, prior)
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            arguments = Namespace(out_root=ROOT / "results/refused-batch02", input_root=source,
                                  audit_root=source, exact_root=source, screen_root=source,
                                  frozen_root=source, archive_records=source, activation_root=source)
            with self.assertRaises(ValueError):
                module.prepare(arguments)
            arguments.out_root = source
            with self.assertRaises(ValueError):
                module.prepare(arguments)

    def test_handoff_private_output_refused_and_definition_escaped(self) -> None:
        spec = importlib.util.spec_from_file_location("prepare_oulu_owner_review", ROOT / "scripts/prepare_oulu_owner_review.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            with self.assertRaises(ValueError):
                module.private_output(ROOT / "results/refused-human-output", [source])
            with self.assertRaises(ValueError):
                module.private_output(source, [source])
        page = module.render_page({"pairs": [], "text": "</script><script>bad</script>"}, "a" * 64)
        self.assertNotIn("</script><script>bad", page)
        self.assertIn("\\u003c", page)

    def fixture(self):
        definition = {"sha256": "a" * 64, "pairs": [{"packet_sha256": format(rank, "064x"),
                      "required_assets_sha256": {"temporal": "b" * 64, **({"full_resolution": "c" * 64} if rank == 4 else {})},
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 4 else "rejected_false_positive"} for rank in range(10)]}
        record = {"version": 1, "reviewer": {"kind": "owner_human", "id": "synthetic-reviewer", "personally_inspected_bound_evidence": True},
                  "review_definition_sha256": definition["sha256"], "reviewed_at_utc": "2026-10-10T00:00:00+00:00",
                  "pairs": [{"queue_rank": rank, "packet_sha256": pair["packet_sha256"],
                             "reviewed_assets_sha256": dict(pair["required_assets_sha256"]), "personally_reviewed": True,
                             "disposition": pair["ai_disposition"], "rationale": "Synthetic fixture only", "capture_provenance_certified": False}
                            for rank, pair in enumerate(definition["pairs"])]}
        return record, definition

    def test_human_attestation_required_not_ai_or_blank_template(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        self.assertEqual(len(validate_human_review(record, definition)), 10)
        record["reviewer"]["kind"] = "AI"
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record["reviewer"]["kind"] = "owner_human"
        record["reviewer"]["personally_inspected_bound_evidence"] = False
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_incomplete_or_duplicate_pair_review_is_rejected(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"].pop()
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record["pairs"].append(record["pairs"][0])
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_full_resolution_hash_and_rationale_are_required(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"][4]["reviewed_assets_sha256"].pop("full_resolution")
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record, definition = self.fixture()
        record["pairs"][0]["rationale"] = " "
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_disagreement_is_preserved_and_confirmation_stops_execution(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"][0]["disposition"] = "confirmed_same_content_or_derived_lineage"
        result = validate_human_review(record, definition)[0]
        self.assertTrue(result["disagreement"])
        self.assertTrue(result["stop_for_prospective_scientific_decision"])
        self.assertEqual(result["effective_disposition"], "uncertain_insufficient_evidence")
        self.assertFalse(result["model_execution_authorized"])

    def test_full_resolution_export_preserves_accepted_rgb_identity(self) -> None:
        from fas.human_review import full_resolution_frames
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "4", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            media = probe_video(path)
            frames = full_resolution_frames(path, media, [0, 2, 3])
            self.assertEqual(frames[2].shape, (48, 64, 3))
            self.assertEqual(hashlib.sha256(frames[2].tobytes()).hexdigest(), media["frame_index"][2]["rgb_sha256"])
            media["frame_index"][2]["rgb_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                full_resolution_frames(path, media, [2])


class OuluVisualTest(unittest.TestCase):
    def test_visual_runner_refuses_repository_and_existing_output(self) -> None:
        import argparse
        spec = importlib.util.spec_from_file_location("prepare_oulu_visual_review", ROOT / "scripts/prepare_oulu_visual_review.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            args = argparse.Namespace(input_root=source, audit_root=source, exact_root=source, screen_root=source,
                                      frozen_root=source, archive_records=source, out_root=ROOT / "results/refused-visual-output")
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.prepare(args)
            args.out_root = source
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.prepare(args)

    def test_review_ranks_are_fixed_and_include_frozen_primary(self) -> None:
        from fas.visual import review_orders
        self.assertEqual(review_orders(1), [0] * 17)
        self.assertEqual(review_orders(8)[8], 3)
        self.assertEqual(review_orders(151)[-1], 150)
        with self.assertRaises(ValueError):
            review_orders(True)

    def test_full_rgb_redecode_reconciles_accepted_frames(self) -> None:
        from fas.visual import verified_thumbnails
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "4", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            media = probe_video(path)
            frames = verified_thumbnails(path, media)
            self.assertEqual(len(frames), 4)
            self.assertEqual(frames[0].shape, (192, 256, 3))
            media["frame_index"][1]["rgb_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "RGB identity"):
                verified_thumbnails(path, media)

    def test_private_png_and_temporal_sheet_geometry(self) -> None:
        import cv2
        import numpy as np
        from fas.visual import pair_sheet, png_bytes
        frames = [np.full((48, 64, 3), [250, 10, 20], dtype=np.uint8)] * 4
        sheet = pair_sheet(frames, frames, list(range(0, 17, 2)))
        self.assertEqual(sheet.shape, (296, 1440, 3))
        decoded = cv2.imdecode(np.frombuffer(png_bytes(frames[0]), dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertTrue(np.array_equal(decoded[0, 0], [20, 10, 250]))
        with self.assertRaises(ValueError):
            pair_sheet(frames, frames, [17])


class OuluLineageTest(unittest.TestCase):
    def test_evidence_runner_refuses_repository_or_existing_output(self) -> None:
        spec = importlib.util.spec_from_file_location("triage_oulu_lineage", ROOT / "scripts/triage_oulu_lineage.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.triage(source, source, source, ROOT / "results/refused-lineage-output")
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.triage(source, source, source, source)

    def media(self, sequence):
        return {"decode_status": "decoded", "frame_count": len(sequence),
                "frame_index": [{"decode_order": order, "decode_success": True,
                                 "width": 32, "height": 24, "timestamp_seconds": str(order),
                                 "rgb_sha256": format(value, "064x")} for order, value in enumerate(sequence)]}

    def test_trimmed_full_sequence_is_rendered_content_not_capture_provenance(self) -> None:
        from fas.lineage import exact_content_evidence
        result = exact_content_evidence(self.media([1, 2, 3]), self.media([0, 1, 2, 3, 4]))
        self.assertEqual(result["disposition"], "confirmed_same_content_or_derived_lineage")
        self.assertEqual(result["longest_exact_contiguous_run"], 3)
        self.assertEqual(result["right_run_start"], 1)
        self.assertFalse(result["capture_provenance_confirmed"])
        reverse = exact_content_evidence(self.media([0, 1, 2, 3, 4]), self.media([1, 2, 3]))
        self.assertEqual(reverse["longest_exact_contiguous_run"], 3)
        self.assertEqual(reverse["left_run_start"], 1)

    def test_missing_or_partial_overlap_never_rejects_candidate(self) -> None:
        from fas.lineage import exact_content_evidence
        for left, right in (([1, 2, 3], [4, 5, 6]), ([1, 2, 3], [0, 1, 2, 4]),
                            ([1, 1], [0, 1, 1, 3]), ([1], [1, 2]), ([1, 2, 3], [3, 2, 1])):
            with self.subTest(left=left, right=right):
                result = exact_content_evidence(self.media(left), self.media(right))
                self.assertEqual(result["disposition"], "uncertain_insufficient_evidence")
                self.assertFalse(result["false_positive_rejection_authorized"])

    def test_repeated_frames_do_not_break_longest_run(self) -> None:
        from fas.lineage import exact_content_evidence
        result = exact_content_evidence(self.media([1, 2, 1, 2]), self.media([0, 1, 2, 1, 2, 3]))
        self.assertEqual(result["longest_exact_contiguous_run"], 4)
        self.assertEqual(result["right_run_start"], 1)

    def test_invalid_full_frame_evidence_fails_closed(self) -> None:
        from fas.lineage import exact_content_evidence
        for key, value in (("rgb_sha256", "bad"), ("decode_order", 7), ("decode_success", False), ("width", True)):
            media = self.media([1, 2])
            media["frame_index"][0][key] = value
            with self.assertRaises(ValueError):
                exact_content_evidence(media, self.media([1, 2]))
        with self.assertRaises(ValueError):
            exact_content_evidence({"decode_status": "failed", "frame_count": 0, "frame_index": []}, self.media([1]))

    def test_priority_is_exclusive_and_no_boundary_is_omitted(self) -> None:
        from fas.lineage import candidate_priority
        for pair, expected in (({"cross_role": True, "cross_partition": True, "conflicting_label": True}, 0),
                               ({"cross_role": True, "cross_partition": True, "conflicting_label": False}, 1),
                               ({"cross_role": False, "cross_partition": True, "conflicting_label": True}, 2),
                               ({"cross_role": False, "cross_partition": False, "conflicting_label": True}, 3),
                               ({"cross_role": False, "cross_partition": False, "conflicting_label": False}, 4)):
            self.assertEqual(candidate_priority(pair), expected)
        with self.assertRaises(ValueError):
            candidate_priority({"cross_role": "true", "cross_partition": False, "conflicting_label": False})


class OuluContentTest(unittest.TestCase):
    def test_runner_refuses_repository_and_existing_output(self) -> None:
        import argparse
        spec = importlib.util.spec_from_file_location("screen_oulu_content", ROOT / "scripts/screen_oulu_content.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            args = argparse.Namespace(input_root=source, audit_root=source, frozen_root=source,
                                      archive_records=source, out_root=ROOT / "results/refused-content-output", workers=4)
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.screen(args)
            args.out_root = source
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.screen(args)

    def test_temporal_ranks_include_frozen_primary(self) -> None:
        from fas.content import temporal_orders
        self.assertEqual(temporal_orders(8), [0, 1, 3, 5, 7])
        self.assertEqual(temporal_orders(1), [0] * 5)
        for invalid in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                temporal_orders(invalid)

    def test_phash_deterministic_and_brightness_invariant(self) -> None:
        import numpy as np
        from fas.content import perceptual_hash
        rgb = np.random.default_rng(42).integers(0, 180, (64, 64, 3), dtype=np.uint8)
        self.assertEqual(perceptual_hash(rgb), perceptual_hash(rgb.copy()))
        distance = (int(perceptual_hash(rgb), 16) ^ int(perceptual_hash(rgb + 30), 16)).bit_count()
        self.assertLessEqual(distance, 4)
        with self.assertRaises(ValueError):
            perceptual_hash(rgb.astype(float))

    def test_all_pairs_include_cross_role_and_failed_coverage(self) -> None:
        from fas.content import candidate_pairs
        def record(identity, value, role):
            return {"video_id": identity, "role": role, "status": "fingerprinted",
                    "samples": [{"phash64": value}] * 5}
        rows = [record("a", "0000000000000000", "train"),
                record("b", "000000000000000f", "branch_calibration"),
                record("c", "ffffffffffffffff", "g_domain"),
                {"video_id": "failed", "status": "unavailable_decode_failure", "samples": []}]
        pairs = list(candidate_pairs(rows, block_size=1))
        self.assertEqual([(pair["left"], pair["right"]) for pair in pairs], [("a", "b")])
        self.assertEqual(pairs[0]["disposition"], "unresolved_candidate_not_confirmed_lineage")
        with self.assertRaises(ValueError):
            list(candidate_pairs(rows + rows[:1]))
        self.assertEqual(list(candidate_pairs([])), [])

    def test_sampled_decode_matches_accepted_hash_and_reencode(self) -> None:
        from fas.content import fingerprint_video
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            other = Path(directory) / "reencoded.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "8", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-c:v", "mjpeg", "-q:v", "6",
                            "-threads", "1", str(other)], check=True)
            media = probe_video(path)
            first = fingerprint_video(path, media)
            second = fingerprint_video(other, probe_video(other))
            self.assertEqual(len(first["samples"]), 5)
            from fas.content import candidate_pairs
            self.assertEqual(len(list(candidate_pairs([dict(first, video_id="a"), dict(second, video_id="b")]))), 1)
            media["frame_index"][0]["rgb_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "RGB identity"):
                fingerprint_video(path, media)
            failed = fingerprint_video(path, {"decode_status": "failed", "frame_count": 0, "frame_index": []})
            self.assertEqual(failed["samples"], [])


class OuluTransactionTest(unittest.TestCase):
    def test_end_to_end_failure_uses_original_denominators_without_fake_detector(self) -> None:
        from fas.contracts import k1_end_to_end_summary
        rows = [{"label": "attack", "detector_status": "success", "final_k1_action": "non_accept"},
                {"label": "bona_fide", "detector_status": "success", "final_k1_action": "accept"},
                {"label": "bona_fide", "detector_status": "not_run", "technical_status": "terminal_failure",
                 "final_k1_action": "non_accept", "model_score": None, "classifier_error": None}]
        result = k1_end_to_end_summary(rows)
        self.assertEqual(result["bona_fide_total"], 2)
        self.assertEqual(result["bfnr_end2end"], 0.5)
        self.assertEqual(result["bona_fide_detector_coverage"], 0.5)
        rows[-1]["model_score"] = 0.1
        with self.assertRaises(ValueError):
            k1_end_to_end_summary(rows)

    def test_transaction_export_refuses_repository_output(self) -> None:
        spec = importlib.util.spec_from_file_location("freeze_oulu_transactions", ROOT / "scripts/freeze_oulu_transactions.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            frozen = Path(directory) / "frozen"
            source.mkdir()
            frozen.mkdir()
            output = ROOT / "results" / "refused-transaction-test-output"
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.export(source, frozen, output)
            self.assertFalse(output.exists())

    def test_policy_bytes_bound_and_semantic_drift_rejected(self) -> None:
        from fas.preregistration import artifact_hashes
        path = ROOT / "configs/transaction_policy_v1.yaml"
        policy = json.loads(path.read_bytes())
        validate_transaction_policy(policy)
        self.assertEqual(artifact_hashes(ROOT)["configs/transaction_policy_v1.yaml"], hashlib.sha256(path.read_bytes()).hexdigest())
        policy["primary_frame"]["even_length_tie"] = "later_decoded_frame"
        with self.assertRaises(ValueError):
            validate_transaction_policy(policy)

    def test_population_denominators_do_not_drop_failed_bona_fide(self) -> None:
        good = technical_transaction(self.media(5))
        media = self.media(0)
        media.update(video_id="failed-id", decode_status="failed")
        failed = technical_transaction(media)
        result = technical_population_counts([good, failed])[0]
        self.assertEqual(result["original_denominator"], 2)
        self.assertEqual(result["primary_frame_available"], 1)
        self.assertEqual(result["terminal_technical_failures"], 1)
        self.assertEqual(result["forced_bfnr_numerator"], 1)
        failed["retain_original_denominator"] = False
        with self.assertRaises(ValueError):
            technical_population_counts([good, failed])

    def media(self, count: int) -> dict:
        return {"video_id": "synthetic-id", "binary_label": "bona_fide", "role": "branch_calibration",
                "decode_status": "decoded", "frame_count": count,
                "frame_index": [{"decode_order": order, "timestamp_seconds": str(order),
                                 "width": 32, "height": 24, "decode_success": True,
                                 "rgb_sha256": "a" * 64} for order in range(count)]}

    def test_odd_even_and_single_frame_primary(self) -> None:
        for count, expected in ((1, 0), (5, 2), (8, 3)):
            with self.subTest(count=count):
                self.assertEqual(select_primary_frame(self.media(count))["decode_order"], expected)

    def test_inclusive_interval_and_no_replacement(self) -> None:
        media = self.media(8)
        self.assertEqual(select_primary_frame(media, interval=("2", "5"))["decode_order"], 3)
        self.assertIsNone(select_primary_frame(media, interval=("10", "11")))
        self.assertEqual(technical_transaction(media, interval=("10", "11"))["final_k1_action"], "non_accept")
        with self.assertRaises(ValueError):
            select_primary_frame(media, interval=("5", "2"))

    def test_failed_calibration_transaction_retains_denominator_without_error(self) -> None:
        media = self.media(0)
        media["decode_status"] = "failed"
        transaction = technical_transaction(media)
        self.assertTrue(transaction["retain_original_denominator"])
        self.assertEqual(transaction["final_k1_action"], "non_accept")
        self.assertEqual(transaction["detector_status"], "not_run")
        self.assertIsNone(transaction["classifier_error"])
        self.assertEqual(calibration_fit_rows([transaction]), [])
        transaction["model_score"] = 0.1
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction])

    def test_successful_frame_is_not_a_model_score(self) -> None:
        transaction = technical_transaction(self.media(5))
        self.assertEqual(calibration_fit_rows([transaction]), [])
        transaction.update(model_score=0.2, detector_status="success")
        self.assertEqual(calibration_fit_rows([transaction]), [transaction])
        transaction["model_score"] = float("nan")
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction])

    def test_bad_index_unknown_decode_and_duplicate_ids_fail_closed(self) -> None:
        media = self.media(3)
        media["frame_index"][1]["decode_order"] = 0
        with self.assertRaises(ValueError):
            select_primary_frame(media)
        media["decode_status"] = "not_probed"
        with self.assertRaises(ValueError):
            select_primary_frame(media)
        transaction = technical_transaction(self.media(3))
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction, transaction])


class OuluMediaTest(unittest.TestCase):
    def test_batch06_packet_retry_requires_review180_and_exact179_CI(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/180-review-doc179-oulu-recovery-aware-guard.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review180 acceptance", encoding="ascii")
                recovery = {"binding_sha256": "a" * 64, "accepted177_report_sha256": "b" * 64,
                            "archive_pin_report_sha256": "c" * 64, "review178_sha256": "d" * 64}
                report = repo / "results/phase1/oulu-recovery-aware-guard-v1.json"
                runner = "4996ee828d1a159184616669033e324b1dadf3335a480402cb2ad62e8e9fd62b"
                write_immutable_record(report, {"runner_sha256": runner, "guard_integration_checkpoint_review_pending": True,
                    "packet_preparation_authorized": False, "accepted_environment_binding_sha256": recovery["binding_sha256"],
                    **{field: recovery[field] for field in ("accepted177_report_sha256", "archive_pin_report_sha256", "review178_sha256")}})
                check = {"head_sha": "63505d1c1b2f940fa077398127ef29a49ede95ef", "run_id": 38676766354,
                         "job_id": 116232038205, "status": "completed", "conclusion": "success",
                         "job_status": "completed", "job_conclusion": "success"}
                authority = {"accepted_by_Review180": True, "packet_preparation_checkpoint": "181",
                    "review180_sha256": module._sha256(review), "accepted179_report_sha256": module._sha256(report),
                    "accepted179_runner_sha256": runner, "publication_CI": check}
                preflight = {"guard_acceptance": authority, "packet_preparation_authorized": True,
                             "queue_ranks": list(range(50, 60)), "accepted_recovery": recovery, "protected_snapshots": {}}
                before = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "guard_acceptance": None}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(60, 70))}]
                    for field, value in (("accepted_by_Review180", False), ("packet_preparation_checkpoint", "179"),
                                         ("review180_sha256", "0" * 64), ("accepted179_report_sha256", "0" * 64),
                                         ("accepted179_runner_sha256", "0" * 64)):
                        invalid.append({**preflight, "guard_acceptance": {**authority, field: value}})
                    for field, value in (("head_sha", "0" * 40), ("run_id", 38673838230), ("job_id", 116222822739),
                                         ("status", "in_progress"), ("conclusion", "failure"), ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "guard_acceptance": {**authority, "publication_CI": {**check, field: value}}})
                    for field in recovery:
                        invalid.append({**preflight, "accepted_recovery": {**recovery, field: "0" * 64}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, guard_only=False, out_root=root / "never-created")
                        with self.assertRaises(ValueError):
                            module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    self.assertEqual(json.dumps(preflight, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_recovery_aware_fast_guard_binds_authority_and_rejects_every_stat_drift(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, pins_root, recovered, repo = (root / name for name in ("source", "pins", "recovered", "repo"))
                for folder in (source, pins_root, recovered):
                    folder.mkdir()
                pins, rows, anchors = {}, {}, {}
                for name in module.ANCHORS:
                    path = source / name
                    path.write_bytes(b"synthetic bytes")
                    current = module.file_identity(path.stat())
                    old = {key: value for key, value in current.items() if key != "byte_size"}
                    old["device"] += 1
                    pin_path = pins_root / (name + ".sha256.json")
                    write_immutable_record(pin_path, {"file_identity": old})
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    anchors[name] = digest
                    pins[name] = {"sha256": digest, "byte_size": current["byte_size"], "private_record_sha256": module._sha256(pin_path)}
                    rows[name] = {"old_private_record_sha256": module._sha256(pin_path), "old_file_identity": old,
                                  "current_file_identity": current, "byte_size": current["byte_size"], "current_sha256": digest,
                                  "frozen_sha256": digest, "whole_file_read": True, "content_hash_matches_frozen": True,
                                  "stat_identity_stable_during_hash": True, "changed_fields": ["device"]}
                    write_immutable_record(recovered / (name + ".rehash.json"), rows[name])
                public = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                write_immutable_record(public, {"media_archives": pins})
                binding_path = recovered / "environment_binding.json"
                write_immutable_record(binding_path, {"archives": rows, "recovery_checkpoint_review_pending": True,
                                                     "old_archive_pins_unchanged": True, "archive_pin_report_sha256": module._sha256(public)})
                report_path = repo / "results/phase1/oulu-archive-identity-recovery-v1.json"
                write_immutable_record(report_path, {"private_environment_binding_sha256": module._sha256(binding_path),
                                                     "archive_pin_report_sha256": module._sha256(public),
                                                     "archive_results": {name: {"rehash_record_sha256": module._sha256(recovered / (name + ".rehash.json"))} for name in pins}})
                review = repo / "docs/178-review-doc177-oulu-archive-identity-recovery.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic acceptance", encoding="ascii")
                recovery = {"accepted_by_Review178": True, "review178_sha256": module._sha256(review),
                            "accepted177_report_sha256": module._sha256(report_path), "archive_pin_report_sha256": module._sha256(public),
                            "binding_path": str(binding_path), "binding_sha256": module._sha256(binding_path)}
                marker = root / "protected/marker.json"
                write_immutable_record(marker, {"prior": True})
                preflight = root / "preflight.json"
                write_immutable_record(preflight, {"accepted_recovery": recovery, "packet_preparation_authorized": False,
                    "protected_snapshots": {str(marker.parent): {marker.name: module._sha256(marker)}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {},
                    "preparation_code_sha256": module._sha256(Path(module.__file__)),
                    "activation_CI": {"head_sha": "226943f77710a938b54581ccb03381e69c0d7fba", "run_id": 38666749697,
                                      "job_id": 116200334607, "status": "completed", "conclusion": "success"}})
                args = Namespace(input_root=source, audit_root=root / "audit", exact_root=root / "exact", screen_root=root / "screen",
                                 frozen_root=root / "frozen", archive_records=pins_root, activation_root=root / "activation",
                                 preflight=preflight, guard_only=True, out_root=root / "never-created")
                before = json.dumps(recovery, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "ANCHORS", anchors):
                    self.assertEqual(len(module.verified_archive_identities(source, pins_root, recovery)), 3)
                    self.assertEqual(module.prepare(args)["archives_verified"], 3)
                    self.assertFalse(args.out_root.exists())
                    with self.assertRaises(ValueError):
                        module.verified_archive_identities(source, pins_root)
                    original = module.file_identity
                    for field in ("device", "inode", "byte_size", "mtime_ns", "ctime_ns"):
                        with patch.object(module, "file_identity", side_effect=lambda value, field=field: {**original(value), field: original(value)[field] + 1}):
                            with self.assertRaisesRegex(ValueError, "archive identity drift"):
                                module.prepare(args)
                            self.assertFalse(args.out_root.exists())
                    for field, value in (("binding_sha256", "0" * 64), ("archive_pin_report_sha256", "0" * 64),
                                         ("accepted177_report_sha256", "0" * 64), ("review178_sha256", "0" * 64), ("accepted_by_Review178", False)):
                        with self.assertRaises(ValueError):
                            module.verified_archive_identities(source, pins_root, {**recovery, field: value})
                    with self.assertRaisesRegex(ValueError, "requires review"):
                        module.prepare(Namespace(**{**vars(args), "guard_only": False}))
                    marker.write_bytes(b"changed prior evidence")
                    with self.assertRaisesRegex(ValueError, "protected prior evidence drift"):
                        module.prepare(args)
                    self.assertFalse(args.out_root.exists())
                    self.assertEqual(json.dumps(recovery, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_archive_identity_recovery_requires_full_hash_and_stable_device_only_drift(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import recover_oulu_archive_identity as module
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "synthetic.tar"
                payload = b"synthetic archive container, not a decoded video"
                path.write_bytes(payload)
                old = {**module.file_identity(path.stat()), "device": path.stat().st_dev + 1}
                expected = {"sha256": hashlib.sha256(payload).hexdigest(), "byte_size": len(payload)}
                before = json.dumps([expected, old], sort_keys=True)
                row = module.rehash_archive(path, expected, old)
                self.assertEqual(row["current_sha256"], expected["sha256"])
                self.assertEqual(row["changed_fields"], ["device"])
                self.assertTrue(row["whole_file_read"] and row["stat_identity_stable_during_hash"])
                self.assertEqual(json.dumps([expected, old], sort_keys=True), before)
                for wrong in ({**expected, "sha256": "0" * 64}, {**expected, "byte_size": len(payload) + 1}):
                    with self.assertRaises(ValueError):
                        module.rehash_archive(path, wrong, old)
                for wrong in ({**old, "device": path.stat().st_dev}, {**old, "inode": old["inode"] + 1}):
                    with self.assertRaises(ValueError):
                        module.rehash_archive(path, expected, wrong)
                original = module.hashlib.file_digest

                def mutate(source, algorithm):
                    digest = original(source, algorithm)
                    path.write_bytes(payload + b"changed during read")
                    return digest

                with patch.object(module.hashlib, "file_digest", side_effect=mutate):
                    with self.assertRaisesRegex(ValueError, "changed during hash"):
                        module.rehash_archive(path, expected, old)
                path.write_bytes(payload)
                link = root / "link.tar"
                link.symlink_to(path)
                with self.assertRaises(ValueError):
                    module.rehash_archive(link, expected, old)
                from argparse import Namespace
                for output in (ROOT / "results/refused-recovery", root, root / "source/refused"):
                    with self.assertRaises(ValueError):
                        module.recover(Namespace(input_root=root / "source", archive_records=root / "pins",
                                                 preflight=root / "preflight.json", out_root=output))
                source_root, pin_root, repo = root / "source", root / "pins", root / "repo"
                source_root.mkdir()
                pin_root.mkdir()
                anchors = {name: expected["sha256"] for name in module.ANCHORS}
                pins = {}
                for name, digest in anchors.items():
                    archive = source_root / name
                    archive.write_bytes(payload)
                    record = pin_root / (name + ".sha256.json")
                    module.write_immutable_record(record, {"file_identity": {**module.file_identity(archive.stat()), "device": archive.stat().st_dev + 1}})
                    pins[name] = {"sha256": digest, "byte_size": len(payload), "private_record_sha256": module._sha256(record)}
                report = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                review = repo / "docs/176-review-doc175-oulu-batch06-archive-device-blocker.md"
                module.write_immutable_record(report, {"media_archives": pins})
                review.parent.mkdir(parents=True)
                review.write_text("synthetic recovery authority", encoding="ascii")
                preflight = root / "preflight.json"
                module.write_immutable_record(preflight, {
                    "protected_snapshots": {str(pin_root): {item.name: module._sha256(item) for item in pin_root.iterdir()}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {},
                    "recovery_code_sha256": module._sha256(Path(module.__file__)), "review176_sha256": module._sha256(review),
                    "archive_anchor_sha256": anchors, "archive_pin_report_sha256": module._sha256(report),
                    "source175_CI": {"head_sha": "d54f6723f3852bd1a0ef2d8d1862f1799639a0cb", "run_id": 38669499099,
                                     "job_id": 116209003838, "status": "completed", "conclusion": "success"}})
                with patch.object(module, "ROOT", repo), patch.object(module, "ANCHORS", anchors):
                    output = root / "success"
                    binding = module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=output))
                    self.assertEqual(len(binding["archives"]), 3)
                    self.assertEqual(binding["total_bytes_hashed"], 3 * len(payload))
                    self.assertTrue(binding["recovery_checkpoint_review_pending"])
                    self.assertFalse(binding["packet_preparation_authorized_by_this_record"])
                    with self.assertRaises(ValueError):
                        module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=output))
                    (source_root / "Test_files.tar").write_bytes(payload.replace(b"synthetic", b"different"))
                    refused = root / "mismatch"
                    with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
                        module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=refused))
                    self.assertTrue((refused / "Dev_files.tar.rehash.json").is_file())
                    self.assertFalse((refused / "environment_binding.json").exists())
                    self.assertFalse((refused / "Train_files.tar.rehash.json").exists())
        finally:
            sys.path.pop(0)

    def test_decode_count_mismatch_fails_closed(self) -> None:
        probe = {"streams": [{"codec_name": "rawvideo", "avg_frame_rate": "4/1"}],
                 "format": {"format_name": "avi", "duration": "1"},
                 "frames": [{"best_effort_timestamp_time": "0", "width": 32, "height": 24, "key_frame": 1}]}
        responses = [subprocess.CompletedProcess([], 0, json.dumps(probe), ""),
                     subprocess.CompletedProcess([], 0, "# empty decoded output\n", "")]
        with patch("fas.media.subprocess.run", side_effect=responses):
            result = probe_video(Path("never-opened.avi"))
        self.assertEqual(result["decode_status"], "failed")
        self.assertEqual(result["middle_decoded_candidates"], [])

    def test_runner_refuses_new_output_inside_repository(self) -> None:
        spec = importlib.util.spec_from_file_location("audit_oulu_media", ROOT / "scripts/audit_oulu_media.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            inputs = Path(directory) / "input"
            frozen = Path(directory) / "frozen"
            inputs.mkdir()
            frozen.mkdir()
            output = ROOT / "results" / "refused-private-media-test-output"
            args = module.argparse.Namespace(input_root=inputs, frozen_root=frozen, out_root=output, workers=1)
            with self.assertRaisesRegex(ValueError, "unsafe output"):
                module.audit(args)
            self.assertFalse(output.exists())

    def test_probe_rejects_corrupt_video_without_leaking_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private-corrupt.avi"
            path.write_bytes(b"not a video")
            result = probe_video(path)
        self.assertEqual(result["decode_status"], "failed")
        self.assertIsNone(result["decoded_rgb_sequence_sha256"])
        self.assertEqual(result["middle_decoded_candidates"], [])
        self.assertNotIn("private-corrupt", json.dumps(result))

    def test_full_decode_count_middle_and_reproducible_rgb_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.avi"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=32x24:rate=4", "-frames:v", "8", "-c:v",
                "rawvideo", "-pix_fmt", "bgr24", "-threads", "1", str(path),
            ], check=True, capture_output=True)
            result = probe_video(path)
            self.assertEqual(result, probe_video(path))
        self.assertEqual(result["decode_status"], "decoded")
        self.assertEqual(result["frame_count"], 8)
        self.assertEqual(result["fps"], "4")
        self.assertEqual(result["duration_ms"], 2000)
        self.assertEqual(result["middle_decoded_candidates"], [3, 4])
        self.assertEqual(len(result["frame_index"]), 8)
        self.assertEqual(result["frame_index"][4]["timestamp_seconds"], "1")

    def test_timeout_is_terminal_not_a_frame_replacement(self) -> None:
        with patch("fas.media.subprocess.run", side_effect=subprocess.TimeoutExpired("ffprobe", 1)):
            result = probe_video(Path("never-opened.avi"), timeout_seconds=1)
        self.assertEqual(result["failure_reason"], "timeout")
        self.assertEqual(result["decode_status"], "failed")
        self.assertEqual(result["middle_decoded_candidates"], [])


class OuluTest(unittest.TestCase):
    def test_training_polarity_and_documented_identity(self) -> None:
        records = parse_protocol("+1,1_1_01_1\n-1,1_1_01_2\n-1,1_1_01_4\n", "Protocols/Protocol_1/Train.txt")
        self.assertEqual([encode_label(row["binary_label"]) for row in records], [0, 1, 1])
        self.assertEqual([row["attack_family"] for row in records], ["none", "print", "replay"])
        self.assertEqual(records[0]["subject_id"], "subject-01")
        self.assertEqual(records[0]["sensor_id"], "phone-1")
        self.assertEqual(records[0]["session_id"], "session-1")
        self.assertEqual(records[0]["environment"], "unknown")
        self.assertEqual(records[1]["instrument"], "printer-1")
        self.assertEqual(records[2]["instrument"], "display-1")
        self.assertEqual(records[2]["raw_label_token"], "-1")
        self.assertEqual(records[2]["label_source"], "Protocols/Protocol_1/Train.txt")

    def test_test_labels_distinguish_print_and_replay(self) -> None:
        records = parse_protocol("+1,1_3_36_1\n-1,1_3_36_3\n-2,1_3_36_5\n", "Protocols/Protocol_4/Test_1.txt")
        self.assertEqual([row["raw_label_token"] for row in records], ["+1", "-1", "-2"])
        self.assertEqual([encode_label(row["binary_label"]) for row in records], [0, 1, 1])
        self.assertTrue(all(row["official_split"] == "test" and row["protocol_fold"] == 1 for row in records))
        self.assertEqual(records[1]["instrument"], "printer-2")
        self.assertEqual(records[2]["instrument"], "display-2")

    def test_unknown_inconsistent_and_malformed_labels_fail(self) -> None:
        for text in ("0,1_1_01_1", "1,1_1_01_1", "-1,1_1_01_1", "+1,1_1_01_2", "-2,1_1_01_4", "", "\n", "label,video", "+1,1_1_01_1,extra", '"+1,1_1_01_1'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_protocol(text, "Protocols/Protocol_1/Train.txt")
        with self.assertRaises(ValueError):
            parse_protocol("-1,1_3_36_4", "Protocols/Protocol_1/Test.txt")
        with self.assertRaises(ValueError):
            encode_label("unknown")

    def test_duplicate_and_unsafe_identifiers_fail(self) -> None:
        with self.assertRaises(ValueError):
            parse_protocol("+1,1_1_01_1\n+1,1_1_01_1", "Protocols/Protocol_1/Train.txt")
        for value in ("../1_1_01_1", "1_1_01_1.avi", "1_1_1_1", "7_1_01_1", "1_4_01_1", "1_1_00_1", "1_1_56_1", "1_1_01_6", "1_1_01_1\x00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_video_id(value)

    def test_protocol_membership_and_fold_authority(self) -> None:
        for text, path in (("+1,1_1_21_1", "Protocols/Protocol_1/Train.txt"), ("+1,1_3_01_1", "Protocols/Protocol_1/Train.txt"), ("-1,1_1_01_3", "Protocols/Protocol_2/Train.txt"), ("+1,1_1_01_1", "Protocols/Protocol_3/Train_1.txt"), ("+1,2_1_36_1", "Protocols/Protocol_3/Test_1.txt"), ("+1,1_1_01_1", "Protocols/Protocol_1/Train_1.txt"), ("+1,1_1_01_1", "Protocols/Protocol_3/Train.txt"), ("+1,1_1_01_1", "../Protocols/Protocol_1/Train.txt")):
            with self.subTest(path=path, text=text), self.assertRaises(ValueError):
                parse_protocol(text, path)
        records = parse_protocol("+1,2_2_21_1", "Protocols/Protocol_3/Dev_1.txt")
        self.assertEqual(records[0]["official_split"], "development")

    def test_mapping_hash_is_deterministic_and_score_contract(self) -> None:
        digest = hashlib.sha256(json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, LABEL_MAPPING_HASH)
        self.assertEqual(parse_video_id("1_1_01_1")["label_mapping_hash"], digest)
        for binary_label in ("bona_fide", "attack"):
            truth = encode_label(binary_label)
            for attack_score in (0.1, 0.9):
                prediction = int(attack_score >= 0.5)
                error = int(prediction != truth)
                self.assertEqual(error, 0 if prediction == truth else 1)
        self.assertGreater(encode_label("attack"), encode_label("bona_fide"))


class OuluInventoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "private-input"
        self.root.mkdir()
        (self.root / "Readme.pdf").write_bytes(b"synthetic documentation, not a real PDF")
        self.archives: dict[str, dict[str, bytes]] = {}
        self.partitions: dict[str, list[str]] = {}
        for storage, subject, session in (("Train_files", 1, 1), ("Dev_files", 21, 1), ("Test_files", 36, 3)):
            identifiers = [f"{phone}_{session}_{subject:02d}_1" for phone in range(1, 7)]
            if storage == "Train_files":
                identifiers += ["1_1_01_2", "2_1_01_4"]
            if storage == "Test_files":
                identifiers += ["1_3_36_3", "2_3_36_5"]
            self.partitions[storage] = identifiers
            self.archives[f"{storage}.tar"] = {
                f"{storage}/{video_id}{suffix}": b"synthetic bytes " + video_id.encode()
                for video_id in identifiers for suffix in (".avi", ".txt")
            }
        protocols: dict[str, bytes] = {}
        for protocol in range(1, 5):
            for fold in ((None,) if protocol < 3 else range(1, 7)):
                for name, storage in (("Train", "Train_files"), ("Dev", "Dev_files"), ("Test", "Test_files")):
                    rows = []
                    for video_id in self.partitions[storage]:
                        phone, session, subject, access = (int(part) for part in video_id.split("_"))
                        if fold is not None and ((phone == fold) != (name == "Test")):
                            continue
                        if protocol in (2, 4) and access not in ((1, 3, 5) if name == "Test" else (1, 2, 4)):
                            continue
                        token = "+1" if access == 1 else "-2" if name == "Test" and access >= 4 else "-1"
                        rows.append(f"{token},{video_id}\n")
                    suffix = "" if fold is None else f"_{fold}"
                    protocols[f"Protocols/Protocol_{protocol}/{name}{suffix}.txt"] = "".join(rows).encode()
        self.archives["Protocols.tar"] = protocols
        self.write_archives()

    def write_archives(self) -> None:
        for name, entries in self.archives.items():
            with tarfile.open(self.root / name, "w") as archive:
                for relative, payload in entries.items():
                    member = tarfile.TarInfo(relative)
                    member.size = len(payload)
                    archive.addfile(member, io.BytesIO(payload))

    def inventory(self, **options) -> dict:
        return inventory_archives(self.root, release_id="synthetic-release", protocol_id="synthetic-protocol", **options)

    def test_reconciles_synthetic_media_and_all_protocol_memberships(self) -> None:
        result = self.inventory()
        self.assertEqual(len(result["videos"]), 22)
        self.assertEqual(len(result["protocol_sha256"]), 42)
        self.assertEqual(result, self.inventory())
        self.assertFalse(result["scientific_readiness"])
        self.assertFalse(result["acquisition_verified"])
        self.assertTrue(all(row["official_split"] and row["protocol_memberships"] for row in result["videos"]))
        self.assertTrue(all(row["raw_label_token"] and row["label_source"] for row in result["videos"]))
        replay = next(row for row in result["videos"] if row["video_id"] == "2_3_36_5")
        self.assertTrue(all(row["raw_label_token"] == "-2" for row in replay["protocol_memberships"]))

    def test_header_only_mode_never_opens_video_payload(self) -> None:
        original = tarfile.TarFile.extractfile
        def guarded(archive, member):
            if member.name.endswith(".avi"):
                raise AssertionError("header-only inventory opened a video")
            return original(archive, member)
        with patch.object(tarfile.TarFile, "extractfile", guarded):
            result = self.inventory()
        self.assertTrue(result["no_media_decoding"])
        self.assertTrue(all(row["media_sha256"] is None and row["decode_status"] == "not_probed" for row in result["videos"]))

    def test_optional_byte_hashes_do_not_imply_decoding(self) -> None:
        result = self.inventory(hash_media=True)
        self.assertTrue(result["media_hashes_computed"])
        for row in result["videos"]:
            payload = self.archives[row["media_archive"]][row["media_relpath"]]
            self.assertEqual(row["media_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(row["decode_status"], "not_probed")
        self.assertTrue(all(value is not None for value in result["archive_sha256"].values()))

    def test_protocol_omission_or_missing_media_fails_closed(self) -> None:
        key = "Protocols/Protocol_1/Train.txt"
        original = self.archives["Protocols.tar"][key]
        self.archives["Protocols.tar"][key] = original.split(b"\n", 1)[1]
        self.write_archives()
        with self.assertRaisesRegex(ValueError, "membership disagree"):
            self.inventory()
        self.archives["Protocols.tar"][key] = original
        del self.archives["Train_files.tar"]["Train_files/1_1_01_1.avi"]
        self.write_archives()
        with self.assertRaises(ValueError):
            self.inventory()

    def test_missing_protocol_and_incomplete_release_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "full release"):
            self.inventory(require_full_release=True)
        del self.archives["Protocols.tar"]["Protocols/Protocol_4/Test_6.txt"]
        self.write_archives()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.inventory()

    def test_unsafe_members_links_and_duplicate_archive_paths_fail(self) -> None:
        archive = self.root / "Train_files.tar"
        for name, kind in (("../outside", tarfile.REGTYPE), ("Train_files/1_1_01_1.avi", tarfile.SYMTYPE), ("Train_files/1_1_01_1.avi", tarfile.LNKTYPE), ("Train_files/1_1_01_1.avi", tarfile.REGTYPE)):
            with self.subTest(name=name, kind=kind):
                self.write_archives()
                with tarfile.open(archive, "a") as target:
                    member = tarfile.TarInfo(name)
                    member.type = kind
                    member.size = 1 if kind == tarfile.REGTYPE else 0
                    member.linkname = "outside"
                    target.addfile(member, io.BytesIO(b"x") if member.size else None)
                with self.assertRaises(ValueError):
                    self.inventory()

    def command(self, output: Path, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run([
            sys.executable, str(ROOT / "scripts" / "inventory_oulu.py"),
            "--input-root", str(self.root), "--release-id", "synthetic-private-release",
            "--protocol-id", "synthetic-private-protocol", "--unverified-local",
            "--out", str(output), *extra,
        ], capture_output=True, text=True, check=False)

    def test_cli_writes_private_immutable_output_and_redacts_stdout(self) -> None:
        output = self.root.parent / "inventory.json"
        result = self.command(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["status"], "metadata_reconciled")
        self.assertFalse(summary["scientific_readiness"])
        self.assertFalse(summary["acquisition_verified"])
        self.assertNotIn("videos", summary)
        for secret in (str(self.root), "synthetic-private-release", "subject-01", "1_1_01_1"):
            self.assertNotIn(secret, result.stdout + result.stderr)
        original = output.read_bytes()
        self.assertEqual(len(json.loads(original)["videos"]), 22)
        self.assertEqual(self.command(output).returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def test_cli_blocks_reconciliation_failures_and_preserves_inputs(self) -> None:
        key = "Protocols/Protocol_1/Train.txt"
        self.archives["Protocols.tar"][key] = b"0,1_1_01_1\n"
        self.write_archives()
        output = self.root.parent / "blocked.json"
        result = self.command(output)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(output.exists())
        self.assertNotIn("1_1_01_1", result.stdout + result.stderr)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        original = (self.root / "Readme.pdf").read_bytes()
        self.assertEqual(self.command(self.root / "Readme.pdf").returncode, 2)
        self.assertEqual((self.root / "Readme.pdf").read_bytes(), original)
        self.assertEqual(self.command(ROOT / "results" / "refused-oulu.json").returncode, 2)

    def test_cli_full_release_flag_rejects_partial_synthetic_fixture(self) -> None:
        result = self.command(self.root.parent / "full.json", "--require-full-release")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root.parent / "full.json").exists())

    def test_invalid_documentation_symlink_and_corrupt_archive_fail_closed(self) -> None:
        document = self.root / "Readme.pdf"
        document.unlink()
        outside = self.root.parent / "outside.pdf"
        outside.write_bytes(b"outside documentation")
        document.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.inventory()
        document.unlink()
        document.write_bytes(b"synthetic documentation")
        (self.root / "Protocols.tar").write_bytes(b"not a tar archive")
        result = self.command(self.root.parent / "corrupt.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)

    def test_cli_redacts_required_file_symlink_loop(self) -> None:
        document = self.root / "Readme.pdf"
        document.unlink()
        document.symlink_to(document.name)
        result = self.command(self.root.parent / "loop.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertFalse((self.root.parent / "loop.json").exists())


if __name__ == "__main__":
    unittest.main()