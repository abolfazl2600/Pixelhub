"""Contract and regression coverage for 20 new city-specific 96x96 pictures.

Tests are provided for CI / future validation; generating the art never
requires modifying published levels or touching installed application data.
"""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_isfahan_shiraz_20_96_pack import PICTURES, SIDE, PALETTE, create_pack, make_level
from online_release import checksum


class IsfahanShirazOnlinePaintingsTest(unittest.TestCase):
    def test_ten_new_scenes_for_each_city(self):
        self.assertEqual(SIDE, 96)
        self.assertEqual(len(PICTURES), 20)
        self.assertEqual(sum(x[3] == "isfahan" for x in PICTURES), 10)
        self.assertEqual(sum(x[3] == "shiraz" for x in PICTURES), 10)
        self.assertEqual(len({x[0] for x in PICTURES}), 20)
        self.assertEqual(len({x[1] for x in PICTURES}), 20)
        self.assertEqual(len({x[2].casefold() for x in PICTURES}), 20)
        self.assertEqual(len({x[4] for x in PICTURES}), 20)

    def test_original_detailed_pixels_and_valid_new_identities(self):
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len({tuple(x["cells"]) for x in levels}), 20)
        for (slug, persian, english, city, _), level in zip(PICTURES, levels):
            with self.subTest(slug=slug):
                self.assertEqual(level["levelId"], f"online-iran-{city}-{slug}-96")
                self.assertEqual((level["width"], level["height"]), (96, 96))
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(level["titles"], {"fa": persian, "en": english})
                self.assertEqual(level["palette"], PALETTE)
                self.assertEqual(len(level["cells"]), 96 * 96)
                self.assertTrue(all(0 <= pixel < len(PALETTE)
                                    for pixel in level["cells"]))
                self.assertGreaterEqual(len(set(level["cells"])), 8)
                self.assertEqual(checksum(level), level["checksum"])

    def test_immutable_zip_has_playable_json_and_png_previews(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "content.zip"
            create_pack(path)
            with zipfile.ZipFile(path) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                self.assertEqual(len(catalog["pictures"]), 20)
                self.assertEqual(len(archive.namelist()), 41)
                for item in catalog["pictures"]:
                    with self.subTest(id=item["id"]):
                        self.assertEqual(item["version"], 1)
                        self.assertEqual(item["category"], "patterns")
                        self.assertEqual((item["width"], item["height"]), (96, 96))
                        stem = item["id"] + "-v1"
                        json_content = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        level = json.loads(json_content)
                        self.assertEqual(len(json_content), item["bytes"])
                        self.assertLessEqual(len(json_content), 262144)
                        self.assertEqual(level["checksum"], item["checksum"])
                        self.assertEqual(checksum(level), item["checksum"])
                        self.assertEqual(level["levelId"], item["id"])
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (96, 96))


if __name__ == "__main__":
    unittest.main()
