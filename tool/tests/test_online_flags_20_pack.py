"""Contract tests for the 20 exact 10x10 online country flag artworks."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_flags_20_pack import COUNTRIES, COLORS, SIZE, create_pack, flag_cells, make_level
from online_release import checksum


class CountryFlags20PackTests(unittest.TestCase):
    def test_country_count_and_unique_10_by_10_designs(self):
        self.assertEqual(SIZE, 10)
        self.assertEqual(len(COUNTRIES), 20)
        self.assertEqual(len({country for country, _, _ in COUNTRIES}), 20)
        self.assertIn("iran", {country for country, _, _ in COUNTRIES})
        levels = [make_level(item) for item in COUNTRIES]
        self.assertEqual(len({level["levelId"] for level in levels}), 20)
        self.assertEqual(len({tuple(flag_cells(item[0])) for item in COUNTRIES}), 20)
        for item, level in zip(COUNTRIES, levels):
            with self.subTest(country=item[0]):
                self.assertEqual((level["width"], level["height"]), (10, 10))
                self.assertEqual(len(level["cells"]), 100)
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertGreaterEqual(len(set(level["cells"])), 3)
                self.assertTrue(all(0 <= c < len(level["palette"])
                                    for c in level["cells"]))
                self.assertEqual(len(level["checksum"]), 64)
                self.assertEqual(level["checksum"], checksum(level))
                self.assertTrue(level["titles"]["fa"].startswith("پرچم "))
                self.assertTrue(level["titles"]["en"].endswith(" Flag"))

    def test_iran_flag_contains_correct_horizontal_bands_and_red_center(self):
        symbols = flag_cells("iran")
        at = lambda x, y: symbols[y * SIZE + x]
        self.assertEqual([at(0, y) for y in range(2, 8)],
                         ["g", "g", "w", "w", "r", "r"])
        self.assertEqual(at(4, 4), "r")
        self.assertEqual(at(5, 5), "r")
        self.assertNotEqual(COLORS["g"], COLORS["r"])

    def test_pack_manifest_json_previews_and_existing_categories(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "content.zip"
            create_pack(target)
            with zipfile.ZipFile(target) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 20)
                self.assertEqual({p["category"] for p in pictures}, {"patterns"})
                self.assertEqual(len(archive.namelist()), 41)
                for picture in pictures:
                    with self.subTest(level=picture["id"]):
                        self.assertEqual((picture["width"], picture["height"]), (10, 10))
                        self.assertEqual(picture["version"], 1)
                        stem = f"{picture['id']}-v1"
                        body = archive.read(f"levels/{stem}.json")
                        preview = archive.read(f"previews/{stem}.png")
                        level = json.loads(body)
                        self.assertEqual(level["levelId"], picture["id"])
                        self.assertEqual(level["titles"]["fa"], picture["title"])
                        self.assertEqual(level["titles"]["en"], picture["titleEn"])
                        self.assertEqual(level["checksum"], picture["checksum"])
                        self.assertEqual(len(body), picture["bytes"])
                        self.assertLessEqual(len(body), 262144)
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (10, 10))


if __name__ == "__main__":
    unittest.main()
