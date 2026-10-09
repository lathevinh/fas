"""Pure synthetic contracts for the frozen Phase 0 research specification."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any


MCIO_DOMAINS = {"OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"}
CORE_DOMAINS = {"OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"}
SIWMV2_ATTACK_FAMILIES = {
    "Makeup_Co": "makeup", "Makeup_Im": "makeup", "Makeup_Ob": "makeup",
    "Mask_Half": "mask", "Mask_Mann": "mask", "Mask_Paper": "mask",
    "Mask_Silicone": "mask", "Mask_Trans": "mask", "Paper": "print",
    "Partial_Eye": "partial", "Partial_Funnyeye": "partial",
    "Partial_Mouth": "partial", "Partial_Paperglass": "partial", "Replay": "replay",
}
GROUP_BOUNDARIES = (
    "permanent_source_roles", "head_inner_validation", "matched_sample_oof",
    "fold_local_calibration", "derived_frame_crop_ancestry", "target_bootstrap",
)
RQ1_DEPENDENCIES = (
    "heterogeneous_complete_competence",
    "dino_anchor_nondegeneracy",
)
RQ2_DEPENDENCIES = (
    "heterogeneous_complete_competence",
    "same_family_complete_competence",
    "dino_anchor_nondegeneracy",
)
PRIMARY_SEEDS = (20260917, 20260923, 20261001)


def _source_records(artifact: Mapping[str, Any], name: str, errors: list[str]) -> dict[tuple[str, int], Mapping[str, Any]]:
    records = artifact.get("records")
    if not isinstance(records, list) or len(records) != 12:
        errors.append(f"{name} contents require all four excluded-target folds and three seeds")
        return {}
    indexed: dict[tuple[str, int], Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            errors.append(f"{name} contents require typed source records")
            continue
        target, seed = record.get("outer_target"), record.get("seed")
        if not isinstance(target, str) or target not in CORE_DOMAINS or type(seed) is not int or seed not in PRIMARY_SEEDS:
            errors.append(f"{name} contents require frozen fold/seed identities")
            continue
        sources = record.get("source_domains")
        if not isinstance(sources, list) or not all(isinstance(domain, str) for domain in sources) or len(sources) != 3 or set(sources) != CORE_DOMAINS - {target}:
            errors.append(f"{name} contents require exactly the three non-target source domains")
        key = (target, seed)
        if key in indexed:
            errors.append(f"{name} contents contain a duplicate fold/seed")
        indexed[key] = record
    if set(indexed) != {(target, seed) for target in CORE_DOMAINS for seed in PRIMARY_SEEDS}:
        errors.append(f"{name} contents omit a frozen fold/seed")
    return indexed


def _finite_number(value: Any, minimum: float, maximum: float | None = None) -> bool:
    return (
        isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value) and value >= minimum
        and (maximum is None or value <= maximum)
    )


def _event_count(value: Any) -> bool:
    return type(value) is int and value >= 0


def validate_source_evidence(
    competence: Mapping[str, Any], applicability: Mapping[str, Any],
) -> list[str]:
    """Validate source-only evidence, not target results or scientific outcomes."""
    errors: list[str] = []
    for name, artifact in (("competence.json", competence), ("applicability.json", applicability)):
        if type(artifact.get("version")) is not int or artifact.get("version") != 1 or artifact.get("no_target_selection_input") is not True:
            errors.append(f"{name} contents require version 1 and source-only lineage")
    competence_records = _source_records(competence, "competence.json", errors)
    applicability_records = _source_records(applicability, "applicability.json", errors)
    if applicability.get("n_error_min") != 20 or type(applicability.get("n_error_min")) is not int:
        errors.append("applicability.json contents require the frozen n_error_min=20")
    if applicability.get("target_event_support") != "not_inspected":
        errors.append("applicability.json contents cannot attest target event support before evaluation")
    for key, record in competence_records.items():
        systems = record.get("systems")
        system_names = {"dino_reg", "openclip", "heterogeneous", "same_family"}
        if not isinstance(systems, Mapping) or set(systems) != system_names:
            errors.append(f"competence.json contents require all four systems for {key}")
            continue
        computed: dict[str, bool] = {}
        nondegenerate: dict[str, bool] = {}
        for name, values in systems.items():
            if not isinstance(values, Mapping):
                errors.append(f"competence.json contents require typed {name} metrics for {key}")
                continue
            numerical = ("macro_auroc", "macro_balanced_accuracy", "macro_auroc_lcb")
            flags = ("finite_scores", "both_classes", "finite_calibration", "pass")
            valid = all(_finite_number(values.get(field), 0, 1) for field in numerical)
            valid = valid and _finite_number(values.get("score_range"), 0)
            valid = valid and all(type(values.get(field)) is bool for field in flags)
            if not valid:
                errors.append(f"competence.json contents require finite typed {name} metrics for {key}")
                continue
            nondegenerate[name] = (
                values["finite_scores"] and values["both_classes"]
                and values["finite_calibration"] and values["score_range"] > 1e-6
            )
            computed[name] = (
                nondegenerate[name] and values["macro_auroc"] >= 0.55
                and values["macro_balanced_accuracy"] >= 0.55
                and values["macro_auroc_lcb"] > 0.50
            )
            if values["pass"] is not computed[name]:
                errors.append(f"competence.json contents have inconsistent {name} pass for {key}")
        if set(computed) != system_names:
            continue
        anchor = nondegenerate["dino_reg"]
        if record.get("dino_anchor_pass") is not anchor:
            errors.append(f"competence.json contents have inconsistent DINO anchor pass for {key}")
        risk_fit = record.get("heterogeneous_risk_fit")
        if not isinstance(risk_fit, Mapping) or not all(_event_count(risk_fit.get(field)) for field in ("error_count", "correct_count")):
            errors.append(f"competence.json contents require typed risk-fit counts for {key}")
            continue
        risk_pass = risk_fit["error_count"] >= 20 and risk_fit["correct_count"] >= 20
        if risk_fit.get("pass") is not risk_pass:
            errors.append(f"competence.json contents have inconsistent risk-fit pass for {key}")
        rq1_eligible = computed["heterogeneous"] and anchor and risk_pass
        rq2_eligible = computed["heterogeneous"] and computed["same_family"] and anchor
        if not rq1_eligible:
            errors.append(f"competence.json contents do not satisfy core source prerequisites for {key}")
        application = applicability_records.get(key)
        if application is None:
            continue
        expected_claims = {
            "rq1_oof_transfer": "eligible" if rq1_eligible else "not_applicable",
            "rq2_complete_system": "eligible" if rq2_eligible else "not_applicable",
        }
        if application.get("claims") != expected_claims:
            errors.append(f"applicability.json contents disagree with claim-specific competence for {key}")
        events = application.get("source_events")
        if not isinstance(events, Mapping) or set(events) != CORE_DOMAINS - {key[0]}:
            errors.append(f"applicability.json contents require non-target source event counts for {key}")
            continue
        totals = {"error_count": 0, "correct_count": 0}
        valid_events = True
        for domain, counts in events.items():
            if not isinstance(counts, Mapping) or not all(_event_count(counts.get(field)) for field in totals):
                errors.append(f"applicability.json contents require typed event counts for {key}/{domain}")
                valid_events = False
                continue
            estimable = counts["error_count"] > 0 and counts["correct_count"] > 0
            supported = estimable and counts["error_count"] >= 20
            if counts.get("ap_estimable") is not estimable or counts.get("meets_n_error_min") is not supported:
                errors.append(f"applicability.json contents have inconsistent event support for {key}/{domain}")
            for field in totals:
                totals[field] += counts[field]
        if valid_events and any(totals[field] != risk_fit[field] for field in totals):
            errors.append(f"applicability.json contents do not reconcile with risk-fit counts for {key}")
    return errors


@dataclass(frozen=True)
class Applicability:
    """Event-support state for one target across three optimization seeds."""

    target_eligible: bool
    supporting_seed_count: int
    status: str


def aggregate_seed_then_target(
    deltas: Mapping[str, Sequence[float]],
) -> tuple[dict[str, float], float]:
    """Average exactly three seeds per target, then all four amended targets."""
    if set(deltas) != CORE_DOMAINS:
        raise ValueError("deltas must contain exactly the four amended targets")
    target_deltas: dict[str, float] = {}
    for target, seed_deltas in deltas.items():
        if len(seed_deltas) != 3:
            raise ValueError(f"{target} must contain exactly three seed deltas")
        if any(
            not isinstance(delta, (int, float))
            or isinstance(delta, bool)
            or not math.isfinite(delta)
            for delta in seed_deltas
        ):
            raise ValueError(f"{target} seed deltas must be finite numbers")
        target_deltas[target] = sum(seed_deltas) / 3
    return target_deltas, sum(target_deltas.values()) / 4


def evaluate_rq1_applicability(
    error_counts: Sequence[int],
    ap_estimable: Sequence[bool],
    n_error_min: int = 20,
) -> Applicability:
    """Classify target support without deleting an underpowered seed."""
    if len(error_counts) != 3 or len(ap_estimable) != 3:
        raise ValueError("RQ1 applicability requires exactly three seeds")
    if any(
        not isinstance(count, int) or isinstance(count, bool) or count < 0
        for count in error_counts
    ):
        raise ValueError("error counts must be nonnegative integers")
    if any(not isinstance(value, bool) for value in ap_estimable):
        raise ValueError("AP estimability flags must be booleans")
    supporting = sum(
        estimable and count >= n_error_min
        for count, estimable in zip(error_counts, ap_estimable, strict=True)
    )
    eligible = all(ap_estimable) and supporting >= 2
    return Applicability(
        target_eligible=eligible,
        supporting_seed_count=supporting,
        status="eligible" if eligible else "inconclusive",
    )


def class_balanced_aurc(
    attack: Sequence[tuple[float, int]],
    bona_fide: Sequence[tuple[float, int]],
) -> float:
    """Return the equal-class raw AURC with expectation-based tie handling."""
    return (_tie_stable_aurc(attack) + _tie_stable_aurc(bona_fide)) / 2


def paired_cluster_multiplicities(
    cluster_ids: Sequence[str],
    repetitions: int,
    seed: int,
) -> list[dict[str, int]]:
    """Generate reusable cluster multiplicities for paired bootstrap replicates."""
    clusters = sorted(set(cluster_ids))
    if not clusters or any(not isinstance(cluster, str) or not cluster for cluster in clusters):
        raise ValueError("cluster IDs must contain nonempty strings")
    if not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions <= 0:
        raise ValueError("bootstrap repetitions must be a positive integer")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("bootstrap seed must be an integer")
    generator = random.Random(seed)
    resamples: list[dict[str, int]] = []
    for _ in range(repetitions):
        multiplicities = {cluster: 0 for cluster in clusters}
        for _ in clusters:
            multiplicities[generator.choice(clusters)] += 1
        resamples.append(multiplicities)
    return resamples


def k1_end_to_end_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, float | int]:
    """Compute K=1 rates over original class denominators, including failures."""
    if not rows:
        raise ValueError("K=1 summary requires transaction rows")
    attack_rows = [row for row in rows if row.get("label") == "attack"]
    bona_rows = [row for row in rows if row.get("label") == "bona_fide"]
    if len(attack_rows) + len(bona_rows) != len(rows):
        raise ValueError("K=1 rows require attack or bona_fide labels")
    if not attack_rows or not bona_rows:
        raise ValueError("K=1 summary requires both classes")
    for row in rows:
        if row.get("detector_status") not in {"success", "failure", "not_run"}:
            raise ValueError("K=1 rows require valid detector status")
        if row["detector_status"] == "not_run" and row.get("technical_status") != "terminal_failure":
            raise ValueError("unexecuted detector requires terminal technical failure")
        if row.get("technical_status") == "terminal_failure" and (
            row["detector_status"] != "not_run" or row.get("model_score") is not None
            or row.get("classifier_error") is not None
        ):
            raise ValueError("pre-detector failure cannot fabricate detector or classifier evidence")
        if row.get("final_k1_action") not in {"accept", "non_accept"}:
            raise ValueError("K=1 rows require accept or non_accept actions")
        if row["detector_status"] in {"failure", "not_run"} and row["final_k1_action"] != "non_accept":
            raise ValueError("detector failure must be terminal non-accept")
    return {
        "attack_total": len(attack_rows),
        "bona_fide_total": len(bona_rows),
        "fa_end2end": sum(row["final_k1_action"] == "accept" for row in attack_rows)
        / len(attack_rows),
        "bfnr_end2end": sum(row["final_k1_action"] != "accept" for row in bona_rows)
        / len(bona_rows),
        "attack_detector_coverage": sum(
            row["detector_status"] == "success" for row in attack_rows
        )
        / len(attack_rows),
        "bona_fide_detector_coverage": sum(
            row["detector_status"] == "success" for row in bona_rows
        )
        / len(bona_rows),
    }


def _tie_stable_aurc(observations: Sequence[tuple[float, int]]) -> float:
    if not observations:
        raise ValueError("AURC requires at least one transaction in each class")
    for risk, error in observations:
        if not isinstance(risk, (int, float)) or isinstance(risk, bool) or not math.isfinite(risk):
            raise ValueError("risk scores must be finite numbers")
        if error not in (0, 1) or isinstance(error, bool):
            raise ValueError("error labels must be binary integers")

    ordered = sorted(observations, key=lambda item: item[0])
    cumulative_errors = 0.0
    risk_sum = 0.0
    position = 0
    while position < len(ordered):
        end = position + 1
        while end < len(ordered) and ordered[end][0] == ordered[position][0]:
            end += 1
        block = ordered[position:end]
        expected_error_per_item = sum(error for _, error in block) / len(block)
        for offset in range(1, len(block) + 1):
            retained = position + offset
            expected_cumulative = cumulative_errors + offset * expected_error_per_item
            risk_sum += expected_cumulative / retained
        cumulative_errors += sum(error for _, error in block)
        position = end
    return risk_sum / len(ordered)


def validate_rq1_pair(
    domain_rows: Sequence[Mapping[str, Any]],
    sample_rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    """Require identical transactions, predictions, and error labels for RQ1."""
    errors: list[str] = []
    domain = _rows_by_id(domain_rows, "domain-OOF", errors)
    sample = _rows_by_id(sample_rows, "sample-OOF", errors)
    if set(domain) != set(sample):
        errors.append("RQ1 comparators must contain identical transaction IDs")
        return errors
    for transaction_id in sorted(domain):
        for field in ("prediction", "error"):
            if domain[transaction_id].get(field) != sample[transaction_id].get(field):
                errors.append(
                    f"RQ1 comparators differ in {field} for transaction {transaction_id}"
                )
    return errors


def _rows_by_id(
    rows: Sequence[Mapping[str, Any]],
    label: str,
    errors: list[str],
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        transaction_id = row.get("transaction_id")
        if not isinstance(transaction_id, str) or not transaction_id:
            errors.append(f"{label} row requires a nonempty transaction ID")
            continue
        if transaction_id in indexed:
            errors.append(f"{label} contains duplicate transaction {transaction_id}")
        indexed[transaction_id] = row
    return indexed


def validate_transaction_ledger(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Validate common detector masks and K=1 detector-failure semantics."""
    errors: list[str] = []
    by_system: dict[str, dict[str, Mapping[str, Any]]] = {
        "heterogeneous": {},
        "same_family": {},
    }
    required_fields = {
        "transaction_id",
        "sample_id",
        "dataset",
        "subject_id",
        "video_id",
        "outer_target",
        "system",
        "ground_truth",
        "detector_status",
        "pad_score",
        "pad_threshold",
        "pad_decision",
        "risk_score",
        "gate_threshold",
        "gate_action",
        "final_k1_action",
        "classifier_artifact_hash",
        "risk_artifact_hash",
        "policy_artifact_hash",
    }
    for row in rows:
        missing = required_fields - row.keys()
        if missing:
            errors.append("transaction ledger row is missing: " + ", ".join(sorted(missing)))
            continue
        system = row["system"]
        transaction_id = row["transaction_id"]
        if system not in by_system or not isinstance(transaction_id, str) or not transaction_id:
            errors.append("transaction ledger requires a known system and nonempty ID")
            continue
        if transaction_id in by_system[system]:
            errors.append(f"duplicate {system} transaction {transaction_id}")
        by_system[system][transaction_id] = row
        for field in ("sample_id", "dataset", "video_id"):
            if not isinstance(row[field], str) or not row[field]:
                errors.append(f"transaction {transaction_id} requires nonempty {field}")
        if row["dataset"] == "SiW-Mv2":
            if row["subject_id"] is not None:
                errors.append(f"transaction {transaction_id} requires unknown SiW-Mv2 subject_id as null")
        elif not isinstance(row["subject_id"], str) or not row["subject_id"]:
            errors.append(f"transaction {transaction_id} requires nonempty subject_id")
        if row["outer_target"] not in CORE_DOMAINS:
            errors.append(f"transaction {transaction_id} requires a frozen amended outer target")
        if row["dataset"] != row["outer_target"]:
            errors.append(f"transaction {transaction_id} dataset must match its outer target")
        if row["ground_truth"] not in {"attack", "bona_fide"}:
            errors.append(f"transaction {transaction_id} has invalid ground truth")
        for field in (
            "classifier_artifact_hash",
            "risk_artifact_hash",
            "policy_artifact_hash",
        ):
            if not _sha256(row[field]):
                errors.append(f"transaction {transaction_id} requires valid {field}")
        status = row["detector_status"]
        if status not in {"success", "failure"}:
            errors.append(f"invalid detector status for transaction {transaction_id}")
        if status == "failure":
            nullable = (
                "pad_score",
                "pad_threshold",
                "pad_decision",
                "risk_score",
                "gate_threshold",
                "gate_action",
            )
            if any(row[field] is not None for field in nullable):
                errors.append("detector failures require null scores and decisions")
            if row["final_k1_action"] != "non_accept":
                errors.append("detector failures must be terminal non-accepts under K=1")
        elif status == "success":
            for field in ("pad_score", "pad_threshold", "risk_score"):
                value = row[field]
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or not math.isfinite(value)
                ):
                    errors.append(f"detector success requires finite {field}")
            if row["pad_decision"] not in {"attack", "bona_fide"}:
                errors.append("detector success requires a typed PAD decision")
            if row["final_k1_action"] not in {"accept", "non_accept"}:
                errors.append("detector success requires a typed final K=1 action")
            if row["pad_decision"] == "attack":
                if row["gate_threshold"] is not None or row["gate_action"] is not None:
                    errors.append("gate is not applied to PAD attack decisions; gate fields must be null")
                if row["final_k1_action"] != "non_accept":
                    errors.append("PAD attack decisions must be terminal non-accepts under K=1")
            elif row["pad_decision"] == "bona_fide":
                if not _finite_number(row["gate_threshold"], -math.inf):
                    errors.append("predicted-live decisions require a finite gate_threshold")
                if row["gate_action"] not in {"accept", "non_accept"}:
                    errors.append("predicted-live decisions require a typed gate action")
                if row["final_k1_action"] != row["gate_action"]:
                    errors.append("predicted-live final K=1 action must match gate action")

    heterogeneous = by_system["heterogeneous"]
    same_family = by_system["same_family"]
    if set(heterogeneous) != set(same_family):
        errors.append("RQ2 systems require bit-identical transaction IDs")
        return errors
    for transaction_id in heterogeneous:
        left = heterogeneous[transaction_id]
        right = same_family[transaction_id]
        if left["detector_status"] != right["detector_status"]:
            errors.append("RQ2 systems require a bit-identical detector-success mask")
        identity_fields = (
            "sample_id",
            "dataset",
            "subject_id",
            "video_id",
            "outer_target",
            "ground_truth",
        )
        if any(left[field] != right[field] for field in identity_fields):
            errors.append("RQ2 systems require bit-identical paired identity and ground truth")
    return errors


def _sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_risk_view(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Require risk-metric views to contain detector-successful transactions only."""
    errors: list[str] = []
    transaction_ids: set[str] = set()
    for row in rows:
        transaction_id = row.get("transaction_id")
        if not isinstance(transaction_id, str) or not transaction_id:
            errors.append("risk view requires a nonempty transaction ID")
        elif transaction_id in transaction_ids:
            errors.append(f"risk view contains duplicate transaction {transaction_id}")
        else:
            transaction_ids.add(transaction_id)
        if row.get("detector_status") != "success":
            errors.append("risk view may contain detector-successful transactions only")
        risk_score = row.get("risk_score")
        if (
            not isinstance(risk_score, (int, float))
            or isinstance(risk_score, bool)
            or not math.isfinite(risk_score)
        ):
            errors.append("risk view requires a finite risk score")
    return errors


def competence_allows_claim(
    claim_id: str,
    competence: Mapping[str, bool],
) -> bool:
    """Apply claim-specific competence dependencies without branch kill switches."""
    dependencies = {
        "rq1_oof_transfer": RQ1_DEPENDENCIES,
        "rq2_complete_system": RQ2_DEPENDENCIES,
        "openclip_standalone": ("openclip_standalone_competence",),
        "dino_standalone": ("dino_standalone_competence",),
    }
    if claim_id not in dependencies:
        raise ValueError(f"unknown competence claim: {claim_id}")
    return all(competence.get(dependency) is True for dependency in dependencies[claim_id])