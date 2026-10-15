"""Regression tests for Issue #23 without building a new app release."""
import json
import pathlib
import tempfile
import unittest
import zipfile

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from online_release import assemble, checksum
from online_masterworks_pack import create_pack as original_masterworks_pack
from online_requested_remakes_pack import create_pack as requested_remakes_pack
from online_starry_night_replacement_pack import (
    ID, create_pack as detailed_pack, draw,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
SIZES = {
    "planet": 128, "tree": 32, "star": 32,
    "gem": 64, "mountain": 32, "owl": 32,
}


class ArtworkRedesignTests(unittest.TestCase):
    def test_six_bundled_artworks_replaced_without_duplicates(self):
        catalog = json.loads(
            (ROOT / "apps/game/assets/levels/catalog.json").read_text("utf-8"))
        self.assertEqual(len(catalog), len(set(catalog)))
        for ident, size in SIZES.items():
            self.assertEqual(catalog.count(f"{ident}.json"), 1)
            level = json.loads((
                ROOT / f"apps/game/assets/levels/{ident}.json"
            ).read_text("utf-8"))
            self.assertEqual(level["levelId"], ident)
            self.assertEqual((level["width"], level["height"]), (size, size))
            self.assertEqual(level["levelVersion"], 1)
            self.assertEqual(len(level["cells"]), size * size)
            self.assertEqual(level["checksum"], checksum(level))
            self.assertGreaterEqual(len(set(level["cells"])), 8)
            self.assertLessEqual(len(level["palette"]), 48)
            animation = json.loads((
                ROOT / f"apps/game/assets/animations/{ident}-v1.json"
            ).read_text("utf-8"))
            self.assertEqual(animation["levelId"], ident)
            self.assertEqual(animation["levelChecksum"], level["checksum"])
            self.assertEqual(animation["levelVersion"], level["levelVersion"])
            self.assertGreaterEqual(len(animation["frames"]), 3)
            self.assertEqual(animation["frames"][0]["changes"], [])
            self.assertEqual(animation["frames"][-1]["changes"], [])
            for frame in animation["frames"]:
                indices = set()
                for index, color in frame["changes"]:
                    self.assertTrue(0 <= index < size * size)
                    self.assertTrue(0 <= color < len(level["palette"]))
                    self.assertNotIn(index, indices)
                    indices.add(index)
            self.assertTrue(animation["frames"][1]["changes"])

    def test_planet_and_star_are_not_old_stripes_or_cross(self):
        levels = {}
        for ident in ("planet", "star"):
            levels[ident] = json.loads(
                (ROOT / f"apps/game/assets/levels/{ident}.json").read_text("utf-8"))
        planet = levels["planet"]
        self.assertGreater(len(set(planet["cells"])), 12)
        self.assertNotEqual(planet["cells"][64 * 128 + 64], 0)
        self.assertNotEqual(planet["cells"][79 * 128 + 15], 0)
        star = levels["star"]
        c = star["cells"]
        self.assertNotEqual(c[5 * 32 + 16], c[5 * 32 + 5])
        self.assertNotEqual(c[13 * 32 + 5], c[5 * 32 + 5])
        self.assertEqual(c[3 * 32 + 3], c[28 * 32 + 28])

    def test_starry_night_has_real_80x80_detail_and_retires_original(self):
        rendered = draw()
        self.assertEqual(rendered.side, 80)
        self.assertEqual(len(rendered.cells), 6400)
        self.assertGreaterEqual(len(set(rendered.cells)), 12)
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            old = root / "packs/pixelhub-content-masterworks-6-v1/content.zip"
            new = root / "packs/pixelhub-content-starry-night-detailed-1-v1/content.zip"
            original_masterworks_pack(old)
            detailed_pack(new)
            # The new catalog also retires the original Mona Lisa; include its
            # immutable replacement when assembling this historical fixture.
            requested_remakes_pack(
                root / "packs/pixelhub-content-requested-remakes-4-v1/content.zip"
            )
            with zipfile.ZipFile(new) as archive:
                manifest = json.loads(archive.read("catalog.json"))
                item = manifest["pictures"][0]
                self.assertEqual(item["id"], ID)
                self.assertEqual((item["width"], item["height"]), (80, 80))
                painting = json.loads(archive.read(f"levels/{ID}-v1.json"))
                self.assertEqual(painting["checksum"], checksum(painting))
                self.assertEqual(painting["levelId"], ID)
                self.assertEqual(item["checksum"], painting["checksum"])
            out = root / "site"
            assemble(root / "packs", out)
            entries = json.loads((out / "catalog.json").read_text("utf-8"))
            ids = [p["id"] for p in entries["pictures"]]
            self.assertNotIn("online-starry-night", ids)
            self.assertEqual(ids.count(ID), 1)
            self.assertIn("online-starry-night", entries["retiredIds"])
            self.assertTrue((out / "levels/online-starry-night-v1.json").exists())
            self.assertTrue((out / f"previews/{ID}-v1.png").exists())


if __name__ == "__main__":
    unittest.main()
