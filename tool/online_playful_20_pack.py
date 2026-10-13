#!/usr/bin/env python3
"""Twenty original playful pixel-art pictures for immutable online Releases.

The source contains hand-authored drawing instructions only. On publication,
content.zip holds numbered schema-v2 JSON levels, previews and catalog metadata.
Previously published assets and their level IDs are never overwritten.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

# Twelve accessible, distinctive colors per image: paper, ink, main color,
# lighter/darker main, yellow, blush, cream, sky blue, gray, leaf, lilac.
THEMES = {
    "sunny": ("FFFFF8E7", "FFF5B941", "FFFFDD74", "FFD68B35"),
    "rose": ("FFFFF3F6", "FFEE7DAD", "FFFFBCD1", "FFB34F7C"),
    "sky": ("FFF1F8FF", "FF69A9E7", "FFB6DFF9", "FF386BAA"),
    "mint": ("FFECFBF5", "FF56B795", "FFABE8CB", "FF317E68"),
    "violet": ("FFF7F2FF", "FF9C7AE3", "FFCFB9F3", "FF6751B0"),
    "coral": ("FFFFF4EF", "FFFF9478", "FFFFC5AC", "FFB45856"),
    "teal": ("FFEBFAFC", "FF57BACA", "FFA6E1E9", "FF397E92"),
    "berry": ("FFFFF2FA", "FFCA76BA", "FFF2BADD", "FF89478C"),
    "navy": ("FFEFF5FF", "FF6385C2", "FFA3B9E9", "FF36558A"),
    "lime": ("FFF4FAE9", "FF87B850", "FFC7E58D", "FF557D36"),
}


def draw(theme, instructions):
    background, main, highlight, shadow = THEMES[theme]
    palette = [
        background, "FF333D59", main, highlight, shadow, "FFFFCA52",
        "FFFF7F9E", "FFFFF9E8", "FF80C9E9", "FF9FB0C9",
        "FF66B784", "FFCEB2F3",
    ]
    sprite = Sprite(48, palette)
    # Grounding shadow keeps stickers legible on small phones.
    sprite.ellipse(24, 43, 15, 1.5, 9)
    for line in instructions.strip().splitlines():
        parts = line.strip().split()
        if not parts or parts[0] == "#":
            continue
        op, *args = parts
        if op == "R":
            sprite.rect(*(int(value) for value in args))
        elif op == "E":
            sprite.ellipse(*(float(value) for value in args[:4]), int(args[4]))
        elif op == "L":
            x0, y0, x1, y1 = (float(value) for value in args[:4])
            sprite.line(x0, y0, x1, y1, int(args[4]),
                        radius=float(args[5]) if len(args) == 6 else 0.8)
        elif op == "P":
            sprite.polygon(
                [tuple(float(n) for n in point.split(",")) for point in args[1:]],
                int(args[0]),
            )
        elif op == "D":
            sprite.dot(*(int(value) for value in args))
        else:
            raise ValueError(f"Unknown drawing command: {line}")
    return sprite


# Each illustration has its own silhouette and layered details.
# Commands: R rect, E ellipse, L line, P polygon, D single pixel.
PICTURES = [
    ("smiling-sun", "خورشید خندان", "Smiling Sun", "nature", "sunny", """
L 24 2 24 9 5 1.8
L 24 39 24 45 5 1.8
L 2 24 10 24 5 1.8
L 38 24 46 24 5 1.8
L 8 8 13 13 5 1.8
L 35 35 40 40 5 1.8
L 40 8 35 13 5 1.8
L 13 35 8 40 5 1.8
E 24 24 14 14 1
E 24 24 13 13 5
E 20 21 2 2.6 1
E 28 21 2 2.6 1
D 20 20 7
D 28 20 7
E 17 27 3 2 6
E 31 27 3 2 6
L 18 29 21 32 1 1.2
L 21 32 27 32 1 1.2
L 27 32 30 29 1 1.2
"""),
    ("rainbow-cloud", "ابر رنگین‌کمانی", "Rainbow Cloud", "nature", "sky", """
E 24 27 21 18 6
E 24 27 18 15 5
E 24 27 15 12 10
E 24 27 12 9 8
E 24 27 9 6 7
E 24 27 6 3 0
R 0 27 47 42 0
E 12 32 9 7 1
E 12 32 8 6 7
E 20 29 10 8 1
E 20 29 9 7 7
E 31 31 11 8 1
E 31 31 10 7 7
E 38 34 6 5 1
E 38 34 5 4 7
R 9 32 40 36 7
D 5 12 5
D 41 12 5
D 44 20 8
"""),
    ("heart-smile", "قلب مهربان", "Smiling Heart", "patterns", "rose", """
P 1 24,41 6,24 5,16 9,10 16,10 24,17 32,10 39,10 43,16 42,24
P 2 24,39 8,23 7,17 11,12 17,12 24,20 31,12 37,12 41,17 40,23
P 3 11,14 16,12 23,20 20,22 15,17 11,17
E 18 24 1.9 2.5 1
E 30 24 1.9 2.5 1
D 18 23 7
D 30 23 7
E 13 29 2.6 1.6 6
E 35 29 2.6 1.6 6
L 19 31 23 34 1 1.2
L 23 34 27 34 1 1.2
L 27 34 30 31 1 1.2
D 4 7 5
D 43 6 5
"""),
    ("lucky-clover", "شبدر خوش‌شانس", "Lucky Clover", "nature", "lime", """
L 23 25 29 40 1 2.5
L 23 25 29 40 10 1.5
E 18 17 9 8 1
E 18 17 8 7 2
E 30 17 9 8 1
E 30 17 8 7 10
E 18 28 9 8 1
E 18 28 8 7 10
E 30 28 9 8 1
E 30 28 8 7 2
E 24 22 5 5 5
E 24 22 3.2 3.2 7
L 16 14 20 11 3 1
L 30 29 34 31 3 1
E 39 9 2.7 2.7 5
D 39 9 7
E 8 37 2 2 6
"""),
    ("friendly-ghost", "روح بازیگوش", "Friendly Ghost", "patterns", "violet", """
P 1 11,40 8,24 8,16 12,9 20,5 29,5 37,10 40,19 40,39 34,35 29,40 24,35 18,40 13,35
P 7 12,37 10,23 10,17 14,11 20,7 29,7 35,11 38,19 38,36 34,32 29,37 24,32 19,37 13,32
E 19 21 3.2 4.5 1
E 29 21 3.2 4.5 1
D 18 19 7
D 28 19 7
E 15 29 2.6 2 6
E 34 29 2.6 2 6
E 24 29 3 3.5 1
E 24 30 1.3 1.4 6
D 4 11 5
D 43 8 5
D 5 31 11
D 43 31 11
"""),
    ("one-eyed-monster", "هیولای یک‌چشم", "One-Eyed Monster", "patterns", "mint", """
L 14 12 11 5 1 2
L 34 12 38 5 1 2
E 11 5 3 3 6
E 38 5 3 3 5
E 24 25 17 16 1
E 24 25 15.5 14.5 2
E 24 22 9.5 9 1
E 24 22 8 7.5 7
E 24 22 4.6 5 8
E 24 22 2.4 3.4 1
D 22 19 7
E 15 29 2.2 2 6
E 33 29 2.2 2 6
E 24 34 8 3.7 1
R 20 33 22 36 7
R 25 33 27 36 7
L 12 37 9 41 1 1.7
L 36 37 39 41 1 1.7
E 16 10 2 2 11
"""),
    ("flying-saucer", "بشقاب‌پرنده بامزه", "Cute UFO", "space", "navy", """
D 5 5 5
D 42 6 7
D 12 12 8
D 39 16 5
D 5 33 7
E 24 18 11 10 1
E 24 18 10 9 8
E 24 16 6 5 3
E 24 26 21 8 1
E 24 26 19 6 2
E 24 23 14 3 3
E 12 27 2.5 2.5 5
E 24 30 2.5 2.5 5
E 36 27 2.5 2.5 5
P 8 16,33 32,33 39,43 10,43
P 3 19,34 29,34 35,41 13,41
D 20 16 1
D 28 16 1
L 21 20 27 20 1 1
"""),
    ("magic-wand", "چوب جادویی", "Magic Wand", "objects", "violet", """
L 12 39 31 18 1 3
L 12 39 31 18 9 1.4
P 1 31,2 35,12 46,14 37,21 40,31 30,24 20,31 23,20 13,15 27,12
P 5 31,6 34,15 42,15 34,21 37,28 30,23 23,28 25,19 17,17 29,15
E 30 17 3 3 7
D 3 10 5
D 43 5 5
D 8 25 6
D 42 31 8
L 8 5 8 10 5 1.1
L 5 8 11 8 5 1.1
L 38 32 38 38 6 1.1
L 35 35 41 35 6 1.1
"""),
    ("party-hat", "کلاه جشن", "Party Hat", "objects", "coral", """
P 1 23,4 7,36 40,36
P 2 23,7 10,34 37,34
P 5 21,14 25,21 19,25 16,22
P 6 16,27 21,24 26,30 24,35 18,35
P 8 30,23 35,33 28,34 26,30
L 8 36 40 36 1 2
L 9 37 39 37 5 1.7
E 23 4 4 4 1
E 23 4 3 3 5
D 15 31 7
D 27 27 7
D 24 13 7
L 5 10 9 10 6 1
L 7 8 7 12 6 1
D 41 10 8
D 42 24 5
"""),
    ("birthday-cake", "کیک تولد رنگی", "Birthday Cake", "objects", "rose", """
R 11 25 37 40 1
R 13 27 35 38 2
R 13 27 35 30 7
E 17 31 2 3 7
E 24 30 2.5 3.5 7
E 31 31 2 3 7
R 9 22 39 26 1
R 11 23 37 25 3
R 22 12 26 22 1
R 23 13 25 22 7
P 5 24,5 20,11 23,13 28,11
P 6 24,7 22,11 24,11 26,10
E 24 10 1.8 2.7 5
D 16 34 5
D 30 35 5
D 24 37 6
R 8 40 40 41 1
E 7 11 2 2 8
E 41 14 2 2 8
"""),
    ("popcorn-carton", "پاپ‌کورن خندان", "Smiling Popcorn", "objects", "amber", """
E 15 14 6 6 1
E 15 14 5 5 7
E 25 10 6 6 1
E 25 10 5 5 7
E 34 15 6 6 1
E 34 15 5 5 7
E 21 17 7 5 1
E 21 17 6 4 7
P 1 8,19 40,19 36,40 13,40
P 6 11,21 37,21 34,38 15,38
P 7 16,21 22,21 22,38 18,38
P 7 28,21 33,21 30,38 26,38
E 20 28 1.8 2.4 1
E 30 28 1.8 2.4 1
L 20 33 24 35 1 1.1
L 24 35 28 33 1 1.1
D 18 11 5
D 32 12 5
"""),
    ("bubble-tea", "بابل‌تی بامزه", "Bubble Tea", "objects", "teal", """
L 26 12 36 2 1 2.2
L 26 12 36 2 6 1.2
R 12 13 36 17 1
R 14 14 34 16 7
P 1 12,17 36,17 32,41 16,41
P 2 14,19 34,19 30,39 18,39
R 16 24 32 27 3
E 20 33 2.4 2.4 1
E 27 35 2.4 2.4 1
E 24 30 2.4 2.4 1
E 19 27 1.4 1.4 4
E 29 27 1.4 1.4 4
L 20 31 24 33 1 1
L 24 33 28 31 1 1
E 16 5 2 2 5
D 41 9 6
D 8 30 5
"""),
    ("rubber-duck", "اردک اسباب‌بازی", "Rubber Duck", "objects", "sunny", """
E 22 29 16 12 1
E 22 29 14.5 10.5 5
E 30 16 10 10 1
E 30 16 9 9 5
P 1 20,18 11,25 20,27
P 2 20,20 14,25 20,25
P 1 38,17 46,20 38,23
P 6 38,18 43,20 38,22
E 33 15 1.5 2 1
D 33 14 7
E 15 29 6.5 5.5 1
E 15 29 5.5 4.5 3
L 13 31 16 32 4 1
E 8 38 2 2 8
E 41 36 2 2 8
"""),
    ("teddy-bear", "خرس عروسکی", "Teddy Bear", "objects", "coral", """
E 11 11 7 7 1
E 11 11 6 6 4
E 37 11 7 7 1
E 37 11 6 6 4
E 11 11 3.5 3.5 6
E 37 11 3.5 3.5 6
E 24 34 13 10 1
E 24 34 11 8 2
E 10 33 5 6 1
E 10 33 4 5 2
E 38 33 5 6 1
E 38 33 4 5 2
E 24 18 14 13 1
E 24 18 12.5 11.5 2
E 19 17 2 2.4 1
E 29 17 2 2.4 1
D 19 16 7
D 29 16 7
E 24 23 7 5 3
E 24 21 2.8 2 1
L 24 24 24 26 1 1
L 24 26 21 27 1 1
L 24 26 27 27 1 1
E 24 35 5 4 7
E 24 35 3 2.5 6
"""),
    ("rainbow-yo-yo", "یویوی رنگی", "Rainbow Yo-yo", "objects", "violet", """
L 24 30 33 10 1 0.9
L 33 10 40 6 1 0.9
E 22 29 14 13 1
E 22 29 12.5 11.5 2
E 22 29 9 9 5
E 22 29 6.5 6.5 8
E 22 29 4 4 6
E 22 29 2 2 7
E 40 6 3 3 1
E 40 6 2 2 3
D 7 7 5
D 11 12 6
D 41 28 8
D 4 30 11
"""),
    ("paper-kite", "بادبادک خندان", "Paper Kite", "objects", "sky", """
P 1 24,3 40,19 24,34 8,19
P 2 24,5 38,19 24,32 10,19
P 6 24,5 24,32 10,19
P 5 24,5 38,19 24,19
P 3 24,19 38,19 24,32
E 20 17 1.5 2 1
E 29 17 1.5 2 1
L 19 23 24 25 1 1
L 24 25 29 23 1 1
L 24 34 22 40 1 1
L 22 40 27 44 1 1
P 6 20,35 15,32 16,38
P 5 24,39 29,36 28,42
D 6 7 5
D 42 8 8
D 7 29 6
"""),
    ("smiling-moon", "ماه خندان", "Smiling Moon", "space", "navy", """
E 23 24 17 17 1
E 23 24 15 15 5
E 32 16 12 13 0
E 25 26 1.5 2.3 1
D 25 25 7
E 17 24 2 2 6
L 23 31 26 33 1 1
L 26 33 29 32 1 1
L 28 29 29 32 1 1
L 7 10 7 15 5 1
L 5 12 10 12 5 1
L 39 32 39 38 8 1
L 36 35 42 35 8 1
D 42 9 5
D 12 40 8
D 4 29 11
"""),
    ("star-buddy", "ستاره بامزه", "Cute Star Buddy", "patterns", "sunny", """
P 1 24,3 30,16 44,18 34,28 37,42 24,35 11,42 14,28 4,18 18,16
P 5 24,6 29,18 40,20 32,28 34,38 24,32 14,38 16,28 8,20 19,18
P 3 21,10 25,10 28,18 24,19 20,18
E 19 24 2 2.6 1
E 29 24 2 2.6 1
D 19 23 7
D 29 23 7
E 13 28 2.5 1.7 6
E 35 28 2.5 1.7 6
L 20 29 23 32 1 1
L 23 32 26 32 1 1
L 26 32 29 29 1 1
D 4 7 8
D 42 8 6
D 44 39 8
"""),
    ("neon-jellyfish", "عروس دریایی نئونی", "Neon Jellyfish", "animals", "berry", """
L 13 27 9 39 1 2.2
L 13 27 9 39 8 1.1
L 19 28 17 42 1 2.2
L 19 28 17 42 11 1.1
L 26 28 29 41 1 2.2
L 26 28 29 41 8 1.1
L 34 27 39 39 1 2.2
L 34 27 39 39 11 1.1
E 24 20 18 14 1
E 24 19 16 12 2
E 24 13 10 5 3
R 8 22 40 27 1
R 10 22 38 25 2
E 17 19 2 2.5 1
E 31 19 2 2.5 1
D 17 18 7
D 31 18 7
E 13 24 3 1.5 6
E 35 24 3 1.5 6
L 21 25 24 27 1 0.8
L 24 27 27 25 1 0.8
E 4 12 2.5 2.5 8
E 43 8 2 2 8
E 40 36 2.5 2.5 8
"""),
    ("candy-land", "سرزمین آب‌نبات", "Candy Land", "patterns", "rose", """
R 0 40 47 47 10
L 9 25 9 40 1 2
L 9 25 9 40 7 1
E 9 18 9 9 1
E 9 18 8 8 6
E 9 18 5.5 5.5 7
E 9 18 3 3 5
L 30 22 30 40 1 2
L 30 22 30 40 7 1
E 30 16 10 10 1
E 30 16 9 9 5
E 30 16 6 6 8
E 30 16 3.5 3.5 6
P 1 32,36 45,29 45,43
P 2 34,36 43,32 43,41
P 1 15,33 23,28 23,38
P 11 16,33 21,30 21,36
E 19 41 5 2 7
E 39 41 4 2 7
D 18 6 8
D 44 12 6
D 4 36 5
"""),
]


def create_pack(destination):
    if len(PICTURES) != 20:
        raise ValueError("The playful collection must contain exactly 20 pictures")
    manifest = []
    files = {}
    for slug, title_fa, title_en, category, theme, instructions in PICTURES:
        ident = f"online-playful-{slug}"
        sprite = draw(theme, instructions)
        level = {
            "schemaVersion": 2,
            "levelId": ident,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": sprite.side, "height": sprite.side,
            "palette": sprite.palette, "cells": sprite.cells,
        }
        level["checksum"] = checksum(level)
        payload = compact(level)
        if len(payload) > 262144:
            raise ValueError(f"Picture is too large: {ident}")
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1,
            "title": title_fa, "titleEn": title_en,
            "category": category, "width": sprite.side, "height": sprite.side,
            "bytes": len(payload), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = payload
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    output = pathlib.Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, payload in files.items():
            bundle.writestr(name, payload)
    print(f"Prepared {len(manifest)} playful coloring levels: {output}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_playful_20_pack.py <content.zip>")
    create_pack(sys.argv[1])
