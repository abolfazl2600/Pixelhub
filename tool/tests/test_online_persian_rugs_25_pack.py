"""Contract tests for the 25 original 65x65 Persian rug online paintings."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_persian_rugs_25_pack import PALETTES, PICTURES, SIDE, create_pack, make_level
from online_release import checksum


class PersianRugs25Tests(unittest.TestCase):
    def test_unique_artwork_ids_and_exact_65x65_compositions(self):
        self.assertEqual(SIDE, 65)
        self.assertEqual(len(PICTURES), 25)
        ids = [item[0] for item in PICTURES]
        self.assertEqual(len(set(ids)), 25)
        self.assertEqual(len({item[3] for item in PICTURES}), 25)
        self.assertTrue(all(item[4] in PALETTES for item in PICTURES))
        self.assertTrue(all(0 <= item[5] <= 5 for item in PICTURES))
        artworks = [make_level(item) for item in PICTURES]
        self.assertEqual(len({tuple(level["cells"]) for level in artworks}), 25)
        for level in artworks:
            with self.subTest(level_id=level["levelId"]):
                self.assertEqual((level["width"], level["height"]), (65, 65))
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(len(level["cells"]), 4225)
                self.assertGreaterEqual(len(set(level["cells"])), 5)
                self.assertGreaterEqual(len(level["palette"]), 8)
                self.assertTrue(all(0 <= c < len(level["palette"]) for c in level["cells"]))
                self.assertEqual(checksum(level), level["checksum"])
                self.assertTrue(level["levelId"].startswith("online-persian-rug-"))
                self.assertTrue(level["titles"]["fa"])
                self.assertTrue(level["titles"]["en"])

    def test_release_json_png_and_legacy_compatible_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "content.zip"
            create_pack(target)
            with zipfile.ZipFile(target) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                pictures = catalog["pictures"]
                self.assertEqual(catalog["schemaVersion"], 1)
                self.assertEqual(len(pictures), 25)
                self.assertEqual({item["category"] for item in pictures}, {"patterns"})
                self.assertEqual(len(archive.namelist()), 51)
                for entry in pictures:
                    with self.subTest(level_id=entry["id"]):
                        self.assertEqual(entry["version"], 1)
                        self.assertEqual((entry["width"], entry["height"]), (65, 65))
                        stem = entry["id"] + "-v1"
                        body = archive.read("levels/" + stem + ".json")
                        image = archive.read("previews/" + stem + ".png")
                        level = json.loads(body)
                        self.assertEqual(level["levelId"], entry["id"])
                        self.assertEqual(level["titles"]["fa"], entry["title"])
                        self.assertEqual(level["titles"]["en"], entry["titleEn"])
                        self.assertEqual(entry["checksum"], level["checksum"])
                        self.assertEqual(entry["bytes"], len(body))
                        self.assertLessEqual(len(body), 262144)
                        self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", image[16:24]), (65, 65))


if __name__ == "__main__":
    unittest.main()
