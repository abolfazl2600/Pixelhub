"""Regression coverage for twenty original Iranian 65x65 online levels."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_iran_more_20_pack import PICTURES, SIDE, create_pack, make_level
from online_release import checksum


class Iranian65OnlinePackTests(unittest.TestCase):
    def test_exact_canvas_unique_ids_and_distinct_pixels(self):
        self.assertEqual(SIDE, 65)
        self.assertEqual(len(PICTURES), 20)
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len({level["levelId"] for level in levels}), 20)
        self.assertEqual(len({tuple(level["cells"]) for level in levels}), 20)
        for item, level in zip(PICTURES, levels):
            with self.subTest(level=item[0]):
                self.assertEqual((level["width"], level["height"]), (65, 65))
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(len(level["cells"]), 65 * 65)
                self.assertTrue(level["titles"]["fa"])
                self.assertTrue(level["titles"]["en"])
                self.assertGreaterEqual(len(set(level["cells"])), 4)
                self.assertGreater(len(set(level["palette"])), 8)
                self.assertGreaterEqual(min(level["cells"]), 0)
                self.assertLess(max(level["cells"]), len(level["palette"]))
                self.assertEqual(level["checksum"], checksum(level))
                self.assertTrue(level["levelId"].startswith("online-iran-"))

    def test_immutable_release_contains_playable_json_and_png(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "content.zip"
            create_pack(path)
            with zipfile.ZipFile(path) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 20)
                self.assertTrue({p["category"] for p in pictures}.issubset(
                    {"patterns", "nature", "objects"}
                ))
                self.assertEqual(
                    len(archive.namelist()),
                    1 + 2 * len(pictures),
                )
                for picture in pictures:
                    with self.subTest(level=picture["id"]):
                        self.assertEqual(picture["version"], 1)
                        self.assertEqual((picture["width"], picture["height"]), (65, 65))
                        stem = picture["id"] + "-v1"
                        body = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        level = json.loads(body)
                        self.assertEqual(level["levelId"], picture["id"])
                        self.assertEqual(level["checksum"], picture["checksum"])
                        self.assertEqual(level["titles"]["fa"], picture["title"])
                        self.assertEqual(level["titles"]["en"], picture["titleEn"])
                        self.assertEqual(len(body), picture["bytes"])
                        self.assertLessEqual(len(body), 262144)
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (65, 65))


if __name__ == "__main__":
    unittest.main()
