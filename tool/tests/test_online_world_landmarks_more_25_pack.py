"""Contract tests for 25 fresh exact-80x80 world landmark online levels."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_release import checksum, LEGACY_PUBLIC_CATEGORIES
from online_world_landmarks_25_pack import PICTURES as FIRST_LANDMARKS
from online_world_landmarks_more_25_pack import PICTURES, SIDE, make_level, create_pack


class WorldLandmarks80PackTests(unittest.TestCase):
    def test_twenty_five_distinct_new_structures_never_repeat_old_pack(self):
        self.assertEqual(len(PICTURES), 25)
        slugs = {item[0] for item in PICTURES}
        self.assertEqual(len(slugs), 25)
        self.assertEqual(len({item[1] for item in PICTURES}), 25)
        self.assertEqual(len({item[2] for item in PICTURES}), 25)
        earlier = {item[0] for item in FIRST_LANDMARKS}
        identifiers = {"online-world-more-" + name + "-80" for name in slugs}
        self.assertFalse(earlier.intersection(identifiers))
        self.assertTrue(all(not name.endswith("-50") for name in slugs))
        self.assertEqual(SIDE, 80)

    def test_every_composition_is_exact_80_square_checksum_bound_and_unique(self):
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len({lvl["levelId"] for lvl in levels}), 25)
        self.assertEqual(len({tuple(lvl["cells"]) for lvl in levels}), 25)
        for item, level in zip(PICTURES, levels):
            with self.subTest(level=item[0]):
                self.assertEqual(level["levelId"], "online-world-more-" + item[0] + "-80")
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual((level["width"], level["height"]), (80, 80))
                self.assertEqual(len(level["cells"]), 6400)
                self.assertGreaterEqual(len(set(level["cells"])), 5)
                self.assertGreaterEqual(len(level["palette"]), 20)
                self.assertTrue(all(0 <= pixel < len(level["palette"])
                                    for pixel in level["cells"]))
                self.assertTrue(level["titles"]["fa"])
                self.assertTrue(level["titles"]["en"])
                self.assertEqual(level["checksum"], checksum(level))

    def test_immutable_release_catalog_json_and_png_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "content.zip"
            create_pack(output)
            with zipfile.ZipFile(output) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 25)
                self.assertEqual({p["category"] for p in pictures}, {"patterns"})
                self.assertTrue({p["category"] for p in pictures}
                                <= LEGACY_PUBLIC_CATEGORIES)
                self.assertEqual(len(archive.namelist()), 51)
                for picture in pictures:
                    with self.subTest(id=picture["id"]):
                        self.assertEqual(picture["version"], 1)
                        self.assertEqual((picture["width"], picture["height"]), (80, 80))
                        stem = picture["id"] + "-v1"
                        level_bytes = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        level = json.loads(level_bytes)
                        self.assertEqual(level["levelId"], picture["id"])
                        self.assertEqual(level["titles"]["fa"], picture["title"])
                        self.assertEqual(level["titles"]["en"], picture["titleEn"])
                        self.assertEqual(len(level_bytes), picture["bytes"])
                        self.assertLessEqual(len(level_bytes), 262144)
                        self.assertEqual(level["checksum"], picture["checksum"])
                        self.assertEqual(checksum(level), picture["checksum"])
                        self.assertEqual(len(level["cells"]), 6400)
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (80, 80))


if __name__ == "__main__":
    unittest.main()
