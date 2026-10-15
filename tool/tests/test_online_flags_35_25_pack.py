"""Contract tests for 25 new original 35x35 country flag online levels."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_flags_20_pack import COUNTRIES as PREVIOUS_COUNTRIES
from online_flags_35_25_pack import (
    BOTTOM, TOP, COUNTRIES, SIDE, create_pack, flag, make_level,
)
from online_release import checksum


class CountryFlags35PackTests(unittest.TestCase):
    def test_new_countries_are_not_in_earlier_twenty(self):
        old = {item[0] for item in PREVIOUS_COUNTRIES}
        new = {item[0] for item in COUNTRIES}
        self.assertEqual(len(COUNTRIES), 25)
        self.assertEqual(len(new), 25)
        self.assertFalse(old.intersection(new))
        self.assertEqual(len(old | new), 45)

    def test_all_25_pixel_compositions_are_unique_and_exactly_35_square(self):
        self.assertEqual(SIDE, 35)
        self.assertEqual((TOP, BOTTOM), (6, 28))
        levels = [make_level(item) for item in COUNTRIES]
        self.assertEqual(len({level["levelId"] for level in levels}), 25)
        self.assertEqual(len({tuple(level["cells"]) for level in levels}), 25)
        for item, level in zip(COUNTRIES, levels):
            with self.subTest(country=item[0]):
                self.assertEqual((level["width"], level["height"]), (35, 35))
                self.assertEqual(len(level["cells"]), 35 * 35)
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertGreaterEqual(len(set(level["cells"])), 3)
                self.assertTrue(all(0 <= index < len(level["palette"])
                                    for index in level["cells"]))
                self.assertEqual(level["checksum"], checksum(level))
                self.assertTrue(level["titles"]["fa"].startswith("پرچم "))
                self.assertTrue(level["titles"]["en"].endswith(" Flag"))
                self.assertEqual(
                    level["levelId"], "online-flag-" + item[0] + "-35"
                )
                sprite = flag(item[0])
                self.assertEqual(len(sprite.cells), 1225)
                self.assertTrue(all(sprite.cells[x] == 0 for x in range(35)))
                self.assertTrue(all(
                    sprite.cells[y * 35 + x] == 0
                    for y in range(29, 35) for x in range(35)
                ))

    def test_critical_color_geometry_for_simple_flags(self):
        def pixel(country, x, y):
            return flag(country).cells[y * 35 + x]

        self.assertEqual(pixel("belgium", 2, 17), 11)
        self.assertEqual(pixel("belgium", 17, 17), 9)
        self.assertEqual(pixel("belgium", 32, 17), 2)
        self.assertEqual(pixel("austria", 17, 8), 2)
        self.assertEqual(pixel("austria", 17, 17), 1)
        self.assertEqual(pixel("austria", 17, 27), 2)
        self.assertEqual(pixel("czechia", 1, 17), 4)
        self.assertEqual(pixel("ireland", 1, 17), 7)
        self.assertEqual(pixel("ireland", 17, 17), 1)
        self.assertEqual(pixel("ireland", 33, 17), 10)
        self.assertEqual(pixel("saudi-arabia", 2, 25), 8)

    def test_packed_release_has_25_valid_35_pixel_pngs_and_levels(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "content.zip"
            create_pack(target)
            with zipfile.ZipFile(target) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 25)
                self.assertEqual({entry["category"] for entry in pictures},
                                 {"patterns"})
                self.assertEqual(len(archive.namelist()), 1 + 2 * 25)
                for entry in pictures:
                    with self.subTest(level=entry["id"]):
                        self.assertEqual(entry["version"], 1)
                        self.assertEqual(
                            (entry["width"], entry["height"]), (35, 35)
                        )
                        stem = entry["id"] + "-v1"
                        raw_level = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        level = json.loads(raw_level)
                        self.assertEqual(len(raw_level), entry["bytes"])
                        self.assertLessEqual(len(raw_level), 262144)
                        self.assertEqual(level["titles"]["fa"], entry["title"])
                        self.assertEqual(level["titles"]["en"], entry["titleEn"])
                        self.assertEqual(level["checksum"], entry["checksum"])
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(
                            struct.unpack(">II", preview[16:24]), (35, 35)
                        )


if __name__ == "__main__":
    unittest.main()
