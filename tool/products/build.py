#!/usr/bin/env python3
"""Build one product; release fails closed before invoking Flutter.

Environment uses private *_UPLOAD_* inputs. The selected values are mapped
to the existing Gradle *_RELEASE_* interface without changing PixelHub keys.
"""
from __future__ import annotations
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from zipfile import ZipFile
from registry import ROOT, select, ConfigurationError

KINDS = ['preview-apk','release-apk','play-aab','release-all']


def run(args, **kwargs):
    return subprocess.check_output([str(x) for x in args], text=True, **kwargs)


def android_tool(name):
    root=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','/opt/android-sdk')))
    files=list((root/'build-tools').glob(f'*/{name}'))
    if not files: raise ConfigurationError(f'Android SDK tool unavailable: {name}')
    return sorted(files,key=lambda p:tuple(int(x) for x in p.parent.name.split('.') if x.isdigit()))[-1]


def signature_fingerprint(output):
    import re
    match=re.search(r'certificate SHA-256 digest:\s*([a-fA-F0-9:]+)',output)
    if not match: raise ConfigurationError('No signer SHA-256 certificate in verification output')
    return match.group(1).replace(':','').lower()


def verify_apk(path, product, release, expected_cert=None):
    output=run([android_tool('apksigner'),'verify','--verbose','--print-certs',path])
    cert=signature_fingerprint(output)
    if release and ('CN=Android Debug' in output or cert != expected_cert):
        raise ConfigurationError('Release APK signer does not match the selected upload key')
    dump=run([android_tool('aapt'),'dump','badging',path])
    import re
    match=re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'",dump)
    if not match or match.groups()!=(product.application_id,str(product.version_code),product.version_name):
        raise ConfigurationError('APK application ID/version mismatch')
    return cert


def verify_aab(path, product, expected_cert):
    # jarsigner validates every signed entry's digest. Explicitly require a
    # signature, since jarsigner returns zero even for an unsigned archive.
    output=run(['jarsigner','-J-Duser.language=en','-verify','-verbose','-certs',path])
    if 'jar verified.' not in output or 'jar is unsigned' in output:
        raise ConfigurationError('AAB JAR signature verification failed')
    cert_output=run(['keytool','-J-Duser.language=en','-printcert','-jarfile',path])
    import re
    match=re.search(r'SHA256:\s*([A-Fa-f0-9:]+)',cert_output)
    if not match or match.group(1).replace(':','').lower()!=expected_cert:
        raise ConfigurationError('AAB signer does not match the selected upload key')
    with ZipFile(path) as archive:
        if not {'base/manifest/AndroidManifest.xml','BundleConfig.pb'} <= set(archive.namelist()):
            raise ConfigurationError('Invalid AAB structure')
        raw=archive.read('base/manifest/AndroidManifest.xml')
        verify_jar_coverage(archive)
    attrs = aab_manifest_attributes(raw)
    if attrs.get('package') != product.application_id or attrs.get('versionCode') != str(product.version_code) or attrs.get('versionName') != product.version_name:
        raise ConfigurationError(f'AAB application ID/version mismatch: {attrs}')
    return expected_cert


def verify_jar_coverage(archive):
    """A verified JAR must not hide unlisted, unsigned payload entries."""
    import re
    try:
        manifest=archive.read('META-INF/MANIFEST.MF').decode('utf-8')
    except (KeyError, UnicodeError) as exc:
        raise ConfigurationError('Missing or invalid JAR signing manifest') from exc
    # JAR headers may continue on the following line, prefixed by one space.
    manifest=manifest.replace('\r\n','\n').replace('\n ','')
    signed=set()
    for section in manifest.split('\n\n'):
        values=dict(line.split(': ',1) for line in section.splitlines() if ': ' in line)
        if 'Name' in values and any(key.endswith('-Digest') for key in values): signed.add(values['Name'])
    for name in archive.namelist():
        signature=name=='META-INF/MANIFEST.MF' or re.fullmatch(r'META-INF/[^/]+\.(?:SF|RSA|DSA|EC)',name,re.I)
        if not name.endswith('/') and not signature and name not in signed:
            raise ConfigurationError(f'Unsigned AAB payload entry: {name}')


def protobuf_fields(data):
    """Decode length-delimited/varint fields; AAB manifest is aapt2 XmlNode."""
    def varint(offset):
        value=0; shift=0
        while offset<len(data) and shift<70:
            byte=data[offset]; offset+=1; value|=(byte&127)<<shift
            if byte<128: return value,offset
            shift+=7
        raise ConfigurationError('Malformed protobuf varint')
    offset=0
    while offset<len(data):
        tag,offset=varint(offset); kind=tag&7; number=tag>>3
        if kind==2:
            size,offset=varint(offset); value=data[offset:offset+size]; offset+=size
            if len(value)!=size: raise ConfigurationError('Truncated protobuf field')
        elif kind==0: value,offset=varint(offset)
        elif kind in (1,5):
            size=8 if kind==1 else 4; value=data[offset:offset+size];offset+=size
        else: raise ConfigurationError('Unsupported protobuf wire type')
        yield number,value


def aab_manifest_attributes(raw):
    # frameworks/base/tools/aapt2/Resources.proto: XmlNode.element=1,
    # XmlElement.attribute=4, XmlAttribute.name=2, value=3.
    element=next((v for n,v in protobuf_fields(raw) if n==1),None)
    if not isinstance(element,bytes): raise ConfigurationError('AAB manifest has no root element')
    result={}
    for number,value in protobuf_fields(element):
        if number==4:
            fields=dict(protobuf_fields(value))
            if 2 in fields and 3 in fields: result[fields[2].decode()]=fields[3].decode()
    return result


def build(product,kind,output):
    product.require_ready()
    if 'android' not in product.data['distribution']['targets']: raise ConfigurationError('Android target disabled')
    app=ROOT/'apps/game'; output.mkdir(parents=True,exist_ok=True)
    release=kind!='preview-apk'; env=os.environ.copy(); env['PIXELHUB_BUILD_PRODUCT']=product.id
    source_dirty=bool(run(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT).strip())
    # Always clear ambient signing before selecting this product's values.
    for key in ['STORE_FILE','STORE_PASSWORD','KEY_ALIAS','KEY_PASSWORD']:
        env.pop('PIXELHUB_RELEASE_'+key,None)
    with tempfile.TemporaryDirectory(prefix='pixelhub-signing-') as private_dir:
        cert=None
        if release:
            prefix=product.signing_prefix+'_UPLOAD_'
            values={key:os.environ.get('PRODUCT_UPLOAD_'+key) or os.environ.get(prefix+key,'') for key in ['KEYSTORE_BASE64','STORE_PASSWORD','KEY_ALIAS','KEY_PASSWORD']}
            if not all(values.values()): raise ConfigurationError(f'{product.id}: missing private {prefix} signing secrets; use preview-apk')
            keyfile=Path(private_dir)/'upload.jks'
            keyfile.write_bytes(base64.b64decode(values['KEYSTORE_BASE64'],validate=True)); keyfile.chmod(0o600)
            env.update({'PIXELHUB_RELEASE_STORE_FILE':str(keyfile),**{'PIXELHUB_RELEASE_'+key:values[key] for key in ['STORE_PASSWORD','KEY_ALIAS','KEY_PASSWORD']}})
            # Read the public certificate without putting a password on argv.
            cert_json=run(['keytool','-J-Duser.language=en','-list','-v','-keystore',keyfile,'-alias',values['KEY_ALIAS'],'-storepass:env','PIXELHUB_RELEASE_STORE_PASSWORD'],env=env)
            import re
            match=re.search(r'SHA256:\s*([A-Fa-f0-9:]+)',cert_json)
            if not match or 'CN=Android Debug' in cert_json: raise ConfigurationError('Invalid or debug release certificate')
            cert=match.group(1).replace(':','').lower()
        subprocess.run(['flutter','pub','get','--enforce-lockfile'],cwd=app,check=True,env=env)
        subprocess.run(['dart','run','tool/generate_launcher_icons.dart',product.id],cwd=app,check=True,env=env)
        common=['--flavor',product.id,f'--dart-define=PRODUCT_ID={product.id}','--build-name',product.version_name,'--build-number',str(product.version_code),'--no-pub']
        targets=['apk','appbundle'] if kind=='release-all' else ['appbundle'] if kind=='play-aab' else ['apk']
        sha=run(['git','rev-parse','HEAD'],cwd=ROOT).strip()
        artifacts=[]
        for target in targets:
            mode='release' if release else 'debug'
            subprocess.run(['flutter','build',target,'--'+mode,*common],cwd=app,check=True,env=env)
            path=app/f'build/app/outputs/flutter-apk/app-{product.id}-{mode}.apk' if target=='apk' else app/f'build/app/outputs/bundle/{product.id}Release/app-{product.id}-release.aab'
            if not path.is_file(): raise ConfigurationError(f'Missing build output: {path}')
            signer=verify_apk(path,product,release,cert) if target=='apk' else verify_aab(path,product,cert)
            label='preview' if not release else 'play' if target=='appbundle' else 'release'
            name=f'{product.data["distribution"]["artifact_prefix"]}-{label}-v{product.version_name}+{product.version_code}-{sha[:8]}{path.suffix}'
            destination=output/name;shutil.copyfile(path,destination)
            artifacts.append(dict(file=name,sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),signing_verified=True,signer_sha256=signer,signing_type='upload-key' if release else 'debug'))
        manifest=dict(source_dirty=source_dirty,product_id=product.id,application_id=product.application_id,version_name=product.version_name,version_code=product.version_code,commit_sha=sha,build_type=kind,build_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),artifacts=artifacts)
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'Verified {product.id}: '+', '.join(a['file'] for a in artifacts))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--product',required=True);parser.add_argument('--type',choices=KINDS,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.product == 'all': parser.error('Build one product per invocation; use the Actions matrix for all products')
    try: build(select(args.product)[0],args.type,args.output.resolve())
    except (ConfigurationError,ValueError) as exc: raise SystemExit(str(exc))
