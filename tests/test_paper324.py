import copy
import csv
from fractions import Fraction
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("paper324_export", ROOT / "scripts/paper324/export.py")
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def fixture():
    contexts = []
    for target in export.TARGETS:
        for seed in export.SEEDS:
            cases = []
            for system in export.SYSTEMS:
                for alpha in export.ALPHAS:
                    budget = int(Fraction(alpha)*20)
                    fa, bfa = ((.05, .5) if budget >= 1 else (0., 0.))
                    policy = {"original_attack": 20., "original_bona_fide": 10.,
                              "usable_attack": 20., "usable_bona_fide": 10.,
                              "accepted_attack": 1., "accepted_bona_fide": 4.,
                              "FA": .05, "BFA": .4, "AUROC_usable": .8,
                              "FA_within_constraint": budget >= 1, "utility_feasible": False}
                    oracle = {"attack_error_budget": budget, "original_attack": 20, "original_bona_fide": 10,
                              "oracle_FA": fa, "oracle_max_BFA": bfa,
                              "oracle_accepted_attack": int(fa*20), "oracle_accepted_bona_fide": int(bfa*10),
                              "empirically_attainable": bfa >= .5, "uses_evaluation_labels": True}
                    cases.append({"system": system, "alpha": alpha, "policy": policy, "oracle": oracle,
                                  "limiting_sources": ["MSU-MFSD"], "source_attack_budgets": {"MSU-MFSD": 0}})
            analysis = {"cases": cases, "curves": {s: [[0., 0.], [.05, .5], [1., 1.]] for s in export.SYSTEMS},
                        "bootstrap_unit": ("video_exact_frame_component" if target == "SiW-Mv2"
                                           else "subject_exact_frame_component"), "oracle_intervals": None}
            for field, systems in (("conditional_intervals", export.SYSTEMS),
                                   ("paired_minus_dino_reg", export.SYSTEMS[1:])):
                analysis[field] = [{"system": system, "alpha": alpha, "metric": metric,
                                    "valid_repetitions": 2000, "total_repetitions": 2000,
                                    "percentile95": [.01, .9] if field == "conditional_intervals" else [0., 0.]}
                                   for system in systems for alpha in export.ALPHAS for metric in export.METRICS]
            contexts.append({"target": target, "seed": seed, "analysis": analysis})
    return {"contexts": contexts, "aggregate": export.runner.study.aggregate(contexts),
            "fit_starts": {"frozen": 24, "specialist": 7, "calibrator": 32},
            "cumulative_fit_starts": {"frozen": 39, "specialist": 12, "calibrator": 52},
            "retained_complete_contexts": 4, "new_foundation_encoder_forwards": 0, "oracle_is_diagnostic": True}


class ExportTests(unittest.TestCase):
    def test_complete_shapes_no_best_seed_filter_and_paired_estimates(self):
        source = fixture()
        export.validate(source)
        contexts = source["contexts"]
        cases = export.case_rows(contexts)
        intervals = export.interval_rows(contexts)
        summary = export.summaries(contexts)
        self.assertEqual(len(cases), 144)
        self.assertEqual(sum(r["alpha"] == "1/20" for r in cases), 48)
        self.assertEqual(len(intervals), 756)
        self.assertEqual(len(summary), 48)
        self.assertTrue(all(r["estimate"] == 0 for r in intervals if r["kind"] == "paired_minus_dino_reg"))
        csv_rows = list(csv.DictReader(io.StringIO(export.csv_bytes(cases).decode())))
        self.assertEqual(len(csv_rows), 144)
        self.assertEqual({int(r["seed"]) for r in csv_rows}, set(export.SEEDS))
        tables = export.tables(contexts, summary, intervals).decode()
        self.assertIn("All 48", tables)
        self.assertIn("SiW-Mv2", tables)
        self.assertIn("not same-security gains", tables)
        self.assertTrue(all(r["policy_utility_feasible"] == 0 for r in summary))

    def test_missing_duplicate_or_inconsistent_cases_fail_closed(self):
        for mutate in (
                lambda x: x["contexts"].pop(),
                lambda x: x["contexts"][0]["analysis"]["cases"].pop(),
                lambda x: x["contexts"][0]["analysis"]["cases"][0]["policy"].update(FA=.9),
                lambda x: x["contexts"][0]["analysis"]["cases"][0]["oracle"].update(oracle_max_BFA=.9),
                lambda x: x["contexts"][0]["analysis"]["cases"][0]["policy"].update(utility_feasible=True),
                lambda x: x["contexts"][0]["analysis"]["conditional_intervals"].pop(),
                lambda x: x["contexts"][0]["analysis"].update(bootstrap_unit="video_exact_frame_component"),
                lambda x: x["contexts"][0]["analysis"]["curves"]["dino_reg"].reverse(),
                lambda x: x.update(cumulative_fit_starts={"frozen": 36, "specialist": 12, "calibrator": 48})):
            source = fixture()
            mutate(source)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                export.validate(source)

    def test_undefined_intervals_retain_valid_draw_counts(self):
        source = fixture()
        item = source["contexts"][0]["analysis"]["conditional_intervals"][0]
        item.update(valid_repetitions=1899, percentile95=None)
        export.validate(source)
        row = export.interval_rows(source["contexts"])[0]
        self.assertEqual(row["valid_repetitions"], 1899)
        self.assertIsNone(row["lower95"])
        self.assertIsNone(row["upper95"])
        invalid = copy.deepcopy(source)
        invalid["contexts"][0]["analysis"]["conditional_intervals"][0]["valid_repetitions"] = 1900
        with self.assertRaisesRegex(ValueError, "valid-draw"):
            export.validate(invalid)


if __name__ == "__main__":
    unittest.main()
