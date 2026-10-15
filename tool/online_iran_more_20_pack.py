#!/usr/bin/env python3
"""Twenty original 65x65 Iranian color-by-number illustrations.

Only drawing recipes are committed. The Web Pages publisher generates the
immutable release ZIP with schema-v2 JSON levels and PNG previews.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 65
PALETTE = [
    "FFEAF3F5",  # 0 sky
    "FF303E50",  # 1 contour
    "FF76665A",  # 2 stone shade
    "FFCA9A71",  # 3 stone
    "FFF2D2A5",  # 4 light stone
    "FF2686A1",  # 5 turquoise tile
    "FF76C8CE",  # 6 tile shine
    "FF39694F",  # 7 deep green
    "FF83B187",  # 8 foliage
    "FF285976",  # 9 deep water
    "FF62B3C9",  # 10 water
    "FF88563F",  # 11 timber
    "FFBA7558",  # 12 brick
    "FFDCA77E",  # 13 warm clay
    "FFFEF1D9",  # 14 ivory
    "FFE5BB53",  # 15 gold
    "FFC35147",  # 16 red
    "FF263344",  # 17 cave/night
    "FF9DA0A4",  # 18 grey rock
    "FFFFDD89",  # 19 sunlight
    "FF876E93",  # 20 mauve
    "FFE9B5B0",  # 21 pink
    "FFB4A188",  # 22 earth
    "FFFFFFFF",  # 23 white
]

# Existing published IDs are never reused.
PICTURES = [
    ("online-iran-tabiat-bridge-65", "پل طبیعت تهران", "Tabiat Bridge, Tehran", "patterns", "tabiat"),
    ("online-iran-quran-gate-65", "دروازه قرآن شیراز", "Quran Gate, Shiraz", "patterns", "quran"),
    ("online-iran-veresk-bridge-65", "پل ورسک", "Veresk Railway Bridge", "patterns", "veresk"),
    ("online-iran-white-bridge-ahvaz-65", "پل سفید اهواز", "White Bridge, Ahvaz", "patterns", "white"),
    ("online-iran-rudkhan-castle-65", "قلعه رودخان", "Rudkhan Castle", "patterns", "rudkhan"),
    ("online-iran-alamut-castle-65", "قلعه الموت", "Alamut Castle", "patterns", "alamut"),
    ("online-iran-babak-castle-65", "قلعه بابک", "Babak Castle", "patterns", "babak"),
    ("online-iran-shushtar-watermills-65", "سازه‌های آبی شوشتر", "Shushtar Historical Hydraulic System", "patterns", "shushtar"),
    ("online-iran-shazdeh-garden-65", "باغ شاهزاده ماهان", "Shazdeh Garden, Mahan", "nature", "shazdeh"),
    ("online-iran-agha-bozorg-65", "مسجد آقابزرگ کاشان", "Agha Bozorg Mosque, Kashan", "patterns", "agha"),
    ("online-iran-isfahan-jameh-65", "مسجد جامع اصفهان", "Jameh Mosque of Isfahan", "patterns", "jameh"),
    ("online-iran-yazd-fire-temple-65", "آتشکده زرتشتیان یزد", "Yazd Fire Temple", "patterns", "fire"),
    ("online-iran-saad-al-saltaneh-65", "کاروانسرای سعدالسلطنه", "Sa'd al-Saltaneh Caravanserai", "patterns", "saad"),
    ("online-iran-ali-sadr-cave-65", "غار علیصدر همدان", "Ali-Sadr Cave", "nature", "alisadr"),
    ("online-iran-badab-e-surt-65", "چشمه‌های باداب سورت", "Badab-e Surt Springs", "nature", "badab"),
    ("online-iran-chabahar-martian-65", "کوه‌های مریخی چابهار", "Martian Mountains of Chabahar", "nature", "martian"),
    ("online-iran-boteh-jegheh-65", "بته‌جقه ایرانی", "Persian Boteh Jegheh Motif", "patterns", "boteh"),
    ("online-iran-lalejin-pottery-65", "سفال لالجین", "Lalejin Glazed Pottery", "objects", "pottery"),
    ("online-iran-persian-tar-65", "ساز تار ایرانی", "Persian Tar Instrument", "objects", "tar"),
    ("online-iran-persian-gulf-lenj-65", "لنج سنتی جنوب ایران", "Traditional Persian Gulf Lenj", "objects", "lenj"),
]


def canvas(color=0):
    art = Sprite(SIDE, PALETTE)
    if color:
        art.rect(0, 0, 64, 64, color)
    return art


def daytime(s, ground=54, ground_color=8):
    s.ellipse(52, 10, 5, 5, 19)
    for x, y in ((7, 10), (22, 7), (43, 17)):
        s.ellipse(x, y, 5, 2, 23)
        s.ellipse(x + 4, y + 1, 4, 2, 23)
    if ground < 65:
        s.rect(0, ground, 64, 64, ground_color)
        s.line(0, ground, 64, ground, 7)


def mountains(s, color=18, baseline=52):
    s.polygon([(0, baseline), (0, 32), (12, 21), (21, 34), (33, 17),
               (44, 32), (55, 23), (64, 34), (64, baseline)], color)
    s.polygon([(27, 25), (33, 17), (39, 26), (34, 23), (31, 25)], 23)


def pine(s, x, base, height=18):
    s.rect(x-1, base-5, x+1, base, 11)
    s.polygon([(x, base-height), (x-6, base-4), (x+6, base-4)], 7)
    s.polygon([(x, base-height+4), (x-5, base-6), (x+5, base-6)], 8)


def arch(s, x, top, bottom, half, frame=1, fill=4, opening=17):
    s.polygon([(x-half, bottom), (x-half, top+half*.54), (x, top),
               (x+half, top+half*.54), (x+half, bottom)], frame)
    h = max(1, half-2)
    s.polygon([(x-h, bottom-1), (x-h, top+h*.54+3), (x, top+3),
               (x+h, top+h*.54+3), (x+h, bottom-1)], fill)
    h = max(1, half-5)
    s.polygon([(x-h, bottom-1), (x-h, top+h*.55+6), (x, top+7),
               (x+h, top+h*.55+6), (x+h, bottom-1)], opening)


def dome(s, x, center_y, radius=11, tile=5):
    s.ellipse(x, center_y, radius+1, radius*.84, 1)
    s.ellipse(x, center_y+1, radius, radius*.78, tile)
    s.rect(x-radius, center_y, x+radius, center_y+radius, 1)
    s.rect(x-radius+2, center_y, x+radius-2, center_y+radius-2, tile)
    s.ellipse(x-4, center_y-3, 4, 2, 6)
    s.line(x, center_y-radius-5, x, center_y-radius, 15, radius=.8)
    s.dot(x, center_y-radius-6, 15)


def tower(s, x, top, bottom, width=6, color=3):
    s.rect(x-width//2-1, top, x+width//2+1, bottom, 1)
    s.rect(x-width//2, top+1, x+width//2, bottom-1, color)
    s.rect(x-width//2-2, top-2, x+width//2+2, top+1, 1)
    s.rect(x-width//2-1, top-1, x+width//2+1, top, 4)
    s.rect(x-1, top+6, x+1, top+11, 17)


def battlements(s, start, end, y, size=4):
    s.rect(start, y+3, end, y+7, 2)
    for x in range(start, end, size+2):
        s.rect(x, y, min(x+size-1, end), y+3, 3)


def water(s, start=51):
    s.rect(0, start, 64, 64, 9)
    for y in range(start+2, 65, 4):
        for x in range((y*3)%11, 63, 15):
            s.line(x, y, x+7, y, 10)


def bricks(s, x0, y0, x1, y1):
    for y in range(y0, y1, 5):
        for x in range(x0 + (3 if y//5 % 2 else 0), x1, 9):
            s.line(x, y, min(x+5, x1), y, 4)


def scene(kind):
    s = canvas(17 if kind in {"alisadr", "saad"} else 0)
    if kind == "tabiat":
        daytime(s, 56)
        for x in (4, 11, 56, 62):
            pine(s, x, 58, 21)
        s.polygon([(0, 35), (22, 27), (48, 31), (64, 22),
                   (64, 29), (46, 39), (20, 35), (0, 43)], 1)
        s.polygon([(0, 36), (22, 29), (47, 33), (64, 25),
                   (64, 28), (47, 36), (21, 32), (0, 40)], 12)
        s.line(5, 46, 58, 40, 1, radius=2)
        s.line(4, 44, 58, 38, 15, radius=1)
        for x in range(8, 63, 8):
            s.line(x, 40-(x*.1), x+2, 52, 2)
            s.line(x+2, 52, x+3, 56, 1)
        for x in (19, 47):
            s.line(x, 32, x+4, 47, 1)
            s.line(x+4, 47, x+12, 35, 1)
    elif kind == "quran":
        daytime(s, 57, 22); mountains(s, 18, 57)
        s.rect(9, 25, 55, 56, 1); s.rect(11, 27, 53, 55, 3)
        arch(s, 32, 28, 57, 17, 1, 4, 0)
        s.rect(14, 17, 50, 25, 1); s.rect(15, 18, 49, 24, 4)
        s.rect(19, 12, 45, 18, 1); s.rect(20, 13, 44, 17, 3)
        for x in (14, 50): tower(s, x, 23, 56, 4)
        for x in range(22, 45, 5): s.dot(x, 20, 5)
        s.rect(0, 59, 64, 64, 18)
    elif kind == "veresk":
        daytime(s, 58, 7)
        s.polygon([(0, 26), (10, 18), (23, 26), (24, 56), (0, 63)], 18)
        s.polygon([(64, 16), (51, 26), (43, 28), (44, 58), (64, 64)], 2)
        s.polygon([(0, 32), (16, 30), (22, 38), (22, 58), (0, 64)], 7)
        s.rect(17, 26, 48, 30, 1)
        s.rect(18, 27, 47, 29, 4)
        s.ellipse(32, 41, 16, 17, 1)
        s.ellipse(32, 43, 13, 15, 3)
        s.ellipse(32, 46, 10, 14, 0)
        s.rect(17, 29, 47, 33, 2)
        for x in range(19, 49, 4): s.rect(x, 24, x+1, 26, 1)
        s.line(29, 61, 31, 55, 10)
    elif kind == "white":
        daytime(s, 55, 9); water(s, 52)
        s.line(0, 39, 64, 39, 23, radius=2)
        s.line(0, 43, 64, 43, 1, radius=1)
        for x in (14, 49):
            s.line(x, 13, x, 49, 23, radius=2.4)
            s.line(x, 13, x, 49, 18, radius=.7)
        s.polygon([(0, 26), (15, 32), (30, 36), (48, 30), (64, 24),
                   (64, 28), (48, 34), (30, 40), (15, 36), (0, 30)], 23)
        for x in range(3, 63, 5):
            height = 25+abs(32-x)*.23
            s.line(x, height, x, 39, 23)
        for x in (14, 49): s.rect(x-3, 47, x+3, 52, 2)
    elif kind == "rudkhan":
        daytime(s, 62, 7); mountains(s, 8, 56)
        s.polygon([(0, 60), (9, 46), (18, 51), (29, 35),
                   (42, 47), (54, 33), (64, 43), (64, 64), (0, 64)], 7)
        s.polygon([(6, 55), (20, 42), (39, 44), (55, 34),
                   (61, 39), (62, 58)], 2)
        s.polygon([(7, 53), (20, 43), (38, 45), (53, 36),
                   (58, 39), (61, 53)], 3)
        battlements(s, 12, 52, 34)
        for x, top in ((12, 29), (32, 26), (52, 27)):
            tower(s, x, top, 47, 8)
            s.rect(x-3, top-5, x+3, top-3, 1)
        for x in (6, 60): pine(s, x, 60, 27)
    elif kind == "alamut":
        daytime(s, 62, 22); mountains(s, 18, 52)
        s.polygon([(5, 64), (21, 41), (27, 26), (38, 22),
                   (49, 39), (63, 64)], 2)
        s.polygon([(9, 64), (25, 43), (29, 30), (38, 26),
                   (47, 45), (59, 64)], 18)
        s.polygon([(18, 37), (22, 25), (28, 21), (45, 21),
                   (48, 28), (48, 39)], 1)
        s.polygon([(20, 36), (24, 27), (29, 23), (43, 23),
                   (46, 28), (46, 37)], 3)
        battlements(s, 23, 46, 18, 3)
        tower(s, 30, 10, 30, 6)
        tower(s, 43, 14, 34, 5)
        arch(s, 34, 28, 39, 5, 1, 4, 17)
        for x, y in ((13, 50), (52, 52), (21, 60)):
            s.line(x, y, x+4, y-5, 2)
    elif kind == "babak":
        daytime(s, 63, 8)
        s.polygon([(0, 63), (17, 40), (26, 32), (35, 19),
                   (45, 35), (64, 63)], 18)
        s.polygon([(5, 64), (27, 38), (35, 21),
                   (43, 40), (62, 64)], 2)
        s.polygon([(18, 35), (27, 25), (43, 25),
                   (48, 37), (44, 41), (20, 40)], 1)
        s.polygon([(20, 35), (27, 27), (42, 27),
                   (46, 36), (43, 39), (22, 38)], 4)
        battlements(s, 24, 44, 20, 3)
        tower(s, 20, 18, 39, 6)
        tower(s, 45, 15, 40, 6)
        s.rect(31, 28, 37, 39, 1)
        s.rect(33, 30, 35, 38, 17)
        for x, y in ((9, 49), (52, 55), (30, 55)):
            s.line(x, y, x+5, y+4, 22)
    elif kind == "shushtar":
        daytime(s, 60, 22)
        s.rect(3, 18, 61, 38, 2); s.rect(5, 20, 59, 37, 3)
        battlements(s, 4, 60, 16, 4)
        for x in (13, 32, 51):
            arch(s, x, 22, 46, 8, 1, 4, 9)
        water(s, 50)
        for x in (11, 20, 30, 42, 53):
            s.rect(x, 39, x+5, 52, 6)
            for y in range(42, 63, 4):
                s.line(x, y, x+2, y+2, 23)
        s.line(0, 46, 64, 46, 15, radius=1)
    elif kind == "shazdeh":
        daytime(s, 64, 7); mountains(s, 18, 40)
        s.rect(14, 19, 50, 35, 1); s.rect(16, 21, 48, 33, 4)
        s.rect(20, 13, 44, 21, 3); s.polygon([(19, 14), (32, 7), (45, 14)], 1)
        arch(s, 32, 24, 35, 6, 1, 4, 17)
        for x in (20, 44): arch(s, x, 25, 34, 3, 1, 3, 5)
        s.polygon([(23, 35), (41, 35), (60, 64), (4, 64)], 4)
        s.polygon([(28, 36), (36, 36), (46, 64), (18, 64)], 9)
        s.polygon([(29, 36), (35, 36), (43, 64), (21, 64)], 10)
        for y, left, right in ((40, 26, 38), (46, 22, 42), (53, 17, 47), (60, 12, 52)):
            s.line(left, y, right, y, 23, radius=1)
            s.dot(32, y-1, 6)
        for x in (8, 15, 50, 57):
            pine(s, x, 57, 23 if x in (8, 57) else 18)
    elif kind == "agha":
        daytime(s, 63, 22)
        s.rect(3, 33, 61, 62, 1); s.rect(5, 35, 59, 60, 3)
        dome(s, 32, 26, 10)
        for x in (11, 53):
            tower(s, x, 12, 51, 5, 5)
            s.rect(x-3, 17, x+3, 21, 6)
        arch(s, 32, 35, 62, 12, 1, 5, 17)
        for x in (11, 53): arch(s, x, 43, 58, 5, 1, 4, 9)
        s.polygon([(19, 61), (27, 54), (37, 54), (45, 61)], 22)
        s.line(0, 62, 64, 62, 5)
    elif kind == "jameh":
        daytime(s, 62, 22)
        s.rect(4, 30, 60, 61, 1); s.rect(6, 32, 58, 59, 3)
        dome(s, 19, 26, 12, 5)
        dome(s, 48, 29, 8, 6)
        arch(s, 34, 27, 62, 13, 1, 5, 17)
        arch(s, 34, 35, 62, 9, 4, 6, 9)
        for x in (8, 57):
            tower(s, x, 14, 57, 5, 5)
        for x in (15, 54): arch(s, x, 43, 59, 4, 1, 4, 9)
        for x in range(23, 47, 4): s.dot(x, 39, 6)
    elif kind == "fire":
        daytime(s, 61, 8)
        s.rect(5, 25, 59, 57, 1); s.rect(7, 27, 57, 55, 4)
        s.polygon([(4, 25), (32, 13), (60, 25)], 1)
        s.polygon([(8, 24), (32, 16), (56, 24)], 3)
        for x in (11, 19, 45, 53):
            s.rect(x, 30, x+3, 54, 1)
            s.rect(x+1, 31, x+2, 53, 14)
        arch(s, 32, 33, 56, 9, 1, 4, 17)
        # Simplified gold Faravahar emblem in the tympanum.
        s.ellipse(32, 21, 3, 3, 15)
        s.line(15, 21, 29, 22, 15, radius=1)
        s.line(35, 22, 49, 21, 15, radius=1)
        for d in range(3):
            s.line(17+d, 23+d, 27, 24+d, 12)
            s.line(37, 24+d, 47-d, 23+d, 12)
        s.rect(0, 58, 64, 64, 22)
    elif kind == "saad":
        s.rect(0, 0, 64, 64, 2)
        s.polygon([(0, 0), (64, 0), (51, 23), (13, 23)], 12)
        s.polygon([(0, 64), (20, 38), (44, 38), (64, 64)], 3)
        s.polygon([(0, 0), (17, 26), (17, 52), (0, 64)], 11)
        s.polygon([(64, 0), (47, 26), (47, 52), (64, 64)], 11)
        arch(s, 32, 6, 57, 23, 1, 3, 17)
        arch(s, 32, 16, 55, 15, 1, 12, 17)
        arch(s, 32, 27, 54, 8, 1, 4, 5)
        for x in (9, 55):
            arch(s, x, 25, 61, 7, 1, 3, 17)
        for x in (13, 51):
            s.line(x, 0, x, 64, 4, radius=1)
        bricks(s, 4, 5, 15, 45)
        bricks(s, 49, 5, 61, 45)
        s.line(20, 63, 28, 45, 4)
        s.line(44, 63, 36, 45, 4)
    elif kind == "alisadr":
        s.polygon([(0, 0), (64, 0), (64, 19), (52, 32),
                   (40, 16), (28, 29), (12, 20), (0, 29)], 2)
        s.polygon([(0, 0), (64, 0), (64, 12), (53, 18),
                   (39, 11), (25, 20), (8, 13), (0, 24)], 18)
        for x, y, h in ((4, 5, 26), (14, 2, 30), (27, 4, 18),
                        (38, 3, 24), (53, 3, 28), (62, 5, 19)):
            s.polygon([(x-4, y), (x+4, y), (x, y+h)], 11)
            s.polygon([(x-2, y), (x+2, y), (x, y+h-6)], 3)
        water(s, 43)
        for x in (7, 20, 49, 59):
            s.polygon([(x-4, 64), (x, 48), (x+5, 64)], 2)
        s.polygon([(17, 49), (50, 49), (44, 56), (23, 56)], 1)
        s.polygon([(20, 49), (47, 49), (42, 54), (24, 54)], 12)
        for x in (28, 39):
            s.ellipse(x, 45, 2.4, 2.4, 14)
            s.rect(x-2, 48, x+2, 51, 16)
        s.line(44, 46, 47, 58, 4)
    elif kind == "badab":
        daytime(s, 64, 22)
        mountains(s, 18, 40)
        bands = [(36, 3, 12, 47, 9), (43, 1, 17, 56, 6),
                 (50, 0, 19, 63, 10), (57, 0, 14, 64, 15)]
        for y, left, color, right, trim in bands:
            s.polygon([(left, y), (right, y-5), (right, y+7), (left, y+9)], color)
            s.line(left, y+2, right, y-3, trim, radius=1.2)
            s.line(left, y+5, right, y, 23, radius=.7)
        for x, y, rx in ((10, 42, 10), (35, 40, 12), (50, 47, 14),
                         (21, 54, 16), (43, 58, 19), (17, 62, 18)):
            s.ellipse(x, y, rx, 3, 3)
            s.ellipse(x, y-1, rx-2, 2, 6 if y%2 else 10)
        for x, y in ((8, 49), (51, 38), (28, 60)):
            s.dot(x, y, 23)
    elif kind == "martian":
        daytime(s, 64, 22)
        s.polygon([(0, 56), (8, 22), (16, 45), (25, 13),
                   (34, 47), (44, 18), (54, 46), (63, 26),
                   (64, 64), (0, 64)], 12)
        s.polygon([(0, 64), (9, 32), (15, 56), (26, 23),
                   (33, 57), (45, 30), (53, 59), (64, 38),
                   (64, 64)], 3)
        for x, top in ((8, 22), (25, 13), (44, 18), (63, 26)):
            for y in range(top+6, 62, 6):
                s.line(max(0, x-5), y, min(64, x+5), y+2, 2)
        s.polygon([(0, 58), (18, 55), (35, 60), (50, 55),
                   (64, 59), (64, 64), (0, 64)], 22)
        for x in (7, 30, 56): s.line(x, 62, x+4, 62, 14)
    elif kind == "boteh":
        s.rect(0, 0, 64, 64, 14)
        for x in range(3, 64, 9):
            s.dot(x, 3, 5); s.dot(x, 61, 5)
        for y in range(7, 61, 9):
            s.dot(3, y, 5); s.dot(61, y, 5)
        s.polygon([(24, 56), (13, 46), (10, 34), (14, 22), (24, 15),
                   (29, 4), (40, 9), (34, 18), (44, 25),
                   (52, 37), (48, 49), (39, 57)], 1)
        s.polygon([(24, 53), (16, 45), (14, 34), (18, 23), (28, 16),
                   (30, 9), (36, 10), (30, 20), (41, 27),
                   (48, 37), (45, 47), (37, 53)], 16)
        s.polygon([(26, 47), (19, 38), (21, 29), (31, 22),
                   (40, 32), (43, 41), (36, 49)], 15)
        s.ellipse(31, 36, 7, 8, 5)
        s.ellipse(31, 36, 4, 5, 6)
        for x, y in ((18, 27), (39, 41), (26, 49), (40, 30)):
            s.dot(x, y, 23)
        for x, y in ((10, 12), (51, 16), (10, 54), (53, 53)):
            s.ellipse(x, y, 4, 4, 5)
            s.ellipse(x, y, 2, 2, 15)
    elif kind == "pottery":
        daytime(s, 61, 22)
        s.ellipse(32, 57, 24, 3, 2)
        s.ellipse(32, 40, 20, 21, 1)
        s.ellipse(32, 39, 18, 19, 5)
        s.rect(25, 11, 39, 28, 1); s.rect(27, 12, 37, 28, 6)
        s.ellipse(32, 11, 10, 3.5, 1)
        s.ellipse(32, 10, 8, 2, 6)
        s.ellipse(32, 9, 5, 1.5, 17)
        s.ellipse(32, 39, 13, 12, 6)
        s.ellipse(32, 39, 10, 9, 5)
        for y in (30, 46, 52):
            s.line(16, y, 48, y, 1)
            s.line(18, y+1, 46, y+1, 14)
        for x in (21, 31, 41):
            s.polygon([(x, 37), (x+4, 42), (x, 46), (x-4, 42)], 15)
            s.dot(x, 42, 23)
        s.ellipse(18, 26, 6, 9, 1)
        s.ellipse(46, 26, 6, 9, 1)
        s.ellipse(18, 26, 3, 6, 0)
        s.ellipse(46, 26, 3, 6, 0)
    elif kind == "tar":
        s.rect(0, 0, 64, 64, 14)
        s.polygon([(9, 59), (16, 44), (24, 39), (28, 24),
                   (37, 24), (42, 40), (51, 46), (55, 60),
                   (49, 63), (14, 63)], 22)
        s.ellipse(25, 50, 15, 12, 1)
        s.ellipse(40, 53, 15, 11, 1)
        s.ellipse(26, 50, 13, 10, 11)
        s.ellipse(40, 53, 13, 9, 12)
        s.ellipse(26, 50, 8, 7, 4)
        s.ellipse(40, 53, 8, 6, 4)
        s.polygon([(28, 19), (36, 19), (37, 49), (28, 49)], 1)
        s.polygon([(30, 19), (34, 19), (35, 47), (30, 47)], 11)
        s.rect(28, 8, 37, 21, 1)
        s.rect(30, 9, 35, 20, 11)
        for y in (10, 14, 18):
            s.line(27, y, 23, y-2, 15)
            s.line(38, y, 42, y-2, 15)
        for x in (31, 33, 35):
            s.line(x, 9, x-2, 60, 23, radius=.5)
        s.rect(26, 46, 39, 48, 1)
        s.line(20, 62, 45, 62, 2)
    elif kind == "lenj":
        daytime(s, 64, 10); water(s, 48)
        s.polygon([(4, 43), (59, 43), (51, 56), (18, 57)], 1)
        s.polygon([(7, 45), (56, 45), (49, 54), (19, 55)], 11)
        s.line(12, 48, 53, 48, 15, radius=.6)
        for x in range(18, 53, 7):
            s.dot(x, 51, 4)
        s.line(32, 9, 32, 43, 1, radius=1.7)
        s.polygon([(30, 11), (30, 39), (9, 40)], 4)
        s.polygon([(35, 15), (35, 40), (53, 40)], 23)
        s.line(7, 42, 32, 8, 11, radius=.7)
        s.line(32, 9, 57, 43, 11, radius=.7)
        s.polygon([(32, 10), (42, 12), (32, 16)], 16)
        s.rect(41, 40, 54, 43, 1)
        s.rect(43, 36, 52, 40, 4)
        for x in (45, 50): s.dot(x, 38, 9)
        for x in (12, 36, 59): s.line(x, 60, x+5, 60, 23)
    else:
        raise ValueError("Unknown Iranian illustration: " + kind)
    return s


def make_level(item):
    identifier, title_fa, title_en, _category, kind = item
    art = scene(kind)
    level = {
        "schemaVersion": 2,
        "levelId": identifier,
        "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": SIDE,
        "height": SIDE,
        "palette": art.palette,
        "cells": art.cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(PICTURES) != 20 or len({item[0] for item in PICTURES}) != 20:
        raise ValueError("Expected twenty unique Iranian illustrations")
    manifest, assets = [], {}
    for item in PICTURES:
        identifier, title_fa, title_en, category, _kind = item
        level = make_level(item)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Online illustration exceeds download limit: " + identifier)
        stem = identifier + "-v1"
        manifest.append({
            "id": identifier, "version": 1, "title": title_fa,
            "titleEn": title_en, "category": category,
            "width": SIDE, "height": SIDE,
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
        for filename, body in assets.items():
            archive.writestr(filename, body)
    print("Prepared 20 distinct 65x65 Iranian levels:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_iran_more_20_pack.py <content.zip>")
    create_pack(sys.argv[1])
