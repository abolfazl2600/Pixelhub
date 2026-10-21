#!/usr/bin/env python3
"""Validated registry selection for local tools and Actions planning."""
import argparse
import json
import subprocess
from registry import ROOT, load_registry, select, ConfigurationError


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['validate','matrix','affected'])
    parser.add_argument('--application',default='all')
    parser.add_argument('--base')
    args=parser.parse_args()
    registry=load_registry()
    if args.command=='validate':
        print(f'Validated {len(registry)} products; ready: '+', '.join(p.id for p in registry.values() if p.ready))
    elif args.command=='matrix':
        print(json.dumps({'include':[{'product':p.id,'signing_prefix':p.signing_prefix,'environment':p.data['distribution']['environment']} for p in select(args.application)]},separators=(',',':')))
    else:
        paths=subprocess.check_output(['git','diff','--name-only',args.base,'HEAD'],cwd=ROOT,text=True).splitlines() if args.base else []
        derived={'products/android-products.json','apps/game/lib/products/products.g.dart'}
        shared=not paths or any(p not in derived and not p.startswith(('products/','apps/game/assets/products/','docs/')) for p in paths)
        affected=[p.id for p in registry.values() if p.ready and (shared or f'products/{p.id}.yaml' in paths or p.data['content']['offline_manifest'] in paths or 'products/schema.json' in paths)]
        print(json.dumps(affected))

if __name__=='__main__':
    try: main()
    except (ConfigurationError, OSError, ValueError) as exc: raise SystemExit(str(exc))
