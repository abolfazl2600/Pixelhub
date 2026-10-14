"""Regression tests for the 20 immutable 12x12 online animation levels."""
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_animated_12_pack import (
    ARTWORKS, PREFIX, animation_frames, animated_cells, build, make_level,
)
from online_release import assemble, checksum


class AnimatedMiniTwelvePackTests(unittest.TestCase):
    def test_twenty_distinct_exact_12x12_color_by_number_levels(self):
        self.assertEqual(len(ARTWORKS), 20)
        ids, grids = set(), set()
        for item in ARTWORKS:
            level = make_level(item)
            self.assertEqual((level["width"], level["height"]), (12, 12))
            self.assertEqual(len(level["cells"]), 144)
            self.assertEqual(level["levelVersion"], 1)
            self.assertEqual(level["checksum"], checksum(level))
            self.assertEqual(len(level["palette"]), 6)
            self.assertTrue(all(0 <= c < 6 for c in level["cells"]))
            self.assertIn(item["category"], {"objects", "animals", "nature", "space"})
            self.assertTrue(level["titles"]["fa"] and level["titles"]["en"])
            self.assertTrue(level["levelId"].startswith(PREFIX))
            self.assertNotIn(level["levelId"], ids)
            self.assertNotIn(tuple(level["cells"]), grids)
            ids.add(level["levelId"])
            grids.add(tuple(level["cells"]))

    def test_every_picture_has_distinct_looping_animation_without_changing_level(self):
        for item in ARTWORKS:
            level = make_level(item)
            original_cells = level["cells"][:]
            original_checksum = level["checksum"]
            frames = animation_frames(level, item["slug"])
            self.assertEqual(len(frames), 8)
            self.assertEqual(frames[0], {"changes": []})
            poses = []
            for phase, frame in enumerate(frames):
                pose = original_cells[:]
                positions = set()
                for position, color in frame["changes"]:
                    self.assertTrue(0 <= position < 144)
                    self.assertTrue(0 <= color < 6)
                    self.assertNotIn(position, positions)
                    positions.add(position)
                    pose[position] = color
                self.assertEqual(pose, animated_cells(level, item["slug"], phase))
                poses.append(tuple(pose))
            self.assertGreaterEqual(len(set(poses)), 3, item["slug"])
            self.assertEqual(level["cells"], original_cells)
            self.assertEqual(level["checksum"], original_checksum)

    def test_release_zip_and_assembled_catalog_include_all_sidecars(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            pack = root / "pixelhub-content-animated-mini-12-20-v1" / "content.zip"
            build(pack)
            with zipfile.ZipFile(pack) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(len(catalog["pictures"]), 20)
                scenarios = json.loads(archive.read("animation-scenarios.json"))
                self.assertEqual(len(scenarios["scenarios"]), 20)
                for entry in catalog["pictures"]:
                    stem = entry["id"] + "-v1"
                    level_blob = archive.read("levels/" + stem + ".json")
                    preview = archive.read("previews/" + stem + ".png")
                    animation_blob = archive.read("animations/" + stem + ".json")
                    level = json.loads(level_blob)
                    animation = json.loads(animation_blob)
                    self.assertEqual(entry["bytes"], len(level_blob))
                    self.assertEqual(entry["checksum"], level["checksum"])
                    self.assertEqual((entry["width"], entry["height"]), (12, 12))
                    self.assertEqual(preview[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual(struct.unpack(">II", preview[16:24]), (12, 12))
                    self.assertEqual(entry["animation"]["bytes"], len(animation_blob))
                    self.assertEqual(entry["animation"]["sha256"],
                                     hashlib.sha256(animation_blob).hexdigest())
                    self.assertEqual(entry["animation"]["frameCount"], 8)
                    self.assertEqual(animation["levelChecksum"], level["checksum"])
                    self.assertEqual(animation["levelId"], entry["id"])
                    self.assertEqual(animation["levelVersion"], 1)
                    self.assertEqual(animation["frameDurationMs"], 180)
                    self.assertEqual(len(animation["frames"]), 8)
            output = root / "assembled"
            assemble(root, output)
            published = json.loads((output / "catalog.json").read_text("utf-8"))
            mine = [entry for entry in published["pictures"]
                    if entry["id"].startswith(PREFIX)]
            self.assertEqual(len(mine), 20)
            self.assertTrue(all(entry.get("animation", {}).get("frameCount") == 8
                                for entry in mine))


if __name__ == "__main__":
    unittest.main()
