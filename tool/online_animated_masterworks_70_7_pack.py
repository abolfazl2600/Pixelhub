#!/usr/bin/env python3
"""Detailed 70x70 redraws for seven animated classic-painting levels.

The existing 64x64 recipes remain the recognizable base composition. These
replacements are re-rasterized to a 70x70 grid and receive additional authored
pixel-level accents, textile folds, masonry, foliage, facial features and water
details. All previews, level JSON and animation companions are generated in CI
and distributed as immutable GitHub Release assets, never bundled in the APK.
"""
import hashlib
import pathlib
import sys
import zipfile

from online_animated_masterworks_64_15_designs import PICTURES
from online_animated_masterworks_64_15_pack import animation_pose, draw_scene
from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 70
PREFIX = "online-classic-animated70-"
OLD_PREFIX = "online-classic-animated64-"
FRAME_DURATION_MS = 180
SELECTED_SLUGS = (
    "luncheon-grass",
    "olympia",
    "lady-shalott",
    "ophelia",
    "hunters-snow",
    "tower-babel",
    "primavera",
)

# Four extra shades per work are used for fine linework and material accents.
DETAIL_COLORS = {
    "primavera": ["FF3B2D25", "FFF8E8CA", "FFB7D79A", "FFF0A8B7"],
    "tower-babel": ["FF55443B", "FFEAD7B6", "FFC66D57", "FF91A99A"],
    "hunters-snow": ["FFF4C86A", "FF2B3432", "FFFAFBF4", "FF829B9E"],
    "ophelia": ["FF241F1A", "FFB4D7A0", "FFFFF5DE", "FFD8899D"],
    "lady-shalott": ["FF8D3534", "FFFFE7A2", "FF3B2C24", "FFB7D8D2"],
    "olympia": ["FFB97969", "FFFFF6E9", "FF81977C", "FF171716"],
    "luncheon-grass": ["FF1C3028", "FFFFF0D2", "FF9BBF7C", "FFD4B58B"],
}


def project(value):
    """Map original recipe coordinates [0, 63] onto the 70-cell canvas."""
    return max(0, min(SIDE - 1, round(float(value) * (SIDE - 1) / 63)))


def dot(s, x, y, color):
    s.dot(project(x), project(y), color)


def line(s, x0, y0, x1, y1, color, radius=0.6):
    s.line(project(x0), project(y0), project(x1), project(y1),
           color, radius=max(0.55, radius * SIDE / 64))


def rect(s, x0, y0, x1, y1, color):
    s.rect(project(x0), project(y0), project(x1), project(y1), color)


def ellipse(s, x, y, rx, ry, color):
    s.ellipse(project(x), project(y),
              max(0.7, rx * SIDE / 64), max(0.7, ry * SIDE / 64), color)


def polygon(s, points, color):
    s.polygon([(project(x), project(y)) for x, y in points], color)


def upsample(base, palette):
    """Nearest-neighbour resampling that preserves the original pixel palette."""
    result = Sprite(SIDE, palette)
    for y in range(SIDE):
        source_y = min(63, int((y + 0.5) * 64 / SIDE))
        for x in range(SIDE):
            source_x = min(63, int((x + 0.5) * 64 / SIDE))
            result.cells[y * SIDE + x] = base.cells[source_y * 64 + source_x]
    return result


def add_details(s, slug, palette_length):
    dark, light, accent, soft = range(palette_length, palette_length + 4)

    if slug == "primavera":
        # Foliage veins, bark grain, embroidered gowns and individual faces.
        for a, b, c, d in [
            (5, 18, 12, 11), (10, 13, 15, 9), (43, 15, 51, 10),
            (48, 11, 55, 15), (54, 18, 60, 13), (8, 22, 14, 18),
        ]:
            line(s, a, b, c, d, dark, 0.7)
        for y in range(3, 29, 4):
            line(s, 21, y, 23, y + 2, dark, 0.65)
            dot(s, 20, y + 1, accent)
        for x, y in [(31, 25), (13, 31), (50, 28), (7, 32),
                     (58, 32), (23, 33), (40, 33)]:
            dot(s, x - 1, y, 1)
            dot(s, x + 1, y, 1)
            dot(s, x, y + 2, dark)
            line(s, x - 2, y - 2, x + 1, y - 3, dark, 0.6)
        for a, b, c, d in [
            (29, 35, 28, 42), (32, 36, 34, 43), (13, 35, 12, 40),
            (50, 33, 51, 39), (22, 37, 21, 42), (40, 37, 41, 42),
        ]:
            line(s, a, b, c, d, light, 0.65)
        for x, y in [(26, 39), (30, 41), (34, 39), (47, 39),
                     (10, 43), (56, 43), (18, 49), (43, 50)]:
            dot(s, x, y, soft)
            dot(s, x + 1, y - 1, accent)
        for x, y in [(4, 57), (15, 60), (25, 56), (38, 58), (51, 61)]:
            line(s, x, y, x + 2, y - 2, accent, 0.65)
            dot(s, x + 3, y - 2, light)

    elif slug == "tower-babel":
        # Courses of stone, brighter masonry edges, scaffolding and lit windows.
        courses = [
            (54, 10, 55), (49, 13, 53), (44, 16, 52), (39, 19, 50),
            (34, 22, 48), (29, 25, 46), (24, 28, 44), (19, 31, 42),
            (15, 34, 40),
        ]
        for y, x0, x1 in courses:
            line(s, x0, y, x1, min(63, y + 1), dark, 0.65)
            for x in range(x0 + 2, x1 - 1, 7):
                dot(s, x, y - 1, light)
        for x, y in [
            (15, 51), (21, 48), (27, 45), (34, 42), (40, 38),
            (44, 34), (38, 29), (35, 25), (32, 21), (29, 17),
        ]:
            rect(s, x, y, x + 1, y + 2, 7)
            dot(s, x, y + 1, accent)
        for x, y in [(18, 50), (25, 46), (32, 43), (38, 39),
                     (42, 35), (39, 30), (36, 25), (32, 20)]:
            line(s, x, y, x + 2, y, light, 0.55)
        # Timber scaffold across the lower tiers.
        line(s, 8, 55, 24, 43, dark, 0.8)
        line(s, 14, 57, 31, 43, dark, 0.8)
        line(s, 8, 51, 25, 52, accent, 0.65)
        line(s, 17, 45, 37, 46, dark, 0.7)
        for x, y in [(7, 56), (11, 55), (56, 57), (58, 55)]:
            dot(s, x, y, accent)
            dot(s, x + 1, y - 1, light)
        for x, y in [(4, 10), (8, 13), (12, 9), (55, 11), (59, 16)]:
            dot(s, x, y, light)
            dot(s, x + 1, y, 1)

    elif slug == "hunters-snow":
        # Tree branchlets, bark, cabin windows, skates and snow crystals.
        for a, b, c, d in [
            (3, 17, 9, 12), (5, 25, 12, 19), (8, 32, 14, 27),
            (13, 17, 19, 13), (12, 25, 19, 21), (13, 34, 20, 29),
        ]:
            line(s, a, b, c, d, dark, 0.75)
        for y in range(5, 48, 6):
            line(s, 3, y, 5, y + 3, 5, 0.7)
            dot(s, 4, y + 1, accent)
        # Windows on the distant cottages; roof snow remains crisp.
        for x, y in [(41, 37), (45, 37), (52, 35), (56, 35), (35, 39)]:
            rect(s, x, y, x + 1, y + 2, 3)
            dot(s, x, y, light)
        for x, y in [(10, 48), (18, 48), (26, 52), (45, 54), (52, 52)]:
            dot(s, x - 1, y, 4)
            dot(s, x + 1, y, 4)
            dot(s, x, y + 2, 5)
        for a, b, c, d in [
            (30, 56, 37, 55), (39, 58, 47, 57), (48, 55, 57, 54),
            (26, 61, 35, 60), (4, 61, 12, 60),
        ]:
            line(s, a, b, c, d, accent, 0.7)
        for x, y in [(28, 12), (36, 18), (47, 12), (58, 24),
                     (30, 31), (61, 43), (24, 8), (50, 28)]:
            dot(s, x, y, light)
            dot(s, x - 1, y, 8)
            dot(s, x + 1, y, 8)

    elif slug == "ophelia":
        # Hair strands, face features, gown folds, lily pads and water glints.
        for a, b, c, d in [
            (13, 43, 17, 47), (15, 42, 20, 46), (18, 43, 21, 48),
            (20, 44, 23, 47), (23, 47, 28, 50), (26, 49, 30, 54),
        ]:
            line(s, a, b, c, d, dark, 0.7)
        dot(s, 16, 45, 1)
        dot(s, 18, 45, 1)
        dot(s, 17, 47, soft)
        line(s, 20, 49, 24, 51, light, 0.7)
        line(s, 24, 52, 28, 56, light, 0.7)
        line(s, 31, 49, 35, 54, dark, 0.7)
        line(s, 36, 49, 40, 53, light, 0.7)
        for x, y in [(7, 43), (57, 42), (9, 58), (52, 57), (34, 59)]:
            ellipse(s, x, y, 2.3, 1.1, accent)
            dot(s, x, y, soft)
            line(s, x - 2, y + 1, x + 2, y + 1, dark, 0.55)
        for a, b, c, d in [
            (0, 48, 11, 47), (22, 50, 30, 49), (42, 52, 53, 51),
            (5, 55, 15, 54), (28, 57, 38, 56), (47, 60, 61, 59),
        ]:
            line(s, a, b, c, d, light, 0.6)
        for x, y in [(4, 50), (14, 59), (45, 56), (60, 47)]:
            dot(s, x, y, soft)
            dot(s, x + 1, y, accent)

    elif slug == "lady-shalott":
        # Face, braided hair, embroidered red bodice, boat planks and lanterns.
        dot(s, 28, 30, 13)
        dot(s, 30, 30, 13)
        dot(s, 29, 32, 12)
        line(s, 26, 27, 30, 26, dark, 0.7)
        line(s, 25, 31, 24, 35, dark, 0.65)
        line(s, 33, 31, 35, 35, dark, 0.65)
        line(s, 25, 39, 29, 43, light, 0.7)
        line(s, 31, 40, 35, 43, light, 0.7)
        line(s, 24, 44, 28, 46, dark, 0.7)
        line(s, 29, 44, 33, 46, dark, 0.7)
        for x, y in [(24, 39), (27, 41), (30, 39), (33, 42)]:
            dot(s, x, y, soft)
        # Boat timber and reflections.
        for a, b, c, d in [
            (4, 51, 22, 52), (23, 52, 41, 52), (43, 52, 59, 51),
            (7, 56, 25, 57), (30, 56, 49, 56), (9, 60, 31, 60),
        ]:
            line(s, a, b, c, d, dark, 0.7)
        for x, y in [(47, 28), (52, 34)]:
            dot(s, x, y - 2, light)
            dot(s, x - 1, y, accent)
            dot(s, x + 1, y, light)
        for a, b, c, d in [
            (1, 54, 8, 53), (14, 57, 21, 56), (34, 58, 42, 59),
            (51, 55, 62, 56), (4, 62, 15, 61),
        ]:
            line(s, a, b, c, d, accent, 0.65)

    elif slug == "olympia":
        # Facial details and hair, folds in the linen, and a defined black cat.
        dot(s, 19, 34, 8)
        dot(s, 22, 34, 8)
        dot(s, 20, 36, dark)
        line(s, 17, 31, 22, 30, dark, 0.7)
        line(s, 18, 32, 16, 35, dark, 0.65)
        line(s, 23, 32, 25, 35, dark, 0.65)
        dot(s, 21, 37, accent)
        # Linen folds and highlights across the bed.
        for a, b, c, d in [
            (5, 41, 17, 43), (8, 45, 22, 44), (12, 47, 27, 46),
            (29, 44, 40, 45), (35, 47, 48, 46), (42, 49, 57, 48),
        ]:
            line(s, a, b, c, d, light, 0.8)
            line(s, a, b + 1, c, d + 1, accent, 0.55)
        # Cat eyes, nose and whiskers.
        dot(s, 50, 42, accent)
        dot(s, 53, 42, accent)
        dot(s, 52, 44, dark)
        line(s, 49, 44, 45, 43, dark, 0.55)
        line(s, 54, 44, 58, 43, dark, 0.55)
        # Flowers and reflected curtain highlights.
        for x, y in [(58, 23), (60, 25), (57, 27), (61, 28)]:
            dot(s, x, y, light)
            dot(s, x + 1 if x < 62 else x - 1, y, accent)
        for y in (4, 12, 20, 28):
            line(s, 4, y, 10, y + 2, soft, 0.65)

    elif slug == "luncheon-grass":
        # Hair and facial marks, tailored clothing, picnic cloth and woven basket.
        for x, y in [(16, 34), (34, 32), (49, 17)]:
            dot(s, x - 1, y, 1)
            dot(s, x + 1, y, 1)
            dot(s, x, y + 2, dark)
            line(s, x - 2, y - 2, x + 1, y - 3, dark, 0.65)
        line(s, 15, 38, 18, 43, light, 0.7)
        line(s, 34, 36, 36, 42, dark, 0.7)
        line(s, 30, 39, 27, 44, accent, 0.7)
        line(s, 37, 39, 40, 44, accent, 0.7)
        # Cloth creases and basket weave.
        for a, b, c, d in [
            (38, 48, 44, 53), (42, 47, 49, 53), (47, 47, 54, 52),
            (39, 51, 54, 55), (8, 55, 17, 55), (8, 57, 17, 57),
        ]:
            line(s, a, b, c, d, light, 0.7)
        for x in (10, 13, 16):
            line(s, x, 54, x + 1, 58, dark, 0.6)
        # Leaf veins and textured tree trunks.
        for a, b, c, d in [
            (2, 14, 8, 10), (8, 18, 15, 14), (48, 13, 55, 9),
            (52, 18, 60, 14), (4, 23, 11, 20), (51, 24, 57, 20),
        ]:
            line(s, a, b, c, d, accent, 0.7)
        for y in range(5, 42, 5):
            line(s, 5, y, 6, y + 2, dark, 0.6)
            line(s, 57, y, 56, y + 2, dark, 0.6)
        for x, y in [(4, 49), (21, 60), (30, 58), (47, 60), (59, 48)]:
            dot(s, x, y, accent)
            dot(s, x + 1, y - 1, light)
    else:
        raise ValueError("No detail recipe for: " + slug)


def detailed_art(scene):
    base = draw_scene(scene)
    extra = DETAIL_COLORS[scene["slug"]]
    artwork = upsample(base, list(scene["palette"]) + extra)
    add_details(artwork, scene["slug"], len(scene["palette"]))
    return base, artwork


def detailed_animation_pose(base64, artwork70, slug, phase):
    """Reuse the original motion beats while preserving the new fine detail."""
    if phase == 0:
        return artwork70.cells[:]
    old_pose = animation_pose(base64, slug, phase)
    pose = artwork70.cells[:]
    for index, (before, after) in enumerate(zip(base64.cells, old_pose)):
        if before == after:
            continue
        x, y = index % 64, index // 64
        pose[project(x) + project(y) * SIDE] = after
    return pose


def animation_frames(base64, artwork70, slug):
    base = artwork70.cells
    frames = []
    for phase in range(8):
        pose = detailed_animation_pose(base64, artwork70, slug, phase)
        frames.append({
            "changes": [[i, color] for i, color in enumerate(pose)
                        if color != base[i]],
        })
    return frames


def create_pack(destination):
    by_slug = {scene["slug"]: scene for scene in PICTURES}
    if len(SELECTED_SLUGS) != 7 or len(set(SELECTED_SLUGS)) != 7:
        raise ValueError("Expected exactly seven distinct detailed paintings")
    manifest, assets, scenarios = [], {}, {}
    for slug in SELECTED_SLUGS:
        scene = by_slug[slug]
        base, artwork = detailed_art(scene)
        ident = PREFIX + slug
        if artwork.side != SIDE or len(artwork.cells) != SIDE * SIDE:
            raise ValueError("Invalid dimensions: " + slug)
        if len(artwork.palette) > 48 or any(
            type(cell) is not int or cell < 0 or cell >= len(artwork.palette)
            for cell in artwork.cells
        ):
            raise ValueError("Invalid palette index: " + slug)
        level = {
            "schemaVersion": 2, "levelId": ident, "levelVersion": 1,
            "titles": {"fa": scene["fa"], "en": scene["en"]},
            "width": SIDE, "height": SIDE,
            "palette": artwork.palette, "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        body = compact(level)
        frames = animation_frames(base, artwork, slug)
        poses = [detailed_animation_pose(base, artwork, slug, phase)
                 for phase in range(8)]
        if len(set(tuple(pose) for pose in poses)) < 3:
            raise ValueError("Insufficient animation variation: " + slug)
        animation = {
            "schemaVersion": 1, "levelId": ident, "levelVersion": 1,
            "levelChecksum": level["checksum"],
            "frameDurationMs": FRAME_DURATION_MS, "frames": frames,
        }
        anim_body = compact(animation)
        stem = ident + "-v1"
        manifest.append({
            "id": ident, "version": 1,
            "title": scene["fa"], "titleEn": scene["en"],
            "category": "patterns", "width": SIDE, "height": SIDE,
            "bytes": len(body), "checksum": level["checksum"],
            "animation": {
                "bytes": len(anim_body),
                "sha256": hashlib.sha256(anim_body).hexdigest(),
                "frameCount": len(frames),
            },
        })
        assets["levels/" + stem + ".json"] = body
        assets["previews/" + stem + ".png"] = png(level)
        assets["animations/" + stem + ".json"] = anim_body
        scenarios[ident] = {
            "titleFa": scene["fa"], "titleEn": scene["en"],
            "artist": scene["artist"],
            "motionFa": scene["motionFa"], "motionEn": scene["motionEn"],
            "frameCount": len(frames), "frameDurationMs": FRAME_DURATION_MS,
        }
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json",
                         compact({"schemaVersion": 1, "pictures": manifest}))
        for name, body in assets.items():
            archive.writestr(name, body)
        archive.writestr("animation-scenarios.json",
                         compact({"schemaVersion": 1, "scenarios": scenarios}))
    print("Generated seven detailed 70x70 animated classics: " + str(target))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_animated_masterworks_70_7_pack.py <content.zip>")
    create_pack(sys.argv[1])
