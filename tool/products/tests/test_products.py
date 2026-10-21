import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import registry
from registry import ConfigurationError, load_registry, select, validate_schema
from build import aab_manifest_attributes, verify_aab, verify_jar_coverage, build
from publish_catalogs import publish

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.products=load_registry()
        self.schema=json.loads((registry.ROOT/'products/schema.json').read_text())

    def test_ready_selection_and_original_identity(self):
        self.assertEqual({p.id for p in select('all')},{'pixelhub','kids','art'})
        self.assertEqual(self.products['pixelhub'].application_id,'io.github.abolfazl2600.pixelhub')
        self.assertEqual(self.products['pixelhub'].version_code,8)
        for pid in ('animals','relax','unknown'):
            with self.assertRaises(ConfigurationError):select(pid)

    def test_rejects_unknown_flags_boolean_coercion_and_invalid_versions(self):
        for location,value in [('features',{'coins':'false'}),('identity',{'version_code':True}),('identity',{'version_code':0}),('identity',{'application_id':'not a package'}),('appearance',{'primary':'purple'})]:
            with self.subTest(location=location,value=value):
                data=copy.deepcopy(self.products['kids'].data);data[location].update(value)
                with self.assertRaises(ConfigurationError):validate_schema(data,self.schema)
        data=copy.deepcopy(self.products['kids'].data);data['features']['typo']=True
        with self.assertRaises(ConfigurationError):validate_schema(data,self.schema)

    def test_runtime_catalogs_are_audience_specific_without_copying_levels(self):
        for pid in ('kids','art'):
            p=self.products[pid];files=json.loads((registry.ROOT/p.data['content']['offline_manifest']).read_text())
            self.assertTrue(files)
            for filename in files:
                level=json.loads((registry.ROOT/'apps/game/assets/levels'/filename).read_text())
                if pid=='kids':self.assertLessEqual(max(level['width'],level['height']),32)
                else:self.assertTrue(filename.startswith('offline-'))
        self.assertFalse(self.products['kids'].data['features']['coins'])
        self.assertFalse(self.products['kids'].data['features']['image_import'])
        self.assertTrue(self.products['art'].data['features']['canvas_painting'])

    def test_online_manifests_are_isolated_and_reuse_asset_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);catalog={'schemaVersion':1,'pictures':[
                {'id':'online-kid','category':'animals','width':16,'height':16},
                {'id':'online-classic-sample','category':'patterns','width':96,'height':96},
                {'id':'online-other','category':'objects','width':128,'height':128}]}
            original=json.dumps(catalog);(root/'catalog.json').write_text(original)
            publish(root)
            kids=json.loads((root/'products/kids/catalog.json').read_text());art=json.loads((root/'products/art/catalog.json').read_text())
            self.assertEqual([p['id'] for p in kids['pictures']],['online-kid'])
            self.assertEqual([p['id'] for p in art['pictures']],['online-classic-sample'])
            self.assertEqual((root/'catalog.json').read_text(),original)
            self.assertFalse((root/'products/kids/levels').exists())

    def test_release_stops_before_flutter_if_signing_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ',{},clear=True), patch('build.subprocess.run') as run:
            with self.assertRaisesRegex(ConfigurationError,'missing private KIDS_UPLOAD_'):
                build(self.products['kids'],'release-all',Path(tmp))
            self.assertFalse(any(call.args and call.args[0][0] in ('flutter','dart') for call in run.call_args_list))

    def test_aab_manifest_parser_reads_package_and_versions(self):
        def field(number,payload):return bytes([number*8+2,len(payload)])+payload
        def attr(key,value):return field(4,field(2,key.encode())+field(3,value.encode()))
        raw=field(1,attr('package','example.test.art')+attr('versionName','1.0.0')+attr('versionCode','2'))
        self.assertEqual(aab_manifest_attributes(raw),{'package':'example.test.art','versionName':'1.0.0','versionCode':'2'})
        with self.assertRaises(ConfigurationError):aab_manifest_attributes(b'\x0a\x7f')

    def test_unsigned_aab_is_rejected_even_when_jarsigner_exits_zero(self):
        with patch('build.run',return_value='jar is unsigned.'):
            with self.assertRaisesRegex(ConfigurationError,'signature verification failed'):
                verify_aab(Path('unsigned.aab'),self.products['art'],'abc')

    def test_unsigned_payload_in_otherwise_signed_jar_is_rejected(self):
        from io import BytesIO
        from zipfile import ZipFile
        stream=BytesIO()
        with ZipFile(stream,'w') as z:
            z.writestr('META-INF/MANIFEST.MF','Manifest-Version: 1.0\r\n\r\nName: base/manifest/AndroidManifest.xml\r\nSHA-256-Digest: test\r\n\r\n')
            z.writestr('base/manifest/AndroidManifest.xml',b'test')
        with ZipFile(stream) as z: verify_jar_coverage(z)
        with ZipFile(stream,'a') as z: z.writestr('unexpected',b'unsigned')
        with ZipFile(stream) as z:
            with self.assertRaisesRegex(ConfigurationError,'Unsigned AAB payload'):verify_jar_coverage(z)

    def test_main_storage_key_contract_is_preserved(self):
        # Runtime isolation is additionally exercised in product_storage_test.dart.
        self.assertEqual(self.products['pixelhub'].data['identity']['storage_scope'],'pixelhub')
        self.assertEqual(self.products['kids'].data['identity']['storage_scope'],'pixelhub_kids')
        self.assertFalse(self.products['art'].data['identity']['storage_scope'].startswith('pixelhub.'))

if __name__=='__main__':unittest.main()
