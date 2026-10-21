"""Check existing OULU records under the explicitly adopted benchmark policy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from fas.freeze import write_immutable_record
from fas.transactions import calibration_fit_rows, technical_population_counts


ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/e/FAS-private/artifacts/phase1')
FROZEN = Path('/mnt/e/FAS-private/frozen/source_roles_v2')
TRANSACTIONS = Path('/mnt/e/FAS-private/frozen/oulu_transactions_v1')


def group_checks(metadata: list[dict], roles: list[dict]) -> dict:
    indexed = {row['video_id']: row for row in metadata}
    assigned = {row['video_id']: row for row in roles}
    if len(indexed) != len(metadata) or len(assigned) != len(roles):
        raise ValueError('duplicate video identity')
    if set(indexed) != set(assigned):
        raise ValueError('role population mismatch')
    groups = {'role': defaultdict(set), 'official_split': defaultdict(set)}
    for identity, row in indexed.items():
        role = assigned[identity]
        if not row.get('subject_id'):
            raise ValueError('missing subject identity')
        if any(role[key] != row[key] for key in ('dataset', 'subject_id', 'binary_label')):
            raise ValueError('role identity or label drift')
        if role['role'] not in {'train', 'branch_calibration', 'g_domain'}:
            raise ValueError('unknown frozen role')
        if row['official_split'] not in {'train', 'development', 'test'}:
            raise ValueError('unknown official partition')
        groups['role'][role['role']].add(row['subject_id'])
        groups['official_split'][row['official_split']].add(row['subject_id'])
    intersections = []
    for boundary, partitions in groups.items():
        for left, right in combinations(sorted(partitions), 2):
            overlap = sorted(partitions[left] & partitions[right])
            intersections.append({'boundary': boundary, 'left': left, 'right': right,
                                  'count': len(overlap), 'subject_ids': overlap})
    return {'intersections': intersections,
            'groups': {boundary: {name: len(members) for name, members in partitions.items()}
                       for boundary, partitions in groups.items()},
            'forbidden_group_crossings': sum(row['count'] for row in intersections)}


def exact_checks(groups: list[dict], metadata: dict, roles: dict) -> list[dict]:
    results = []
    seen = set()
    for group in groups:
        members = group['video_ids']
        key = group['identity_type'], tuple(sorted(members))
        if key in seen or len(members) != len(set(members)) or len(members) < 2:
            raise ValueError('duplicate or invalid exact group')
        seen.add(key)
        if any(identity not in metadata or identity not in roles for identity in members):
            raise ValueError('exact group identity lacks frozen parent')
        partitions = sorted({metadata[identity]['official_split'] for identity in members})
        assignments = sorted({roles[identity]['role'] for identity in members})
        subjects = sorted({metadata[identity]['subject_id'] for identity in members})
        labels = sorted({metadata[identity]['binary_label'] for identity in members})
        if partitions != group['partitions'] or assignments != group['roles']:
            raise ValueError('recorded exact group boundary drift')
        results.append({'identity_type': group['identity_type'], 'members': members,
                        'partitions': partitions, 'roles': assignments,
                        'prohibited': any(len(values) != 1 for values in
                                          (partitions, assignments, subjects, labels))})
    return results


def protocol_checks(records: list[dict]) -> list[dict]:
    protocol_subjects = defaultdict(lambda: defaultdict(set))
    for row in records:
        for membership in row['protocol_memberships']:
            protocol = (membership['protocol_number'], membership['protocol_fold'])
            protocol_subjects[protocol][membership['official_split']].add(row['subject_id'])
    intersections = []
    for protocol, partitions in sorted(protocol_subjects.items()):
        for left, right in combinations(sorted(partitions), 2):
            intersections.append({'protocol': list(protocol), 'left': left, 'right': right,
                                  'count': len(partitions[left] & partitions[right])})
    if not intersections:
        raise ValueError('official protocol coverage missing')
    return intersections


def historical_checks(records: list[dict]) -> dict:
    for row in records:
        activation = row['activation_record']
        disposition = activation.get('effective_disposition', activation.get('disposition'))
        if disposition != 'rejected_false_positive' or activation.get('reconciliation_required') is not False:
            raise ValueError('unresolved or confirmed historical relationship')
    return {'accepted_prefix_records': len(records), 'new_dispositions': 0,
            'acceptance_chain': 'inherited_accepted268_snapshot_not_fresh_activation_recertification'}


def audit() -> tuple[dict, dict]:
    started = time.monotonic()
    parents = {}

    def load(path: Path, expected: str | None = None) -> dict:
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError('parent hash drift: ' + path.name)
        parents[str(path)] = digest
        return json.loads(payload)

    approval = load(BASE / 'benchmark_policy271_owner_approval272_v1.json',
                    '957ff9d337aaf19c181da05c8282a3f100211c99bc15f253518c398867dd2daa')
    review = ROOT / 'docs/271-benchmark-grounded-review-and-fast-audit-proposal.md'
    paragraphs = [line[2:] for line in review.read_text().splitlines() if line.startswith('> ')]
    if (paragraphs != approval['adopted_paragraphs'] or len(paragraphs) != 2
            or hashlib.sha256(review.read_bytes()).hexdigest() != approval['review271_sha256']):
        raise ValueError('adopted policy drift')
    media_public = load(ROOT / 'results/phase1/oulu-per-video-media-audit-v1.json',
                        '04f5555da7493d7ca08cbf9e2fc44b00d5b09cc27d5e4ee441e4cec24f17ae0a')
    transaction_public = load(ROOT / 'results/phase1/oulu-transaction-selector-freeze-v1.json')
    frozen = {}
    for name in ('oulu_npu_metadata.csv', 'oulu_npu_roles.csv', 'oulu_npu_canonical.json'):
        path = FROZEN / name
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != media_public['frozen_artifact_sha256'][name]:
            raise ValueError('accepted frozen identity drift')
        parents[str(path)] = digest
        frozen[name] = (json.loads(payload) if name.endswith('.json') else
                        list(csv.DictReader(payload.decode().splitlines())))
    metadata_rows = frozen['oulu_npu_metadata.csv']
    role_rows = frozen['oulu_npu_roles.csv']
    metadata = {row['video_id']: row for row in metadata_rows}
    roles = {row['video_id']: row for row in role_rows}
    canonical_rows = frozen['oulu_npu_canonical.json']['videos']
    canonical = {row['video_id']: row for row in canonical_rows}
    inventory = load(BASE / 'oulu-inventory-20261006.json',
                     frozen['oulu_npu_canonical.json']['inventory_sha256'])
    inventory_rows = {row['video_id']: row for row in inventory['videos']}
    if (len(metadata) != 4950 or len(canonical_rows) != len(canonical)
            or len(inventory['videos']) != len(inventory_rows)
            or set(metadata) != set(canonical) or set(metadata) != set(inventory_rows)):
        raise ValueError('4950 release/canonical identity mismatch')
    for identity, row in metadata.items():
        for key in ('dataset', 'subject_id', 'binary_label', 'official_split'):
            if row[key] != canonical[identity][key] or row[key] != inventory_rows[identity][key]:
                raise ValueError('release/canonical label or partition mismatch')
        if canonical[identity]['protocol_memberships'] != inventory_rows[identity]['protocol_memberships']:
            raise ValueError('official protocol membership drift')
    grouping = group_checks(metadata_rows, role_rows)
    protocol_intersections = protocol_checks(canonical_rows)
    source = BASE / 'oulu_per_video_audit_v1'
    media_summary = load(source / 'summary.json', media_public['private_summary_sha256'])
    load(source / 'lineage.json', media_public['lineage_sha256'])
    duplicate_record = load(source / 'duplicate_groups.json', media_public['duplicate_groups_sha256'])
    exact = exact_checks(duplicate_record['groups'], metadata, roles)
    exact_counts = dict(Counter(row['identity_type'] for row in exact))
    if exact_counts != media_summary['exact_duplicate_groups']:
        raise ValueError('exact group coverage drift')
    for group in duplicate_record['groups']:
        for identity in group['video_ids']:
            record = load(source / 'videos' / (identity + '.json'))
            if record[group['identity_type']] != group['sha256']:
                raise ValueError('exact member recorded content drift')
    definition = load(TRANSACTIONS / 'definition.json', transaction_public['definition_sha256'])
    summary = load(TRANSACTIONS / 'summary.json', transaction_public['private_summary_sha256'])
    if (summary['definition_sha256'] != transaction_public['definition_sha256']
            or definition['accepted_media_record_bundle_sha256'] != media_summary['video_record_bundle_sha256']):
        raise ValueError('transaction/media lineage drift')
    records = []
    bundle_lines = []
    for path in sorted((TRANSACTIONS / 'transactions').glob('*.json')):
        record = load(path)
        identity = record['video_id']
        if identity != path.stem or identity not in metadata:
            raise ValueError('transaction identity drift')
        if (record['binary_label'] != metadata[identity]['binary_label']
                or record['official_split'] != metadata[identity]['official_split']
                or record['role'] != roles[identity]['role']):
            raise ValueError('transaction label/partition/role drift')
        records.append(record)
        bundle_lines.append(identity + ':' + parents[str(path)] + '\n')
    bundle = hashlib.sha256(''.join(bundle_lines).encode()).hexdigest()
    if (bundle != summary['transaction_record_bundle_sha256']
            or bundle != transaction_public['transaction_record_bundle_sha256']
            or {row['video_id'] for row in records} != set(metadata)):
        raise ValueError('complete accepted transaction bundle drift')
    populations = technical_population_counts(records)
    calibration = [row for row in records if row['role'] == 'branch_calibration']
    accounting = {'original': len(records),
                  'selected': sum(row['selected_frame'] is not None for row in records),
                  'terminal_failures': sum(row['technical_status'] == 'terminal_failure' for row in records),
                  'calibration_original': len(calibration),
                  'calibration_selected': sum(row['selected_frame'] is not None for row in calibration),
                  'calibration_score_fit': len(calibration_fit_rows(calibration))}
    if (accounting != {'original': 4950, 'selected': 4949, 'terminal_failures': 1,
                       'calibration_original': 990, 'calibration_selected': 989,
                       'calibration_score_fit': 0} or populations != summary['populations']):
        raise ValueError('original/terminal/calibration accounting drift')
    ledger = load(BASE / 'oulu_completion264_ledger_v1.json',
                  '066f4d96a81b4c2dd6f0649a6bc424cfbd66d1fdc69bcb5074925ed252bab08a')
    if len(ledger['edge_rows']) != 399 or ledger['new_dispositions'] != 0:
        raise ValueError('retained399 ledger drift')
    controls = load(BASE / 'oulu_control268_inventory_v1.json',
                    '22fa8e9d2f3f2a2423aa3da4564dffe9a74b3c73ddaa66d8f315512430256d95')
    history = historical_checks(controls['accepted85_records'])
    if history['accepted_prefix_records'] != 85:
        raise ValueError('accepted85 history coverage drift')
    confirmed = [row['edge_id'] for row in ledger['edge_rows']
                 if row['original_pair']['evidence']['disposition'] == 'confirmed_same_content_or_derived_lineage']
    forbidden = (grouping['forbidden_group_crossings'] + sum(row['prohibited'] for row in exact)
                 + sum(row['count'] for row in protocol_intersections) + len(confirmed))
    private = {'approval': approval, 'grouping': grouping, 'exact_groups': exact,
               'source_sha256': parents,
               'terminal_transactions': [row for row in records if row['technical_status'] == 'terminal_failure']}
    public = {'version': 1, 'checkpoint': 272, 'policy': 'explicitly_adopted271',
              'accounting': accounting, 'groups': grouping['groups'],
              'official_protocol_intersections': protocol_intersections,
              'accepted_history': history,
              'group_intersections': [{key: value for key, value in row.items() if key != 'subject_ids'}
                                      for row in grouping['intersections']],
              'exact_groups_by_hash_type': exact_counts,
              'exact_distinct_member_sets': len({tuple(sorted(row['members'])) for row in exact}),
              'forbidden_group_or_exact_crossings': forbidden,
              'retained_similarity': {'total': 399, 'witnesses': 5, 'non_detections': 394,
                                      'new_scientific_pair_dispositions': 0},
              'local_mandatory_checks_pass': forbidden == 0,
              'media_bundle_verification': 'inherited_accepted_media_hashes_not_full_media_JSON_rehash',
              'known_derivation_scope': 'exact_member_relationships_and_accepted85_history_not_universal_capture_ancestry',
              'new_media_model_runs': 0, 'scientific_readiness': False,
              'wall_seconds': time.monotonic() - started}
    return public, private


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    arguments = parser.parse_args()
    public_path = ROOT / 'results/phase1/oulu-benchmark272-audit-v1.json'
    private_path = BASE / 'oulu_benchmark272_audit_v1.json'
    if arguments.write and (public_path.exists() or private_path.exists()):
        raise FileExistsError('immutable272 output already exists')
    public, private = audit()
    if arguments.write:
        private['public_result'] = dict(public)
        write_immutable_record(private_path, private)
        public['private_record_sha256'] = hashlib.sha256(private_path.read_bytes()).hexdigest()
        write_immutable_record(public_path, public)
        if (json.loads(private_path.read_bytes()) != private
                or json.loads(public_path.read_bytes()) != public):
            raise ValueError('immutable272 readback mismatch')
    print(json.dumps(public, indent=2, sort_keys=True))