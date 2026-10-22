#!/usr/bin/env python3
"""No automatic increments. Reject version rollback against main and release tags.

Tag releases as <product>/v<name>+<code> only after a store release is approved.
Rebuilding the exact tagged commit is allowed, never another commit at its code.
"""
import argparse
import json
import re
import subprocess
from registry import ROOT, load_registry, ConfigurationError


def check(base=None):
    registry=load_registry()
    if base:
        for product in registry.values():
            old=subprocess.run(['git','show',f'{base}:products/{product.id}.yaml'],cwd=ROOT,text=True,capture_output=True)
            if old.returncode: continue
            prior=json.loads(old.stdout)['identity']
            if product.version_code<prior['version_code'] or (product.version_name!=prior['version_name'] and product.version_code<=prior['version_code']):
                raise ConfigurationError(f'{product.id}: version code must increase with a version change and must never decrease')
    tags=subprocess.check_output(['git','tag','--list'],cwd=ROOT,text=True).splitlines()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for product in registry.values():
        for tag in tags:
            match=re.fullmatch(re.escape(product.id)+r'/v(\d+\.\d+\.\d+)\+(\d+)',tag)
            if not match: continue
            code=int(match.group(2))
            commit=subprocess.check_output(['git','rev-list','-n','1',tag],cwd=ROOT,text=True).strip()
            if product.version_code<code or (product.version_code==code and commit!=head):
                raise ConfigurationError(f'{product.id}: code {code} already released at {tag}; increment version_code')
    print('Product versions are valid; no versions were incremented.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base');args=parser.parse_args()
    try: check(args.base)
    except ConfigurationError as exc: raise SystemExit(str(exc))
