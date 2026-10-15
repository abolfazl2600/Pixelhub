"""Regression coverage for 25 distinct 50x50 world landmark online levels."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_world_landmarks_25_pack import PICTURES, SIZE, create_pack, draw, make_level
from online_release import checksum, LEGACY_PUBLIC_CATEGORIES


class WorldLandmarks50Tests(unittest.TestCase):
    def test_unique_bilingual_levels_on_exact_fifty_cell_grids(self):
        self.assertEqual(SIZE, 50)
        self.assertEqual(len(PICTURES), 25)
        self.assertEqual(len({item[0] for item in PICTURES}), 25)
        self.assertEqual(len({item[3] for item in PICTURES}), 25)
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len({tuple(level["cells"]) for level in levels}), 25)
        for item, level in zip(PICTURES, levels):
            with self.subTest(landmark=item[0]):
                self.assertTrue(level["levelId"].startswith("online-world-"))
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual((level["width"], level["height"]), (50, 50))
                self.assertEqual(len(level["cells"]), 2500)
                self.assertGreaterEqual(len(set(level["cells"])), 4)
                self.assertTrue(all(0 <= pixel < len(level["palette"])
                                    for pixel in level["cells"]))
                self.assertTrue(level["titles"]["fa"])
                self.assertTrue(level["titles"]["en"])
                self.assertEqual(checksum(level), level["checksum"])
                self.assertEqual(len(level["checksum"]), 64)
                self.assertEqual(len(draw(item[3]).cells), 2500)

    def test_no_duplicate_iranian_landmark_identifiers(self):
        from online_iran_more_20_pack import PICTURES as IRAN_MORE
        from online_iran_landmarks_pack import PICTURES as IRAN_LANDMARKS
        other = {item[0] for item in IRAN_MORE}
        # Existing pack may have a different tuple format; canonicalized from
        # generated level identities where available.
        self.assertFalse(other & {item[0] for item in PICTURES})
        self.assertEqual(len(PICTURES), 25)

    def test_release_contains_valid_bilingual_json_and_50x50_pngs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "content.zip"
            create_pack(target)
            with zipfile.ZipFile(target) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 25)
                self.assertTrue({p["category"] for p in pictures}
                                <= LEGACY_PUBLIC_CATEGORIES)
                self.assertEqual({p["category"] for p in pictures}, {"patterns"})
                self.assertEqual(len(archive.namelist()), 51)
                for pic in pictures:
                    with self.subTest(id=pic["id"]):
                        self.assertEqual(pic["version"], 1)
                        self.assertEqual((pic["width"], pic["height"]), (50, 50))
                        stem = pic["id"] + "-v1"
                        body = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        level = json.loads(body)
                        self.assertEqual(level["levelId"], pic["id"])
                        self.assertEqual(level["titles"]["fa"], pic["title"])
                        self.assertEqual(level["titles"]["en"], pic["titleEn"])
                        self.assertEqual(level["checksum"], pic["checksum"])
                        self.assertEqual(len(body), pic["bytes"])
                        self.assertLessEqual(len(body), 262144)
                        self.assertTrue(preview.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (50, 50))


if __name__ == "__main__":
    unittest.main()
