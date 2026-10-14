"""Tests for the exact 10x10 online object artwork pack."""
import pathlib
import sys
import tempfile
import unittest
import zipfile
import json

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_objects_10_pack import PICTURES, create_pack, make_level


class OnlineObjectMiniPackTests(unittest.TestCase):
    def test_twenty_unique_exact_ten_by_ten_levels(self):
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len(levels), 20)
        self.assertEqual(len({level["levelId"] for level in levels}), 20)
        self.assertEqual(len({tuple(level["cells"]) for level in levels}), 20)
        for level in levels:
            with self.subTest(level=level["levelId"]):
                self.assertEqual(level["width"], 10)
                self.assertEqual(level["height"], 10)
                self.assertEqual(len(level["cells"]), 100)
                self.assertGreaterEqual(len(set(level["cells"])), 3)
                self.assertLessEqual(max(level["cells"]), len(level["palette"]) - 1)
                self.assertEqual(len(level["checksum"]), 64)

    def test_pack_contains_bilingual_catalog_levels_and_previews(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "content.zip"
            create_pack(target)
            with zipfile.ZipFile(target) as archive:
                names = set(archive.namelist())
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(len(catalog["pictures"]), 20)
                self.assertEqual({p["category"] for p in catalog["pictures"]}, {"objects"})
                for picture in catalog["pictures"]:
                    stem = f"{picture['id']}-v{picture['version']}"
                    self.assertIn(f"levels/{stem}.json", names)
                    self.assertIn(f"previews/{stem}.png", names)
                    level = json.loads(archive.read(f"levels/{stem}.json"))
                    self.assertEqual(level["titles"]["fa"], picture["title"])
                    self.assertEqual(level["titles"]["en"], picture["titleEn"])
                    self.assertEqual(level["width"] * level["height"], len(level["cells"]))


if __name__ == "__main__":
    unittest.main()
