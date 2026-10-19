"""Validate the ten detailed 15x15 online object paintings and release assets."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_objects_detailed_15_pack import ARTWORKS, PREFIX, SIDE, create_pack, make_level
from online_objects_10_pack import PICTURES as MINI_PICTURES
from online_objects_30_pack import PICTURES as OBJECT_PICTURES
from online_release import assemble, checksum


class DetailedObjectFifteenPackTests(unittest.TestCase):
    def test_ten_independent_exact_15_by_15_paintings(self):
        self.assertEqual(len(ARTWORKS), 10)
        ids, grids = set(), set()
        for item in ARTWORKS:
            with self.subTest(slug=item[0]):
                level = make_level(item)
                self.assertTrue(level["levelId"].startswith(PREFIX))
                self.assertNotIn(level["levelId"], ids)
                self.assertNotIn(tuple(level["cells"]), grids)
                ids.add(level["levelId"])
                grids.add(tuple(level["cells"]))
                self.assertEqual((level["width"], level["height"]), (SIDE, SIDE))
                self.assertEqual(len(level["cells"]), 225)
                self.assertEqual(level["schemaVersion"], 2)
                self.assertEqual(level["levelVersion"], 1)
                self.assertEqual(level["checksum"], checksum(level))
                self.assertEqual(len(level["palette"]), 8)
                self.assertTrue(all(0 <= c < 8 for c in level["cells"]))
                self.assertGreaterEqual(len(set(level["cells"])), 5)
                self.assertGreaterEqual(sum(c != 0 for c in level["cells"]), 35)
                self.assertTrue(level["titles"]["fa"] and level["titles"]["en"])
        self.assertTrue(ids.isdisjoint("online-object-mini-" + p[0] for p in MINI_PICTURES))
        self.assertTrue(ids.isdisjoint("online-object-" + p[0] for p in OBJECT_PICTURES))

    def test_zip_catalog_previews_checksums_and_assembly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            pack = root / "pixelhub-content-objects-detailed-15-10-v1" / "content.zip"
            create_pack(pack)
            with zipfile.ZipFile(pack) as archive:
                entries = json.loads(archive.read("catalog.json"))["pictures"]
                self.assertEqual(len(entries), 10)
                self.assertEqual({p["category"] for p in entries}, {"objects"})
                self.assertEqual(len(archive.namelist()), 21)
                for picture in entries:
                    with self.subTest(id=picture["id"]):
                        self.assertEqual((picture["width"], picture["height"]), (15, 15))
                        stem = picture["id"] + "-v1"
                        body = archive.read("levels/" + stem + ".json")
                        level = json.loads(body)
                        preview = archive.read("previews/" + stem + ".png")
                        self.assertEqual(picture["bytes"], len(body))
                        self.assertEqual(picture["checksum"], level["checksum"])
                        self.assertEqual(picture["title"], level["titles"]["fa"])
                        self.assertEqual(picture["titleEn"], level["titles"]["en"])
                        self.assertEqual(preview[:8], b"\x89PNG\r\n\x1a\n")
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (15, 15))
            output = root / "site"
            assemble(root, output)
            published = json.loads((output / "catalog.json").read_text())
            self.assertEqual(len(published["pictures"]), 10)
            self.assertTrue(all(p["colorCount"] >= 5 for p in published["pictures"]))
            for picture in published["pictures"]:
                stem = picture["id"] + "-v1"
                self.assertTrue((output / "levels" / (stem + ".json")).is_file())
                self.assertTrue((output / "previews" / (stem + ".png")).is_file())


if __name__ == "__main__":
    unittest.main()
