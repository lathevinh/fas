"""Read existing control metadata; never decode media or infer non-copy labels."""

from __future__ import annotations

import csv
import hashlib
import json
import resource
import time
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/e/FAS-private/artifacts/phase1')
FROZEN = Path('/mnt/e/FAS-private/frozen/source_roles_v2')


def index_collection(metadata: list[dict], roles: list[dict], group_unit: str) -> dict:
    if group_unit not in ('subject_id', 'video_id'):
        raise ValueError('explicit subject or video grouping required')
    indexed = {row['video_id']: row for row in metadata}
    assignments = {row['video_id']: row for row in roles}
    if len(indexed) != len(metadata) or len(assignments) != len(roles):
        raise ValueError('duplicate video identity')
    if not set(assignments).issubset(indexed):
        raise ValueError('role assignment lacks metadata parent')
    if any(not row.get(group_unit) for row in metadata):
        raise ValueError('missing originating grouping key')
    for video, role in assignments.items():
        if any(role[key] != indexed[video][key] for key in ('dataset', 'subject_id', 'binary_label')):
            raise ValueError('role metadata identity or label drift')
    return {'metadata_rows': len(metadata), 'assigned_rows': len(roles),
            'group_unit': group_unit, 'metadata_groups': len({row[group_unit] for row in metadata}),
            'assigned_groups': len({indexed[video][group_unit] for video in assignments}),
            'trusted_real_noncopy_labels_supplied': False,
            'label_limitation': 'metadata_and_role_fields_do_not_establish_capture_independence',
            'manifest_candidates': [dict(row, assigned_role=assignments.get(row['video_id'], {}).get('role'),
                                         originating_group=row[group_unit],
                                         noncopy_label=None, copy_parent_label=None)
                                    for row in metadata]}


def read_csv(path: Path, expected_sha256: str) -> tuple[list[dict], str]:
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != expected_sha256:
        raise ValueError('frozen CSV hash drift')
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle)), digest


def observed_scope(joins: list[dict], timestamps: dict[str, dict[int, str]]) -> dict:
    result = {}
    for side in ('left', 'right'):
        orders = [join['native_orders'][side] for join in joins]
        times = [Fraction(timestamps[side][order]) for order in orders]
        boxes = [join['normalized_inlier_bbox_xyxy'][side] for join in joins]
        areas = [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes]
        result[side] = {'selected_orders': orders,
                        'timestamps_seconds_exact': [str(value) for value in times],
                        'observed_first_to_last_span_seconds': float(max(times) - min(times)) if times else None,
                        'inlier_bbox_area_fractions': areas,
                        'true_visible_copied_area_fraction': None,
                        'continuous_copy_duration_established': False}
    return result


def inventory() -> tuple[dict, dict]:
    started = time.monotonic()
    cpu_started = time.process_time()
    freeze_path = FROZEN / 'source_role_freeze.json'
    freeze_bytes = freeze_path.read_bytes()
    freeze = json.loads(freeze_bytes)
    parents = {str(freeze_path): hashlib.sha256(freeze_bytes).hexdigest()}
    collections = {}
    for stem, unit in (('oulu_npu', 'subject_id'), ('casia_fasd', 'subject_id'),
                       ('msu_mfsd', 'subject_id'), ('siw_mv2', 'video_id')):
        records = {}
        for kind in ('metadata', 'roles'):
            name = stem + '_' + kind + '.csv'
            records[kind], parents[str(FROZEN / name)] = read_csv(
                FROZEN / name, freeze['frozen_artifact_sha256'][name])
        collections[stem] = index_collection(records['metadata'], records['roles'], unit)
    ledger_path = BASE / 'oulu_completion264_ledger_v1.json'
    ledger_bytes = ledger_path.read_bytes()
    digest = hashlib.sha256(ledger_bytes).hexdigest()
    if digest != '066f4d96a81b4c2dd6f0649a6bc424cfbd66d1fdc69bcb5074925ed252bab08a':
        raise ValueError('accepted264 ledger drift')
    parents[str(ledger_path)] = digest
    ledger = json.loads(ledger_bytes)
    excluded = {row['frozen_row'][side] for row in ledger['edge_rows'] for side in ('left', 'right')}
    oulu = collections['oulu_npu']
    excluded_groups = {row['subject_id'] for row in oulu['manifest_candidates'] if row['video_id'] in excluded}
    for name, collection in collections.items():
        for row in collection['manifest_candidates']:
            row['in399_decision_endpoints'] = name == 'oulu_npu' and row['video_id'] in excluded
            row['excluded399_subject_group'] = name == 'oulu_npu' and row['subject_id'] in excluded_groups
            row['benchmark_split'] = None
            row['media_availability_rechecked'] = False
            row['pretraining_overlap'] = 'unknown_no_checkpoint_selected'
        collection['candidate_rows_after_known399_group_exclusion'] = sum(
            not row['excluded399_subject_group'] for row in collection['manifest_candidates'])
        collection['candidate_groups_after_known399_group_exclusion'] = len({
            row['originating_group'] for row in collection['manifest_candidates'] if not row['excluded399_subject_group']})
        collection['capture_group_independence_established'] = False
    historical = {}
    for filename, expected in (
        ('oulu_method249_controls_v1.json', '59146afb4f7003b6715ca5a79f3b089d26ce3cde3c411669dd1fa0df76406c18'),
        ('oulu_method249_challenge_v1.json', '3b7d6c0bc2072ebec6c44fb3fe2f59f734862019b44dc19bb8a8465ff137c46f'),
        ('oulu_motion253_ab_controls_v1.json', 'ce4131781dd752e137bbeff40c176075832fe70de26018757b6bc5fcd9d50b68'),
        ('oulu_motion253_dynamic_background_v1.json', 'e8b67a8af0db4faf28a2f8f0f8cd532247f782741116cee6a9a4eea5b7f4fd54')):
        path = BASE / filename
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != expected:
            raise ValueError('historical synthetic control drift')
        parents[str(path)] = digest
        value = json.loads(content)
        if value['real_pairs_screened'] != 0:
            raise ValueError('synthetic-control scope changed')
        historical[filename] = {'rows': len(value['rows']), 'real_pairs_screened': 0,
                                'trusted_real_noncopy_labels': False}
    prefix = []
    for batch in range(1, 10):
        root = BASE / f'oulu_batch{batch:02d}_activation_v1/pairs'
        for path in sorted(root.glob('*.json')):
            content = path.read_bytes()
            parents[str(path)] = hashlib.sha256(content).hexdigest()
            value = json.loads(content)
            original_path = BASE / 'oulu_lineage_evidence_v1/pairs' / f"{value['queue_rank']:06d}.json"
            original_bytes = original_path.read_bytes()
            parents[str(original_path)] = hashlib.sha256(original_bytes).hexdigest()
            original = json.loads(original_bytes)
            prefix.append({'activation_path': str(path), 'activation_record': value,
                           'original_pair_path': str(original_path), 'original_pair_record': original,
                           'scope': 'retain_accepted_screen_level_disposition_not_broad_capture_independence',
                           'eligible_for_new_trusted_noncopy_benchmark': False,
                           'reason': 'accepted_bounded_screen_judgment_not_independent_label_for_proposed_transform_region_duration_scope'})
    if len(prefix) != 85 or {row['activation_record']['queue_rank'] for row in prefix} != set(range(85)):
        raise ValueError('exact accepted85 prefix membership required')
    prefix_videos = {row['original_pair_record']['candidate'][side]
                     for row in prefix for side in ('left', 'right')}
    prefix_groups = {row['subject_id'] for row in oulu['manifest_candidates'] if row['video_id'] in prefix_videos}
    for row in oulu['manifest_candidates']:
        row['accepted85_screen_exposure_group'] = row['subject_id'] in prefix_groups
        row['candidate_after_known399_and85_group_exclusion'] = (
            not row['excluded399_subject_group'] and not row['accepted85_screen_exposure_group'])
    oulu['candidate_rows_after_known399_and85_group_exclusion'] = sum(
        row['candidate_after_known399_and85_group_exclusion'] for row in oulu['manifest_candidates'])
    oulu['candidate_groups_after_known399_and85_group_exclusion'] = len({
        row['originating_group'] for row in oulu['manifest_candidates']
        if row['candidate_after_known399_and85_group_exclusion']})
    applicability = []
    for row in ledger['edge_rows']:
        case = row['observation259']
        if case is None:
            continue
        timestamps = {}
        for side in ('left', 'right'):
            path = BASE / 'oulu_per_video_audit_v1/videos' / (row['frozen_row'][side] + '.json')
            content = path.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if digest != row['original_pair'][side + '_media_record_sha256']:
                raise ValueError('accepted witness media record drift')
            parents[str(path)] = digest
            media = json.loads(content)
            timestamps[side] = {frame['decode_order']: frame['timestamp_seconds'] for frame in media['frame_index']}
        applicability.append({'alias': case['alias'], 'edge_id': row['edge_id'],
                              'branches': {branch: observed_scope(joins, timestamps)
                                           for branch, joins in case['selected_order_and_region_joins'].items() if joins},
                              'scope_eligibility': 'not_established_selected_points_are_not_copy_duration_or_visible_area_labels'})
    public = {name: {key: value for key, value in collection.items() if key != 'manifest_candidates'}
              for name, collection in collections.items()}
    public = {'collections': public, 'excluded399_videos': len(excluded),
              'excluded399_subject_groups': len(excluded_groups),
              'accepted85_screen_exposure_subject_groups': len(prefix_groups),
              'historical_synthetic_controls': historical,
              'accepted85_screen_labels_repurposed_as_noncopy': 0,
              'witness_scope': applicability,
              'remaining394_scope': 'no_ground_truth_copy_duration_or_visible_region_labels_for389_no_geometry_or5_subchain',
              'permission': 'reuse_owner_research_permission_no_provider_contact_or_new_acquisition',
              'evidence_limit': 'bounded_inventory_of_named_existing_records_not_an_exhaustive_search_of_all_possible_material',
              'terminal_decision': 'trustworthy_relevant_real_controls_and_allegation_applicability_unavailable_stop_before_model_resources',
              'new_media_runs': 0, 'new_model_runs': 0, 'new_dispositions': 0}
    measurements = {'wall_seconds': time.monotonic() - started,
                    'cpu_seconds': time.process_time() - cpu_started,
                    'process_high_water_RSS_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}
    if (measurements['wall_seconds'] > 600 or measurements['cpu_seconds'] > 120
            or measurements['process_high_water_RSS_bytes'] > 512 * 1024 * 1024):
        raise ValueError('metadata inventory resource ceiling exceeded')
    return {'collections': collections, 'source_sha256': parents, 'accepted85_records': prefix,
            'witness_scope': applicability, 'public_inventory': public,
            'metadata_measurements': measurements,
            'metadata_caps': {'wall_seconds': 600, 'cpu_seconds': 120,
                              'RSS_bytes': 512 * 1024 * 1024, 'combined_record_bytes': 16 * 1024 * 1024}}, public


if __name__ == '__main__':
    private, public = inventory()
    print('CONTROL268_METADATA_INVENTORY_PASS', json.dumps(public, sort_keys=True))
    print('NO_MEDIA_OR_MODEL_ACCESSED_NO_CONTROL_LABEL_INFERRED')