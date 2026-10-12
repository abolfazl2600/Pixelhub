#!/usr/bin/env python3
"""Package an immutable offline manifest after the Web build (used in CI)."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
excluded = {'offline-worker.js', 'offline-manifest.json', 'commit.txt'}
files = sorted(
    path for path in root.rglob('*')
    if path.is_file() and path.name not in excluded and path.suffix != '.map'
)
digest = hashlib.sha256()
for path in files:
    digest.update(path.relative_to(root).as_posix().encode())
    digest.update(hashlib.sha256(path.read_bytes()).digest())
version = digest.hexdigest()
(root / 'offline-manifest.json').write_text(json.dumps({
    'version': version,
    'files': [path.relative_to(root).as_posix() for path in files],
}, separators=(',', ':')) + '\n')
worker = root / 'offline-worker.js'
worker.write_text(worker.read_text().replace('__PIXELHUB_BUILD_ID__', version))
