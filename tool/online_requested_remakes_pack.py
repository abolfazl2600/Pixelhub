#!/usr/bin/env python3
"""Fresh online replacements for four retired 10x10/32x32 pictures.

Original releases are immutable. This generator publishes only new IDs;
tool/online_release.py retires earlier IDs from the visible catalog.
No application migration, binary assets or version bump are required.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

REPLACEMENTS = (
    ("online-flag-united-kingdom-30", "پرچم بریتانیا", "United Kingdom Flag",
     "patterns", 30),
    ("online-flag-turkey-40", "پرچم ترکیه", "Turkey Flag",
     "patterns", 40),
    ("online-flag-iran-40", "پرچم ایران", "Iran Flag",
     "patterns", 40),
    ("online-mona-lisa-detailed-90", "مونالیزا", "Mona Lisa",
     "patterns", 90),
)


def united_kingdom():
    """Union Jack with eight angled saltire segments and two centered crosses."""
    side = 30
    navy, white, scarlet = 0, 1, 2
    s = Sprite(side, ["FF012169", "FFFFFFFF", "FFC8102E"])
    for y in range(side):
        for x in range(side):
            # Broad white diagonal saltire with narrow red cores.
            d1 = abs(y - x)
            d2 = abs(y - (side - 1 - x))
            if min(d1, d2) <= 4:
                s.dot(x, y, white)
            if min(d1, d2) <= 1:
                s.dot(x, y, scarlet)
            # Wide white St George's cross, over the saltire.
            if 12 <= x <= 17 or 12 <= y <= 17:
                s.dot(x, y, white)
            if 13 <= x <= 16 or 13 <= y <= 16:
                s.dot(x, y, scarlet)
    return s


def turkey():
    """Full crimson field, hollow crescent and a separated five-point star."""
    s = Sprite(40, ["FFE30A17", "FFFFFFFF"])
    for y in range(40):
        for x in range(40):
            if (x - 15) ** 2 + (y - 20) ** 2 <= 11 ** 2:
                s.dot(x, y, 1)
            if (x - 20) ** 2 + (y - 18.4) ** 2 <= 8.8 ** 2:
                s.dot(x, y, 0)
    cx, cy, outer, inner = 30.5, 20, 6.2, 2.45
    vertices = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer if i % 2 == 0 else inner
        vertices.append((cx + radius * math.cos(angle),
                         cy + radius * math.sin(angle)))
    s.polygon(vertices, 1)
    return s


def iran():
    """Iranian tricolor with repeated kufic border detail and center emblem."""
    s = Sprite(40, ["FF239F40", "FFFFFFFF", "FFDA0000", "FF177D35"])
    s.rect(0, 0, 39, 12, 0)
    s.rect(0, 13, 39, 26, 1)
    s.rect(0, 27, 39, 39, 2)
    # Kufic-style border motifs in the two white-adjacent rows.
    for x in range(40):
        if x % 5 in (0, 1, 2):
            s.dot(x, 13, 0)
            s.dot(x, 26, 2)
        if x % 5 in (0, 1):
            s.dot(x, 14, 0)
            s.dot(x, 25, 2)
    # Symmetric, legible red national emblem silhouette at this resolution.
    s.rect(19, 17, 20, 24, 2)
    s.ellipse(19.5, 18, 2.5, 1.25, 2)
    for flip in (-1, 1):
        cx = 19.5 + 4.6 * flip
        for y in range(18, 24):
            for x in range(11, 29):
                d = ((x - cx) / 3.0) ** 2 + ((y - 20.6) / 3.65) ** 2
                inside = ((x - (cx + 1.2 * flip)) / 1.85) ** 2 + (
                    (y - 20.3) / 2.65) ** 2
                if 0.48 <= d <= 1.50 and inside >= 0.9:
                    s.dot(x, y, 2)
        s.line(19.5 + flip * 2.5, 24,
               19.5 + flip * 5.2, 25, 2, radius=0.55)
    s.rect(17, 24, 22, 24, 2)
    return s


def mona_lisa():
    """90x90 hand-drawn interpretation with sfumato tones and crossed hands."""
    s = Sprite(90, [
        "FF777960",  # 0 slate olive upper background
        "FFB4AD87",  # 1 distant amber mist
        "FFDDD0A0",  # 2 glowing horizon
        "FF677967",  # 3 alpine shadow
        "FF465F55",  # 4 dark wooded cliff
        "FF829181",  # 5 distant ridge
        "FF9EA69B",  # 6 pale river
        "FF625F46",  # 7 foreground stone
        "FF302B25",  # 8 near black dress
        "FF46362A",  # 9 warm chestnut hair
        "FF62442D",  # 10 hair highlights
        "FF835B3C",  # 11 warm shadow
        "FFA5794C",  # 12 deep skin
        "FFC49867",  # 13 sunlit skin
        "FFE0B17A",  # 14 skin highlights
        "FFF0C992",  # 15 tiny glowing skin highlights
        "FF674833",  # 16 eyes, mouth and creases
        "FF231E1B",  # 17 hair and deep dress outline
        "FF534E39",  # 18 dress folds
        "FF8A7648",  # 19 embroidery shadows
        "FFB09453",  # 20 gold embroidery
        "FFC4A977",  # 21 horizon highlight
        "FF344A45",  # 22 riverbank shadow
        "FFB5B098",  # 23 stone bridge
        "FF6B5339",  # 24 fingers and face contours
        "FF38352A",  # 25 aged hairline
    ])
    s.rect(0, 0, 89, 25, 0)
    s.rect(0, 26, 89, 40, 1)
    s.rect(0, 41, 89, 89, 7)
    s.polygon([(0, 30), (13, 18), (26, 29), (40, 20),
               (62, 24), (75, 14), (89, 24), (89, 43), (0, 43)], 5)
    s.polygon([(0, 35), (11, 29), (23, 36), (33, 31),
               (55, 33), (73, 27), (89, 35), (89, 53), (0, 51)], 3)
    s.polygon([(0, 49), (13, 32), (25, 42), (37, 47),
               (33, 78), (0, 79)], 4)
    s.polygon([(90, 47), (74, 33), (65, 37), (55, 51),
               (62, 77), (90, 84)], 4)
    # Serpentine distant river with the small old bridge behind the figure.
    s.polygon([(0, 58), (14, 53), (25, 56), (38, 53),
               (56, 49), (74, 48), (90, 52), (90, 56),
               (73, 54), (60, 56), (45, 60), (24, 62), (0, 67)], 6)
    s.line(71, 53, 88, 50, 23, radius=1.5)
    for x in range(73, 88, 5):
        s.line(x, 52, x + 2, 57, 22, radius=.6)
    for y in range(3, 61):
        for x in range(90):
            if s.cells[y * 90 + x] in (0, 3, 4, 5):
                grain = (x * 29 + y * 17 + x * y * 7) % 31
                if grain == 0:
                    s.dot(x, y, 5 if y < 34 else 3)
                elif grain == 7 and y < 33:
                    s.dot(x, y, 1)
    # Seated bust, broad dark gown and left/right draped sleeves.
    s.polygon([(5, 90), (11, 76), (19, 64), (29, 55),
               (40, 50), (55, 51), (65, 57), (77, 69),
               (87, 90)], 17)
    s.polygon([(9, 90), (17, 72), (28, 59), (40, 54),
               (57, 55), (70, 65), (83, 90)], 8)
    s.polygon([(11, 84), (22, 59), (31, 55),
               (32, 73), (29, 90), (9, 90)], 18)
    s.polygon([(57, 58), (64, 57), (78, 81),
               (80, 90), (59, 90), (61, 74)], 18)
    s.polygon([(22, 59), (34, 53), (43, 56),
               (28, 86), (15, 88)], 9)
    s.polygon([(24, 61), (31, 56), (38, 57),
               (27, 79), (19, 86)], 10)
    # Dark cascading hair: silhouette then selected brown strands.
    s.ellipse(44, 31, 23, 29, 17)
    s.polygon([(24, 34), (31, 30), (37, 43),
               (30, 60), (23, 68), (17, 78), (21, 49)], 17)
    s.polygon([(57, 29), (64, 35), (65, 57),
               (76, 83), (59, 78), (55, 52)], 17)
    s.ellipse(44, 29, 20, 26, 9)
    s.polygon([(27, 32), (30, 16), (37, 11), (34, 32),
               (31, 62), (23, 72)], 10)
    s.polygon([(56, 15), (63, 28), (62, 46), (68, 65),
               (58, 61), (55, 41)], 10)
    s.polygon([(37, 8), (50, 8), (59, 15),
               (53, 20), (43, 16), (35, 22)], 17)
    # Face with shadow, asymmetry and soft luminous cheek.
    s.ellipse(44, 32, 14, 20, 11)
    s.ellipse(44, 32, 12, 18.5, 12)
    s.ellipse(42.5, 34, 10, 16, 13)
    s.ellipse(39.5, 37.4, 5.8, 8, 14)
    s.ellipse(38.2, 38, 3.5, 4.8, 15)
    s.ellipse(49, 38, 3.9, 8.2, 12)
    s.polygon([(39, 47), (48, 49), (53, 45),
               (50, 52), (42, 55), (37, 52)], 12)
    s.polygon([(38, 46), (47, 49), (51, 45),
               (48, 50), (42, 52)], 13)
    # Hairline frames rather than obscures the face.
    s.polygon([(30, 30), (28, 22), (30, 13), (40, 9),
               (51, 11), (57, 20), (55, 23),
               (48, 16), (39, 17), (34, 24)], 9)
    s.polygon([(30, 22), (34, 17), (36, 35),
               (33, 46), (27, 59), (29, 35)], 17)
    s.polygon([(54, 19), (60, 27), (58, 49),
               (63, 65), (55, 57), (55, 35)], 17)
    for px, py in [(29, 28), (28, 38), (30, 49),
                   (59, 29), (58, 43), (60, 52)]:
        s.line(px, py, px - 2, py + 11, 10, radius=.45)
    # Downcast almond eyes, understated eyebrows, nose, famous faint smile.
    s.line(35, 30, 42, 29, 16, radius=.6)
    s.line(46, 29, 52, 30, 16, radius=.6)
    s.line(36, 33, 42, 33, 16, radius=.5)
    s.line(46, 33, 51, 33, 16, radius=.5)
    s.ellipse(39.5, 33, 1.25, .85, 17)
    s.ellipse(48.6, 33, 1.15, .85, 17)
    s.dot(39, 33, 15)
    s.dot(48, 33, 15)
    s.line(44.5, 33, 43.5, 40, 13, radius=1)
    s.line(43.5, 39, 46.4, 41, 24, radius=.65)
    s.dot(45, 40, 15)
    s.line(39.3, 44.1, 42, 44.7, 16, radius=.6)
    s.line(42, 44.7, 48, 44.5, 16, radius=.45)
    s.line(48, 44.5, 50, 43.8, 16, radius=.55)
    s.line(42, 46, 47.5, 46, 14, radius=.6)
    # Soft neckline, dark translucent veil and golden dress embroidery.
    s.polygon([(31, 53), (39, 57), (47, 60),
               (56, 57), (63, 59), (51, 67), (36, 66)], 8)
    s.line(30, 62, 41, 67, 19, radius=1.1)
    s.line(41, 67, 58, 66, 20, radius=.9)
    s.line(58, 66, 67, 60, 19, radius=1.1)
    for i in range(13):
        x = 16 + i * 2.1
        y = 74 + 0.12 * i + 0.06 * i * i
        if 12 < x < 60:
            s.dot(int(x), int(y), 19 if i % 2 else 20)
    s.line(20, 77, 60, 82, 10, radius=2)
    s.line(25, 75, 59, 81, 19, radius=.9)
    # Folded hands: one forearm across the lap, the other hand resting above.
    s.polygon([(17, 74), (25, 72), (35, 73), (48, 78),
               (59, 79), (65, 83), (59, 87),
               (38, 82), (24, 80)], 11)
    s.polygon([(20, 75), (28, 74), (41, 76),
               (59, 81), (61, 84), (55, 85),
               (39, 80), (23, 79)], 13)
    s.polygon([(31, 78), (40, 75), (57, 77), (68, 81),
               (71, 84), (63, 87), (50, 85), (36, 82)], 12)
    s.polygon([(34, 79), (41, 77), (56, 79),
               (67, 82), (65, 85), (47, 83)], 14)
    for i in range(4):
        s.line(47 + i, 79 + i * .8, 65 + i * .5,
               83 + i * .6, 24, radius=.28)
    s.line(20, 78, 34, 79, 14, radius=.6)
    s.line(44, 84, 58, 86, 11, radius=.8)
    # Fine fabric strokes without random gradients or blur.
    for y in range(63, 89):
        for x in range(9, 82):
            value = s.cells[y * 90 + x]
            seed = (x * 17 + y * 23 + x * y) % 37
            if value == 8 and seed == 2:
                s.dot(x, y, 18)
            elif value == 9 and seed == 3:
                s.dot(x, y, 10)
    return s


def create_pack(destination):
    painters = [united_kingdom, turkey, iran, mona_lisa]
    manifest, assets = [], {}
    for (ident, fa, en, category, side), painter in zip(REPLACEMENTS, painters):
        art = painter()
        if art.side != side or len(art.cells) != side * side:
            raise ValueError("Incorrect artwork dimensions: " + ident)
        level = {
            "schemaVersion": 2,
            "levelId": ident,
            "levelVersion": 1,
            "titles": {"fa": fa, "en": en},
            "width": side,
            "height": side,
            "palette": art.palette,
            "cells": art.cells,
        }
        level["checksum"] = checksum(level)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Level too large: " + ident)
        stem = ident + "-v1"
        manifest.append({
            "id": ident, "version": 1, "title": fa, "titleEn": en,
            "category": category, "width": side, "height": side,
            "bytes": len(body), "checksum": level["checksum"],
        })
        assets["levels/" + stem + ".json"] = body
        assets["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, body in assets.items():
            archive.writestr(path, body)
    print("Created four replacement online paintings:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_requested_remakes_pack.py <content.zip>")
    create_pack(sys.argv[1])
