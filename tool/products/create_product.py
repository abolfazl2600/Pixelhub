#!/usr/bin/env python3
"""Create a validated draft or ready flavor without copying application code."""
import argparse
import copy
import json
from pathlib import Path
from registry import ROOT, load_registry, validate_schema, ConfigurationError, safe_path
from generate import generate


def create(args):
    registry=load_registry()
    if args.id in registry:raise ConfigurationError(f'Duplicate product ID: {args.id}')
    data=copy.deepcopy(registry[args.template].data)
    data.update(id=args.id,ready=args.ready)
    data['identity'].update(name=args.name,display_name_fa=args.name_fa or args.name,application_id=args.package_id,storage_scope='pixelhub_'+args.id,version_name='1.0.0',version_code=1,icon=args.icon or '')
    data['distribution'].update(signing_prefix=args.id.upper(),environment='release-'+args.id.replace('_','-'),web_base_href='/Pixelhub/'+args.id+'/',artifact_prefix=args.id)
    data['content']['offline_manifest']=args.catalog or ''
    data['content']['online_manifest']=f'products/{args.id}/catalog.json'
    if args.ready and (not args.icon or not args.catalog):
        raise ConfigurationError('--ready requires --icon and --catalog; drafts are never buildable')
    validate_schema(data,json.loads((ROOT/'products/schema.json').read_text()))
    if any(p.application_id==args.package_id for p in registry.values()):raise ConfigurationError('Duplicate application ID')
    if args.icon and not safe_path(args.icon).is_file():raise ConfigurationError('Icon does not exist')
    if args.catalog and not safe_path(args.catalog).is_file():raise ConfigurationError('Catalog does not exist')
    target=ROOT/f'products/{args.id}.yaml'
    # Exclusive create, full-registry validation and rollback on failure.
    try:
        with target.open('x') as output:output.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        load_registry()
        generate()
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    print(f'Created {target.relative_to(ROOT)} ({"ready" if args.ready else "draft: supply brand assets/content and set ready=true"})')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--id',required=True);parser.add_argument('--name',required=True);parser.add_argument('--name-fa');parser.add_argument('--package-id',required=True)
    parser.add_argument('--template',choices=['kids','art','pixelhub'],default='kids');parser.add_argument('--icon');parser.add_argument('--catalog');parser.add_argument('--ready',action='store_true')
    try:create(parser.parse_args())
    except (ConfigurationError,ValueError,OSError) as exc:raise SystemExit(str(exc))
