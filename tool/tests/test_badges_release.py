"""Validate that remote achievement assets are complete and immutable."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
BADGES = ROOT / "badge_content"


class BadgeContentTests(unittest.TestCase):
    def test_manifest_and_pixel_png_checksums(self):
        manifest = json.loads((BADGES / "catalog.json").read_text("utf-8"))
        self.assertEqual(manifest["version"], 1)
        entries = manifest["badges"]
        self.assertGreaterEqual(len(entries), 5)
        self.assertEqual(len({entry["id"] for entry in entries}), len(entries))
        self.assertEqual(entries[0]["id"], "animal_first")
        self.assertEqual(entries[0]["category"], "animals")
        self.assertEqual(entries[0]["required"], 1)
        self.assertTrue(any(e["category"] == "animals" and e["required"] == 5 for e in entries))
        for entry in entries:
            self.assertRegex(entry["id"], r"^[a-z][a-z0-9_]+$")
            self.assertEqual(entry["image"], f"images/{entry['id']}.png")
            self.assertRegex(entry["sha256"], r"^[a-f0-9]{64}$")
            content = (BADGES / entry["image"]).read_bytes()
            self.assertTrue(content.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(len(content), entry["bytes"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])


if __name__ == "__main__":
    unittest.main()
