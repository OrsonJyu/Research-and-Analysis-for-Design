#!/usr/bin/env python3
"""Rebuild portable file indexes and hashes using only Python's standard library."""
from pathlib import Path
from urllib.parse import quote
from collections import defaultdict
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {'metadata/file-catalog.json', 'metadata/FILE_CATALOG.md', 'metadata/SHA256SUMS.txt'}
EXCLUDED_PARTS = {'.git', '__pycache__', 'tmp'}

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(part in EXCLUDED_PARTS for part in p.relative_to(ROOT).parts)
                  and p.name not in {'.DS_Store', '.upload-state.json'}
                  and p.suffix != '.pyc' and p.relative_to(ROOT).as_posix() not in GENERATED)

def main():
    metadata = ROOT / 'metadata'
    metadata.mkdir(exist_ok=True)
    imported = json.loads((metadata / 'import-manifest.json').read_text())['records']
    sources = defaultdict(list)
    for row in imported:
        sources[row['repository_path']].append({k: row[k] for k in ('source_collection', 'source_path', 'status')})
    records = []
    for p in files():
        data = p.read_bytes()
        rel = p.relative_to(ROOT).as_posix()
        records.append({'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                        'git_blob_sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
                        'sources': sources.get(rel, []),
                        'kind': 'imported-source' if rel in sources else 'curated-or-generated'})
    doc = {'schema_version': '1.0', 'repository_version': (ROOT / 'VERSION').read_text().strip(),
           'coverage': 'All repository files except these three generated indexes, Git internals and temporary caches.',
           'excluded_generated_indexes': sorted(GENERATED), 'records': records}
    (metadata / 'file-catalog.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    (metadata / 'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in records))
    md = '# 完整文件目录 File catalog\n\n'
    md += f"Version {doc['repository_version']} · {len(records)} indexed files · {sum(r['bytes'] for r in records):,} bytes.\n\n"
    md += 'Indexes do not hash themselves. Imported sources are also mapped in [import-manifest.json](import-manifest.json).\n\n'
    for category in sorted({r['path'].split('/')[0] for r in records}):
        md += f'## {category}\n\n| File | Bytes | Origin |\n|---|---:|---|\n'
        for r in records:
            if r['path'].split('/')[0] != category:
                continue
            origin = ', '.join(sorted({x['source_collection'] for x in r['sources']})) or 'repository documentation'
            md += f"| [{r['path']}](../{quote(r['path'], safe='/')}) | {r['bytes']:,} | {origin} |\n"
        md += '\n'
    (metadata / 'FILE_CATALOG.md').write_text(md)
    print(f"Indexed {len(records)} files; generated 3 index files.")

if __name__ == '__main__':
    main()
