"""Validate 15 independently designed 64x64 classic paintings and sidecars."""
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))

from online_animated_masterworks_64_15_designs import PICTURES
from online_animated_masterworks_64_15_pack import (
    PREFIX, animation_frames, animation_pose, create_pack, draw_scene,
)
from online_release import assemble, checksum, validated_animation
from online_animated_masterworks_70_7_pack import PREFIX as DETAILED_PREFIX, create_pack as detailed_classics


class AnimatedFifteenClassicPackTests(unittest.TestCase):
    def test_fifteen_distinct_64_by_64_paintings_and_animations(self):
        self.assertEqual(len(PICTURES),15)
        ids, pictures = set(), set()
        for scene in PICTURES:
            slug = scene["slug"]
            ident = PREFIX + slug
            self.assertNotIn(ident,ids)
            ids.add(ident)
            self.assertTrue(scene["fa"] and scene["en"] and scene["artist"])
            self.assertTrue(scene["motionFa"] and scene["motionEn"])
            art = draw_scene(scene)
            self.assertEqual(art.side,64)
            self.assertEqual(len(art.cells),4096)
            self.assertGreaterEqual(len(set(art.cells)),5,slug)
            self.assertGreaterEqual(sum(x != 0 for x in art.cells),800,slug)
            self.assertLessEqual(len(art.palette),48)
            self.assertTrue(all(isinstance(x,int) and 0 <= x < len(art.palette)
                                for x in art.cells))
            self.assertNotIn(tuple(art.cells),pictures)
            pictures.add(tuple(art.cells))
            original = art.cells[:]
            frames = animation_frames(art,slug)
            self.assertEqual(len(frames),8)
            self.assertEqual(frames[0],{"changes":[]})
            poses = []
            for phase,frame in enumerate(frames):
                self.assertLess(len(frame["changes"]),450,slug)
                index_set = set()
                pose = original[:]
                for position,color in frame["changes"]:
                    self.assertNotIn(position,index_set)
                    index_set.add(position)
                    self.assertGreaterEqual(position,0)
                    self.assertLess(position,4096)
                    self.assertTrue(0 <= color < len(art.palette))
                    pose[position] = color
                self.assertEqual(pose,animation_pose(art,slug,phase))
                poses.append(tuple(pose))
            self.assertGreaterEqual(len(set(poses)),3,slug)
            self.assertEqual(art.cells,original)

    def test_release_can_be_assembled_with_all_animated_pictures(self):
        with tempfile.TemporaryDirectory() as work:
            root = pathlib.Path(work)
            zip_path = root / "pixelhub-content-animated-classics-64-15-v1" / "content.zip"
            create_pack(zip_path)
            replacement_zip = root / "pixelhub-content-animated-classics-70-7-v1" / "content.zip"
            detailed_classics(replacement_zip)
            with zipfile.ZipFile(zip_path) as archive:
                manifest = json.loads(archive.read("catalog.json"))
                self.assertEqual(manifest["schemaVersion"],1)
                self.assertEqual(len(manifest["pictures"]),15)
                scenarios = json.loads(archive.read("animation-scenarios.json"))
                self.assertEqual(len(scenarios["scenarios"]),15)
                for entry in manifest["pictures"]:
                    self.assertTrue(entry["id"].startswith(PREFIX))
                    self.assertEqual(entry["version"],1)
                    self.assertEqual(entry["category"],"patterns")
                    self.assertEqual((entry["width"],entry["height"]),(64,64))
                    self.assertEqual(entry["animation"]["frameCount"],8)
                    stem = entry["id"]+"-v1"
                    raw = archive.read("levels/"+stem+".json")
                    preview = archive.read("previews/"+stem+".png")
                    anim = archive.read("animations/"+stem+".json")
                    level = json.loads(raw)
                    self.assertEqual(len(level["cells"]),4096)
                    self.assertEqual(level["checksum"],checksum(level))
                    self.assertEqual(entry["checksum"],level["checksum"])
                    self.assertEqual(entry["bytes"],len(raw))
                    self.assertEqual(preview[:8],b"\x89PNG\r\n\x1a\n")
                    self.assertEqual(struct.unpack(">II",preview[16:24]),(64,64))
                    self.assertEqual(entry["animation"]["bytes"],len(anim))
                    self.assertEqual(entry["animation"]["sha256"],
                                     hashlib.sha256(anim).hexdigest())
                    parsed = json.loads(anim)
                    self.assertEqual(parsed["levelId"],entry["id"])
                    self.assertEqual(parsed["levelVersion"],1)
                    self.assertEqual(parsed["levelChecksum"],entry["checksum"])
                    self.assertEqual(parsed["frameDurationMs"],180)
                    self.assertEqual(len(parsed["frames"]),8)
                    self.assertEqual(validated_animation(archive,stem,entry,level),
                                     ("animations/"+stem+".json",anim))
            output = root / "published"
            assemble(root,output)
            catalog = json.loads((output/"catalog.json").read_text(encoding="utf8"))
            online = [p for p in catalog["pictures"] if p["id"].startswith(PREFIX)]
            detailed = [p for p in catalog["pictures"] if p["id"].startswith(DETAILED_PREFIX)]
            self.assertEqual(len(online), 8)
            self.assertEqual(len(detailed), 7)
            self.assertTrue(all(p["animation"]["frameCount"] == 8 for p in online + detailed))
            for entry in online + detailed:
                stem = entry["id"]+"-v1"
                self.assertTrue((output/"previews"/(stem+".png")).exists())
                self.assertTrue((output/"animations"/(stem+".json")).exists())


if __name__ == "__main__":
    unittest.main()
