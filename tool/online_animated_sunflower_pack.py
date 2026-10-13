#!/usr/bin/env python3
"""Build a new immutable animated sunflower for the optional online catalog.

The downloadable animation is a sparse, validated sidecar. The original
sunflower picture in the APK is unchanged; this new online level has its own ID.
"""
import hashlib
import json
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ID = "online-dancing-sunflower"


def animated_frames(level):
    """Eight different/time-repeated poses: flower head sways in the wind."""
    side = level["width"]
    original = level["cells"]
    frames = []
    for index, shift in enumerate([0, -1, -1, 0, 1, 1, 0, 0]):
        cells = original[:]
        for y in range(2, 9):
            for x in range(1, 15):
                if original[y * side + x]:
                    cells[y * side + x] = 0
        for y in range(2, 9):
            for x in range(2, 14):
                color = original[y * side + x]
                if color:
                    cells[y * side + x + shift] = color
        if index % 4 and cells[(10 + index % 2) * side + 2] == 0:
            cells[(10 + index % 2) * side + 2] = 5
        frames.append({
            "changes": [
                [at, color]
                for at, color in enumerate(cells)
                if color != original[at]
            ]
        })
    return frames


def build(destination):
    base = json.loads(
        (ROOT / "apps/game/assets/levels/sunflower-v2.json").read_text("utf-8")
    )
    level = {
        "schemaVersion": 2,
        "levelId": ID,
        "levelVersion": 1,
        "titles": {"fa": "آفتابگردان رقصان", "en": "Dancing Sunflower"},
        "width": base["width"],
        "height": base["height"],
        "palette": base["palette"],
        "cells": base["cells"],
    }
    level["checksum"] = checksum(level)
    animation = {
        "schemaVersion": 1,
        "levelId": ID,
        "levelVersion": 1,
        "levelChecksum": level["checksum"],
        "frameDurationMs": 180,
        "frames": animated_frames(level),
    }
    animation_blob = compact(animation)
    level_blob = compact(level)
    item = {
        "id": ID,
        "version": 1,
        "title": level["titles"]["fa"],
        "titleEn": level["titles"]["en"],
        "category": "nature",
        "width": level["width"],
        "height": level["height"],
        "bytes": len(level_blob),
        "checksum": level["checksum"],
        "animation": {
            "bytes": len(animation_blob),
            "sha256": hashlib.sha256(animation_blob).hexdigest(),
            "frameCount": len(animation["frames"]),
        },
    }
    validate_new_pack_manifest([item])
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    stem = f"{ID}-v1"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "catalog.json", compact({"schemaVersion": 1, "pictures": [item]})
        )
        archive.writestr(f"levels/{stem}.json", level_blob)
        archive.writestr(f"previews/{stem}.png", png(level))
        archive.writestr(f"animations/{stem}.json", animation_blob)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_animated_sunflower_pack.py <output.zip>")
    build(sys.argv[1])
