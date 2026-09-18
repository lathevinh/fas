from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import CONFIG_FILES, STAGES, validate_stage


class GovernanceContractTest(unittest.TestCase):
    def test_final_stage_names_replace_legacy_stages(self) -> None:
        self.assertEqual(
            STAGES,
            (
                "schema",
                "data-audit",
                "source-dry-run",
                "analysis-freeze",
                "locked-evaluation",
            ),
        )
        for stage in ("data", "pre-pilot", "confirmatory"):
            with self.assertRaises(ValueError):
                validate_stage(ROOT, stage)

    def test_active_config_set_excludes_pilot_and_candidate_selection(self) -> None:
        self.assertIn("experiment_core_v1.yaml", CONFIG_FILES)
        self.assertIn("claims_v1.yaml", CONFIG_FILES)
        self.assertNotIn("pilot_selection_v1.yaml", CONFIG_FILES)
        self.assertNotIn("vlm_candidates_v1.yaml", CONFIG_FILES)

    def test_canonical_schema_is_valid(self) -> None:
        self.assertEqual(validate_stage(ROOT, "schema"), [])

    def test_schema_rejects_legacy_fields(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "experiment_core_v1.yaml"
            config = json.loads(path.read_text(encoding="utf-8"))
            config["pilot_domain"] = "MSU-MFSD"
            config["claim_sequence"] = ["rq2_complete_system"]
            path.write_text(json.dumps(config), encoding="utf-8")

            errors = validate_stage(copy, "schema")

        self.assertTrue(any("forbidden legacy field" in error for error in errors))

    def test_schema_rejects_wrong_primary_models_and_pooling(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "experiment_core_v1.yaml"
            config = json.loads(path.read_text(encoding="utf-8"))
            config["models"]["openclip"]["model"] = "ViT-L-14"
            config["models"]["dino_reg"]["pooling"] = "learned_attention"
            path.write_text(json.dumps(config), encoding="utf-8")

            errors = validate_stage(copy, "schema")

        self.assertTrue(any("OpenCLIP" in error for error in errors))
        self.assertTrue(any("CLS plus mean-patch" in error for error in errors))

    def test_schema_rejects_rq2_metric_sign_or_coverage_predicate_change(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "claims_v1.yaml"
            config = json.loads(path.read_text(encoding="utf-8"))
            rq2 = config["claims"]["rq2_complete_system"]
            rq2["endpoint"] = "prediction_error_ap"
            rq2["contrast"] = "U_heterogeneous_minus_U_same"
            rq2["coverage_role"] = "minimum_coverage_guardrail"
            path.write_text(json.dumps(config), encoding="utf-8")

            errors = validate_stage(copy, "schema")

        self.assertTrue(any("RQ2 claim" in error for error in errors))

    def test_schema_rejects_optional_routing_as_core_dependency(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "claims_v1.yaml"
            config = json.loads(path.read_text(encoding="utf-8"))
            routing = config["claims"]["optional_routing"]
            routing["enabled"] = True
            routing["core_readiness_dependency"] = True
            path.write_text(json.dumps(config), encoding="utf-8")

            errors = validate_stage(copy, "schema")

        self.assertTrue(any("optional routing" in error for error in errors))

    def test_schema_rejects_changed_solver_or_competence_contract(self) -> None:
        with self._copy() as copy:
            recipe_path = copy / "configs" / "source_recipe_v2.yaml"
            recipe = json.loads(recipe_path.read_text())
            recipe["risk_model"]["family"] = "random_forest"
            recipe["risk_features"].remove("R_DV")
            recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
            claims_path = copy / "configs" / "claims_v1.yaml"
            claims = json.loads(claims_path.read_text())
            claims["competence"]["complete_system"]["both_classes_required"] = False
            claims["competence"]["heterogeneous_risk_fit"]["minimum_errors"] = 0
            claims_path.write_text(json.dumps(claims), encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("solver contract" in error for error in errors))
            self.assertTrue(any("competence" in error for error in errors))

    def test_schema_rejects_acer_checkpoint_selection(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "source_recipe_v2.yaml"
            recipe = json.loads(path.read_text())
            recipe["branch_head"]["checkpoint_rule"] = (
                "lowest_source_validation_domain_macro_acer_then_earlier_epoch"
            )
            path.write_text(json.dumps(recipe), encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("solver contract" in error for error in errors))

    def test_schema_rejects_replacement_seed(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "seeds_v1.yaml"
            seeds = json.loads(path.read_text())
            seeds["seeds"][-1] = 20261002
            path.write_text(json.dumps(seeds), encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("frozen primary seeds" in error for error in errors))

    @contextmanager
    def _copy(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "repo"
            shutil.copytree(
                ROOT,
                destination,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            yield destination


if __name__ == "__main__":
    unittest.main()