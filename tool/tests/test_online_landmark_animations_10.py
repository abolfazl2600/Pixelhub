"""Ten additive landmark animations preserve existing released painting pixels."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from online_landmark_animations_10 import ANIMATIONS, BATCH_FILENAME, generate_recipes
from online_release import assemble
from online_world_landmarks_25_pack import create_pack
from pixel_animation_recipes import animation, compact
from publish_animation_companions import publish


class LandmarkAnimationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        pack = self.root / "releases" / "pixelhub-content-world-landmarks-50-25-v1" / "content.zip"
        create_pack(pack)
        self.online = self.root / "online"
        assemble(pack.parent.parent, self.online)
        self.batch_dir = self.root / "batches"

    def test_exactly_ten_previously_unanimated_existing_artworks(self):
        catalog = json.loads((self.online / "catalog.json").read_text())
        pictures = {item["id"]: item for item in catalog["pictures"]}
        self.assertEqual(len(ANIMATIONS), 10)
        existing = set()
        for batch in (Path(__file__).resolve().parents[1] / "animation_batches").glob("online-*.json"):
            existing.update(json.loads(batch.read_text()))
        self.assertFalse(set(ANIMATIONS) & existing)
        for ident in ANIMATIONS:
            with self.subTest(ident=ident):
                self.assertIn(ident, pictures)
                self.assertNotIn("animation", pictures[ident])
                self.assertEqual((pictures[ident]["width"], pictures[ident]["height"]), (50, 50))

    def test_publish_adds_valid_looping_companions_but_never_alters_levels(self):
        original = {
            path.relative_to(self.online): path.read_bytes()
            for path in self.online.rglob("*") if path.is_file()
        }
        filename = generate_recipes(self.online, self.batch_dir)
        self.assertEqual(filename.name, BATCH_FILENAME)
        recipes = json.loads(filename.read_text())
        self.assertEqual(set(recipes), set(ANIMATIONS))
        publish(self.online, self.batch_dir)
        catalog = json.loads((self.online / "catalog.json").read_text())
        pictures = {item["id"]: item for item in catalog["pictures"]}

        for path, body in original.items():
            if path != Path("catalog.json"):
                self.assertEqual((self.online / path).read_bytes(), body, str(path))
        for ident, recipe in recipes.items():
            with self.subTest(ident=ident):
                level = json.loads((self.online / f"levels/{ident}-v1.json").read_bytes())
                body = (self.online / f"animations/{ident}-v1.json").read_bytes()
                rendered = json.loads(body)
                metadata = pictures[ident]["animation"]
                self.assertEqual(body, compact(animation(level, recipe)))
                self.assertEqual(hashlib.sha256(body).hexdigest(),
                                 recipe["animationChecksum"])
                self.assertEqual(metadata["sha256"], recipe["animationChecksum"])
                self.assertEqual(metadata["bytes"], len(body))
                self.assertEqual(metadata["frameCount"], 12)
                self.assertEqual(rendered["levelChecksum"], level["checksum"])
                self.assertEqual(rendered["frames"][0]["changes"], [])
                self.assertEqual(rendered["frames"][-1]["changes"], [])
                self.assertGreaterEqual(len({json.dumps(frame["changes"])
                                             for frame in rendered["frames"]}), 3)

    def test_recipes_are_deterministic(self):
        first = generate_recipes(self.online, self.batch_dir).read_bytes()
        second = generate_recipes(self.online, self.root / "second").read_bytes()
        self.assertEqual(first, second)

    def test_refuses_existing_animation_and_tampered_level(self):
        catalog_path = self.online / "catalog.json"
        original = catalog_path.read_bytes()
        catalog = json.loads(original)
        item = next(p for p in catalog["pictures"] if p["id"] in ANIMATIONS)
        item["animation"] = {"sha256": "already released"}
        catalog_path.write_bytes(compact(catalog))
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            generate_recipes(self.online, self.batch_dir)
        catalog_path.write_bytes(original)

        ident = next(iter(ANIMATIONS))
        path = self.online / f"levels/{ident}-v1.json"
        level = json.loads(path.read_text())
        level["cells"][0] = (level["cells"][0] + 1) % len(level["palette"])
        path.write_bytes(compact(level))
        with self.assertRaisesRegex(ValueError, "checksum"):
            generate_recipes(self.online, self.batch_dir)


if __name__ == "__main__":
    unittest.main()
