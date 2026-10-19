"""Expressive offline animation sidecars must be safe, reproducible and loop cleanly."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ROOT / 'apps/game/assets/levels'
ANIMATIONS = ROOT / 'apps/game/assets/animations'
SUBJECTS = (
    'sunflower', 'butterfly', 'rocket', 'fish', 'bird', 'bee', 'sailboat',
    'umbrella', 'tree', 'cat', 'tulip', 'ufo', 'diamond', 'moon',
)


class ExpressiveBundledAnimationTests(unittest.TestCase):
    def test_scenes_bind_to_immutable_artwork_and_preserve_pixel_bounds(self):
        catalog = json.loads((ANIMATIONS / 'catalog.json').read_text())
        for ident in SUBJECTS:
            with self.subTest(ident=ident):
                source = 'sunflower-v2.json' if ident == 'sunflower' else f'{ident}.json'
                level = json.loads((LEVELS / source).read_text())
                anim = json.loads((ANIMATIONS / catalog[ident]).read_text())
                self.assertEqual(anim['schemaVersion'], 1)
                self.assertEqual(anim['levelId'], level['levelId'])
                self.assertEqual(anim['levelVersion'], level['levelVersion'])
                self.assertEqual(anim['levelChecksum'], level['checksum'])
                self.assertEqual(anim['frameDurationMs'], 125)
                self.assertEqual(len(anim['frames']), 24)
                self.assertEqual(anim['frames'][0]['changes'], [])
                self.assertEqual(anim['frames'][-1]['changes'], [])
                distinct = set()
                for frame in anim['frames']:
                    cells = list(level['cells'])
                    seen = set()
                    for index, color in frame['changes']:
                        self.assertNotIn(index, seen)
                        self.assertTrue(0 <= index < len(cells))
                        self.assertTrue(0 <= color < len(level['palette']))
                        seen.add(index)
                        self.assertNotEqual(cells[index], color)
                        cells[index] = color
                    distinct.add(tuple(cells))
                self.assertGreaterEqual(len(distinct), 5)

    @unittest.skipUnless(shutil.which('node'), 'Node.js unavailable')
    def test_generator_matches_committed_companions_byte_for_byte(self):
        subprocess.run(
            ['node', str(ROOT / 'tool/bundled_animation_v2.mjs'), '--check'],
            cwd=ROOT, check=True, timeout=30,
        )


if __name__ == '__main__':
    unittest.main()
