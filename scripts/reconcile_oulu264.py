"""Reconcile existing OULU metadata without opening media or changing dispositions."""

from __future__ import annotations

import hashlib
import json
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from fas.freeze import write_immutable_record

BASE = Path('/mnt/e/FAS-private/artifacts/phase1')
ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'oulu_investigation257_preflight_v1.json': '5021a83530b34cf2bad7051d94a41efea9845a6c54b9b2aac33a81c9d00c9916',
    'oulu_method249_plan_verification_v1.json': '67520c44ba519afa45d9a4b76275daa33b1139dd7dc34ba56ce6713cb3dbebb9',
    'oulu_cross_role_protocol241_provenance_v1.json': 'fa35cd8ed4281c6d9848b21374de9cd7d5b9f992044002b7d936437dc6b34c29',
    'oulu_investigation257_run_v1/summary.json': 'c89216450e28289a5c8d2101c3dba6ec1769dd9bc8ff6c1e288fe22ef2926c47',
    'oulu_witness259_analysis_v1.json': 'f593249cfe9e3b13975835ed629f4f4f792510f8a9c42b11c640b7ee5b6b05f6',
    'oulu_d261_inspection_v1.json': 'fab137783747b8477866ce5faab010666271d6b8c679dbe58e8750c168e92d93',
}
DECISION = (
    'Cannot complete local OULU lineage acceptance under retained247 using the existing evidence. '
    'Recognize399 completed technical comparisons and the completed five-witness analysis, '
    'but approve zero new scientific dispositions and retain both OULU audit statuses as not_audited. '
    'The five observed correspondence cases remain materially unresolved;394 other candidates '
    'have coarse pHash triggers but no accepted allegation-specific rejection or validated '
    'negative coverage. General blind spots are not394 observed hidden-reuse allegations. '
    'Close this existing-evidence route without commissioning new media, algorithms or paperwork. '
    'No assurance weakening, risk tolerance, exclusion or role/data change is adopted. '
    'Further completion requires a genuinely discriminating disposition basis for A-E and '
    'an accepted finite coverage/rejection basis for the listed non-detection groups; '
    'neither exists in the reconciled records. If unavailable, the local audit remains incomplete.'
)


def read_record(path: Path, expected_sha256: str | None = None) -> tuple[dict, str]:
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError(f'parent hash drift: {path.name}')
    return json.loads(content), digest


def frozen_rows(preflight: dict, plan: dict) -> list[dict]:
    rows = preflight['rows']
    expected = [{key: value for key, value in row.items() if key != 'existing_evidence'}
                for row in plan['rows']]
    ranks = [row['queue_rank'] for row in rows]
    if (len(rows) != 399 or len(set(ranks)) != 399 or rows != expected
            or preflight['videos'] != plan['videos']
            or preflight['components'] != plan['components']
            or len(preflight['videos']) != 438 or len(preflight['components']) != 91):
        raise ValueError('frozen399/438/91 row or parent drift')
    return rows


def evidence_group(candidate: dict, pair: dict, case: dict | None) -> str:
    if candidate['minimum_hamming'] > 4 and candidate['aligned_slots_within_8'] < 3:
        raise ValueError('candidate does not meet the recorded generation rule')
    branches = pair['branches']
    witness = any(branch['witnesses'] for branch in branches.values())
    if (case is not None) != witness:
        raise ValueError('five-case observation coverage does not match witness evidence')
    if any(branch['scientific_disposition'] is not None for branch in branches.values()):
        raise ValueError('unexpected approved scientific disposition')
    if witness:
        return 'witness_' + case['alias']
    reason = ('both_rules' if candidate['minimum_hamming'] <= 4 and candidate['aligned_slots_within_8'] >= 3
              else 'minimum_only' if candidate['minimum_hamming'] <= 4 else 'aligned_only')
    geometry = 'subchain_geometry' if any(branch['geometric_hits'] for branch in branches.values()) else 'no_geometry'
    return 'non_detection_' + reason + '_' + geometry


def group_members(rows: list[dict]) -> dict[str, list[str]]:
    result = {}
    for row in rows:
        result.setdefault(row['evidence_group'], []).append(row['edge_id'])
    members = [member for group in result.values() for member in group]
    if len(members) != 399 or len(set(members)) != 399:
        raise ValueError('group membership must partition exactly399 distinct edges')
    return result


def build_ledger() -> tuple[dict, dict]:
    parents = {}
    cache = {}

    def record(path: Path, expected: str | None = None) -> dict:
        key = str(path)
        if key not in cache:
            cache[key], parents[key] = read_record(path, expected)
        elif expected is not None and parents[key] != expected:
            raise ValueError('inconsistent parent commitment')
        return cache[key]

    sources = {name: record(BASE / name, digest) for name, digest in PINS.items()}
    preflight = sources['oulu_investigation257_preflight_v1.json']
    plan = sources['oulu_method249_plan_verification_v1.json']
    rows = frozen_rows(preflight, plan)
    provenance = sources['oulu_cross_role_protocol241_provenance_v1.json']['metadata_reconciliation']
    summary = sources['oulu_investigation257_run_v1/summary.json']
    analysis = sources['oulu_witness259_analysis_v1.json']
    detail = sources['oulu_d261_inspection_v1.json']
    if (summary['technical_complete'] is not True or summary['failure'] is not None
            or summary['pairs_screened'] != 399 or summary['successful_endpoints'] != 438):
        raise ValueError('accepted complete257 output required')
    members = {member['queue_rank']: member for member in provenance['members']}
    cases = {case['pair_record']['queue_rank']: case for case in analysis['cases']}
    if len(members) != 399 or len(cases) != 5 or {case['alias'] for case in cases.values()} != set('ABCDE'):
        raise ValueError('complete provenance and five observed cases required')
    screen = record(BASE / 'oulu_content_screening_v1/summary.json')
    lineage = record(BASE / 'oulu_content_screening_v1/lineage.json', screen['lineage_sha256'])
    frozen_root = Path(preflight['paths']['frozen_root'])
    frozen = {}
    for name in ('oulu_npu_roles.csv', 'oulu_npu_metadata.csv'):
        path = frozen_root / name
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != lineage['frozen_artifact_sha256'][name]:
            raise ValueError('frozen role/metadata drift')
        parents[str(path)] = digest
        with path.open(newline='') as handle:
            entries = list(csv.DictReader(handle))
        indexed = {entry['video_id']: entry for entry in entries}
        if len(indexed) != len(entries):
            raise ValueError('duplicate frozen video identity')
        frozen[name] = indexed
    wanted = {(row['left'], row['right']) for row in rows}
    candidates = {}
    for chunk in screen['candidate_chunks']:
        path = BASE / 'oulu_content_screening_v1/pairs' / chunk['name']
        for candidate in record(path, chunk['sha256'])['pairs']:
            key = candidate['left'], candidate['right']
            if key in wanted:
                if key in candidates:
                    raise ValueError('duplicate original candidate')
                candidates[key] = (candidate, str(path))
    if set(candidates) != wanted:
        raise ValueError('original candidate join incomplete')
    public_rows = []
    private_rows = []
    viewed = set(analysis['endpoint_parents'])
    pilot_report = ROOT / 'docs/243-review-response-doc242-oulu-consolidated-pilot.md'
    parents[str(pilot_report)] = hashlib.sha256(pilot_report.read_bytes()).hexdigest()
    for index, row in enumerate(rows, 1):
        rank = row['queue_rank']
        member = members[rank]
        if any(member[key] != row[key] for key in ('left', 'right', 'record_sha256')):
            raise ValueError('original provenance membership drift')
        component = preflight['components'][row['component_index']]
        if rank not in component['ranks'] or any(row[side] not in component['videos'] for side in ('left', 'right')):
            raise ValueError('component membership drift')
        original_path = BASE / 'oulu_lineage_evidence_v1/pairs' / f'{rank:06d}.json'
        original = record(original_path, row['record_sha256'])
        candidate, candidate_path = candidates[row['left'], row['right']]
        if original['candidate'] != candidate:
            raise ValueError('candidate differs from pinned original pair')
        pair_path = BASE / 'oulu_investigation257_run_v1/pairs' / f'{rank:06d}.json'
        relative_pair = str(pair_path.relative_to(BASE / 'oulu_investigation257_run_v1'))
        pair = record(pair_path, summary['file_sha256_without_summary'][relative_pair])
        if (any(pair[key] != row[key] for key in ('left', 'right', 'queue_rank', 'record_sha256',
                                                'component_index', 'component_sha256', 'planned_orders'))
                or pair['real_screening_performed'] is not True or pair['effective_disposition'] is not None):
            raise ValueError('comparison parent or disposition drift')
        case = cases.get(rank)
        if case is not None and (case['pair_record'] != pair or case['pair_sha256'] != parents[str(pair_path)]):
            raise ValueError('259 observation pair drift')
        endpoints = {}
        boundaries = {}
        triggers = {}
        endpoint_paths = {}
        fingerprint_paths = {}
        for side in ('left', 'right'):
            video = row[side]
            role = frozen['oulu_npu_roles.csv'][video]
            metadata = frozen['oulu_npu_metadata.csv'][video]
            boundary = original[side + '_metadata']
            if (role['role'] != boundary['role'] or metadata['official_split'] != boundary['official_split']
                    or role['binary_label'] != boundary['binary_label'] or role['subject_id'] != metadata['subject_id']):
                raise ValueError('frozen boundary drift')
            boundaries[side] = {**boundary, 'fold': None}
            endpoint_path = BASE / 'oulu_investigation257_run_v1/endpoints' / (video + '.json')
            relative_endpoint = str(endpoint_path.relative_to(BASE / 'oulu_investigation257_run_v1'))
            endpoint = record(endpoint_path, summary['file_sha256_without_summary'][relative_endpoint])
            endpoint_paths[side] = str(endpoint_path)
            media_sha = original[side + '_media_record_sha256']
            if (endpoint['status'] != 'success' or endpoint['media_record_sha256'] != media_sha
                    or plan['videos'][video]['record_sha256'] != media_sha
                    or endpoint['orders'] != row['planned_orders'][side]
                    or pair['evidence'][0]['endpoint_record_sha256'][side] != parents[str(endpoint_path)]):
                raise ValueError('endpoint/media/order parent drift')
            fingerprint_path = BASE / 'oulu_content_screening_v1/fingerprints' / (video + '.json')
            fingerprint = record(fingerprint_path)
            fingerprint_paths[side] = str(fingerprint_path)
            if (fingerprint['accepted_media_record_sha256'] != media_sha
                    or any(fingerprint[key] != boundary[key] for key in boundary)):
                raise ValueError('original fingerprint parent or boundary drift')
            expected_samples = [endpoint['orders'][slot] for slot in (0, 2, 4, 6, 8)]
            if [sample['decode_order'] for sample in fingerprint['samples']] != expected_samples:
                raise ValueError('five historical candidate sample orders drift')
            sample_rgb = dict(zip(endpoint['orders'], endpoint['branches']['baseline'], strict=True))
            if any(sample['rgb_sha256'] != sample_rgb[sample['decode_order']]['rgb_sha256']
                   for sample in fingerprint['samples']):
                raise ValueError('historical fingerprint RGB differs from257 endpoint')
            triggers[side] = fingerprint['samples']
            endpoints[side] = endpoint
        if (candidate['cross_role'] != (boundaries['left']['role'] != boundaries['right']['role'])
                or candidate['cross_partition'] != (boundaries['left']['official_split'] != boundaries['right']['official_split'])):
            raise ValueError('cross-boundary flags disagree with frozen metadata')
        group = evidence_group(candidate, pair, case)
        branch_details = {}
        for branch, finding in pair['branches'].items():
            branch_details[branch] = {key: finding[key] for key in (
                'finding', 'tested_slot_pairs', 'geometric_hits', 'feature_counts', 'unresolved_reason')}
            branch_details[branch]['selected_witness_orders'] = [
                {side: endpoints[side]['orders'][witness[side + '_slot']] for side in ('left', 'right')}
                for witness in finding['witnesses']]
        public = {
            'edge_id': f'edge-{index:03d}',
            'component': f"component-{row['component_index']:03d}",
            'original_pair_sha256': parents[str(original_path)],
            'comparison257_sha256': parents[str(pair_path)],
            'candidate_scores': {key: candidate[key] for key in (
                'minimum_hamming', 'aligned_slots_within_8', 'cross_role', 'cross_partition',
                'conflicting_label', 'exact_full_video_evidence')},
            'candidate_reason': ';'.join(reason for condition, reason in (
                (candidate['minimum_hamming'] <= 4, 'any25_minimum_le4'),
                (candidate['aligned_slots_within_8'] >= 3, 'aligned_at_least3_le8')) if condition),
            'candidate_cause_localized': False,
            'boundaries': boundaries,
            'fold_recording': 'no_fold_column_in_consumed_frozen_CSVs_not_evidence_of_no_fold_overlap',
            'recorded_candidate_orders': {side: [sample['decode_order'] for sample in triggers[side]]
                                          for side in ('left', 'right')},
            'argmin_slot_pair': None,
            'argmin_slot_pair_note': 'not_recorded_in_original_candidate_no_score_or_trigger_recomputed',
            'exact_evidence': original['evidence'],
            'branches257': branch_details,
            'prior_endpoint_sheets_opened259': {side: row[side] in viewed for side in ('left', 'right')},
            'paired_visual_analysis259': case['alias'] if case is not None else None,
            'observation259_region_order_joins': case['selected_order_and_region_joins'] if case is not None else None,
            'selected_pilot243': rank == provenance['selected_queue_rank'],
            'pilot243_existing_observation': (
                '297_thumbnail_tiles_20_galleries_and_two_native_triggers_reported_viewed;'
                'persistent_dominant_foreground_structural_differences;'
                'coarse_phash_cause_not_localized_no_accepted_scoped_rejection'
                if rank == provenance['selected_queue_rank'] else None),
            'native_D261': case is not None and case['alias'] == 'D',
            'evidence_group': group,
            'pair_specific_observation': case['reason'] if case is not None else 'coarse_phash_trigger_no_recorded_supported_temporal_witness',
            'unobserved_hidden_reuse': 'not_established_by_generic_method_limits',
            'proposal': 'retain_materially_unresolved' if case is not None else 'retain_unadjudicated_not_an_accepted_negative',
            'criterion': 'distinctive_recorded_reuse_or_discriminating_material_explanation_required' if case is not None
                         else 'actual_candidate_reason_needs_accepted_finite_rejection_or_coverage_basis_not_no_witness_alone',
            'approved_scientific_disposition': None,
        }
        public_rows.append(public)
        private_rows.append({'edge_id': public['edge_id'], 'frozen_row': row,
                             'original_pair': original, 'original_pair_path': str(original_path),
                             'candidate_chunk_path': candidate_path, 'comparison_path': str(pair_path),
                             'comparison_record': pair, 'endpoint_paths': endpoint_paths,
                             'fingerprint_paths': fingerprint_paths, 'original_fingerprint_samples': triggers,
                             'frozen_role_rows': {side: frozen['oulu_npu_roles.csv'][row[side]] for side in ('left', 'right')},
                             'frozen_metadata_rows': {side: frozen['oulu_npu_metadata.csv'][row[side]] for side in ('left', 'right')},
                             'observation259': case, 'observation261': detail if public['native_D261'] else None})
    groups = group_members(public_rows)
    public = {'version': 1, 'checkpoint': 264, 'authority': 'Review263_existing_records_only',
              'scientific_acceptance': False, 'proposed_terminal_decision': DECISION,
              'approved_new_dispositions': 0, 'edge_count': 399, 'endpoint_count': 438, 'component_count': 91,
              'candidate_policy': lineage['policy'], 'groups': groups,
              'grouping_rule': 'candidate_trigger_family_and_recorded_subchain_geometry_or_individual_witness_not_connectivity',
              'group_exceptions': 'witnesses_A_to_E_each_separate_D_native_B_baseline_only_E_different_chain_orders_pilot243_edge002_not_accepted_rejection',
              'validation_scope': 'reuse_toy249_253_controls_no_representative_real_negative_validation_supplied',
              'new_media_execution': 0, 'new_matcher_runs': 0, 'new_image_views': 0,
              'source_fingerprint_status': 'historical_samples_read_not_redecoded_or_rescored',
              'historical_pin_scope': 'frozen_pair_plan257_and_observations_pinned_original_candidates_equal_pinned_pairs_screen_chunks_hash_joined_current_summary_fingerprint_RGB_joined257_not_all4950_bundle_rehashed_not_new_independent_certification',
              'visual_scope': 'reuse259_8_unique_sheets72_tiles_261_6_crops_no_new_opens_243_selected_flag_only_older_view_coverage_not_assumed_for_neighbors',
              'edge_rows': public_rows}
    software = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ('scripts/reconcile_oulu264.py', 'tests/test_oulu.py')}
    public['software_sha256'] = software
    public['effort_ceiling_active_hours'] = 8
    public['effort_note'] = 'ceiling_not_a_claim_of_eight_hours_spent_no_continuous_active_time_instrumentation'
    private = {'version': 1, 'checkpoint': 264, 'created_utc': datetime.now(timezone.utc).isoformat(),
               'review263_sha256': hashlib.sha256((ROOT / 'docs/263-corrective-review-oulu-completion-plan.md').read_bytes()).hexdigest(),
               'source_record_sha256': parents, 'edge_rows': private_rows,
               'public_ledger': public, 'new_media_execution': 0, 'new_dispositions': 0}
    if sum(row['paired_visual_analysis259'] is not None for row in public_rows) != 5:
        raise ValueError('five witness rows required')
    return private, public


def inspect_sources() -> None:
    preflight, _ = read_record(BASE / 'oulu_investigation257_preflight_v1.json')
    plan, _ = read_record(BASE / 'oulu_method249_plan_verification_v1.json')
    rows = frozen_rows(preflight, plan)
    print('FROZEN_JOIN_PASS', len(rows), 'ROWS')
    print('ROW', json.dumps(rows[0]))
    print('EXISTING_EVIDENCE', json.dumps(plan['rows'][0]['existing_evidence'])[:1600])
    print('PATHS', json.dumps(preflight['paths']))
    print('COMPONENT', json.dumps(preflight['components'][-1]))
    for name in ('oulu_cross_role_protocol241_provenance_v1.json',
                 'oulu_witness259_analysis_v1.json',
                 'oulu_investigation257_run_v1/pairs/000085.json'):
        record, _ = read_record(BASE / name)
        print('RECORD', name, 'KEYS', list(record))
        if 'metadata_reconciliation' in record:
            metadata = record['metadata_reconciliation']
            print('METADATA_KEYS', list(metadata))
            print('MEMBER', json.dumps(metadata['members'][0]))
        elif 'branches' in record:
            print('NON_BRANCH', json.dumps({key: value for key, value in record.items()
                                           if key != 'branches'})[:2200])
        else:
            for key, value in record.items():
                print('FIELD', key, type(value).__name__,
                      len(value) if isinstance(value, (list, dict)) else repr(value)[:200])
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    print('FIRST_KEYS', key, list(value[0]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--write', action='store_true')
    arguments = parser.parse_args()
    if arguments.inspect:
        inspect_sources()
    else:
        private, public = build_ledger()
        print('LEDGER264_JOIN_PASS', public['edge_count'], 'edges', public['endpoint_count'], 'endpoints')
        print('GROUP_COUNTS', json.dumps({key: len(value) for key, value in public['groups'].items()}))
        print('BOUNDARY_COUNTS', json.dumps(dict(Counter(
            row['boundaries']['left']['role'] + '->' + row['boundaries']['right']['role']
            for row in public['edge_rows']))))
        print('PRIOR_PILOT_EDGES', [row['edge_id'] for row in public['edge_rows'] if row['selected_pilot243']])
        if arguments.write:
            private_path = BASE / 'oulu_completion264_ledger_v1.json'
            public_path = ROOT / 'results/phase1/oulu-completion264-ledger-v1.json'
            if private_path.exists() or public_path.exists():
                raise FileExistsError('264 ledger already exists; never regenerate immutable records')
            write_immutable_record(private_path, private)
            public['private_ledger_sha256'] = hashlib.sha256(private_path.read_bytes()).hexdigest()
            write_immutable_record(public_path, public)
            print('LEDGER264_IMMUTABLE_WRITE_PASS')