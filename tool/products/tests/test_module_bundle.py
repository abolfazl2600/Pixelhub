"""Contracts for per-product Flutter resource selection (no Flutter SDK needed)."""
import sys
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registry import ConfigurationError, load_registry
import module_bundle as bundle


class ModuleBundleTests(unittest.TestCase):
    def setUp(self):
        self.products = load_registry()

    def test_prepared_products_only_include_their_own_levels_and_brand(self):
        plans = {name: bundle.plan_assets(self.products[name])
                 for name in ('pixelhub', 'kids', 'art')}
        for product, plan in plans.items():
            self.assertIn(
                self.products[product].data['identity']['icon'].removeprefix('apps/game/'),
                plan.assets)
            self.assertIn('assets/levels/metadata.json', plan.assets)
            self.assertIn(
                self.products[product].data['content']['offline_manifest'].removeprefix('apps/game/'),
                plan.assets)
            other_brands = {p.data['identity']['icon'].removeprefix('apps/game/')
                            for name, p in self.products.items()
                            if name in plans and name != product}
            self.assertFalse(other_brands.intersection(plan.assets))
            self.assertTrue(all((bundle.APP / asset).is_file() for asset in plan.assets))
        self.assertNotIn('assets/levels/offline-mona-lisa.json', plans['kids'].assets)
        self.assertNotIn('assets/levels/fox.json', plans['art'].assets)
        self.assertNotIn('assets/levels/planet.json', plans['kids'].assets)
        self.assertNotIn('assets/sounds/coin_purchase.wav', plans['kids'].assets)
        self.assertFalse(any(asset.startswith('assets/sounds/') for asset in plans['art'].assets))
        self.assertNotIn('assets/animations/catalog.json', bundle.AssetPlan(
            product='empty',assets=(),modules={}).assets)

    def test_compile_defines_match_manifest_and_pubspec_has_no_wildcard(self):
        plan = bundle.plan_assets(self.products['kids'])
        self.assertIn('--dart-define=MODULE_MUSEUM=false', plan.dart_defines)
        self.assertIn('--dart-define=MODULE_ANIMATIONS=true', plan.dart_defines)
        self.assertIn('--dart-define=MODULE_IMAGE_IMPORT=false', plan.dart_defines)
        self.assertIn('--dart-define=MODULE_PROFILE=false', plan.dart_defines)
        source = bundle.PUBSPEC.read_text()
        generated = bundle.pubspec_for(plan, source)
        self.assertIn('    - assets/brand/kids_mark.png', generated)
        self.assertNotIn('    - assets/levels/\n', generated)
        self.assertNotIn('assets/brand/art_mark.png', generated)
        self.assertEqual(generated.split('  fonts:')[1], source.split('  fonts:')[1])

    def test_restore_pubspec_after_failure(self):
        fixture = 'flutter:\n  assets:\n    - assets/levels/\n  fonts:\n    - family: Roboto\n'
        with TemporaryDirectory() as temp:
            file = Path(temp) / 'pubspec.yaml'
            file.write_text(fixture)
            plan = bundle.AssetPlan('kids',('assets/brand/kids_mark.png',),{})
            with patch.object(bundle,'PUBSPEC',file):
                with self.assertRaisesRegex(RuntimeError,'simulated failure'):
                    with bundle.selected_product_assets(plan):
                        self.assertIn('    - assets/brand/kids_mark.png', file.read_text())
                        raise RuntimeError('simulated failure')
                self.assertEqual(file.read_text(),fixture)

    def test_archive_verifier_rejects_missing_or_unrelated_resources(self):
        plan = bundle.plan_assets(self.products['art'])
        def write_archive(path, filenames):
            with ZipFile(path,'w') as z:
                for name in filenames:
                    z.writestr('base/assets/flutter_assets/' + name, 'data')
        with TemporaryDirectory() as temp:
            apk = Path(temp) / 'app.aab'
            write_archive(apk, plan.assets)
            self.assertEqual(bundle.inspect_android(apk, plan)['asset_count_verified'],
                             len(plan.assets))
            write_archive(apk, [*plan.assets,'assets/brand/kids_mark.png'])
            with self.assertRaisesRegex(ConfigurationError,'unexpected='):
                bundle.inspect_android(apk, plan)
            write_archive(apk,plan.assets[:-1])
            with self.assertRaisesRegex(ConfigurationError,'missing='):
                bundle.inspect_android(apk, plan)


if __name__ == '__main__':
    unittest.main()
