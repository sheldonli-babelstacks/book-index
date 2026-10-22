#!/usr/bin/env python3
"""Verify the imported audit package without modifying it or repository data."""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence(ref):
    name, index = ref.rsplit('#', 1)
    path = ('verification/' if name.startswith('verified-') else 'lanes/') + name
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT), f'Unsafe evidence path: {ref}')
    return read(path)[int(index)]


def main():
    provenance = read('provenance.json')
    for entry in provenance['imported_files']:
        path = (ROOT / entry['path']).resolve()
        require(path.is_relative_to(ROOT), f'Unsafe path: {path}')
        raw = path.read_bytes()
        require(len(raw) == entry['bytes'], f'Size mismatch: {path}')
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], f'Hash mismatch: {path}')

    groups = read('confirmed-clusters.json')
    all_evidence = read('all-evidence.json')
    by_ref = {}
    for row in all_evidence:
        ref = row['evidence_ref']
        require(ref not in by_ref, f'Duplicate evidence reference: {ref}')
        by_ref[ref] = row
        original = evidence(ref)
        require(all(row.get(key) == value for key, value in original.items()), f'Changed evidence: {ref}')

    summary = read('summary.json')
    seen = collections.defaultdict(set)
    cluster_names = set()
    expected_csv = []
    used_refs = set()
    for group in groups:
        typ, ids = group['type'], group['ids']
        name = group['cluster_id']
        require(typ in ('people', 'work', 'book'), f'Unknown type: {typ}')
        require(name not in cluster_names, f'Duplicate cluster: {name}')
        cluster_names.add(name)
        require(len(ids) >= 2 and len(set(ids)) == len(ids), f'Invalid IDs: {name}')
        require(not (seen[typ] & set(ids)), f'Overlapping clusters: {name}')
        seen[typ].update(ids)
        require(group['redundant_records'] == len(ids) - 1, f'Bad redundant count: {name}')
        require([r['id'] for r in group['records']] == ids, f'Record ordering: {name}')
        parent = {id_: id_ for id_ in ids}

        def find(id_):
            while parent[id_] != id_:
                id_ = parent[id_]
            return id_

        for ref in group['evidence_refs']:
            row = by_ref[ref]
            require(row['verdict'] == 'confirmed' and row['entity_type'] == typ, f'Wrong verdict/type: {ref}')
            require(set(row['ids']) <= set(ids), f'Evidence outside cluster: {ref}')
            for id_ in row['ids'][1:]:
                parent[find(id_)] = find(row['ids'][0])
            for id_, path in zip(row['ids'], row['paths'], strict=True):
                require(any(r['id'] == id_ and r['path'] == path for r in group['records']), f'Path mismatch: {ref}')
            used_refs.add(ref)
        require(len({find(id_) for id_ in ids}) == 1, f'Disconnected cluster: {name}')
        for row in group['records']:
            require(provenance['source_commit'] in row['url'], f'Wrong baseline link: {name}')
            expected_csv.append([typ, name, row['id'], row['title'], row['path'], row['url'], str(len(ids)), str(len(ids)-1)])
    require(used_refs == {r['evidence_ref'] for r in all_evidence if r['verdict'] == 'confirmed'}, 'Unaccounted confirmed evidence')
    for typ in ('people', 'work', 'book'):
        subset = [g for g in groups if g['type'] == typ]
        actual = {'groups': len(subset), 'records': len(seen[typ]), 'redundant_records': sum(g['redundant_records'] for g in subset)}
        require(actual == summary[typ], f'Summary mismatch: {typ}')
    require(summary['conflicts'] == [] and summary['validation_errors'] == [], 'Source reports unresolved validation errors')
    with (ROOT / 'confirmed-records.csv').open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.reader(handle))
    require(len(rows[0]) == 8 and rows[1:] == expected_csv, 'CSV mismatch')
    print(f"OK: {len(provenance['imported_files'])} file hashes, {len(all_evidence)} evidence entries, {len(groups)} clusters, {len(expected_csv)} records")
    print('Checks cover package consistency, not historical source records or external authorities.')


if __name__ == '__main__':
    main()
