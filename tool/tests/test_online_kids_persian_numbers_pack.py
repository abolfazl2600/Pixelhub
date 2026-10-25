"""Contract tests for the 20 Kids-only Persian numeral online artworks."""
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

TOOL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
sys.path.insert(0, str(TOOL / "products"))

from online_kids_persian_numbers_pack import (
    GLYPHS, PREFIX, SIDE, create_pack, make_level, persian_number,
)
from online_release import assemble, checksum
from publish_catalogs import publish


class PersianNumeralKidsPackTests(unittest.TestCase):
    def test_twenty_distinct_persian_numbers_have_exact_32_cell_grids(self):
        self.assertEqual(set(GLYPHS), set("۰۱۲۳۴۵۶۷۸۹"))
        ids, checksums, thumbnails = set(), set(), set()
        for number in range(1, 21):
            level = make_level(number)
            self.assertEqual(level["levelId"], f"{PREFIX}{number:02d}")
            self.assertEqual(level["titles"]["fa"], f"عدد {persian_number(number)}")
            self.assertEqual(level["titles"]["en"], f"Persian number {number}")
            self.assertEqual(level["levelVersion"], 1)
            self.assertEqual((level["width"], level["height"]), (SIDE, SIDE))
            self.assertEqual(len(level["cells"]), SIDE * SIDE)
            self.assertTrue(all(0 <= cell < len(level["palette"]) for cell in level["cells"]))
            self.assertGreaterEqual(len(set(level["cells"])), 6)
            self.assertEqual(level["checksum"], checksum(level))
            ids.add(level["levelId"])
            checksums.add(level["checksum"])
            thumbnails.add(tuple(level["cells"]))
        self.assertEqual(len(ids), 20)
        self.assertEqual(len(checksums), 20)
        self.assertEqual(len(thumbnails), 20)

    def test_immutable_release_zip_and_kids_only_catalog_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            path = root / "packs" / "pixelhub-content-kids-persian-numbers-20-v1" / "content.zip"
            create_pack(path)
            with zipfile.ZipFile(path) as bundle:
                entries = json.loads(bundle.read("catalog.json"))["pictures"]
                self.assertEqual(len(entries), 20)
                self.assertEqual([entry["id"] for entry in entries],
                                 [f"{PREFIX}{n:02d}" for n in range(1, 21)])
                for entry in entries:
                    self.assertEqual(entry["category"], "patterns")
                    self.assertEqual(entry["version"], 1)
                    self.assertEqual((entry["width"], entry["height"]), (SIDE, SIDE))
                    stem = entry["id"] + "-v1"
                    data = bundle.read(f"levels/{stem}.json")
                    self.assertEqual(len(data), entry["bytes"])
                    self.assertEqual(json.loads(data)["checksum"], entry["checksum"])
                    self.assertTrue(bundle.read(f"previews/{stem}.png").startswith(
                        b"\x89PNG\r\n\x1a\n"
                    ))
            online = root / "online"
            assemble(root / "packs", online)
            shared = json.loads((online / "catalog.json").read_text())
            self.assertFalse(any(p["id"].startswith(PREFIX) for p in shared["pictures"]))
            publish(online)
            kids = json.loads((online / "products/kids/catalog.json").read_text())
            self.assertEqual(kids["productId"], "kids")
            self.assertEqual(len(kids["pictures"]), 20)
            self.assertEqual({p["id"] for p in kids["pictures"]},
                             {f"{PREFIX}{n:02d}" for n in range(1, 21)})
            art = json.loads((online / "products/art/catalog.json").read_text())
            self.assertFalse(any(p["id"].startswith(PREFIX) for p in art["pictures"]))


if __name__ == "__main__":
    unittest.main()
