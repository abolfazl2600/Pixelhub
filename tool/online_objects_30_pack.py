#!/usr/bin/env python3
"""Thirty original, bilingual object pixel-art levels for online-only Releases.

Only reproducible drawing instructions are committed to Git. Generated numbered
JSON grids and preview PNGs are distributed through a new immutable Release.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


# Background, primary, highlight and shade for each illustration.
THEMES = {
    "blue": ("FFF0F7FF", "FF548FCC", "FF9ACCF0", "FF305E95"),
    "rose": ("FFFFF2F4", "FFE77D97", "FFFFB6C7", "FFAD4669"),
    "mint": ("FFF0FBF5", "FF56AD91", "FFADE7C5", "FF357D76"),
    "amber": ("FFFFF6E9", "FFD89146", "FFF5CC77", "FF986238"),
    "violet": ("FFF8F2FF", "FF9C7DCF", "FFCFB5F0", "FF65519C"),
    "coral": ("FFFFF4F0", "FFED8069", "FFFFBC99", "FFAD5948"),
    "navy": ("FFEFF5FF", "FF536B98", "FF91ADD3", "FF303F69"),
    "jade": ("FFF2F9F0", "FF60A474", "FFA9D7A2", "FF3E7658"),
    "teal": ("FFECF9FB", "FF4DADBE", "FF9BDEE3", "FF327886"),
    "plum": ("FFFAF1F8", "FFC47CAA", "FFE7B4D5", "FF854E7C"),
}


def draw(theme, instructions):
    """Draw one hand-authored 48×48 picture from compact vector primitives.

    R x0 y0 x1 y1 color; E cx cy rx ry color;
    L x0 y0 x1 y1 color [radius]; P color x,y ...; D x y color.
    Indices refer to the stable twelve-color palette below.
    """
    bg, primary, light, dark = THEMES[theme]
    palette = [
        bg, "FF35384B", primary, light, dark, "FFFFC95A",
        "FFE96F8C", "FFFFFAE9", "FF87CDE8", "FFADB9CC",
        "FF65A781", "FFDDE6E9",
    ]
    s = Sprite(48, palette)
    s.ellipse(24, 43, 17, 1.6, 11)
    for line in instructions.splitlines():
        parts = line.strip().split()
        if not parts or parts[0] == "#":
            continue
        command, *args = parts
        if command == "R":
            s.rect(*(int(a) for a in args))
        elif command == "E":
            s.ellipse(*(float(a) for a in args[:4]), int(args[4]))
        elif command == "L":
            x0, y0, x1, y1 = (float(v) for v in args[:4])
            s.line(x0, y0, x1, y1, int(args[4]),
                   radius=float(args[5]) if len(args) == 6 else 0.7)
        elif command == "P":
            s.polygon([tuple(float(n) for n in pair.split(","))
                       for pair in args[1:]], int(args[0]))
        elif command == "D":
            s.dot(int(args[0]), int(args[1]), int(args[2]))
        else:
            raise ValueError(f"Unknown drawing instruction: {line}")
    return s


# Every image has its own geometry, not a recolored copy of another image.
# The existing balloon, coffee, donut, ice cream and watermelon are omitted.
PICTURES = [
    ("alarm-clock", "ساعت زنگ‌دار", "Alarm Clock", "rose", """
E 13 11 6 5 1
E 13 11 5 4 6
E 35 11 6 5 1
E 35 11 5 4 6
L 10 36 7 42 1 2
L 37 36 40 42 1 2
E 24 26 18 18 1
E 24 26 16 16 2
E 24 26 13 13 7
E 24 26 11 11 3
L 24 15 24 17 1 1
L 24 35 24 37 1 1
L 13 26 15 26 1 1
L 33 26 35 26 1 1
L 24 26 24 18 1 1.7
L 24 26 31 30 4 1.5
E 24 26 2.1 2.1 1
R 22 4 26 6 9
"""),
    ("vintage-camera", "دوربین عکاسی", "Vintage Camera", "navy", """
R 8 13 39 37 1
R 10 15 37 35 2
R 11 9 21 14 1
R 12 10 20 13 9
R 28 10 35 14 1
R 29 11 34 13 5
R 32 17 36 20 7
E 24 25 12 12 1
E 24 25 10 10 9
E 24 25 8 8 4
E 24 25 6 6 8
E 24 25 3 3 1
E 22 23 1.5 1.5 7
R 10 32 17 34 3
L 11 17 20 17 3
"""),
    ("headphones", "هدفون", "Headphones", "violet", """
E 24 21 17 18 1
E 24 21 14 15 2
E 24 22 11 13 0
E 24 20 10 11 0
R 5 21 12 38 1
R 7 22 12 36 4
R 9 24 14 35 2
R 36 21 43 38 1
R 36 22 41 36 4
R 34 24 39 35 2
R 11 25 15 33 9
R 33 25 37 33 9
L 15 38 18 41 8 1
L 33 38 30 41 8 1
"""),
    ("electric-guitar", "گیتار برقی", "Electric Guitar", "coral", """
P 1 17,22 11,26 9,35 14,42 24,43 31,37 30,31 25,27 24,22
P 2 17,24 13,27 11,35 15,40 24,40 28,36 28,31 22,28 22,23
E 16 34 5 5 3
R 22 6 26 30 1
R 23 7 25 30 5
P 1 21,5 27,5 29,2 27,1 22,2
D 24 4 5
D 27 3 5
R 20 22 27 24 9
R 20 29 27 31 9
R 19 34 26 35 4
L 23 7 23 37 7
L 25 7 25 37 7
L 24 10 25 10 4
L 24 14 25 14 4
L 24 18 25 18 4
"""),
    ("retro-radio", "رادیوی قدیمی", "Retro Radio", "amber", """
L 12 15 35 3 1 1.4
R 6 14 42 38 1
R 8 16 40 36 2
R 10 19 31 33 4
R 12 21 29 31 9
L 15 21 15 31 1
L 19 21 19 31 1
L 23 21 23 31 1
L 27 21 27 31 1
R 33 19 38 21 7
E 35 27 3.5 3.5 1
E 35 27 2 2 5
E 35 34 1.8 1.8 1
R 10 13 17 15 1
R 11 14 16 14 7
"""),
    ("desk-lamp", "چراغ مطالعه", "Desk Lamp", "mint", """
E 25 40 12 3 1
E 25 39 10 2 2
L 24 37 32 25 1 2.4
L 24 37 32 25 9 1.2
L 32 25 18 17 1 2.2
L 32 25 18 17 3 1.1
E 32 25 3 3 1
E 32 25 1.5 1.5 5
P 1 11,8 26,12 25,21 5,17
P 2 12,10 24,13 23,19 8,16
L 6 18 24 22 5 1.3
E 14 19 3 3 5
E 14 19 1.4 1.4 7
L 21 38 29 38 4
"""),
    ("porcelain-teapot", "قوری چینی", "Porcelain Teapot", "blue", """
E 24 29 13 11 1
E 24 29 11 9 2
E 22 27 7 5 3
E 39 27 7 9 1
E 39 27 4 6 0
P 1 12,26 3,20 6,29 15,33
P 2 13,27 6,23 8,29 15,31
R 14 18 34 21 1
R 17 19 31 20 3
E 24 17 5 2.5 1
E 24 16 3 1.5 5
E 24 28 4 4 7
E 24 28 2.5 2.5 6
D 24 28 5
L 18 36 30 36 3
"""),
    ("rainbow-umbrella", "چتر رنگی", "Rainbow Umbrella", "rose", """
P 1 4,21 8,12 17,7 24,6 31,7 40,12 44,21 38,20 32,22 24,20 16,22 10,20
P 6 6,19 10,13 17,9 24,8 19,20 14,20 10,19
P 5 24,8 31,9 38,13 42,19 38,19 33,21 28,19
P 2 19,20 24,8 28,19 24,21
L 24 20 24 38 1 1.7
L 24 38 20 42 1 1.8
L 20 42 16 39 1 1.8
D 24 5 1
E 24 5 1.5 1.5 5
"""),
    ("backpack", "کوله‌پشتی", "Backpack", "jade", """
L 13 16 11 34 1 4
L 35 16 37 34 1 4
R 18 5 30 14 1
R 20 7 28 15 9
E 24 24 16 18 1
E 24 24 14 16 2
R 12 20 36 35 3
R 16 27 32 36 1
R 18 29 30 34 4
R 20 28 28 29 5
L 12 18 36 18 4 1.7
R 21 12 27 17 1
R 22 13 26 16 5
D 24 32 7
"""),
    ("running-sneaker", "کفش کتانی", "Running Sneaker", "blue", """
P 1 3,31 12,26 18,18 25,18 31,27 42,30 45,35 44,41 4,41
P 2 5,32 13,28 19,20 24,20 30,29 42,32 43,37 5,38
P 7 4,37 44,37 43,40 4,40
P 4 16,25 20,20 25,21 30,29 26,33
P 8 16,28 22,31 33,32 29,34 21,34
L 20 23 27 25 7 1
L 18 26 29 28 7 1
L 17 29 30 31 7 1
L 11 36 17 36 6 1.1
R 38 35 42 36 5
"""),
    ("city-bicycle", "دوچرخه", "City Bicycle", "mint", """
E 11 33 9 9 1
E 11 33 7 7 0
E 37 33 9 9 1
E 37 33 7 7 0
L 11 33 22 22 2 1.4
L 22 22 29 33 2 1.4
L 29 33 11 33 2 1.4
L 29 33 37 33 2 1.4
L 37 33 33 17 2 1.4
L 22 22 33 17 2 1.4
L 20 20 25 20 1 1.4
L 33 17 36 13 1 1.5
L 36 13 41 13 1 1.6
L 21 26 22 22 4 1
E 22 32 3 3 1
E 22 32 1.5 1.5 5
L 22 32 27 36 1 1.2
"""),
    ("sailboat", "قایق بادبانی", "Sailboat", "teal", """
R 0 38 47 47 8
L 2 38 17 38 3 1.4
L 30 41 45 41 3 1.4
P 1 5,32 42,32 34,41 13,41
P 4 8,34 40,34 33,39 14,39
L 24 8 24 32 1 1.4
P 2 22,10 22,31 6,31
P 3 21,13 21,29 9,29
P 5 26,12 26,29 39,29
P 7 27,15 27,28 36,28
L 24 8 29 11 1 1
L 29 11 24 13 6 1
D 5 42 7
D 43 44 7
"""),
    ("steam-train", "قطار بخار", "Steam Train", "navy", """
R 3 36 44 39 1
R 6 22 29 35 4
R 8 24 28 34 2
R 29 17 42 35 1
R 31 19 40 33 2
R 33 21 39 26 8
R 14 15 23 23 1
R 16 17 21 24 5
R 11 12 15 17 1
R 12 13 14 16 9
E 13 8 4 3 11
E 8 5 5 3 11
E 18 4 4 2 11
E 11 38 5 5 1
E 11 38 3 3 5
E 26 38 5 5 1
E 26 38 3 3 5
E 39 38 4.5 4.5 1
E 39 38 2.5 2.5 5
R 4 29 7 34 5
"""),
    ("travel-suitcase", "چمدان سفر", "Travel Suitcase", "coral", """
R 17 8 31 16 1
R 19 10 29 16 9
R 9 14 39 39 1
R 11 16 37 37 2
R 14 18 34 35 3
R 15 18 17 36 4
R 31 18 33 36 4
R 9 23 12 29 5
R 36 23 39 29 5
R 12 39 17 42 1
R 31 39 36 42 1
R 20 24 28 27 1
R 21 25 27 26 7
D 24 32 6
"""),
    ("treasure-chest", "صندوقچه گنج", "Treasure Chest", "amber", """
P 1 7,21 10,12 18,9 30,9 38,12 41,21
P 4 9,20 12,13 20,11 29,11 36,14 39,20
R 7 21 41 38 1
R 9 23 39 36 2
R 13 21 17 38 5
R 31 21 35 38 5
R 9 28 39 30 4
R 20 23 28 34 1
R 22 24 26 32 5
E 24 28 1.7 1.7 1
L 11 17 37 17 3 1
E 24 10 3 2 5
E 29 8 2 2 5
E 19 8 2 2 5
"""),
    ("hourglass", "ساعت شنی", "Hourglass", "violet", """
R 11 7 37 10 1
R 13 8 35 9 5
R 11 38 37 41 1
R 13 39 35 40 5
P 1 13,10 35,10 29,22 35,38 13,38 19,22
P 8 16,11 32,11 27,22 32,37 16,37 21,22
P 5 17,12 31,12 25,21 23,21
P 2 18,36 30,36 24,27
L 24 22 24 29 5 0.7
E 24 29 2 1.4 5
L 14 11 14 37 9 1
L 34 11 34 37 9 1
"""),
    ("telescope", "تلسکوپ", "Telescope", "navy", """
L 24 29 15 42 1 1.6
L 24 29 33 42 1 1.6
L 24 29 24 42 1 1.5
P 1 10,15 34,7 38,16 14,24
P 2 12,16 33,9 35,15 14,22
P 4 8,14 15,12 20,24 13,26
P 5 9,15 14,14 17,23 13,24
L 17 23 26 28 1 2.1
E 25 29 3.5 3.5 1
E 25 29 2 2 5
E 36 11 4.5 5.5 1
E 36 11 2.8 4 8
D 39 8 7
D 43 4 5
D 7 8 5
"""),
    ("microscope", "میکروسکوپ", "Microscope", "mint", """
R 9 38 39 42 1
R 12 39 36 41 2
R 16 29 34 32 1
R 18 30 33 31 9
P 1 24,12 28,14 22,24 19,22
P 9 24,14 26,15 21,22 20,21
P 1 22,6 34,12 31,18 19,12
P 2 23,7 32,12 30,16 21,12
L 28 22 36 30 1 3
L 36 30 32 38 2 3
E 27 26 5 5 1
E 27 26 3 3 9
R 20 34 27 38 1
R 22 35 25 37 5
"""),
    ("toy-robot", "ربات اسباب‌بازی", "Toy Robot", "teal", """
L 24 5 24 9 1 1.5
E 24 4 2.5 2.5 6
R 12 10 36 25 1
R 14 12 34 23 2
R 16 14 32 21 9
E 20 17 2.5 2.5 1
E 28 17 2.5 2.5 1
D 20 16 7
D 28 16 7
R 21 21 27 22 1
R 11 26 37 38 1
R 13 28 35 36 2
R 16 30 32 34 9
E 24 32 3 3 5
R 6 28 11 35 1
R 7 29 10 34 3
R 37 28 42 35 1
R 38 29 41 34 3
R 16 38 20 43 1
R 28 38 32 43 1
R 18 39 19 42 9
R 29 39 30 42 9
"""),
    ("game-controller", "دسته بازی", "Game Controller", "violet", """
P 1 10,19 19,16 29,16 38,19 44,27 43,37 38,39 31,33 17,33 10,39 5,37 4,27
P 2 11,21 19,18 29,18 37,21 42,28 41,36 38,37 31,31 17,31 10,37 7,36 6,28
R 13 22 16 31 1
R 10 25 19 28 1
E 33 24 2.2 2.2 6
E 38 28 2.2 2.2 5
E 32 31 2.2 2.2 8
E 27 27 2.2 2.2 10
R 21 20 27 21 4
D 22 24 7
D 26 24 7
L 11 36 15 34 3 1
L 37 34 41 36 3 1
"""),
    ("typewriter", "ماشین تحریر", "Typewriter", "amber", """
R 14 4 34 23 1
R 16 6 32 23 7
L 19 11 29 11 9 0.7
L 19 15 28 15 9 0.7
L 19 19 29 19 9 0.7
R 8 21 40 38 1
P 2 10,23 38,23 42,36 6,36
R 12 25 36 28 4
R 13 30 35 34 9
R 15 35 33 36 7
E 15 27 1.4 1.4 7
E 21 27 1.4 1.4 7
E 27 27 1.4 1.4 7
E 33 27 1.4 1.4 7
E 17 32 1.4 1.4 7
E 23 32 1.4 1.4 7
E 29 32 1.4 1.4 7
"""),
    ("camping-lantern", "فانوس کمپ", "Camping Lantern", "amber", """
E 24 9 10 8 1
E 24 9 7 5.5 0
R 17 11 31 15 1
R 19 12 29 14 5
R 14 17 34 37 1
R 16 19 32 35 8
E 24 27 6 8 5
E 24 27 4 6 7
R 13 36 35 40 1
R 15 37 33 39 4
L 14 18 14 36 9 1.6
L 34 18 34 36 9 1.6
L 20 16 28 16 5 1.5
D 24 26 7
"""),
    ("world-globe", "کره جغرافیا", "World Globe", "blue", """
E 24 22 17 17 1
E 24 22 15 15 8
P 10 13,16 20,10 26,13 27,19 23,21 18,24 13,20
P 10 26,26 32,22 37,25 34,32 28,34 24,30
P 10 18,29 22,27 24,32 20,35 15,34
E 24 22 8 15 2
E 24 22 6 14 8
L 8 22 40 22 7 0.7
L 24 5 24 38 7 0.7
L 24 38 24 43 1 1.8
R 15 43 33 45 1
R 18 44 30 44 5
"""),
    ("magnetic-compass", "قطب‌نمای سفر", "Compass", "mint", """
E 24 24 19 19 1
E 24 24 17 17 5
E 24 24 15 15 7
E 24 24 12 12 8
P 4 24,7 28,24 24,19 20,24
P 6 24,41 20,24 24,29 28,24
L 24 11 24 14 1 0.8
L 24 34 24 37 1 0.8
L 11 24 14 24 1 0.8
L 34 24 37 24 1 0.8
E 24 24 2.5 2.5 1
E 24 24 1 1 5
D 24 5 9
D 43 24 9
D 24 43 9
D 5 24 9
"""),
    ("paint-palette", "پالت نقاشی", "Paint Palette", "rose", """
P 1 7,23 9,13 17,7 29,7 39,13 42,23 38,31 28,35 19,41 10,37 7,31
P 2 9,23 11,14 18,9 28,9 37,14 40,23 36,29 28,33 19,39 12,35 9,30
E 14 31 4 5 1
E 14 31 2.8 3.5 0
E 18 16 4 4 6
E 29 15 4 4 5
E 35 23 4 4 8
E 25 29 4 4 10
E 16 23 3.2 3.2 7
L 31 38 43 7 1 2.3
L 31 38 41 13 9 1.4
P 4 43,7 45,3 46,10
"""),
    ("book-stack", "کتاب‌های رنگی", "Stacked Books", "violet", """
P 1 7,30 39,30 42,36 9,36
P 2 9,31 38,31 40,35 11,35
R 11 33 39 34 7
P 1 10,22 42,22 39,29 7,29
P 6 12,24 40,24 38,28 9,28
R 13 25 38 27 7
P 1 8,14 36,14 40,21 12,21
P 10 10,16 35,16 38,20 13,20
R 14 17 35 19 7
L 15 15 17 21 5 1
L 12 23 13 29 5 1
L 12 31 13 36 5 1
L 30 13 35 10 1 1
"""),
    ("birthday-gift", "جعبه هدیه", "Gift Box", "coral", """
R 8 21 40 40 1
R 10 23 38 38 2
R 21 22 27 39 5
R 6 17 42 23 1
R 8 19 40 21 3
R 21 18 27 23 5
P 1 23,17 13,14 11,8 15,5 22,8 25,17
P 6 23,16 15,13 14,9 16,8 21,10
P 1 25,17 35,14 37,8 33,5 26,8 23,17
P 6 25,16 33,13 34,9 32,8 27,10
E 24 17 3 3 5
L 17 26 17 36 3 1
L 32 26 32 36 3 1
"""),
    ("table-fan", "پنکه رومیزی", "Table Fan", "teal", """
R 22 34 26 42 1
R 23 35 25 41 9
E 24 42 13 3 1
E 24 41 11 1.5 2
E 24 20 18 18 1
E 24 20 16 16 9
E 24 20 14 14 7
P 2 24,20 17,8 23,5 28,11
P 3 24,20 37,13 40,19 30,25
P 4 24,20 28,34 22,35 18,26
E 24 20 5.5 5.5 1
E 24 20 3.5 3.5 5
E 24 20 1.6 1.6 7
L 8 20 40 20 1 0.5
L 24 4 24 36 1 0.5
"""),
    ("sewing-machine", "چرخ خیاطی", "Sewing Machine", "plum", """
R 6 35 42 40 1
R 8 36 40 38 9
P 1 12,14 35,14 40,20 40,34 33,34 33,21 21,21 20,34 11,34
P 2 14,16 34,16 38,21 38,32 35,32 35,19 19,19 18,32 13,32
E 33 15 5 5 1
E 33 15 3 3 5
L 17 22 17 34 1 1.3
L 14 31 24 31 9 1
R 11 11 22 14 1
R 13 12 20 13 5
R 24 34 30 35 7
D 35 27 7
"""),
    ("fountain-pen", "خودنویس", "Fountain Pen", "navy", """
P 1 11,38 31,10 37,15 17,42
P 2 14,38 32,13 35,15 17,39
P 4 8,41 13,36 18,40 13,44
P 9 31,9 35,5 42,12 38,16
P 1 33,6 36,3 45,11 42,14
L 16 39 9 44 1 1
L 31 11 39 17 5 1.2
L 24 20 29 24 7 1
E 38 10 2 2 5
L 12 42 16 43 6 1
"""),
]


def create_pack(destination):
    if len(PICTURES) != 30:
        raise ValueError("Exactly thirty distinct object levels are required")
    manifest = []
    assets = {}
    seen = set()
    for slug, title_fa, title_en, theme, instructions in PICTURES:
        ident = f"online-object-{slug}"
        if ident in seen:
            raise ValueError(f"Duplicate ID: {ident}")
        seen.add(ident)
        sprite = draw(theme, instructions)
        level = {
            "schemaVersion": 2,
            "levelId": ident,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": sprite.side,
            "height": sprite.side,
            "palette": sprite.palette,
            "cells": sprite.cells,
        }
        level["checksum"] = checksum(level)
        blob = compact(level)
        if len(blob) > 262144:
            raise ValueError(f"Level too large: {ident}")
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1,
            "title": title_fa, "titleEn": title_en,
            "category": "objects",
            "width": sprite.side, "height": sprite.side,
            "bytes": len(blob), "checksum": level["checksum"],
        })
        assets[f"levels/{stem}.json"] = blob
        assets[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, data in assets.items():
            archive.writestr(name, data)
    print(f"Created {len(manifest)} object pictures: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_objects_30_pack.py <content.zip>")
    create_pack(sys.argv[1])
