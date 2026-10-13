#!/usr/bin/env python3
"""Attach new, checksum-bound animations without changing released paintings."""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

from online_release import checksum, compact, validated_animation
from pixel_animation_recipes import ROOT, animation


def publish(destination, batch_dir=None):
    destination = Path(destination)
    batch_dir = Path(batch_dir) if batch_dir else ROOT / 'tool/animation_batches'
    catalog_path = destination / 'catalog.json'
    catalog = json.loads(catalog_path.read_text('utf-8'))
    by_id = {item['id']: item for item in catalog['pictures']}
    seen = set()
    count = 0
    for batch in sorted(batch_dir.glob('online-*.json')):
        recipes = json.loads(batch.read_text('utf-8'))
        if not 1 <= len(recipes) <= 10:
            raise ValueError(f'Animation batch must contain 1-10 pictures: {batch}')
        for ident, recipe in recipes.items():
            if ident in seen:
                raise ValueError(f'Duplicate animation recipe: {ident}')
            seen.add(ident)
            item = by_id[ident]
            if 'animation' in item:
                raise ValueError(f'Existing animation must remain immutable: {ident}')
            stem = f"{ident}-v{item['version']}"
            level = json.loads((destination / f'levels/{stem}.json').read_text('utf-8'))
            if (recipe['checksum'] != item['checksum'] or
                    recipe['version'] != item['version'] or
                    checksum(level) != item['checksum']):
                raise ValueError(f'Animation recipe targets a different painting: {ident}')
            data = compact(animation(level, recipe))
            if hashlib.sha256(data).hexdigest() != recipe['animationChecksum']:
                raise ValueError(f'Animation recipe changed after registration: {ident}')
            metadata = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                        'frameCount': 12}
            # Reuse the Release validator rather than inventing looser rules.
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr(f'animations/{stem}.json', data)
            stream.seek(0)
            with zipfile.ZipFile(stream) as archive:
                validated_animation(archive, stem, {'animation': metadata}, level)
            target = destination / f'animations/{stem}.json'
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f'Refusing to replace an animation: {ident}')
            target.write_bytes(data)
            item['animation'] = metadata
            count += 1
    catalog_path.write_bytes(compact(catalog))
    print(f'Published {count} additive animation companions; original paintings unchanged.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: publish_animation_companions.py <online-directory>')
    publish(sys.argv[1])
