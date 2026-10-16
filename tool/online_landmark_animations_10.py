#!/usr/bin/env python3
"""Attach additive, checksum-bound animations to ten existing world landmarks.

The 50x50 paintings are immutable GitHub Release assets. Only the companion
animation files and catalog animation metadata are generated for Pages; no
level grids, previews, level IDs or saved-progress identities are modified.
"""
import hashlib
import json
from pathlib import Path
import sys

from online_release import checksum, compact
from pixel_animation_recipes import animation


# These IDs belong to the existing 50x50 world-landmark Release. Each chosen
# painting previously had no animation. Keep regions away from important
# architectural silhouettes when moving clouds or shimmering the water.
ANIMATIONS = {
    "online-world-eiffel-tower-50": {
        "motion": "float", "region": [0.04, 0.02, 0.96, 0.24],
        "durationMs": 185,
    },
    "online-world-taj-mahal-50": {
        "motion": "glimmer", "region": [0.13, 0.23, 0.88, 0.83],
        "durationMs": 170,
    },
    "online-world-big-ben-50": {
        "motion": "float", "region": [0.04, 0.02, 0.96, 0.20],
        "durationMs": 185,
    },
    "online-world-statue-liberty-50": {
        "motion": "glimmer", "region": [0.19, 0.12, 0.82, 0.88],
        "durationMs": 170,
    },
    "online-world-sydney-opera-50": {
        "motion": "wave", "region": [0.02, 0.79, 0.98, 0.98],
        "durationMs": 180,
    },
    "online-world-golden-gate-50": {
        "motion": "wave", "region": [0.02, 0.77, 0.98, 0.98],
        "durationMs": 180,
    },
    "online-world-giza-pyramids-50": {
        "motion": "glimmer", "region": [0.13, 0.28, 0.88, 0.84],
        "durationMs": 175,
    },
    "online-world-neuschwanstein-50": {
        "motion": "float", "region": [0.04, 0.02, 0.96, 0.19],
        "durationMs": 185,
    },
    "online-world-saint-basils-50": {
        "motion": "glimmer", "region": [0.13, 0.15, 0.88, 0.80],
        "durationMs": 175,
    },
    "online-world-marina-bay-sands-50": {
        "motion": "wave", "region": [0.02, 0.79, 0.98, 0.98],
        "durationMs": 180,
    },
}

BATCH_FILENAME = "online-22.json"


def generate_recipes(online_dir, batch_dir):
    """Build verified recipes only for these ten still-unanimated pictures."""
    online_dir = Path(online_dir)
    batch_dir = Path(batch_dir)
    catalog = json.loads((online_dir / "catalog.json").read_text(encoding="utf-8"))
    pictures = {item["id"]: item for item in catalog["pictures"]}
    if len(ANIMATIONS) != 10:
        raise ValueError("Exactly ten landmark animations are required")

    recipes = {}
    for ident, design in ANIMATIONS.items():
        item = pictures.get(ident)
        if item is None:
            raise ValueError(f"Landmark is absent from the online catalog: {ident}")
        if "animation" in item:
            raise ValueError(f"Refusing to overwrite an existing animation: {ident}")
        if item["version"] != 1 or (item["width"], item["height"]) != (50, 50):
            raise ValueError(f"Unexpected immutable landmark version or size: {ident}")

        level_path = online_dir / "levels" / f"{ident}-v1.json"
        level = json.loads(level_path.read_text(encoding="utf-8"))
        if (level["levelId"] != ident or level["levelVersion"] != 1 or
                checksum(level) != item["checksum"] or
                level["checksum"] != item["checksum"]):
            raise ValueError(f"Painting checksum does not match published catalog: {ident}")

        recipe = {**design, "version": 1, "checksum": item["checksum"]}
        rendered = animation(level, recipe)
        frames = rendered["frames"]
        if (len(frames) != 12 or frames[0]["changes"] or frames[-1]["changes"] or
                len({json.dumps(f["changes"]) for f in frames}) < 3):
            raise ValueError(f"Animation must visibly change and return to still: {ident}")
        recipe["animationChecksum"] = hashlib.sha256(compact(rendered)).hexdigest()
        recipes[ident] = recipe

    batch_dir.mkdir(parents=True, exist_ok=True)
    target = batch_dir / BATCH_FILENAME
    target.write_text(json.dumps(recipes, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"Prepared {len(recipes)} additive world-landmark animations: {target}")
    return target


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: online_landmark_animations_10.py <online-dir> <batch-dir>")
    generate_recipes(sys.argv[1], sys.argv[2])
