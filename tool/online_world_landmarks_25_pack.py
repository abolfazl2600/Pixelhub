#!/usr/bin/env python3
"""Twenty-five original 50x50 world-landmark color-by-number pictures.

Every landmark has a separately hand-composed pixel illustration. Only the
deterministic drawing recipes are committed: GitHub Releases serve the JSON
level grids and nearest-neighbor PNG previews to online clients.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIZE = 50
PALETTE = [
    "FFE5F4FF",  # 0 day sky
    "FF34465B",  # 1 outline
    "FFF8E9CC",  # 2 pale limestone
    "FFD6B88E",  # 3 warm limestone
    "FFAA8466",  # 4 masonry shadow
    "FFEAC063",  # 5 gold
    "FF326C52",  # 6 deep foliage
    "FF7BA67B",  # 7 foliage
    "FF2F708F",  # 8 dark water/blue
    "FF79C5DB",  # 9 bright cyan
    "FFC65350",  # 10 brick/coral
    "FFE9A3A5",  # 11 pink
    "FF4A5367",  # 12 graphite
    "FFFFFFFF",  # 13 white
    "FFF3D49B",  # 14 sand
    "FF82573D",  # 15 wood/brown
    "FF876DA5",  # 16 purple
    "FF9AABB9",  # 17 metal/stone
    "FFFFDF88",  # 18 sunlight
    "FFABC99A",  # 19 grassy foreground
]

# IDs cannot duplicate any previously published PixelHub online artwork.
# All paintings use a legacy-compatible 'patterns' category for the gallery.
PICTURES = [
    ("online-world-eiffel-tower-50", "برج ایفل", "Eiffel Tower", "eiffel"),
    ("online-world-taj-mahal-50", "تاج محل", "Taj Mahal", "taj"),
    ("online-world-colosseum-50", "کولوسئوم رم", "Roman Colosseum", "colosseum"),
    ("online-world-giza-pyramids-50", "اهرام جیزه", "Pyramids of Giza", "giza"),
    ("online-world-great-wall-china-50", "دیوار بزرگ چین", "Great Wall of China", "greatwall"),
    ("online-world-big-ben-50", "بیگ بن لندن", "Big Ben, London", "bigben"),
    ("online-world-statue-liberty-50", "مجسمه آزادی", "Statue of Liberty", "liberty"),
    ("online-world-sydney-opera-50", "اپرای سیدنی", "Sydney Opera House", "sydney"),
    ("online-world-leaning-pisa-50", "برج کج پیزا", "Leaning Tower of Pisa", "pisa"),
    ("online-world-sagrada-familia-50", "ساگرادا فامیلیا", "Sagrada Família", "sagrada"),
    ("online-world-christ-redeemer-50", "تندیس مسیح منجی", "Christ the Redeemer", "christ"),
    ("online-world-machu-picchu-50", "ماچو پیچو", "Machu Picchu", "machu"),
    ("online-world-petra-treasury-50", "خزانه پترا", "Petra Treasury", "petra"),
    ("online-world-angkor-wat-50", "انگکور وات", "Angkor Wat", "angkor"),
    ("online-world-burj-khalifa-50", "برج خلیفه", "Burj Khalifa", "burj"),
    ("online-world-golden-gate-50", "پل گلدن گیت", "Golden Gate Bridge", "golden"),
    ("online-world-london-tower-bridge-50", "تاور بریج لندن", "Tower Bridge, London", "towerbridge"),
    ("online-world-stonehenge-50", "استون‌هنج", "Stonehenge", "stonehenge"),
    ("online-world-chichen-itza-50", "چیچن ایتزا", "Chichén Itzá", "chichen"),
    ("online-world-easter-island-moai-50", "مجسمه‌های موآی", "Easter Island Moai", "moai"),
    ("online-world-parthenon-50", "معبد پارتنون", "Parthenon", "parthenon"),
    ("online-world-brandenburg-gate-50", "دروازه براندنبورگ", "Brandenburg Gate", "brandenburg"),
    ("online-world-neuschwanstein-50", "قلعه نوی‌شوان‌شتاین", "Neuschwanstein Castle", "neuschwanstein"),
    ("online-world-saint-basils-50", "کلیسای سنت باسیل", "Saint Basil's Cathedral", "basil"),
    ("online-world-marina-bay-sands-50", "مارینا بی سندز", "Marina Bay Sands", "marina"),
]


def sky(s, kind):
    s.rect(0, 0, 49, 49, 0)
    if kind in {"sydney", "liberty", "golden", "towerbridge", "marina"}:
        s.rect(0, 40, 49, 49, 8)
        for y in (42, 46):
            for x in range(0, 48, 12):
                s.line(x, y, x+7, y, 9)
    elif kind in {"giza", "petra", "chichen", "moai"}:
        s.rect(0, 41, 49, 49, 14)
        s.line(0, 42, 49, 42, 3)
    elif kind == "christ":
        s.rect(0, 44, 49, 49, 6)
    else:
        s.rect(0, 43, 49, 49, 19)
        s.line(0, 43, 49, 43, 7)
    s.ellipse(43, 8, 4, 4, 18)
    for x, y in ((7, 8), (26, 5)):
        s.ellipse(x, y, 5, 1.7, 13)
        s.ellipse(x+3, y+1, 3, 1.3, 13)


def outline_rect(s, x0, y0, x1, y1, color=3, rim=1):
    s.rect(x0-1, y0-1, x1+1, y1+1, rim)
    s.rect(x0, y0, x1, y1, color)


def triangle(s, points, color=3, rim=1):
    s.polygon(points, rim)
    cx = sum(x for x, y in points)/3
    cy = sum(y for x, y in points)/3
    s.polygon([(cx+(x-cx)*.88, cy+(y-cy)*.88) for x, y in points], color)


def arch(s, cx, y_top, bottom, radius, fill=3, opening=1):
    s.polygon([(cx-radius, bottom), (cx-radius, y_top+radius*.64),
               (cx, y_top), (cx+radius, y_top+radius*.64),
               (cx+radius, bottom)], 1)
    s.polygon([(cx-radius+1, bottom), (cx-radius+1, y_top+radius*.65+1),
               (cx, y_top+2), (cx+radius-1, y_top+radius*.65+1),
               (cx+radius-1, bottom)], fill)
    r = max(1, radius-3)
    s.polygon([(cx-r, bottom), (cx-r, y_top+r*.68+4),
               (cx, y_top+5), (cx+r, y_top+r*.68+4),
               (cx+r, bottom)], opening)


def window(s, x, y, color=1):
    s.rect(x, y, x+1, y+3, color)
    s.dot(x, y-1, color)


def dome(s, x, base, radius, color=2):
    s.ellipse(x, base, radius, radius*.8, 1)
    s.ellipse(x, base, radius-1, radius*.8-1, color)
    s.rect(x-radius, base, x+radius, base+2, 1)
    s.rect(x-radius+1, base, x+radius-1, base+1, color)
    s.line(x, base-radius*.8-4, x, base-radius*.8, 5)
    s.dot(x, round(base-radius*.8-5), 5)


def column(s, x, y0, y1, color=3, width=3):
    outline_rect(s, x-width//2, y0, x+width//2, y1, color)
    s.rect(x-width//2-1, y0-2, x+width//2+1, y0, 2)
    s.rect(x-width//2-1, y1, x+width//2+1, y1+1, 4)


def spire(s, x, top, bottom, width=5, color=3):
    s.rect(x-width//2, top+6, x+width//2, bottom, 1)
    s.rect(x-width//2+1, top+7, x+width//2-1, bottom-1, color)
    s.polygon([(x, top), (x-width//2-1, top+7),
               (x+width//2+1, top+7)], 1)
    s.polygon([(x, top+2), (x-width//2+1, top+6),
               (x+width//2-1, top+6)], color)


def steps(s, y0, left=7, right=43, count=4, color=3):
    for k in range(count):
        s.rect(left-k, y0+k*2, right+k, y0+k*2+1, 1)
        s.rect(left-k+1, y0+k*2, right+k-1, y0+k*2, color)


def draw(kind):
    s = Sprite(SIZE, PALETTE)
    sky(s, kind)

    if kind == "eiffel":
        s.line(24, 7, 24, 13, 1, radius=1)
        s.polygon([(23, 12), (26, 12), (30, 23), (34, 35),
                   (40, 44), (31, 44), (27, 33), (22, 33),
                   (18, 44), (9, 44), (16, 34), (20, 23)], 1)
        s.polygon([(24, 15), (26, 15), (29, 25), (33, 37),
                   (37, 43), (33, 43), (27, 32), (22, 32),
                   (17, 43), (13, 43), (19, 31), (22, 22)], 4)
        for y, lo, hi in ((19, 21, 27), (26, 18, 30), (34, 15, 33)):
            s.line(lo, y, hi, y, 5)
        for x, y in ((18, 34), (32, 34), (21, 26), (28, 26)):
            s.line(x, y, 24, y+6, 1, radius=.6)
        arch(s, 24, 32, 45, 6, fill=4, opening=0)
        s.rect(8, 44, 41, 46, 1)
    elif kind == "taj":
        outline_rect(s, 7, 30, 42, 43, 2)
        outline_rect(s, 11, 26, 38, 43, 13)
        dome(s, 25, 25, 11, 2)
        arch(s, 25, 29, 43, 7, fill=2, opening=8)
        for x in (5, 44):
            spire(s, x, 13, 42, 5, color=2)
            dome(s, x, 18, 4, 2)
        for x in (15, 35):
            arch(s, x, 33, 42, 3, fill=2, opening=8)
        s.rect(0, 44, 49, 46, 2)
        s.rect(23, 46, 27, 49, 9)
    elif kind == "colosseum":
        s.ellipse(25, 31, 22, 14, 1)
        s.ellipse(25, 31, 20, 12, 3)
        s.rect(4, 27, 45, 43, 1)
        s.rect(6, 28, 43, 41, 3)
        s.rect(5, 15, 26, 27, 1)
        s.rect(6, 17, 25, 26, 3)
        for y in (19, 29, 38):
            for x in range(10 if y != 19 else 8, 44 if y != 19 else 25, 7):
                arch(s, x, y, min(y+8, 43), 2.6, fill=2, opening=1)
        for y in (27, 36, 43):
            s.line(6, y, 44, y, 4)
    elif kind == "giza":
        triangle(s, [(3, 41), (19, 15), (35, 41)], 14)
        triangle(s, [(19, 41), (34, 20), (49, 41)], 3)
        triangle(s, [(0, 42), (7, 31), (16, 42)], 4)
        s.polygon([(16, 20), (19, 15), (22, 21), (19, 19)], 13)
        s.polygon([(31, 25), (34, 20), (37, 25), (34, 23)], 13)
        for x in range(3, 49, 8):
            s.line(x, 45, x+4, 45, 4)
    elif kind == "greatwall":
        s.polygon([(0, 39), (8, 32), (15, 34), (26, 20),
                   (35, 24), (43, 17), (49, 22), (49, 49), (0, 49)], 7)
        s.polygon([(0, 44), (9, 36), (17, 39), (28, 25),
                   (36, 29), (49, 20), (49, 45), (0, 49)], 6)
        s.polygon([(0, 38), (13, 36), (23, 23), (35, 30),
                   (49, 17), (49, 24), (35, 36), (23, 29),
                   (13, 43), (0, 44)], 1)
        s.polygon([(1, 39), (13, 38), (23, 25), (35, 32),
                   (48, 20), (48, 23), (35, 34), (23, 28),
                   (13, 41), (1, 42)], 3)
        for x, y in ((6, 36), (22, 22), (35, 28), (46, 16)):
            outline_rect(s, x-3, y-6, x+3, y+3, 3)
            s.rect(x-4, y-7, x+4, y-5, 1)
            window(s, x-1, y-3)
    elif kind == "bigben":
        outline_rect(s, 15, 18, 32, 44, 3)
        outline_rect(s, 18, 9, 30, 26, 2)
        triangle(s, [(16, 10), (24, 2), (32, 10)], 4)
        s.line(24, 1, 24, 5, 1)
        s.ellipse(24, 19, 6, 6, 1)
        s.ellipse(24, 19, 4, 4, 13)
        s.line(24, 19, 24, 15, 1)
        s.line(24, 19, 27, 20, 1)
        for x in (19, 27):
            for y in (30, 36, 41):
                window(s, x, y)
        for x in (7, 39):
            outline_rect(s, x-5, 32, x+3, 44, 17)
    elif kind == "liberty":
        s.rect(8, 41, 40, 46, 1)
        s.rect(12, 37, 36, 41, 3)
        s.polygon([(19, 36), (17, 22), (20, 20), (20, 14),
                   (28, 14), (30, 22), (33, 36)], 1)
        s.polygon([(20, 35), (19, 23), (22, 21), (22, 15),
                   (27, 15), (28, 23), (31, 35)], 7)
        s.ellipse(24, 15, 5, 6, 1)
        s.ellipse(24, 15, 3.4, 4, 7)
        for x0, x1 in ((17, 12), (20, 18), (24, 24), (28, 30), (31, 36)):
            s.line(x0, 11, x1, 6, 1)
        s.line(20, 24, 12, 20, 7, radius=2)
        s.line(28, 22, 34, 7, 7, radius=2)
        s.rect(32, 3, 36, 8, 5)
        s.ellipse(34, 2, 3, 3, 18)
        s.rect(13, 26, 20, 32, 1)
        s.rect(14, 27, 19, 31, 2)
    elif kind == "sydney":
        s.rect(4, 38, 47, 42, 1)
        s.rect(6, 39, 45, 41, 3)
        for points in (
            [(5, 37), (11, 15), (23, 34)],
            [(12, 37), (24, 9), (32, 37)],
            [(25, 37), (35, 17), (45, 37)],
            [(35, 37), (44, 25), (48, 37)],
        ):
            triangle(s, points, 13)
        for x in range(8, 44, 5):
            s.line(x, 39, x+2, 39, 5)
    elif kind == "pisa":
        # Deliberately lean all seven levels 1 px further right near top.
        for idx, y in enumerate(range(12, 43, 5)):
            shift = 7-idx
            s.polygon([(14+shift, y), (33+shift, y),
                       (34+shift, y+5), (15+shift, y+5)], 1)
            s.polygon([(15+shift, y+1), (32+shift, y+1),
                       (33+shift, y+4), (16+shift, y+4)], 2)
            for x in (17, 22, 27):
                window(s, x+shift, y+2)
            s.line(14+shift, y+5, 34+shift, y+5, 4)
        s.polygon([(20, 12), (23, 7), (40, 8), (41, 12)], 2)
        s.line(8, 45, 44, 45, 4)
    elif kind == "sagrada":
        outline_rect(s, 8, 31, 42, 44, 3)
        for x, t, b, width in ((12, 11, 42, 5), (22, 5, 43, 5),
                               (33, 8, 43, 5), (41, 15, 42, 4)):
            spire(s, x, t, b, width, 4)
            for y in range(t+9, b-3, 5):
                s.dot(x, y, 1)
        arch(s, 25, 28, 44, 11, 3, 1)
        for x in (14, 37):
            arch(s, x, 32, 43, 4, 3, 8)
        for x, y in ((17, 26), (29, 19), (37, 28)):
            s.ellipse(x, y, 2, 2, 9)
    elif kind == "christ":
        s.polygon([(0, 47), (12, 31), (23, 37), (34, 29),
                   (49, 45), (49, 49), (0, 49)], 6)
        s.rect(17, 41, 33, 45, 1)
        s.rect(20, 37, 30, 42, 3)
        s.ellipse(25, 12, 4.4, 5, 1)
        s.ellipse(25, 12, 3, 3.4, 17)
        s.rect(21, 18, 29, 36, 1)
        s.rect(22, 19, 28, 35, 2)
        s.line(6, 21, 44, 21, 1, radius=3)
        s.line(7, 20, 43, 20, 2, radius=1.5)
        s.line(21, 31, 18, 39, 1, radius=2)
        s.line(29, 31, 32, 39, 1, radius=2)
    elif kind == "machu":
        s.polygon([(0, 31), (12, 9), (21, 25),
                   (36, 7), (49, 27), (49, 44), (0, 44)], 17)
        s.polygon([(0, 42), (11, 25), (19, 35),
                   (29, 20), (42, 30), (49, 27), (49, 49), (0, 49)], 6)
        s.polygon([(7, 49), (9, 31), (19, 36), (26, 29),
                   (36, 36), (45, 34), (49, 49)], 7)
        for x0, y, x1 in ((7, 39, 41), (9, 35, 36), (15, 31, 29)):
            s.line(x0, y, x1, y, 2, radius=1)
        for x, y in ((12, 34), (21, 34), (31, 34), (15, 39),
                     (26, 39), (37, 39)):
            outline_rect(s, x-3, y-3, x+3, y+1, 3)
            triangle(s, [(x-4, y-3), (x, y-7), (x+4, y-3)], 4)
    elif kind == "petra":
        s.rect(0, 18, 49, 49, 4)
        s.polygon([(0, 14), (11, 20), (10, 46), (0, 49)], 10)
        s.polygon([(49, 14), (38, 20), (39, 46), (49, 49)], 10)
        outline_rect(s, 13, 24, 37, 43, 3)
        for x in (15, 21, 29, 35):
            column(s, x, 27, 41, 2, 2)
        triangle(s, [(12, 24), (25, 15), (38, 24)], 2)
        outline_rect(s, 21, 10, 29, 17, 3)
        dome(s, 25, 10, 5, 3)
        arch(s, 25, 30, 44, 4, 3, 1)
        steps(s, 44, 12, 38, 3, 3)
    elif kind == "angkor":
        outline_rect(s, 3, 36, 46, 43, 4)
        outline_rect(s, 8, 29, 41, 38, 3)
        for x, top in ((9, 20), (17, 17), (25, 10), (33, 17), (41, 20)):
            spire(s, x, top, 38, 7, 4)
            s.rect(x-5, top+10, x+5, top+12, 1)
            s.rect(x-3, top+8, x+3, top+10, 2)
        for x in (13, 25, 37):
            arch(s, x, 31, 43, 4, 4, 1)
        s.rect(0, 44, 49, 46, 8)
        for x in (5, 22, 39):
            s.line(x, 48, x+6, 48, 9)
    elif kind == "burj":
        s.rect(10, 43, 41, 46, 1)
        s.rect(15, 36, 35, 44, 17)
        s.rect(19, 26, 31, 43, 1)
        s.rect(20, 26, 30, 42, 17)
        s.rect(22, 14, 28, 43, 1)
        s.rect(23, 14, 27, 41, 17)
        s.polygon([(23, 15), (25, 3), (27, 15)], 1)
        s.line(25, 2, 25, 5, 1)
        for y in range(18, 41, 4):
            s.line(22 if y < 26 else 19, y,
                   28 if y < 26 else 31, y, 9)
        for x in (10, 39):
            outline_rect(s, x-3, 37, x+3, 45, 3)
    elif kind == "golden":
        s.line(0, 31, 49, 31, 10, radius=2)
        s.line(0, 34, 49, 34, 1, radius=1)
        for x in (13, 37):
            outline_rect(s, x-3, 11, x+3, 39, 10)
            s.rect(x-1, 15, x+1, 30, 0)
            s.rect(x-4, 10, x+4, 12, 1)
        s.line(0, 22, 13, 11, 10, radius=1)
        s.line(13, 11, 37, 11, 10, radius=1)
        s.line(37, 11, 49, 22, 10, radius=1)
        for x in range(1, 49, 4):
            hang = 11 if 13 <= x <= 37 else 22-int(abs(x-25)/2)
            s.line(x, hang, x, 31, 10, radius=.6)
        s.rect(0, 34, 49, 36, 10)
    elif kind == "towerbridge":
        for x in (12, 37):
            outline_rect(s, x-5, 20, x+5, 40, 3)
            triangle(s, [(x-6, 20), (x, 12), (x+6, 20)], 12)
            spire(s, x-5, 13, 22, 3, 4)
            spire(s, x+5, 13, 22, 3, 4)
            arch(s, x, 27, 41, 4, 3, 8)
        s.rect(16, 23, 33, 25, 1)
        s.rect(16, 25, 33, 26, 5)
        s.line(0, 37, 49, 37, 17, radius=1.6)
        for x in (3, 20, 30, 46):
            s.line(x, 37, x, 40, 1)
        s.line(17, 37, 24, 30, 3)
        s.line(25, 30, 33, 37, 3)
    elif kind == "stonehenge":
        for x, h in ((7, 16), (16, 13), (28, 19), (40, 15)):
            outline_rect(s, x-3, h, x+3, 43, 17)
            s.line(x-2, h+3, x-2, 42, 2)
        s.rect(4, 13, 20, 17, 1)
        s.rect(5, 14, 19, 16, 17)
        s.rect(24, 16, 44, 20, 1)
        s.rect(25, 17, 43, 19, 17)
        s.rect(0, 45, 49, 47, 6)
    elif kind == "chichen":
        for level in range(7):
            left = 6+level*2
            right = 43-level*2
            y = 42-level*4
            s.rect(left-1, y-1, right+1, y+3, 1)
            s.rect(left, y, right, y+2, 3 if level%2 == 0 else 2)
            s.rect(left+1, y, left+4, y, 4)
        outline_rect(s, 19, 10, 30, 18, 4)
        arch(s, 25, 12, 19, 4, 3, 1)
        for yy in range(21, 45, 4):
            s.rect(23, yy, 26, yy+2, 14)
        s.line(4, 46, 46, 46, 4)
    elif kind == "moai":
        s.rect(0, 39, 49, 49, 7)
        for x, base, scale in ((12, 42, 1.0), (30, 45, 1.15)):
            s.polygon([(x-6*scale, base), (x-6*scale, base-21*scale),
                       (x-2*scale, base-28*scale),
                       (x+5*scale, base-26*scale),
                       (x+8*scale, base-21*scale),
                       (x+8*scale, base)], 1)
            s.polygon([(x-5*scale, base-1), (x-5*scale, base-20*scale),
                       (x-1*scale, base-26*scale),
                       (x+4*scale, base-24*scale),
                       (x+7*scale, base-20*scale),
                       (x+7*scale, base-1)], 4)
            s.line(x-4*scale, base-17*scale,
                   x+4*scale, base-17*scale, 1)
            s.polygon([(x, base-18*scale), (x+7*scale, base-12*scale),
                       (x+1*scale, base-11*scale)], 2)
            s.line(x-2*scale, base-8*scale,
                   x+4*scale, base-8*scale, 1)
        s.rect(2, 44, 45, 47, 6)
    elif kind == "parthenon":
        triangle(s, [(4, 22), (25, 10), (46, 22)], 2)
        s.rect(4, 22, 45, 26, 1)
        s.rect(5, 23, 44, 24, 3)
        for x in (9, 17, 25, 33, 41):
            column(s, x, 27, 42, 2, 3)
        s.rect(3, 43, 47, 45, 1)
        s.rect(4, 44, 46, 44, 4)
        steps(s, 45, 6, 44, 2, 2)
        s.polygon([(18, 21), (25, 15), (32, 21)], 4)
    elif kind == "brandenburg":
        s.rect(3, 20, 47, 24, 1)
        s.rect(4, 21, 46, 22, 2)
        s.rect(7, 15, 43, 19, 3)
        for x in (9, 17, 25, 33, 41):
            column(s, x, 25, 43, 2, 4)
        s.rect(2, 43, 48, 46, 1)
        s.rect(3, 44, 47, 45, 3)
        s.rect(21, 11, 29, 15, 1)
        s.rect(22, 12, 28, 14, 6)
        s.line(25, 12, 26, 7, 1, radius=.8)
        for x in (17, 33):
            s.line(x, 11, x+3, 9, 1)
    elif kind == "neuschwanstein":
        s.polygon([(0, 41), (11, 29), (18, 33), (30, 25),
                   (43, 32), (49, 27), (49, 49), (0, 49)], 6)
        outline_rect(s, 8, 28, 42, 43, 2)
        outline_rect(s, 14, 24, 34, 42, 3)
        for x, top, base, w in ((11, 12, 40, 7), (23, 7, 43, 7),
                                (36, 15, 40, 7), (43, 23, 42, 5)):
            spire(s, x, top, base, w, 2)
        for x in (16, 28, 39):
            for y in (30, 37):
                window(s, x, y)
        s.rect(18, 34, 27, 43, 1)
        s.rect(21, 38, 24, 42, 15)
        s.line(5, 45, 45, 45, 1)
    elif kind == "basil":
        outline_rect(s, 7, 31, 43, 44, 3)
        for x, height, r, color in (
            (10, 27, 5, 10), (20, 17, 6, 9),
            (30, 13, 7, 16), (40, 25, 5, 9),
        ):
            spire(s, x, height+5, 41, 5, 3)
            s.ellipse(x, height, r, r*.8, 1)
            s.ellipse(x, height+1, r-1, r*.8-1, color)
            s.line(x, height-r-4, x, height-r, 5)
            s.dot(x, round(height-r-5), 5)
            s.line(x-2, height+1, x+2, height+3, 13)
        arch(s, 25, 32, 44, 7, 2, 8)
        for x in (13, 37):
            arch(s, x, 37, 43, 3, 3, 8)
    elif kind == "marina":
        for x in (9, 23, 37):
            outline_rect(s, x-6, 22, x+6, 42, 17)
            for yy in range(24, 42, 4):
                for xx in range(x-4, x+6, 4):
                    s.rect(xx, yy, xx+1, yy+2, 8)
        s.polygon([(3, 18), (12, 15), (42, 15), (48, 18),
                   (44, 23), (7, 22)], 1)
        s.polygon([(5, 18), (15, 17), (42, 17), (46, 19),
                   (43, 21), (7, 21)], 3)
        s.ellipse(25, 15, 9, 2, 7)
        s.rect(0, 43, 49, 45, 9)
    else:
        raise ValueError("Unknown landmark illustration: " + kind)
    return s


def make_level(item):
    identifier, title_fa, title_en, kind = item
    art = draw(kind)
    level = {
        "schemaVersion": 2,
        "levelId": identifier,
        "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": SIZE,
        "height": SIZE,
        "palette": art.palette,
        "cells": art.cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(PICTURES) != 25 or len({i[0] for i in PICTURES}) != 25:
        raise ValueError("Expected 25 unique world landmark pictures")
    manifest = []
    files = {}
    for item in PICTURES:
        ident, fa, en, _kind = item
        level = make_level(item)
        content = compact(level)
        if len(content) > 262144:
            raise ValueError("Level exceeds online size limit: " + ident)
        stem = ident + "-v1"
        manifest.append({
            "id": ident, "version": 1, "title": fa, "titleEn": en,
            "category": "patterns", "width": SIZE, "height": SIZE,
            "bytes": len(content), "checksum": level["checksum"],
        })
        files["levels/" + stem + ".json"] = content
        files["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    destination = pathlib.Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, body in files.items():
            bundle.writestr(path, body)
    print("Prepared 25 world landmarks at exactly 50x50:", destination)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_world_landmarks_25_pack.py <content.zip>")
    create_pack(sys.argv[1])
