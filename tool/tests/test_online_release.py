"""Regression coverage for the immutable online-content Release policy.

Run in CI with: python3 -m unittest discover -s tool/tests -p 'test_*.py'
"""
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from online_release import (
    LEGACY_AZADI_ID,
    LEGACY_AZADI_V1,
    LEGACY_AZADI_V2,
    assemble,
    checksum,
    compact,
    png,
    validate_new_pack_manifest,
)


class ImmutableOnlineReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.packs = self.root / "packs"
        self.output = self.root / "online"

    def pack(self, tag, entries):
        """Create valid miniature packs with (ID, levelVersion) entries."""
        path = self.packs / tag / "content.zip"
        path.parent.mkdir(parents=True, exist_ok=True)
        pictures = []
        assets = {}
        for ident, version in entries:
            level = {
                "schemaVersion": 2,
                "levelId": ident,
                "levelVersion": version,
                "titles": {"fa": "نمونه", "en": "Example"},
                "width": 2,
                "height": 2,
                "palette": ["FFFFFFFF", "FF000000"],
                "cells": [0, 1, 1, 0],
            }
            level["checksum"] = checksum(level)
            body = compact(level)
            pictures.append({
                "id": ident,
                "version": version,
                "title": level["titles"]["fa"],
                "titleEn": level["titles"]["en"],
                "category": "patterns",
                "width": 2,
                "height": 2,
                "bytes": len(body),
                "checksum": level["checksum"],
            })
            stem = f"{ident}-v{version}"
            assets[f"levels/{stem}.json"] = body
            assets[f"previews/{stem}.png"] = png(level)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr(
                "catalog.json", compact({"schemaVersion": 1, "pictures": pictures})
            )
            for name, body in assets.items():
                bundle.writestr(name, body)
        return path

    def catalog(self):
        return json.loads((self.output / "catalog.json").read_text("utf-8"))

    def test_animation_sidecar_is_published_and_validated(self):
        from online_animated_sunflower_pack import ID, build

        pack = self.packs / "pixelhub-content-animation-test-v1" / "content.zip"
        pack.parent.mkdir(parents=True, exist_ok=True)
        build(pack)
        assemble(self.packs, self.output)
        entry = next(item for item in self.catalog()["pictures"] if item["id"] == ID)
        self.assertEqual(entry["animation"]["frameCount"], 8)
        animation_path = self.output / f"animations/{ID}-v1.json"
        self.assertTrue(animation_path.exists())
        contents = json.loads(animation_path.read_text("utf-8"))
        self.assertEqual(len(contents["frames"]), 8)

        with zipfile.ZipFile(pack) as archive:
            data = {name: archive.read(name) for name in archive.namelist()}
        catalog = json.loads(data["catalog.json"])
        catalog["pictures"][0]["animation"]["sha256"] = "0" * 64
        data["catalog.json"] = compact(catalog)
        with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, blob in data.items():
                archive.writestr(name, blob)
        with self.assertRaisesRegex(ValueError, "animation digest"):
            assemble(self.packs, self.output)

    def test_distinct_ids_allow_similar_designs_and_retain_both(self):
        original = "online-landmark-tower"
        remake = "online-landmark-tower-redesigned"
        self.pack("pixelhub-content-first-v1", [(original, 1)])
        self.pack("pixelhub-content-second-v1", [(remake, 1)])
        assemble(self.packs, self.output)
        pictures = self.catalog()["pictures"]
        self.assertEqual(self.catalog()["schemaVersion"], 1)
        self.assertEqual({x["id"] for x in pictures}, {original, remake})
        self.assertEqual({x["version"] for x in pictures}, {1})
        self.assertTrue((self.output / f"levels/{original}-v1.json").exists())
        self.assertTrue((self.output / f"levels/{remake}-v1.json").exists())

    def test_duplicate_id_across_packs_same_version_is_rejected(self):
        self.pack("pixelhub-content-one-v1", [("online-cat", 1)])
        self.pack("pixelhub-content-two-v1", [("online-cat", 1)])
        with self.assertRaisesRegex(ValueError, "Duplicate online content ID"):
            assemble(self.packs, self.output)

    def test_duplicate_id_across_packs_higher_version_is_rejected(self):
        self.pack("pixelhub-content-one-v1", [("online-cat", 1)])
        self.pack("pixelhub-content-two-v1", [("online-cat", 2)])
        with self.assertRaisesRegex(ValueError, "Duplicate online content ID"):
            assemble(self.packs, self.output)

    def test_duplicate_id_inside_one_pack_is_rejected(self):
        self.pack("pixelhub-content-one-v1", [
            ("online-cat", 1),
            ("online-cat", 2),
        ])
        with self.assertRaisesRegex(ValueError, "Duplicate online content ID"):
            assemble(self.packs, self.output)

    def test_new_id_cannot_start_at_version_two(self):
        self.pack("pixelhub-content-one-v1", [("online-new-cat", 2)])
        with self.assertRaisesRegex(ValueError, "levelVersion 1"):
            assemble(self.packs, self.output)

    def test_new_pack_validator_rejects_duplicate_and_non_one_version(self):
        with self.assertRaisesRegex(ValueError, "Duplicate online content ID"):
            validate_new_pack_manifest([
                {"id": "online-cat", "version": 1},
                {"id": "online-cat", "version": 1},
            ])
        with self.assertRaisesRegex(ValueError, "levelVersion 1"):
            validate_new_pack_manifest([{"id": "online-cat", "version": 2}])
        validate_new_pack_manifest([
            {"id": "online-cat", "version": 1},
            {"id": "online-cat-remake", "version": 1},
        ])

    def test_new_catalog_categories_are_not_published_to_legacy_clients(self):
        with self.assertRaisesRegex(ValueError, "Unknown legacy online category"):
            validate_new_pack_manifest([
                {"id": "online-new-art", "version": 1,
                 "category": "masterpieces"},
            ])

    def test_archived_azadi_exception_keeps_both_files(self):
        self.pack(LEGACY_AZADI_V1[0], [(LEGACY_AZADI_ID, 1)])
        self.pack(LEGACY_AZADI_V2[0], [(LEGACY_AZADI_ID, 2)])
        assemble(self.packs, self.output)
        entries = self.catalog()["pictures"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], LEGACY_AZADI_ID)
        self.assertEqual(entries[0]["version"], 2)
        for version in (1, 2):
            self.assertTrue(
                (self.output / f"levels/{LEGACY_AZADI_ID}-v{version}.json").exists()
            )
            self.assertTrue(
                (self.output / f"previews/{LEGACY_AZADI_ID}-v{version}.png").exists()
            )

    def test_missing_archived_original_cannot_legitimize_v2(self):
        self.pack(LEGACY_AZADI_V2[0], [(LEGACY_AZADI_ID, 2)])
        with self.assertRaisesRegex(ValueError, "levelVersion 1"):
            assemble(self.packs, self.output)

    def test_other_pack_cannot_reuse_archived_azadi_id(self):
        self.pack("pixelhub-content-new-design-v1", [(LEGACY_AZADI_ID, 1)])
        with self.assertRaisesRegex(ValueError, "Reserved historical online ID"):
            assemble(self.packs, self.output)

    def test_third_azadi_version_cannot_be_published(self):
        self.pack(LEGACY_AZADI_V1[0], [(LEGACY_AZADI_ID, 1)])
        self.pack(LEGACY_AZADI_V2[0], [(LEGACY_AZADI_ID, 2)])
        self.pack("pixelhub-content-new-azadi-v1", [(LEGACY_AZADI_ID, 3)])
        with self.assertRaisesRegex(ValueError, "Reserved historical online ID"):
            assemble(self.packs, self.output)

    def test_real_historical_pack_generators_still_assemble(self):
        """Ensure the shipped, unchanged historic v1/v2 recipes remain usable."""
        from online_iran_architecture_pack import create_pack as architecture_pack
        from online_iran_landmarks_pack import create_pack as landmarks_pack

        first = self.packs / LEGACY_AZADI_V1[0] / "content.zip"
        second = self.packs / LEGACY_AZADI_V2[0] / "content.zip"
        first.parent.mkdir(parents=True, exist_ok=True)
        second.parent.mkdir(parents=True, exist_ok=True)
        landmarks_pack(first)
        architecture_pack(second)
        assemble(self.packs, self.output)
        pictures = self.catalog()["pictures"]
        self.assertEqual(len(pictures), 20)  # 10 + 11, minus historical ID reuse
        self.assertEqual(
            next(p["version"] for p in pictures if p["id"] == LEGACY_AZADI_ID),
            2,
        )


if __name__ == "__main__":
    unittest.main()
