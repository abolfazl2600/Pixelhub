#!/usr/bin/env python3
"""25 original Persian-rug-inspired 65x65 online coloring designs.

These are individually drawn geometric/floral interpretations, not scans of
existing carpets. Only recipes are committed. The Pages workflow publishes
immutable schema-v2 color-by-number JSON levels and PNG previews as a Release.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 65
# Palette indices: fringe, outline, field, border, turquoise, leaf,
# cream, gold, coral, highlight. Each illustration has its own colorway.
PALETTES = {
    "ruby": ["FFF4E7D4", "FF372B3B", "FF9E3849", "FF6C283E", "FF227D91",
             "FF4B825C", "FFFBE9BD", "FFE8B858", "FFE98874", "FF8FD0C0"],
    "navy": ["FFF1E8D9", "FF242F4B", "FF263F72", "FF41618C", "FF2993AA",
             "FF698A66", "FFF9E6BD", "FFE5B966", "FFBA5266", "FF99C7DA"],
    "ivory": ["FFF2E4D1", "FF42506A", "FFF2E7CF", "FFB2B4AD", "FF286F9F",
              "FF64836B", "FFFFFFFF", "FFD5A34A", "FFAE6276", "FF93C9D0"],
    "teal": ["FFF1E4CB", "FF264D5B", "FF197B7B", "FF23556C", "FF57BEC2",
             "FF578564", "FFFFE8BD", "FFE8BF70", "FFCD685F", "FFAFDACA"],
    "saffron": ["FFF1DDC3", "FF584438", "FFC68B37", "FF985C39", "FF396F87",
                "FF527052", "FFFFE4A5", "FFF5CA61", "FFC7504A", "FF9ACAB8"],
    "plum": ["FFF2E4CF", "FF322E47", "FF694264", "FF976F91", "FF3A8290",
             "FF4A795B", "FFFFE8CC", "FFF0C36D", "FFE09587", "FFB4C3D1"],
    "earth": ["FFEADAC5", "FF493A32", "FF835A40", "FFB3815B", "FF568F8C",
              "FF657744", "FFF8DEAE", "FFECC06B", "FFBD5749", "FFB5CEB4"],
    "rose": ["FFF6E5DF", "FF4D344B", "FFC46877", "FF973F58", "FF437E91",
             "FF528368", "FFFFE5CE", "FFE1AB63", "FFF6B2A1", "FF9CD3CC"],
}

# Fresh stable identifiers; not named online-iran-* so rug art stays in
# the Patterns gallery category rather than the Iranian-architecture overlay.
# id, Persian label, English label, motif, palette, border style
PICTURES = [
    ("online-persian-rug-tabriz-medallion-65", "فرش ترنج تبریز", "Tabriz Medallion Rug", "tabriz", "ruby", 0),
    ("online-persian-rug-kashan-flowers-65", "فرش گل‌وبوته کاشان", "Kashan Floral Rug", "kashan", "navy", 1),
    ("online-persian-rug-isfahan-arabesque-65", "فرش اسلیمی اصفهان", "Isfahan Arabesque Rug", "isfahan", "teal", 2),
    ("online-persian-rug-nain-ivory-65", "فرش لچک ترنج نائین", "Nain Ivory Corner-Medallion Rug", "nain", "ivory", 3),
    ("online-persian-rug-qom-silk-65", "فرش ابریشمی قم", "Qom Silk Bouquet Rug", "qom", "rose", 4),
    ("online-persian-rug-heriz-geometric-65", "فرش هندسی هریس", "Heriz Geometric Rug", "heriz", "ruby", 5),
    ("online-persian-rug-bijar-herati-65", "فرش ماهی بیجار", "Bijar Herati Rug", "bijar", "navy", 0),
    ("online-persian-rug-senneh-boteh-65", "فرش بته‌جقه سنه", "Senneh Boteh Rug", "senneh", "plum", 1),
    ("online-persian-rug-bakhtiari-garden-65", "فرش خشتی بختیاری", "Bakhtiari Garden Rug", "bakhtiari", "earth", 2),
    ("online-persian-rug-qashqai-diamonds-65", "قالی سه‌ترنج قشقایی", "Qashqai Triple-Diamond Rug", "qashqai", "saffron", 3),
    ("online-persian-rug-gabbeh-lion-65", "گبه شیر فارس", "Fars Lion Gabbeh Rug", "gabbeh", "earth", 4),
    ("online-persian-rug-turkmen-gul-65", "قالی گل ترکمن", "Turkmen Gul Rug", "turkmen", "ruby", 5),
    ("online-persian-rug-baluch-prayer-65", "قالی محرابی بلوچ", "Baluch Prayer Rug", "baluch", "plum", 0),
    ("online-persian-rug-afshar-diamonds-65", "قالی لوزی افشار", "Afshar Diamond Rug", "afshar", "teal", 1),
    ("online-persian-rug-kerman-tree-65", "فرش درخت زندگی کرمان", "Kerman Tree of Life Rug", "kerman", "ivory", 2),
    ("online-persian-rug-mashhad-medallion-65", "فرش ترنج مشهد", "Mashhad Floral Medallion Rug", "mashhad", "rose", 3),
    ("online-persian-rug-ardabil-star-65", "فرش ستاره اردبیل", "Ardabil Star Rug", "ardabil", "navy", 4),
    ("online-persian-rug-varamin-minakhani-65", "فرش میناخانی ورامین", "Varamin Mina Khani Rug", "varamin", "teal", 5),
    ("online-persian-rug-sarouk-roses-65", "فرش دسته‌گل ساروق", "Sarouk Rose Bouquet Rug", "sarouk", "ruby", 0),
    ("online-persian-rug-hamedan-stripes-65", "قالی راه‌راه همدان", "Hamedan Striped Rug", "hamedan", "earth", 1),
    ("online-persian-rug-shiraz-cypress-65", "فرش سرو شیراز", "Shiraz Cypress Rug", "shiraz", "saffron", 2),
    ("online-persian-rug-yazd-four-gardens-65", "فرش چهارباغ یزد", "Yazd Four Gardens Rug", "yazd", "ivory", 3),
    ("online-persian-rug-sistan-sun-65", "گلیم خورشیدی سیستان", "Sistan Sun Kilim", "sistan", "saffron", 4),
    ("online-persian-rug-mazandaran-kilim-65", "گلیم راه‌راه مازندران", "Mazandaran Striped Kilim", "mazandaran", "teal", 5),
    ("online-persian-rug-lori-animals-65", "گلیم حیوانات لری", "Lori Animal Motif Kilim", "lori", "plum", 0),
]


def diamond(s, x, y, rx, ry, color):
    s.polygon([(x, y-ry), (x+rx, y), (x, y+ry), (x-rx, y)], color)


def star(s, x, y, outer, inner, color, points=8):
    vertices = []
    for step in range(points*2):
        theta = -math.pi/2 + step*math.pi/points
        radius = outer if step % 2 == 0 else inner
        vertices.append((x+radius*math.cos(theta), y+radius*math.sin(theta)))
    s.polygon(vertices, color)


def bloom(s, x, y, scale=3, color=8):
    for ox, oy in ((-scale, 0), (scale, 0), (0, -scale), (0, scale)):
        s.ellipse(x+ox, y+oy, max(1, scale*.72), max(1, scale*.72), color)
    s.ellipse(x, y, max(1.1, scale*.78), max(1.1, scale*.78), 7)
    s.dot(x, y, 6)


def leaf(s, x, y, direction=1):
    s.ellipse(x, y, 2.6, 1.8, 5)
    s.line(x-2, y, x+2, y, 9, radius=.5)
    s.dot(x+direction, y-1, 9)


def boteh(s, x, y, scale=1, color=8):
    # Asymmetric curling paisley with an interior droplet.
    vertices = [(x-5*scale, y+8*scale), (x-9*scale, y+2*scale),
                (x-7*scale, y-6*scale), (x-1*scale, y-10*scale),
                (x+3*scale, y-15*scale), (x+9*scale, y-11*scale),
                (x+5*scale, y-7*scale), (x+9*scale, y+1*scale),
                (x+5*scale, y+9*scale)]
    s.polygon(vertices, 1)
    s.polygon([(x-4*scale, y+5*scale), (x-6*scale, y),
               (x-4*scale, y-5*scale), (x+1*scale, y-7*scale),
               (x+4*scale, y-12*scale), (x+6*scale, y-11*scale),
               (x+3*scale, y-6*scale), (x+7*scale, y+1*scale),
               (x+3*scale, y+6*scale)], color)
    if scale >= .65:
        diamond(s, x, y, 3*scale, 5*scale, 7)


def medallion(s, x=32, y=32, rx=18, ry=21, colors=(1, 7, 4, 6)):
    for r, c in ((1, colors[0]), (.87, colors[1]), (.70, colors[2]),
                 (.53, colors[0]), (.38, colors[3])):
        diamond(s, x, y, rx*r, ry*r, c)
    star(s, x, y, rx*.32, rx*.16, 8)
    s.dot(x, y, 7)


def vine(s, x0, y0, x1, y1):
    s.line(x0, y0, x1, y1, 5, radius=.8)
    s.line(x0, y0, x1, y1, 9, radius=.35)


def bird(s, x, y, flip=1):
    s.ellipse(x, y, 4.0, 2.5, 1)
    s.ellipse(x, y, 3.1, 1.8, 4)
    s.ellipse(x+4*flip, y-3, 1.9, 1.9, 1)
    s.ellipse(x+4*flip, y-3, 1.2, 1.2, 6)
    s.polygon([(x-3*flip, y), (x-7*flip, y-5),
               (x-5*flip, y+2)], 8)
    s.dot(x+4*flip, y-4, 1)
    s.line(x-1, y+2, x-1, y+5, 1)
    s.line(x+1, y+2, x+1, y+5, 1)


def cypress(s, x, top, base):
    s.rect(x-2, base-5, x+2, base, 1)
    s.polygon([(x, top), (x-5, base-8), (x-2, base-8),
               (x-7, base-5), (x+7, base-5), (x+2, base-8),
               (x+5, base-8)], 5)
    s.polygon([(x, top+6), (x-3, base-10), (x+2, base-11)], 9)


def rug_border(s, style):
    # Leave two pixel rows of pale fringe above/below the carpet.
    for x in range(6, 60, 3):
        s.line(x, 0, x, 2, 1)
        s.line(x, 62, x, 64, 1)
    for y in (4, 60):
        s.line(5, y, 59, y, 1)
    for x in (5, 59):
        s.line(x, 4, x, 60, 1)
    s.rect(6, 5, 58, 8, 3)
    s.rect(6, 56, 58, 59, 3)
    s.rect(6, 9, 10, 55, 3)
    s.rect(54, 9, 58, 55, 3)
    s.line(11, 9, 53, 9, 1)
    s.line(11, 55, 53, 55, 1)
    s.line(11, 9, 11, 55, 1)
    s.line(53, 9, 53, 55, 1)

    for x in range(10, 57, 7):
        if style in (0, 3):
            diamond(s, x, 7, 2, 2, 7)
            diamond(s, x, 57, 2, 2, 7)
        elif style in (1, 4):
            bloom(s, x, 7, 1, 8)
            bloom(s, x, 57, 1, 8)
        else:
            star(s, x, 7, 2.5, 1.0, 6, points=6)
            star(s, x, 57, 2.5, 1.0, 6, points=6)
    for y in range(13, 55, 7):
        if style % 2 == 0:
            diamond(s, 8, y, 2, 2, 7)
            diamond(s, 56, y, 2, 2, 7)
        else:
            star(s, 8, y, 2.4, 1, 6, points=6)
            star(s, 56, y, 2.4, 1, 6, points=6)
    for x, y in ((8, 7), (56, 7), (8, 57), (56, 57)):
        s.dot(x, y, 6)


def motif(kind, s):
    if kind == "tabriz":
        medallion(s, rx=18, ry=21)
        for x, y in ((16, 16), (48, 16), (16, 48), (48, 48)):
            bloom(s, x, y, 3, 8)
            diamond(s, x, y, 2.6, 4, 4)
        for x, y in ((32, 14), (32, 50), (14, 32), (50, 32)):
            star(s, x, y, 3.5, 1.8, 8)
    elif kind == "kashan":
        for x in (17, 32, 47):
            vine(s, x, 14, 32, 49)
            for y in (18, 32, 46):
                bloom(s, x, y, 2.6, 8 if x != 32 else 4)
        for x, y in ((22, 24), (42, 24), (22, 40), (42, 40)):
            s.line(x-4, y+4, x+4, y-4, 5)
            bloom(s, x, y, 2.5, 8)
    elif kind == "isfahan":
        medallion(s, rx=15, ry=18, colors=(1, 6, 4, 7))
        for ox, oy in ((0, -19), (0, 19), (-19, 0), (19, 0)):
            star(s, 32+ox, 32+oy, 5, 2, 7)
        for x, y in ((18, 17), (46, 17), (18, 47), (46, 47)):
            s.ellipse(x, y, 5, 3, 5)
            s.ellipse(x, y, 3.5, 1.7, 9)
            bloom(s, x, y, 2, 8)
        for x in (14, 50):
            vine(s, x, 15, x, 49)
    elif kind == "nain":
        medallion(s, rx=13, ry=16, colors=(1, 4, 6, 7))
        for x, y, direction in ((13, 13, 1), (51, 13, -1),
                                (13, 51, -1), (51, 51, 1)):
            diamond(s, x, y, 13, 13, 4)
            diamond(s, x, y, 10, 10, 6)
            star(s, x+3*direction, y, 4, 1.4, 8)
        for x, y in ((32, 12), (32, 52), (12, 32), (52, 32)):
            bloom(s, x, y, 2, 8)
    elif kind == "qom":
        for x, y in ((32, 21), (25, 27), (39, 27), (20, 37),
                     (32, 36), (44, 37), (27, 45), (37, 45)):
            vine(s, 32, 50, x, y)
            bloom(s, x, y, 3.1, 8)
        for x, y in ((16, 17), (49, 17), (16, 50), (49, 50)):
            bloom(s, x, y, 2, 4)
        s.polygon([(29, 48), (36, 48), (40, 53), (24, 53)], 7)
    elif kind == "heriz":
        diamond(s, 32, 32, 21, 24, 1)
        diamond(s, 32, 32, 18, 21, 8)
        diamond(s, 32, 32, 15, 17, 7)
        diamond(s, 32, 32, 10, 13, 4)
        diamond(s, 32, 32, 6, 8, 6)
        for x, y in ((16, 17), (48, 17), (16, 47), (48, 47)):
            star(s, x, y, 7, 3, 7)
        for x in (20, 44):
            s.line(x-3, 25, x+3, 25, 6)
            s.line(x-3, 40, x+3, 40, 6)
    elif kind == "bijar":
        # Allover linked Herati "fish" leaves and rosettes.
        for y in range(17, 51, 11):
            for x in range(18+(y//11)%2*5, 53, 11):
                diamond(s, x, y, 5, 5, 1)
                diamond(s, x, y, 3.5, 3.5, 4)
                leaf(s, x-5, y-4)
                leaf(s, x+5, y+4)
                s.dot(x, y, 7)
    elif kind == "senneh":
        for y in (19, 38, 51):
            for x in (21, 43):
                boteh(s, x, y, .52, 8 if y == 38 else 4)
        for x in (16, 32, 48):
            star(s, x, 13, 2.7, 1.3, 7)
    elif kind == "bakhtiari":
        for col in range(3):
            for row in range(3):
                x0, y0 = 13+col*14, 13+row*14
                s.rect(x0, y0, x0+12, y0+12, 1)
                s.rect(x0+1, y0+1, x0+11, y0+11, 6 if (row+col)%2 else 4)
                if (row+col)%3 == 0:
                    cypress(s, x0+6, y0+2, y0+11)
                elif (row+col)%3 == 1:
                    bloom(s, x0+6, y0+6, 2.6, 8)
                else:
                    diamond(s, x0+6, y0+6, 5, 5, 7)
                    s.dot(x0+6, y0+6, 8)
    elif kind == "qashqai":
        for y, radius in ((19, 12), (33, 14), (47, 12)):
            diamond(s, 32, y, radius, 10, 1)
            diamond(s, 32, y, radius-3, 7, 4)
            diamond(s, 32, y, radius-6, 4, 8)
            s.dot(32, y, 6)
        for x in (16, 48):
            for y in (15, 29, 44, 51):
                star(s, x, y, 3, 1.5, 7)
    elif kind == "gabbeh":
        # A legible lion silhouette on an uncluttered field.
        s.ellipse(32, 29, 9, 9, 1)
        s.ellipse(32, 29, 7.5, 7.5, 7)
        s.ellipse(29, 28, 1.5, 1.5, 6)
        s.ellipse(35, 28, 1.5, 1.5, 6)
        s.dot(29, 28, 1); s.dot(35, 28, 1)
        diamond(s, 32, 33, 2, 2, 8)
        s.ellipse(32, 43, 13, 7, 1)
        s.ellipse(32, 43, 11, 5, 7)
        for x in (24, 29, 38, 43):
            s.rect(x, 45, x+2, 52, 1)
        s.line(43, 43, 50, 38, 1, radius=1.5)
        s.line(50, 38, 47, 35, 1, radius=1)
        for x, y in ((17, 19), (48, 19), (17, 49), (49, 49)):
            star(s, x, y, 4, 1.6, 8)
    elif kind == "turkmen":
        for y in (18, 32, 46):
            for x in (19, 32, 45):
                s.rect(x-6, y-6, x+6, y+6, 1)
                s.rect(x-5, y-5, x+5, y+5, 8)
                diamond(s, x, y, 5, 5, 7)
                star(s, x, y, 4, 2, 4)
                s.dot(x, y, 6)
    elif kind == "baluch":
        # A mihrab with an outlined pointed arch and a hanging lamp.
        s.polygon([(14, 52), (14, 28), (32, 12), (50, 28),
                   (50, 52)], 1)
        s.polygon([(17, 50), (17, 29), (32, 17), (47, 29),
                   (47, 50)], 4)
        s.polygon([(20, 48), (20, 30), (32, 22), (44, 30),
                   (44, 48)], 2)
        s.line(32, 17, 32, 33, 7)
        s.ellipse(32, 37, 6, 6, 1)
        s.ellipse(32, 37, 4, 4, 7)
        star(s, 32, 37, 3.5, 1.4, 8)
        for x, y in ((21, 40), (43, 40), (26, 26), (38, 26)):
            bloom(s, x, y, 2, 8)
    elif kind == "afshar":
        for y in (17, 30, 43):
            for x in (18, 32, 46):
                diamond(s, x, y, 9, 9, 1)
                diamond(s, x, y, 7, 7, 8)
                diamond(s, x, y, 5, 5, 4)
                diamond(s, x, y, 2, 3, 7)
        for x in range(16, 51, 7):
            s.dot(x, 52, 6)
    elif kind == "kerman":
        s.line(32, 50, 32, 22, 1, radius=2)
        s.line(32, 43, 18, 32, 5, radius=1.6)
        s.line(32, 36, 47, 25, 5, radius=1.6)
        s.line(32, 30, 24, 19, 5, radius=1.6)
        for x, y in ((20, 30), (17, 26), (27, 21), (24, 16),
                     (42, 29), (47, 23), (39, 18), (33, 14)):
            s.ellipse(x, y, 5, 2.8, 5)
            bloom(s, x, y, 2.5, 8)
        bird(s, 20, 47, 1)
        bird(s, 45, 46, -1)
        s.rect(26, 49, 38, 52, 11 if False else 3)
    elif kind == "mashhad":
        medallion(s, rx=16, ry=20, colors=(1, 8, 4, 7))
        for x, y in ((16, 17), (48, 17), (16, 47), (48, 47)):
            bloom(s, x, y, 3, 7)
        for y in (19, 45):
            for x in (24, 40):
                bloom(s, x, y, 1.7, 8)
        for x, y in ((14, 32), (50, 32)):
            diamond(s, x, y, 4, 8, 7)
    elif kind == "ardabil":
        star(s, 32, 32, 21, 13, 1, points=16)
        star(s, 32, 32, 18, 10, 7, points=16)
        star(s, 32, 32, 14, 8, 4, points=8)
        star(s, 32, 32, 10, 5, 6)
        star(s, 32, 32, 5, 2, 8)
        for x in (16, 48):
            s.line(x, 12, x, 17, 7)
            diamond(s, x, 24, 4, 7, 7)
            diamond(s, x, 24, 2, 5, 8)
            s.dot(x, 30, 6)
    elif kind == "varamin":
        for y in (17, 28, 39, 50):
            for x in (17, 28, 39, 50):
                bloom(s, x, y, 2.8, 8 if (x+y)%2 else 7)
                for dx, dy in ((-5, -4), (5, -4), (-5, 4), (5, 4)):
                    leaf(s, x+dx, y+dy)
    elif kind == "sarouk":
        for x, y, r in ((32, 17, 3.2), (22, 25, 3.5), (42, 25, 3.5),
                        (17, 35, 3), (32, 33, 4), (47, 35, 3),
                        (23, 44, 3), (41, 44, 3)):
            vine(s, 32, 50, x, y)
            bloom(s, x, y, r, 8)
        for x, y in ((21, 19), (43, 19), (18, 47), (46, 47)):
            leaf(s, x, y)
        s.polygon([(26, 48), (38, 48), (36, 53), (28, 53)], 7)
    elif kind == "hamedan":
        for y in range(13, 54, 7):
            s.rect(12, y, 52, y+2, 4 if y%2 else 8)
            for x in range(13, 53, 8):
                s.line(x, y+4, x+4, y+2, 1)
                s.line(x+4, y+2, x+8, y+4, 7)
        for y in (20, 34, 48):
            for x in (19, 32, 45):
                diamond(s, x, y, 3, 3, 6)
    elif kind == "shiraz":
        cypress(s, 32, 13, 51)
        for x, y in ((17, 21), (47, 21), (17, 38), (47, 38),
                     (20, 48), (44, 48)):
            bloom(s, x, y, 3, 8)
        for x in (16, 48):
            vine(s, x, 17, x, 50)
        star(s, 32, 14, 3, 1.3, 7)
    elif kind == "yazd":
        # Four rectangular garden panels separated by water channels.
        s.rect(30, 12, 34, 52, 4)
        s.rect(13, 30, 51, 34, 4)
        for x, y in ((21, 21), (43, 21), (21, 43), (43, 43)):
            s.rect(x-8, y-8, x+8, y+8, 1)
            s.rect(x-7, y-7, x+7, y+7, 5)
            bloom(s, x, y, 3.2, 8)
            for dx, dy in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
                s.dot(x+dx, y+dy, 6)
        star(s, 32, 32, 5.2, 2.2, 7)
    elif kind == "sistan":
        star(s, 32, 32, 21, 10, 1, points=12)
        star(s, 32, 32, 18, 8, 7, points=12)
        s.ellipse(32, 32, 11, 11, 8)
        s.ellipse(32, 32, 8, 8, 7)
        star(s, 32, 32, 7, 3, 6)
        for x, y in ((17, 17), (47, 17), (17, 47), (47, 47)):
            diamond(s, x, y, 5, 5, 4)
            diamond(s, x, y, 2, 2, 6)
    elif kind == "mazandaran":
        for y in range(12, 54, 5):
            s.rect(12, y, 52, y+2, [4, 8, 6, 7][(y//5)%4])
            for x in range(13, 52, 7):
                s.line(x, y, x+3, y+2, 1)
        for x, y in ((21, 20), (43, 20), (21, 43), (43, 43)):
            diamond(s, x, y, 4, 5, 1)
            diamond(s, x, y, 2, 3, 7)
        s.line(14, 32, 50, 32, 6, radius=1)
    elif kind == "lori":
        for x, y in ((21, 22), (44, 22), (21, 44), (44, 44)):
            # Stylized mountain goat: horns, legs, body and tail.
            s.ellipse(x, y, 6, 3.3, 7)
            s.ellipse(x+6, y-3, 2.3, 2.3, 7)
            s.line(x+6, y-5, x+3, y-9, 1)
            s.line(x+7, y-5, x+9, y-9, 1)
            s.line(x-4, y+2, x-4, y+7, 1)
            s.line(x+3, y+2, x+3, y+7, 1)
            s.line(x-6, y, x-9, y-3, 1)
            s.dot(x+7, y-3, 6)
        star(s, 32, 32, 9, 4, 8)
        star(s, 32, 32, 5, 2, 4)
        for x in (16, 48):
            diamond(s, x, 33, 3, 6, 6)
    else:
        raise ValueError("Unknown Persian carpet style: " + kind)


def make_level(item):
    ident, fa, en, kind, palette, border_style = item
    s = Sprite(SIDE, PALETTES[palette])
    s.rect(0, 0, 64, 64, 0)
    s.rect(5, 3, 59, 61, 1)
    s.rect(6, 4, 58, 60, 3)
    s.rect(11, 9, 53, 55, 2)
    motif(kind, s)
    rug_border(s, border_style)
    level = {
        "schemaVersion": 2,
        "levelId": ident,
        "levelVersion": 1,
        "titles": {"fa": fa, "en": en},
        "width": SIDE,
        "height": SIDE,
        "palette": s.palette,
        "cells": s.cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(PICTURES) != 25 or len({item[0] for item in PICTURES}) != 25:
        raise ValueError("Exactly 25 unique Persian carpet levels are required")
    manifest, assets = [], {}
    for item in PICTURES:
        ident, fa, en, _kind, _palette, _border = item
        level = make_level(item)
        data = compact(level)
        if len(data) > 262144:
            raise ValueError("Level exceeds online size limit: " + ident)
        stem = ident + "-v1"
        manifest.append({
            "id": ident, "version": 1, "title": fa,
            "titleEn": en, "category": "patterns",
            "width": SIDE, "height": SIDE,
            "bytes": len(data), "checksum": level["checksum"],
        })
        assets["levels/" + stem + ".json"] = data
        assets["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, payload in assets.items():
            bundle.writestr(name, payload)
    print("Prepared 25 unique Persian 65x65 rug levels:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_persian_rugs_25_pack.py <content.zip>")
    create_pack(sys.argv[1])
