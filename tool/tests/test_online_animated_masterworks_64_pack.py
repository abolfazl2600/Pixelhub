"""End-to-end checks for ten distinct animated 64x64 online masterworks."""
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_animated_masterworks_64_pack import (
    PICTURES, PREFIX, animation_frames, create_pack, motion_frame,
)
from online_release import assemble, checksum, validated_animation
from online_classics_detailed_96_5_pack import PREFIX as DETAILED_PREFIX, create_pack as detailed_five_classics


class AnimatedClassicMasterworks64Tests(unittest.TestCase):
    def test_all_ten_original_grids_are_distinct_and_valid(self):
        self.assertEqual(len(PICTURES), 10)
        ids, images = set(), set()
        for slug, fa, en, artist, painter, motion_en, motion_fa in PICTURES:
            art = painter()
            ident = PREFIX + slug
            self.assertNotIn(ident, ids)
            ids.add(ident)
            self.assertEqual(art.side, 64)
            self.assertEqual(len(art.cells), 4096)
            self.assertLessEqual(len(art.palette), 48)
            self.assertGreaterEqual(len(set(art.cells)), 6)
            self.assertTrue(all(type(v) is int and 0 <= v < len(art.palette)
                                for v in art.cells))
            self.assertTrue(all(len(c) == 8 for c in art.palette))
            self.assertNotIn(tuple(art.cells), images)
            images.add(tuple(art.cells))
            self.assertTrue(all((fa, en, artist, motion_en, motion_fa)))
            frames = animation_frames(art, slug)
            self.assertEqual(len(frames), 8)
            self.assertEqual(frames[0]["changes"], [])
            poses = []
            base = art.cells[:]
            for phase, frame in enumerate(frames):
                self.assertLess(len(frame["changes"]), 400, slug)
                seen = set()
                pose = base[:]
                for index, color in frame["changes"]:
                    self.assertTrue(0 <= index < 4096)
                    self.assertTrue(0 <= color < len(art.palette))
                    self.assertNotIn(index, seen)
                    seen.add(index)
                    pose[index] = color
                self.assertEqual(pose, motion_frame(art, slug, phase))
                poses.append(tuple(pose))
            self.assertGreaterEqual(len(set(poses)), 3, slug)
            self.assertEqual(base, art.cells, "animation must not change numbered level")

    def test_pack_has_ten_checksum_bound_animations_and_valid_pngs(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = pathlib.Path(tmp)
            pack = parent / "pixelhub-content-animated-masterworks-64-10-v1" / "content.zip"
            create_pack(pack)
            with zipfile.ZipFile(pack) as archive:
                catalog = json.loads(archive.read("catalog.json"))
                self.assertEqual(catalog["schemaVersion"], 1)
                self.assertEqual(len(catalog["pictures"]), 10)
                scenarios = json.loads(archive.read("animation-scenarios.json"))
                self.assertEqual(len(scenarios["scenarios"]), 10)
                for item in catalog["pictures"]:
                    self.assertEqual((item["width"], item["height"]), (64, 64))
                    self.assertEqual(item["version"], 1)
                    self.assertEqual(item["category"], "patterns")
                    self.assertTrue(item["id"].startswith(PREFIX))
                    stem = item["id"] + "-v1"
                    raw_level = archive.read("levels/" + stem + ".json")
                    level = json.loads(raw_level)
                    self.assertEqual(item["bytes"], len(raw_level))
                    self.assertEqual(level["checksum"], checksum(level))
                    self.assertEqual(item["checksum"], level["checksum"])
                    self.assertEqual(len(level["cells"]), 4096)
                    preview = archive.read("previews/" + stem + ".png")
                    self.assertEqual(preview[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual(struct.unpack(">II", preview[16:24]), (64,64))
                    anim_blob = archive.read("animations/" + stem + ".json")
                    anim = json.loads(anim_blob)
                    self.assertEqual(anim["levelChecksum"], level["checksum"])
                    self.assertEqual(anim["levelId"], level["levelId"])
                    self.assertEqual(anim["levelVersion"], 1)
                    self.assertEqual(anim["frameDurationMs"], 180)
                    self.assertEqual(len(anim["frames"]), 8)
                    self.assertEqual(item["animation"]["bytes"], len(anim_blob))
                    self.assertEqual(item["animation"]["frameCount"], 8)
                    self.assertEqual(item["animation"]["sha256"],
                                     hashlib.sha256(anim_blob).hexdigest())
                    self.assertEqual(validated_animation(archive, stem, item, level),
                                     ("animations/" + stem + ".json", anim_blob))
            detailed_five_classics(
                parent / "pixelhub-content-detailed-classics-96-5-v1" / "content.zip"
            )
            output = parent / "pages"
            assemble(parent, output)
            combined = json.loads((output / "catalog.json").read_bytes())
            ours = [entry for entry in combined["pictures"]
                    if entry["id"].startswith(PREFIX)]
            self.assertEqual(len(ours), 8)  # Mother and Parasol are superseded.
            detailed = [entry for entry in combined["pictures"]
                        if entry["id"].startswith(DETAILED_PREFIX)]
            self.assertEqual(len(detailed), 5)
            self.assertTrue(all(entry.get("animation", {}).get("frameCount") == 8
                                for entry in ours))
            self.assertEqual(sum("animation" in entry for entry in detailed), 4)
            for item in ours:
                stem = item["id"] + "-v1"
                self.assertTrue((output / "animations" / (stem+".json")).is_file())


if __name__ == "__main__":
    unittest.main()
