"""Checksum-bound, additive animations must preserve every published painting."""
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from online_release import assemble, sample
from pixel_animation_recipes import ROOT, animation, compact
from publish_animation_companions import publish
from online_iranian_heritage_23_pack import generate_recipes


class AnimationCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.packs = cls.root / 'packs'
        workflow = (ROOT / '.github/workflows/web-pages.yml').read_text()
        for tag, script in re.findall(
                r'if ! gh release view ([\w-]+).*?python3 tool/(\w+)\.py', workflow, re.S):
            target = cls.packs / tag / 'content.zip'
            target.parent.mkdir(parents=True, exist_ok=True)
            module = importlib.import_module(script)
            builder = sample if script == 'online_release' else getattr(
                module, 'create_pack', getattr(module, 'build', None))
            builder(target)

    def setUp(self):
        self.online = self.root / self.id().split('.')[-1]
        assemble(self.packs, self.online)
        self.batch_dir = self.root / (self.id().split('.')[-1] + '-batches')
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        for batch in (ROOT / 'tool/animation_batches').glob('online-*.json'):
            shutil.copy2(batch, self.batch_dir / batch.name)
        self.generated_dir = self.root / (self.id().split('.')[-1] + '-generated')
        generate_recipes(self.online, self.generated_dir)
        for batch in self.generated_dir.glob('online-*.json'):
            shutil.copy2(batch, self.batch_dir / batch.name)

    def test_registered_batches_preserve_pixels_metadata_and_release_animations(self):
        before = {p.relative_to(self.online): p.read_bytes()
                  for p in self.online.rglob('*') if p.is_file()}
        catalog_before = json.loads(before[Path('catalog.json')])
        publish(self.online)
        after = json.loads((self.online / 'catalog.json').read_text())
        for path, body in before.items():
            if path != Path('catalog.json'):
                self.assertEqual((self.online / path).read_bytes(), body, str(path))
        recipes = {}
        for batch in (ROOT / 'tool/animation_batches').glob('online-*.json'):
            entries = json.loads(batch.read_text())
            self.assertTrue(1 <= len(entries) <= 10)
            self.assertFalse(set(recipes) & set(entries))
            recipes.update(entries)
        for batch in self.generated_dir.glob('online-*.json'):
            entries = json.loads(batch.read_text())
            self.assertFalse(set(recipes) & set(entries))
            recipes.update(entries)
        original = {p['id']: p for p in catalog_before['pictures']}
        for item in after['pictures']:
            if item['id'] not in recipes:
                self.assertEqual(item, original[item['id']])
                continue
            self.assertEqual({k: v for k, v in item.items() if k != 'animation'}, original[item['id']])
            level = json.loads((self.online / f"levels/{item['id']}-v{item['version']}.json").read_text())
            data = (self.online / f"animations/{item['id']}-v{item['version']}.json").read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), recipes[item['id']]['animationChecksum'])
            frames = json.loads(data)['frames']
            self.assertEqual(frames[0]['changes'], [])
            self.assertEqual(frames[-1]['changes'], [])
            self.assertTrue(any(frame['changes'] for frame in frames))
            self.assertEqual(data, compact(animation(level, recipes[item['id']])))

    def test_transformed_solid_shapes_have_no_sampling_holes(self):
        from online_release import checksum
        level = {'schemaVersion': 2, 'levelId': 'online-solid', 'levelVersion': 1,
                 'titles': {'fa': 'آزمایش', 'en': 'Solid'}, 'width': 32, 'height': 32,
                 'palette': ['FFFFFFFF', 'FF223344'],
                 'cells': [int(8 <= x < 24 and 8 <= y < 24)
                           for y in range(32) for x in range(32)]}
        level['checksum'] = checksum(level)
        for motion in ['pulse', 'spin', 'flap']:
            for frame in animation(level, {'motion': motion})['frames']:
                pixels = level['cells'][:]
                for at, color in frame['changes']:
                    pixels[at] = color
                for y in range(32):
                    row = pixels[y * 32:(y + 1) * 32]
                    occupied = [x for x, color in enumerate(row) if color]
                    if occupied:
                        self.assertTrue(all(row[min(occupied):max(occupied) + 1]), motion)

    def test_wrong_painting_or_changed_animation_is_rejected(self):
        batches = self.root / 'invalid'
        batches.mkdir(exist_ok=True)
        registered = sorted((ROOT / 'tool/animation_batches').glob('online-*.json'))
        if not registered:
            self.skipTest('No online batches registered yet')
        ident, recipe = next(iter(json.loads(registered[0].read_text()).items()))
        for field in ['checksum', 'animationChecksum']:
            (batches / 'online-01.json').write_text(json.dumps({ident: {**recipe, field: '0' * 64}}))
            with self.assertRaises(ValueError):
                publish(self.online, batches)

    def test_duplicate_and_oversized_batches_are_rejected(self):
        batches = self.root / 'duplicate'
        batches.mkdir(exist_ok=True)
        registered = sorted((ROOT / 'tool/animation_batches').glob('online-*.json'))
        if not registered:
            self.skipTest('No online batches registered yet')
        entries = json.loads(registered[0].read_text())
        for number in [1, 2]:
            (batches / f'online-{number}.json').write_text(json.dumps(entries))
        with self.assertRaises(ValueError):
            publish(self.online, batches)
        (batches / 'online-2.json').unlink()
        (batches / 'online-1.json').write_text(json.dumps({str(n): {} for n in range(11)}))
        with self.assertRaises(ValueError):
            publish(self.online, batches)
