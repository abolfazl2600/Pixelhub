#!/usr/bin/env python3
"""Build one product into its own Web directory; never deploy implicitly."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from registry import ROOT, select
from module_bundle import plan_assets, selected_product_assets, inspect_web


def build(product):
    if 'web' not in product.data['distribution']['targets']: raise SystemExit('Web target disabled')
    app=ROOT/'apps/game';web=app/'build/web';target=app/f'build/products/{product.id}'
    plan=plan_assets(product)
    with selected_product_assets(plan):
        subprocess.run(['flutter','pub','get','--enforce-lockfile'],cwd=app,check=True)
        subprocess.run(['dart','run','tool/generate_launcher_icons.dart',product.id],cwd=app,check=True)
        subprocess.run(['flutter','build','web','--release','--base-href',
            product.data['distribution']['web_base_href'],
            f'--dart-define=PRODUCT_ID={product.id}',*plan.dart_defines,
            '--no-web-resources-cdn','--pwa-strategy=none','--no-pub'],cwd=app,check=True)
        inspect_web(web,plan)
    manifest=json.loads((web/'manifest.json').read_text());manifest.update(name=product.data['identity']['name'],short_name=product.data['identity']['name'],id=product.data['distribution']['web_base_href'],scope=product.data['distribution']['web_base_href'],theme_color=product.data['appearance']['primary'],background_color=product.data['appearance']['background'])
    (web/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    import html
    name=html.escape(product.data['identity']['name'],quote=True)
    index=(web/'index.html').read_text().replace('<title>PixelHub</title>',f'<title>{name}</title>')
    index=index.replace('content="PixelHub"',f'content="{name}"').replace('<strong>PixelHub</strong>',f'<strong>{name}</strong>')
    if product.id != 'pixelhub':
        index=index.replace('#069AEA',product.data['appearance']['primary']).replace('#316349',product.data['appearance']['primary']).replace('#f9f7f1',product.data['appearance']['background'])
    (web/'index.html').write_text(index)
    if not (web/'privacy.html').is_file():raise SystemExit('Missing privacy page')
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (web/'commit.txt').write_text(sha+'\n')
    (web/'product.json').write_text(json.dumps(dict(product_id=product.id,application_id=product.application_id,version_name=product.version_name,version_code=product.version_code,commit_sha=sha,module_bundle=plan.as_report()))+'\n')
    subprocess.run(['python3',ROOT/'tool/prepare_offline_web.py',web],check=True)
    if target.exists():shutil.rmtree(target)
    shutil.copytree(web,target)
    return target

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--product',default='pixelhub');args=parser.parse_args()
    for p in select(args.product):print(build(p))
