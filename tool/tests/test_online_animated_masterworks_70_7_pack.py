"""Validate detailed 70x70 replacements and their animation companions."""
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_animated_masterworks_70_7_pack import (
    PREFIX, SELECTED_SLUGS, animation_frames, create_pack, detailed_art,
)
from online_animated_masterworks_64_15_designs import PICTURES
from online_release import checksum, validated_animation


class DetailedSevenClassicPackTests(unittest.TestCase):
    def test_seven_selected_pictures_have_more_detail_on_70_grid(self):
        self.assertEqual(len(SELECTED_SLUGS), 7)
        by_slug = {scene["slug"]: scene for scene in PICTURES}
        for slug in SELECTED_SLUGS:
            with self.subTest(picture=slug):
                base, art = detailed_art(by_slug[slug])
                self.assertEqual(art.side, 70)
                self.assertEqual(len(art.cells), 4900)
                self.assertGreaterEqual(len(set(art.cells)), 10)
                self.assertGreater(len(art.palette), len(base.palette))
                self.assertLessEqual(len(art.palette), 48)
                self.assertTrue(all(0 <= cell < len(art.palette) for cell in art.cells))
                self.assertNotEqual(
                    tuple(art.cells),
                    tuple(base.cells[y * 64 // 70 * 64 + x * 64 // 70]
                          for y in range(70) for x in range(70)),
                )

    def test_release_has_seven_checksum_bound_levels_and_animations(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "content.zip"
            create_pack(path)
            with zipfile.ZipFile(path) as archive:
                manifest = json.loads(archive.read("catalog.json"))
                self.assertEqual(manifest["schemaVersion"], 1)
                self.assertEqual(len(manifest["pictures"]), 7)
                self.assertEqual(len(archive.namelist()), 23)
                scenarios = json.loads(archive.read("animation-scenarios.json"))
                self.assertEqual(len(scenarios["scenarios"]), 7)
                self.assertEqual(
                    {item["id"] for item in manifest["pictures"]},
                    {PREFIX + slug for slug in SELECTED_SLUGS},
                )
                for item in manifest["pictures"]:
                    with self.subTest(picture=item["id"]):
                        self.assertEqual(item["version"], 1)
                        self.assertEqual(item["category"], "patterns")
                        self.assertEqual((item["width"], item["height"]), (70, 70))
                        self.assertEqual(item["animation"]["frameCount"], 8)
                        stem = item["id"] + "-v1"
                        raw = archive.read("levels/" + stem + ".json")
                        preview = archive.read("previews/" + stem + ".png")
                        animation_bytes = archive.read("animations/" + stem + ".json")
                        level = json.loads(raw)
                        self.assertEqual(len(level["cells"]), 4900)
                        self.assertEqual(level["checksum"], checksum(level))
                        self.assertEqual(item["checksum"], level["checksum"])
                        self.assertEqual(len(raw), item["bytes"])
                        self.assertEqual(preview[:8], b"\x89PNG\r\n\x1a\n")
                        self.assertEqual(struct.unpack(">II", preview[16:24]), (70, 70))
                        self.assertEqual(item["animation"]["bytes"], len(animation_bytes))
                        self.assertEqual(
                            item["animation"]["sha256"],
                            hashlib.sha256(animation_bytes).hexdigest(),
                        )
                        animation = json.loads(animation_bytes)
                        self.assertEqual(animation["levelId"], item["id"])
                        self.assertEqual(animation["levelChecksum"], item["checksum"])
                        self.assertEqual(animation["frameDurationMs"], 180)
                        self.assertEqual(len(animation["frames"]), 8)
                        self.assertEqual(animation["frames"][0], {"changes": []})
                        self.assertEqual(
                            validated_animation(archive, stem, item, level),
                            ("animations/" + stem + ".json", animation_bytes),
                        )


if __name__ == "__main__":
    unittest.main()
