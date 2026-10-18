"""Five detailed 96x96 classic paintings match the published reference recipes."""
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from online_classics_detailed_96_5_pack import (
    DRAWINGS, PREFIX, SIDE, WORKS, animation_frames, create_pack, draw_scene,
)
from online_release import checksum, validated_animation


class DetailedClassic96Tests(unittest.TestCase):
    def test_reproducible_96x96_hand_drawn_pixel_art(self):
        self.assertEqual(len(WORKS), 5)
        self.assertEqual(len(DRAWINGS), 5)
        for slug, fa, en, artist, *_ in WORKS:
            with self.subTest(painting=slug):
                art = draw_scene(slug)
                self.assertEqual(art.side, 96)
                self.assertEqual(len(art.cells), SIDE ** 2)
                self.assertGreaterEqual(len(set(art.cells)), 15)
                self.assertGreaterEqual(len(set(art.palette)), 15)
                self.assertLessEqual(len(art.palette), 48)
                self.assertTrue(all(0 <= pixel < len(art.palette)
                                    for pixel in art.cells))
                self.assertEqual(art.cells, draw_scene(slug).cells)
                self.assertTrue(fa and en and artist)
                self.assertGreaterEqual(len(DRAWINGS[slug].splitlines()), 45)

    def test_pack_schemas_dimensions_animation_hashes_and_pixel_previews(self):
        with tempfile.TemporaryDirectory() as temp:
            filename = pathlib.Path(temp) / "content.zip"
            create_pack(filename)
            with zipfile.ZipFile(filename) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                items = catalog["pictures"]
                self.assertEqual(len(items), 5)
                self.assertEqual({p["id"] for p in items},
                                 {PREFIX + w[0] for w in WORKS})
                scenarios = json.loads(archive.read("animation-scenarios.json"))
                self.assertEqual(len(scenarios["scenarios"]), 4)
                self.assertEqual(len(archive.namelist()), 16)
                for entry in items:
                    with self.subTest(picture=entry["id"]):
                        self.assertEqual((entry["width"], entry["height"]),
                                         (96, 96))
                        self.assertEqual(entry["version"], 1)
                        self.assertEqual(entry["category"], "patterns")
                        stem = entry["id"] + "-v1"
                        data = archive.read("levels/" + stem + ".json")
                        level = json.loads(data)
                        self.assertEqual(len(level["cells"]), 9216)
                        self.assertEqual(level["checksum"], checksum(level))
                        self.assertEqual(entry["checksum"], level["checksum"])
                        self.assertEqual(entry["bytes"], len(data))
                        self.assertLess(len(data), 262144)
                        preview = archive.read("previews/" + stem + ".png")
                        self.assertEqual(preview[:8], b"\x89PNG\r\n\x1a\n")
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (96, 96))
                        if entry["id"].endswith("girl-pearl"):
                            self.assertNotIn("animation", entry)
                            self.assertNotIn("animations/" + stem + ".json",
                                             archive.namelist())
                        else:
                            raw = archive.read("animations/" + stem + ".json")
                            animation = json.loads(raw)
                            self.assertEqual(entry["animation"]["frameCount"], 8)
                            self.assertEqual(entry["animation"]["bytes"], len(raw))
                            self.assertEqual(entry["animation"]["sha256"],
                                             hashlib.sha256(raw).hexdigest())
                            self.assertEqual(animation["levelChecksum"],
                                             level["checksum"])
                            self.assertEqual(animation["frames"][0], {"changes": []})
                            self.assertGreater(len({tuple(map(tuple, frame["changes"]))
                                                    for frame in animation["frames"]}), 2)
                            self.assertEqual(
                                validated_animation(archive, stem, entry, level),
                                ("animations/" + stem + ".json", raw),
                            )


if __name__ == "__main__":
    unittest.main()
