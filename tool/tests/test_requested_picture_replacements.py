"""Requested replacement assets and immutable publication regressions."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_flags_20_pack import create_pack as historical_flags
from online_masterworks_pack import create_pack as historical_masterworks
from online_release import RETIRED_ONLINE_IDS, assemble, checksum
from online_requested_remakes_pack import (
    REPLACEMENTS, create_pack, iran, mona_lisa, turkey, united_kingdom,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
PREVIOUS = {
    "online-flag-united-kingdom-10": "online-flag-united-kingdom-30",
    "online-flag-turkey-10": "online-flag-turkey-40",
    "online-flag-iran-10": "online-flag-iran-40",
    "online-mona-lisa": "online-mona-lisa-detailed-90",
}


class RequestedPictureReplacementsTests(unittest.TestCase):
    def test_four_new_pictures_are_exact_size_and_not_simple_scaling(self):
        expected = [30, 40, 40, 90]
        sprites = [united_kingdom(), turkey(), iran(), mona_lisa()]
        self.assertEqual(len(REPLACEMENTS), 4)
        self.assertEqual([s.side for s in sprites], expected)
        for art, side in zip(sprites, expected):
            with self.subTest(size=side):
                self.assertEqual(len(art.cells), side * side)
                self.assertGreaterEqual(len(set(art.cells)), 2)
                self.assertLessEqual(len(art.palette), 48)
                self.assertTrue(all(0 <= c < len(art.palette)
                                    for c in art.cells))
        self.assertGreaterEqual(len(set(sprites[3].cells)), 18)
        # Red crescent must be hollow; flag cores are full-bleed.
        flag = sprites[1]
        at = lambda x, y: flag.cells[y * flag.side + x]
        self.assertEqual(at(15, 20), 1)
        self.assertEqual(at(22, 20), 0)
        self.assertEqual(at(30, 17), 1)
        iran_flag = sprites[2]
        at_iran = lambda x, y: iran_flag.cells[y * 40 + x]
        self.assertEqual([at_iran(0, y) for y in (2, 20, 37)],
                         [0, 1, 2])
        self.assertNotEqual(at_iran(19, 20), at_iran(8, 20))
        uk = sprites[0]
        self.assertNotEqual(uk.cells[0], uk.cells[14 * 30 + 14])

    def test_pack_checksums_previews_and_palette(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "content.zip"
            create_pack(p)
            with zipfile.ZipFile(p) as archive:
                manifest = json.loads(archive.read("catalog.json"))
                self.assertEqual(len(manifest["pictures"]), 4)
                self.assertEqual(len(archive.namelist()), 9)
                for item, expected in zip(manifest["pictures"], [30, 40, 40, 90]):
                    with self.subTest(picture=item["id"]):
                        self.assertEqual((item["width"], item["height"]),
                                         (expected, expected))
                        self.assertEqual(item["version"], 1)
                        name = item["id"] + "-v1"
                        data = archive.read("levels/" + name + ".json")
                        level = json.loads(data)
                        self.assertEqual(len(level["cells"]), expected ** 2)
                        self.assertEqual(level["checksum"], checksum(level))
                        self.assertEqual(len(data), item["bytes"])
                        self.assertEqual(level["checksum"], item["checksum"])
                        image = archive.read("previews/" + name + ".png")
                        self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(struct.unpack(">II", image[16:24]),
                                         (expected, expected))

    def test_historic_images_are_retired_not_duplicated_or_mutated(self):
        for old, fresh in PREVIOUS.items():
            self.assertEqual(RETIRED_ONLINE_IDS[old], fresh)
        with tempfile.TemporaryDirectory() as t:
            root = pathlib.Path(t)
            packs = root / "packs"
            for tag, generator in [
                ("pixelhub-content-country-flags-10-20-v1", historical_flags),
                ("pixelhub-content-masterworks-6-v1", historical_masterworks),
                ("pixelhub-content-requested-remakes-4-v1", create_pack),
            ]:
                path = packs / tag / "content.zip"
                generator(path)
            dest = root / "web"
            assemble(packs, dest)
            catalog = json.loads((dest / "catalog.json").read_text("utf8"))
            published = {x["id"]: x for x in catalog["pictures"]}
            for old, new in PREVIOUS.items():
                self.assertNotIn(old, published)
                self.assertIn(old, catalog["retiredIds"])
                self.assertIn(new, published)
                self.assertTrue((dest / f"levels/{old}-v1.json").exists())
                self.assertTrue((dest / f"previews/{old}-v1.png").exists())
                self.assertTrue((dest / f"levels/{new}-v1.json").exists())
            self.assertEqual(published["online-mona-lisa-detailed-90"]["width"],
                             90)

    def test_snowflake_removed_and_lighthouse_replaces_catalog_position(self):
        levels = ROOT / "apps/game/assets/levels"
        animations = ROOT / "apps/game/assets/animations"
        names = json.loads((levels / "catalog.json").read_text("utf8"))
        metadata = json.loads((levels / "metadata.json").read_text("utf8"))
        animation_catalog = json.loads(
            (animations / "catalog.json").read_text("utf8")
        )
        self.assertNotIn("snowflake.json", names)
        self.assertFalse((levels / "snowflake.json").exists())
        self.assertFalse((animations / "snowflake-v1.json").exists())
        self.assertNotIn("snowflake", metadata)
        self.assertNotIn("snowflake", animation_catalog)
        self.assertEqual(names.count("lighthouse.json"), 1)
        self.assertEqual(metadata["lighthouse"]["category"], "objects")
        level = json.loads((levels / "lighthouse.json").read_text("utf8"))
        self.assertEqual(level["levelId"], "lighthouse")
        self.assertEqual((level["width"], level["height"]), (60, 60))
        self.assertEqual(len(level["cells"]), 3600)
        self.assertGreaterEqual(len(set(level["cells"])), 15)
        self.assertLessEqual(len(level["palette"]), 48)
        self.assertEqual(level["checksum"], checksum(level))


if __name__ == "__main__":
    unittest.main()
