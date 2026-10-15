"""Contract checks for 15 NEW exact-70x70 famous landmark online pictures."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_release import checksum, LEGACY_PUBLIC_CATEGORIES
from online_world_landmarks_25_pack import PICTURES as FIRST_50
from online_world_landmarks_more_25_pack import PICTURES as SECOND_80
from online_world_landmarks_15_70_pack import PICTURES, SIDE, PALETTE, paint, make_level, create_pack


class WorldLandmarks70PackTests(unittest.TestCase):
    def test_15_new_subjects_without_title_or_id_collisions(self):
        self.assertEqual(SIDE, 70)
        self.assertEqual(len(PICTURES), 15)
        slugs = {picture[0] for picture in PICTURES}
        self.assertEqual(len(slugs), 15)
        self.assertEqual(len({p[1] for p in PICTURES}), 15)
        self.assertEqual(len({p[2].casefold() for p in PICTURES}), 15)
        previous_names = ({item[2].casefold() for item in FIRST_50} |
                          {item[2].casefold() for item in SECOND_80})
        self.assertFalse(previous_names & {p[2].casefold() for p in PICTURES})
        previous_ids = ({item[0] for item in FIRST_50} |
                        {"online-world-more-" + item[0] + "-80" for item in SECOND_80})
        new_ids = {"online-world-new-" + slug + "-70" for slug in slugs}
        self.assertFalse(new_ids & previous_ids)

    def test_70_by_70_unique_artworks_and_bilingual_metadata(self):
        self.assertEqual(len(PALETTE), 25)
        levels = [make_level(item) for item in PICTURES]
        self.assertEqual(len({level["levelId"] for level in levels}), 15)
        self.assertEqual(len({tuple(level["cells"]) for level in levels}), 15)
        for item, level in zip(PICTURES, levels):
            with self.subTest(slug=item[0]):
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(level["levelId"],
                                 "online-world-new-" + item[0] + "-70")
                self.assertEqual((level["width"], level["height"]), (70, 70))
                self.assertEqual(len(level["cells"]), 4900)
                self.assertGreaterEqual(len(set(level["cells"])), 5)
                self.assertTrue(all(0 <= c < len(level["palette"])
                                    for c in level["cells"]))
                self.assertEqual(len(level["checksum"]), 64)
                self.assertEqual(checksum(level), level["checksum"])
                self.assertEqual(level["titles"]["fa"], item[1])
                self.assertEqual(level["titles"]["en"], item[2])
                self.assertEqual(len(paint(item[0]).cells), 4900)

    def test_release_zip_contract_levels_pngs_and_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive_path = pathlib.Path(temp) / "content.zip"
            create_pack(archive_path)
            with zipfile.ZipFile(archive_path) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                pictures = catalog["pictures"]
                self.assertEqual(len(pictures), 15)
                self.assertEqual(len(archive.namelist()), 31)
                self.assertEqual({p["category"] for p in pictures}, {"patterns"})
                self.assertTrue({p["category"] for p in pictures}
                                <= LEGACY_PUBLIC_CATEGORIES)
                for picture in pictures:
                    with self.subTest(id=picture["id"]):
                        self.assertEqual(picture["version"], 1)
                        self.assertEqual((picture["width"],picture["height"]), (70,70))
                        stem = picture["id"] + "-v1"
                        raw = archive.read("levels/" + stem + ".json")
                        png = archive.read("previews/" + stem + ".png")
                        level = json.loads(raw)
                        self.assertEqual(level["levelId"], picture["id"])
                        self.assertEqual(level["titles"]["fa"], picture["title"])
                        self.assertEqual(level["titles"]["en"], picture["titleEn"])
                        self.assertEqual(level["checksum"], picture["checksum"])
                        self.assertEqual(checksum(level), picture["checksum"])
                        self.assertEqual(len(level["cells"]), 4900)
                        self.assertEqual(len(raw), picture["bytes"])
                        self.assertLessEqual(len(raw), 262144)
                        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", png[16:24]), (70,70))


if __name__ == "__main__":
    unittest.main()
