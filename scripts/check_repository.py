#!/usr/bin/env python3
"""Check source preservation, local navigation, graph references and catalog freshness."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import sys
from build_catalog import ROOT, files

def main():
    errors = []
    catalog = json.loads((ROOT / 'metadata/file-catalog.json').read_text())
    recorded = {r['path']: r for r in catalog['records']}
    actual = {p.relative_to(ROOT).as_posix(): p for p in files()}
    if set(recorded) != set(actual):
        errors.append('Catalog file set is stale: ' + str(sorted(set(recorded) ^ set(actual))))
    for rel, p in actual.items():
        if rel not in recorded:
            continue
        data = p.read_bytes()
        r = recorded[rel]
        if len(data) != r['bytes'] or hashlib.sha256(data).hexdigest() != r['sha256']:
            errors.append('Stale catalog hash: ' + rel)
    imported = json.loads((ROOT / 'metadata/import-manifest.json').read_text())['records']
    for row in imported:
        p = ROOT / row['repository_path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            errors.append('Imported source changed or missing: ' + row['repository_path'])
    project = json.loads((ROOT / 'metadata/project.json').read_text())
    if project['repository_version'] != (ROOT / 'VERSION').read_text().strip():
        errors.append('VERSION and project.json disagree')
    graph = json.loads((ROOT / 'knowledge/graph.json').read_text())
    ids = [n['id'] for n in graph['nodes']]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate graph node IDs')
    for edge in graph['edges']:
        if edge['from'] not in ids or edge['to'] not in ids:
            errors.append('Invalid graph edge: ' + edge['id'])
        for source in edge.get('source_paths', []):
            if not (ROOT / source).is_file():
                errors.append('Missing graph source: ' + source)
    for n in graph['nodes']:
        for source in n.get('source_paths', []):
            if not (ROOT / source).is_file():
                errors.append('Missing node source: ' + source)
    # Historical originals deliberately keep their original paths. Check curated entry points.
    curated = [ROOT / x for x in ('README.md','README.en.md','AGENTS.md','CONTRIBUTING.md','CHANGELOG.md')]
    curated += list((ROOT / 'docs').rglob('*.md'))
    curated += [p for folder in ('archive','deliverables','references','knowledge') for p in (ROOT / folder).rglob('README.md')
                if '2026-09-21' not in p.parts and 'literature' not in p.parts]
    curated.append(ROOT / 'metadata/FILE_CATALOG.md')
    for p in curated:
        if not p.exists():
            errors.append('Missing entry point: ' + str(p.relative_to(ROOT)))
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', p.read_text()):
            target = target.strip().strip('<>')
            if target.startswith('#') or urlsplit(target).scheme:
                continue
            dest = (p.parent / unquote(target.split('#')[0])).resolve()
            if not dest.exists():
                errors.append(f"Broken link in {p.relative_to(ROOT)}: {target}")
    for p in ROOT.rglob('*.json'):
        if '.git' not in p.parts:
            try:
                json.loads(p.read_text())
            except Exception as exc:
                errors.append(f'Invalid JSON {p.relative_to(ROOT)}: {exc}')
    if errors:
        print('\n'.join(errors))
        return 1
    print(f"PASS: {len(actual)} indexed files, {len(imported)} source records, {len(ids)} graph nodes, {len(graph['edges'])} edges; source hashes and curated links verified.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
