"""Tests for the online 8x8 abstract-pattern pack and animation sidecars."""
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_abstract_8_pack import ID_PREFIX, PATTERNS, animation_frames, build, make_level
from online_release import assemble


class AbstractEightPackTests(unittest.TestCase):
    def test_ten_unique_exact_8x8_levels_and_valid_animation_frames(self):
        self.assertEqual(len(PATTERNS), 10)
        ids = set()
        for item in PATTERNS:
            level = make_level(item)
            self.assertEqual((level["width"], level["height"]), (8, 8))
            self.assertEqual(len(level["cells"]), 64)
            self.assertTrue(level["levelId"].startswith(ID_PREFIX))
            self.assertNotIn(level["levelId"], ids)
            ids.add(level["levelId"])
            frames = animation_frames(level, item[4])
            self.assertEqual(len(frames), 8)
            for frame in frames:
                seen = set()
                for position, color in frame["changes"]:
                    self.assertTrue(0 <= position < 64)
                    self.assertTrue(0 <= color < len(level["palette"]))
                    self.assertNotIn(position, seen)
                    seen.add(position)

    def test_release_pack_contains_previews_scenarios_and_validated_animations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            pack = root / "pixelhub-content-abstract-mini-10-v1" / "content.zip"
            pack.parent.mkdir(parents=True)
            build(pack)
            with zipfile.ZipFile(pack) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(len(catalog["pictures"]), 10)
                self.assertTrue(all(item["width"] == item["height"] == 8
                                    for item in catalog["pictures"]))
                self.assertTrue(all(item["animation"]["frameCount"] == 8
                                    for item in catalog["pictures"]))
                self.assertIn("animation-scenarios.json", archive.namelist())
                for item in catalog["pictures"]:
                    stem = f"{item['id']}-v1"
                    self.assertIn(f"previews/{stem}.png", archive.namelist())
                    animation = json.loads(archive.read(f"animations/{stem}.json"))
                    self.assertEqual(len(animation["frames"]), 8)
                    self.assertEqual(animation["levelChecksum"], item["checksum"])
            output = root / "site"
            assemble(root, output)
            published = json.loads((output / "catalog.json").read_text("utf-8"))
            entries = [item for item in published["pictures"]
                       if item["id"].startswith(ID_PREFIX)]
            self.assertEqual(len(entries), 10)
            self.assertTrue(all("animation" in item for item in entries))


if __name__ == "__main__":
    unittest.main()
