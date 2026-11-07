"""Verify Kids small animal levels, immutable ZIPs and catalog separation."""
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

TOOL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
sys.path.insert(0, str(TOOL / "products"))

from online_kids_animals_pack import PREFIX, PICTURES, create_pack, make_level
from online_kids_persian_numbers_pack import create_pack as numbers_pack
from online_release import assemble, checksum
from publish_catalogs import publish


class KidsAnimalPackTests(unittest.TestCase):
    def test_twelve_distinct_color_by_number_animals(self):
        self.assertEqual(len(PICTURES), 12)
        ids, checksums, art = set(), set(), set()
        dimensions = set()
        for name, fa, en, draw in PICTURES:
            level = make_level(name, fa, en, draw)
            side = level["width"]
            dimensions.add(side)
            self.assertIn(side, (16, 24, 32))
            self.assertEqual(level["height"], side)
            self.assertEqual(level["schemaVersion"], 2)
            self.assertEqual(level["levelVersion"], 1)
            self.assertEqual(len(level["cells"]), side * side)
            self.assertTrue(all(0 <= cell < len(level["palette"])
                                for cell in level["cells"]))
            self.assertGreaterEqual(len(set(level["cells"])), 4)
            self.assertEqual(level["checksum"], checksum(level))
            ids.add(level["levelId"])
            checksums.add(level["checksum"])
            art.add(tuple(level["cells"]))
        self.assertEqual(len(ids), 12)
        self.assertTrue(all(ident.startswith(PREFIX) for ident in ids))
        self.assertEqual(len(checksums), 12)
        self.assertEqual(len(art), 12)
        self.assertEqual(dimensions, {16, 24, 32})

    def test_animal_pack_is_only_in_kids_online_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            packs = root / "packs"
            animal_pack = packs / "pixelhub-content-kids-animals-12-v1" / "content.zip"
            number_pack = packs / "pixelhub-content-kids-persian-numbers-20-v1" / "content.zip"
            create_pack(animal_pack)
            numbers_pack(number_pack)
            with zipfile.ZipFile(animal_pack) as archive:
                entries = json.loads(archive.read("catalog.json"))["pictures"]
                self.assertEqual(len(entries), 12)
                for entry in entries:
                    self.assertEqual(entry["category"], "animals")
                    self.assertLessEqual(max(entry["width"], entry["height"]), 32)
                    stem = entry["id"] + "-v1"
                    data = archive.read(f"levels/{stem}.json")
                    self.assertEqual(len(data), entry["bytes"])
                    self.assertEqual(json.loads(data)["checksum"], entry["checksum"])
                    self.assertTrue(archive.read(f"previews/{stem}.png").startswith(
                        bytes((137, 80, 78, 71, 13, 10, 26, 10))
                    ))
            online = root / "online"
            assemble(packs, online)
            shared = json.loads((online / "catalog.json").read_text())
            self.assertEqual(shared["pictures"], [])
            publish(online)
            kids = json.loads((online / "products/kids/catalog.json").read_text())
            animals = [p for p in kids["pictures"] if p["id"].startswith(PREFIX)]
            self.assertEqual(len(animals), 12)
            self.assertEqual(len(kids["pictures"]), 32)
            self.assertTrue(all(p["category"] == "animals" for p in animals))
            self.assertTrue(all(max(p["width"], p["height"]) <= 32
                                for p in kids["pictures"]))
            art = json.loads((online / "products/art/catalog.json").read_text())
            self.assertFalse(any(p["id"].startswith(PREFIX) for p in art["pictures"]))


if __name__ == "__main__":
    unittest.main()
