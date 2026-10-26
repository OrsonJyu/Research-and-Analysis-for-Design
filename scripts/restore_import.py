#!/usr/bin/env python3
"""Reassemble an explicitly prepared import, verifying it against the final catalog."""
from pathlib import Path
import base64
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
IMPORT = ROOT / '.github' / 'imports'

def main():
    manifest_path = IMPORT / 'manifest.json'
    if not manifest_path.exists():
        print('No pending import manifest.')
        return
    manifest = json.loads(manifest_path.read_text())
    catalog = {r['path']: r for r in json.loads((ROOT / 'metadata/file-catalog.json').read_text())['records']}
    restored = []
    for item in manifest['files']:
        rel = item['path']
        expected = catalog.get(rel)
        if expected is None or expected['sha256'] != item['sha256'] or expected['bytes'] != item['bytes']:
            raise ValueError('Import is not authorised by the final catalog: ' + rel)
        target = (ROOT / rel).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError('Target outside repository')
        data = bytearray()
        for part in item['parts']:
            source = (ROOT / part['path']).resolve()
            if not source.is_relative_to(IMPORT):
                raise ValueError('Part outside import directory')
            chunk = source.read_bytes()
            if part.get('encoding') == 'base64':
                chunk = base64.b64decode(chunk, validate=True)
            if len(chunk) != part['bytes'] or hashlib.sha256(chunk).hexdigest() != part['sha256']:
                raise ValueError('Corrupt import part: ' + part['path'])
            data.extend(chunk)
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError('Original file checksum mismatch: ' + rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        restored.append(rel)
    shutil.rmtree(IMPORT)
    print('Restored and verified original files: ' + str(len(restored)))

if __name__ == '__main__':
    main()
