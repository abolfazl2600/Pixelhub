#!/usr/bin/env python3
"""Publish independent product manifests referencing immutable shared assets.

Run after assembling the legacy online catalog and adding animation sidecars.
The original catalog is never rewritten. No level/preview/animation is copied.
"""
import argparse
import json
from pathlib import Path
from registry import load_registry

REPLACEMENTS = {}  # Loaded from the existing authoritative publishing tool.


def category(picture):
    value=picture['category'];pid=picture['id']
    if value=='patterns':
        if pid.startswith('online-classic-') or pid in {'online-mona-lisa','online-starry-night','online-the-scream','online-sunflowers','online-girl-pearl','online-great-wave'}:return 'masterpieces'
        if pid.startswith('online-iran-'): return 'persian_architecture'
    return value


def publish(root):
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from online_release import RETIRED_ONLINE_IDS
    source=json.loads((root/'catalog.json').read_text())
    for product in load_registry().values():
        if product.id=='pixelhub' or not product.ready or not product.data['features']['online_catalog']: continue
        content=product.data['content']
        pictures=[p for p in source['pictures'] if category(p) in content['categories'] and max(p['width'],p['height'])<=content['max_dimension']]
        ids={p['id'] for p in pictures}
        result={**source,'productId':product.id,'pictures':pictures}
        for field in ('retiredIds','retiredIdsV2'):
            if field in result:result[field]=[pid for pid in result[field] if RETIRED_ONLINE_IDS.get(pid) in ids]
        target=root/content['online_manifest'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
        print(f'{product.id}: {len(pictures)} online pictures; shared immutable assets')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('online_root',type=Path);publish(parser.parse_args().online_root)
