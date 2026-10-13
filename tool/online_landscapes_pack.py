#!/usr/bin/env python3
"""Ten original, detailed 64x64 landscape color-by-number paintings.

Drawing instructions alone live in Git. The verified Web Pages workflow
packages schema-v2 numbered level JSONs, small PNG previews and the manifest
as an immutable GitHub Release, outside the app and Git history.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


SIZE = 64


def scene(palette, bands):
    s = Sprite(SIZE, palette)
    start = 0
    for until, color in bands:
        s.rect(0, start, SIZE - 1, until - 1, color)
        start = until
    return s


def ridge(s, points, color):
    """Solid land from an interpolated ridge to the bottom edge."""
    segments = iter(zip(points, points[1:]))
    a, b = next(segments)
    for x in range(SIZE):
        while x > b[0]:
            try:
                a, b = next(segments)
            except StopIteration:
                break
        span = max(1, b[0] - a[0])
        t = max(0.0, min(1.0, (x - a[0]) / span))
        y = round(a[1] * (1 - t) + b[1] * t)
        s.rect(x, max(0, y), x, 63, color)


def cloud(s, x, y, size, shadow, light):
    s.ellipse(x-size*0.45, y+size*.18, size*.55, size*.28, shadow)
    s.ellipse(x, y, size*.72, size*.38, shadow)
    s.ellipse(x+size*.48, y+size*.15, size*.5, size*.3, shadow)
    s.ellipse(x-size*.2, y-size*.1, size*.50, size*.27, light)
    s.ellipse(x+size*.25, y-size*.03, size*.5, size*.29, light)


def conifer(s, x, foot, height, dark, leaf, trunk, shine=None):
    crown = foot - height
    s.rect(x-1, foot-6, x+1, foot, trunk)
    for top, spread in ((0, .22), (.19, .30), (.4, .39), (.58, .46)):
        y = round(crown + height*top)
        h = max(3, round(height*(.46-top*.28)))
        w = max(2, round(height*spread))
        s.polygon([(x, y), (x-w, y+h), (x+w, y+h)], dark)
        s.polygon([(x, y+2), (x-w+2, y+h-1), (x, y+h-1)], leaf)
    if shine is not None:
        s.line(x-2, crown+height*.33, x-4, crown+height*.57, shine)


def leafy_tree(s, x, foot, radius, trunk, dark, light, accent):
    s.rect(x-2, foot-round(radius*1.8), x+2, foot, trunk)
    for dx, dy, scale in [
        (-.67, -.35, .7), (.5, -.65, .8), (0, -1, 1),
        (-.3, -.98, .7), (.75, 0, .6)
    ]:
        s.ellipse(x+dx*radius, foot-(1.9+dy)*radius,
                  radius*scale, radius*scale, dark)
    s.ellipse(x-radius*.25, foot-2.6*radius, radius*.7, radius*.6, light)
    s.ellipse(x+radius*.55, foot-2.25*radius, radius*.48, radius*.4, accent)


def flower(s, x, y, petals, center, leaf):
    s.dot(x-1, y, petals)
    s.dot(x+1, y, petals)
    s.dot(x, y-1, petals)
    s.dot(x, y+1, petals)
    s.dot(x, y, center)
    s.dot(x, y+2, leaf)


def birds(s, x, y, count, ink):
    for i in range(count):
        xx = x + i*5
        yy = y + (i % 2)*3
        s.line(xx-2, yy-1, xx, yy, ink)
        s.line(xx, yy, xx+2, yy-1, ink)


def sunset_mountains():
    s = scene([
        "FF412F60",  # 0 deep violet sky
        "FF7F518A",  # 1 dusk
        "FFCE7A96",  # 2 rose
        "FFF3AD86",  # 3 apricot
        "FFFFD8A0",  # 4 horizon
        "FFF9EDC7",  # 5 sun
        "FF81749E",  # 6 far peaks
        "FF554E82",  # 7 middle range
        "FF303B64",  # 8 foreground
        "FF263E56",  # 9 pines
        "FF96A0B5",  # 10 snow
        "FFEDA9A1",  # 11 clouds
    ], [(10, 0), (19, 1), (28, 2), (39, 3), (64, 4)])
    s.ellipse(46, 29, 10, 10, 3)
    s.ellipse(46, 29, 7, 7, 5)
    cloud(s, 15, 15, 11, 1, 11)
    cloud(s, 44, 10, 8, 1, 2)
    ridge(s, [(0, 43), (11, 31), (16, 36), (30, 20),
              (41, 39), (52, 27), (63, 41)], 6)
    for x, y in [(11, 31), (30, 20), (52, 27)]:
        s.polygon([(x, y), (x-6, y+10), (x-1, y+7),
                   (x+3, y+10), (x+7, y+12)], 10)
    ridge(s, [(0, 54), (12, 43), (24, 48), (36, 37),
              (47, 49), (58, 40), (63, 47)], 7)
    ridge(s, [(0, 58), (10, 56), (22, 61), (36, 54), (48, 59), (63, 51)], 8)
    for x, foot, h in [(3, 60, 17), (12, 63, 23), (22, 62, 14),
                       (41, 63, 16), (54, 62, 22), (62, 61, 15)]:
        conifer(s, x, foot, h, 9, 8, 9)
    return s


def alpine_lake():
    s = scene([
        "FFE1F4FF", "FFA9DAEF", "FFF9FEFF", "FF829FB1",
        "FF577B90", "FFDAE9EB", "FF2B6E80", "FF64B9CE",
        "FF9FDEE4", "FF244C4E", "FF3E8C78", "FF71B396",
        "FFB7CD95",
    ], [(16, 0), (38, 1), (64, 7)])
    cloud(s, 14, 12, 10, 1, 2)
    cloud(s, 49, 9, 7, 1, 2)
    ridge(s, [(0, 39), (10, 28), (16, 32), (31, 13),
              (46, 31), (55, 22), (63, 31)], 3)
    ridge(s, [(0, 43), (10, 32), (17, 37), (31, 18),
              (46, 37), (55, 27), (63, 35)], 4)
    for peak_x, peak_y in [(10, 28), (31, 13), (55, 22)]:
        s.polygon([(peak_x, peak_y), (peak_x-8, peak_y+13),
                   (peak_x-3, peak_y+8), (peak_x, peak_y+11),
                   (peak_x+4, peak_y+8), (peak_x+8, peak_y+13)], 5)
    s.rect(0, 44, 63, 63, 6)
    s.rect(2, 45, 61, 46, 8)
    for y, half in [(48, 13), (52, 20), (57, 29), (61, 24)]:
        for xx in range(32-half, 32+half, 7):
            s.line(xx, y, xx+4, y, 7)
    for xx, yy in [(23, 49), (41, 51), (28, 57), (47, 59),
                   (12, 54), (53, 46)]:
        s.line(xx, yy, xx+3, yy, 8)
    s.polygon([(0, 44), (7, 41), (14, 46), (15, 64), (0, 64)], 12)
    s.polygon([(47, 51), (55, 41), (63, 42), (63, 64), (47, 64)], 12)
    for x, foot, h in [(0, 53, 20), (8, 52, 29), (16, 49, 13),
                       (52, 52, 21), (60, 58, 29)]:
        conifer(s, x, foot, h, 9, 10, 9, 11)
    for x, y in [(5, 58), (11, 61), (56, 60), (61, 61)]:
        s.ellipse(x, y, 3, 1.7, 11)
    return s


def waterfall():
    s = scene([
        "FFE1F2F2", "FFA7D7D1", "FF547F76", "FF806F63",
        "FFB49579", "FFD7B896", "FF5EACA9", "FF8BD9DB",
        "FFDFFBFA", "FF285E57", "FF6C9D69", "FFB3CD8A",
    ], [(17, 0), (31, 1), (64, 2)])
    cloud(s, 34, 10, 10, 1, 0)
    s.polygon([(0, 19), (11, 21), (18, 16), (24, 25),
               (23, 55), (18, 64), (0, 64)], 3)
    s.polygon([(64, 18), (50, 17), (44, 23), (42, 51),
               (48, 64), (64, 64)], 3)
    s.polygon([(0, 21), (10, 23), (18, 19), (22, 27),
               (18, 38), (0, 43)], 4)
    s.polygon([(64, 20), (50, 20), (45, 26), (47, 42),
               (64, 44)], 4)
    for x, y, c in [(5, 30, 5), (12, 35, 5), (8, 43, 2),
                     (53, 30, 5), (58, 39, 5), (50, 47, 2)]:
        s.line(x, y, x+5, y+1, c)
    s.polygon([(23, 22), (41, 22), (40, 54), (43, 61),
               (19, 61), (24, 53)], 7)
    s.rect(25, 24, 39, 53, 6)
    for x in (27, 30, 34, 37):
        s.line(x, 25, x+(x%3)-1, 53, 8, radius=.75)
    for x in (24, 40):
        s.line(x, 26, x-1 if x==24 else x+1, 48, 6, radius=1.0)
    s.ellipse(32, 54, 16, 5, 8)
    s.ellipse(32, 56, 14, 3, 7)
    s.rect(0, 58, 63, 63, 6)
    s.ellipse(32, 58, 16, 4, 7)
    for x, y in [(17, 55), (22, 58), (42, 56), (47, 59)]:
        s.ellipse(x, y, 4, 1.8, 8)
    for x, foot, h in [(6, 27, 13), (15, 25, 14), (52, 26, 18), (60, 27, 15)]:
        conifer(s, x, foot, h, 9, 10, 3)
    for x, y in [(5, 51), (11, 53), (53, 52), (59, 49)]:
        s.ellipse(x, y, 4, 2.7, 10)
        s.dot(x, y, 11)
    return s


def cottage_meadow():
    s = scene([
        "FFE1F5FF", "FFA8DBF0", "FFF7FDFF", "FF8DC59D",
        "FF67A776", "FF3E8061", "FFFFDA9D", "FFCB7957",
        "FF825550", "FFF6D8A6", "FF8BB7C2", "FFEFA8AE",
        "FFF4E8BC", "FF58866F",
    ], [(18, 0), (38, 1), (64, 3)])
    cloud(s, 14, 11, 10, 1, 2)
    cloud(s, 48, 15, 12, 1, 2)
    ridge(s, [(0, 38), (9, 34), (19, 38), (32, 33),
              (46, 37), (58, 32), (63, 34)], 3)
    ridge(s, [(0, 45), (11, 40), (28, 45), (42, 39),
              (57, 42), (63, 40)], 4)
    ridge(s, [(0, 56), (14, 50), (27, 52), (40, 47),
              (52, 52), (63, 50)], 5)
    # Cottage with steep tile roof, chimney and warm glowing windows.
    s.rect(22, 31, 42, 49, 8)
    s.rect(23, 32, 41, 48, 9)
    s.polygon([(19, 33), (32, 20), (45, 33)], 8)
    s.polygon([(21, 32), (32, 22), (43, 32)], 7)
    for x in range(24, 41, 5):
        s.line(x, 30, 32, 23, 6)
    s.rect(37, 21, 40, 27, 8)
    s.rect(38, 21, 39, 26, 7)
    for x in (26, 37):
        s.rect(x-2, 36, x+2, 41, 8)
        s.rect(x-1, 37, x+1, 40, 6)
        s.dot(x, 39, 12)
    s.rect(30, 40, 35, 49, 8)
    s.rect(31, 41, 34, 49, 7)
    s.dot(34, 46, 6)
    # A winding earthen path, rail fence and scattered flowers.
    s.polygon([(31, 49), (37, 49), (47, 64), (22, 64)], 12)
    s.polygon([(32, 50), (36, 50), (42, 64), (29, 64)], 9)
    for x in (3, 9, 15, 48, 54, 60):
        s.rect(x, 47, x+1, 55, 8)
        s.rect(x-1, 49, x+3, 50, 12)
        s.rect(x-1, 53, x+3, 53, 12)
    leafy_tree(s, 8, 47, 5, 8, 5, 4, 3)
    for x, y, c in [(4, 60, 11), (12, 56, 6), (18, 61, 2),
                     (49, 55, 11), (56, 61, 6), (61, 56, 2)]:
        flower(s, x, y, c, 6, 4)
    return s


def golden_desert():
    s = scene([
        "FFBA6479", "FFF09A80", "FFFBC59A", "FFFFE0A1",
        "FFFFF0BF", "FFD98F61", "FFEDB275", "FFF6CA82",
        "FFFFDEA1", "FF987051", "FF617F67", "FF92A27D",
    ], [(10, 0), (23, 1), (37, 2), (64, 3)])
    s.ellipse(44, 23, 11, 11, 3)
    s.ellipse(44, 23, 7, 7, 4)
    cloud(s, 14, 14, 11, 0, 1)
    ridge(s, [(0, 45), (12, 38), (25, 36), (41, 44),
              (55, 38), (63, 43)], 5)
    ridge(s, [(0, 52), (13, 44), (25, 47), (42, 38),
              (54, 40), (63, 44)], 6)
    ridge(s, [(0, 51), (15, 50), (31, 58), (48, 48), (63, 50)], 7)
    ridge(s, [(0, 59), (15, 56), (25, 54), (41, 59),
              (53, 54), (63, 56)], 8)
    for x, y in [(6, 54), (14, 57), (28, 61), (51, 59), (58, 55)]:
        s.line(x, y, x+4, y, 9)
    # Large, silhouetted saguaro with two upright arms.
    s.rect(14, 42, 18, 58, 9)
    s.rect(15, 43, 17, 57, 10)
    s.ellipse(16, 42, 2, 3, 10)
    s.rect(9, 46, 12, 49, 9)
    s.rect(9, 42, 11, 47, 9)
    s.rect(10, 43, 10, 47, 10)
    s.rect(20, 50, 23, 53, 9)
    s.rect(22, 45, 24, 51, 9)
    s.rect(23, 46, 23, 50, 10)
    s.line(16, 45, 16, 55, 11)
    s.rect(39, 54, 41, 61, 9)
    s.rect(40, 53, 40, 60, 10)
    s.ellipse(40, 53, 1.5, 2, 10)
    for x, y in [(4, 61), (31, 60), (55, 58), (59, 61)]:
        s.dot(x, y, 10)
        s.dot(x+1, y, 11)
    return s


def tropical_beach():
    s = scene([
        "FFB5E8FA", "FFDBF6FA", "FFFDF2C6", "FFFFDAA3",
        "FF4DA5BD", "FF77CBD5", "FFB6E8DC", "FFFFE5AE",
        "FFE4BF87", "FF456F66", "FF4C9877", "FF86C9A6",
        "FF73554A", "FFFCF9E9",
    ], [(14, 0), (29, 1), (37, 2), (64, 4)])
    s.ellipse(45, 29, 6, 6, 3)
    s.ellipse(45, 29, 4, 4, 13)
    cloud(s, 16, 11, 9, 0, 1)
    birds(s, 32, 16, 2, 9)
    s.rect(0, 38, 63, 63, 4)
    s.rect(0, 46, 63, 50, 5)
    for y in (41, 45, 52, 56):
        for x in range((y*3)%7, 64, 13):
            s.line(x, y, x+6, y, 6)
    s.polygon([(0, 54), (15, 52), (35, 57), (51, 55),
               (63, 53), (63, 64), (0, 64)], 7)
    s.polygon([(0, 59), (16, 56), (31, 62), (50, 58),
               (63, 58), (63, 64), (0, 64)], 8)
    s.line(0, 53, 13, 51, 13, radius=1.0)
    # Two leaning coconut palms on the left.
    s.line(9, 59, 15, 21, 12, radius=1.5)
    s.line(9, 57, 15, 22, 8, radius=.6)
    for tip in [(1, 14), (4, 22), (9, 11), (17, 9), (31, 16), (31, 24), (20, 30)]:
        s.polygon([(15, 21), (12, 18), tip,
                   (tip[0]+2, tip[1]+3)], 9)
        s.line(15, 21, tip[0], tip[1], 10, radius=.7)
    for x, y in [(14, 23), (17, 24), (15, 26)]:
        s.ellipse(x, y, 2, 2, 12)
    # Sandy shell details, a distant sail and translucent water.
    s.polygon([(45, 34), (45, 43), (52, 43)], 13)
    s.line(45, 33, 45, 45, 9)
    s.line(43, 44, 53, 44, 12)
    s.ellipse(46, 44, 8, 1, 9)
    for x, y in [(34, 60), (38, 62), (56, 61)]:
        s.dot(x, y, 12)
        s.dot(x+1, y, 13)
    return s


def misty_forest():
    s = scene([
        "FFE2F0E8", "FFB8D9D0", "FF91B9AD", "FF709C93",
        "FF5F8B7F", "FF427568", "FF2C534B", "FFE6F0E0",
        "FF8EAD9A", "FF6C9F8D", "FFB7D1B7", "FFDFB1A1",
    ], [(12, 0), (26, 1), (39, 2), (64, 3)])
    cloud(s, 15, 10, 12, 1, 7)
    cloud(s, 50, 17, 13, 2, 7)
    ridge(s, [(0, 35), (9, 32), (24, 37), (37, 29), (51, 34), (63, 30)], 2)
    for x, h in [(4, 21), (14, 25), (25, 17), (39, 23), (51, 21), (62, 26)]:
        conifer(s, x, 44, h, 3, 2, 3)
    s.rect(0, 40, 63, 44, 1)
    ridge(s, [(0, 48), (11, 44), (19, 49), (35, 43),
              (50, 46), (63, 43)], 4)
    for x, h in [(6, 24), (16, 31), (28, 25), (43, 32), (55, 28)]:
        conifer(s, x, 59, h, 5, 4, 6, 9)
    s.rect(0, 54, 63, 55, 2)
    s.rect(8, 49, 42, 50, 10)
    s.rect(37, 51, 63, 52, 1)
    ridge(s, [(0, 60), (14, 58), (29, 62), (43, 56),
              (55, 58), (63, 55)], 6)
    for x, h in [(1, 24), (11, 21), (22, 17), (49, 21), (63, 25)]:
        conifer(s, x, 65, h, 6, 5, 6, 4)
    for x, y in [(6, 61), (17, 63), (35, 60), (58, 62)]:
        s.rect(x, y, x+2, min(63, y+2), 7)
        s.ellipse(x+1, y, 2.8, 1.6, 11)
    return s


def river_bridge():
    s = scene([
        "FFE2F5FC", "FFACDCE9", "FFF9FCF7", "FFB4CCAE",
        "FF7EAF91", "FF4E936F", "FF3C748A", "FF64B3C8",
        "FFB6E4E5", "FF7E665A", "FFB69C83", "FFE2C7A5",
        "FF486C56",
    ], [(20, 0), (40, 1), (64, 3)])
    cloud(s, 14, 11, 10, 1, 2)
    cloud(s, 47, 8, 8, 1, 2)
    ridge(s, [(0, 39), (11, 32), (21, 37), (32, 34),
              (44, 37), (55, 29), (63, 33)], 4)
    ridge(s, [(0, 45), (14, 41), (28, 45), (44, 40),
              (57, 41), (63, 39)], 5)
    # Meandering river and banks, widening into the foreground.
    s.polygon([(25, 38), (40, 38), (40, 43), (48, 49),
               (58, 56), (64, 57), (64, 64), (0, 64),
               (0, 59), (17, 53), (25, 48), (29, 44)], 6)
    s.polygon([(26, 40), (39, 40), (37, 44), (44, 50),
               (55, 57), (63, 59), (63, 64), (2, 64),
               (21, 54), (27, 47)], 7)
    for x, y in [(23, 55), (32, 59), (44, 60), (49, 55),
                 (18, 63), (55, 62)]:
        s.line(x, y, x+5, y, 8)
    # Stone bridge over the narrow upper river.
    s.rect(13, 35, 53, 39, 9)
    s.rect(13, 36, 53, 38, 10)
    s.rect(14, 31, 52, 34, 11)
    s.rect(15, 30, 51, 31, 9)
    for cx in (22, 34, 46):
        s.ellipse(cx, 40, 5, 6, 9)
        s.ellipse(cx, 41, 4, 5, 7)
        s.rect(cx-4, 42, cx+4, 46, 7)
    s.rect(12, 39, 17, 44, 9)
    s.rect(50, 39, 54, 44, 9)
    for x in range(15, 54, 5):
        s.dot(x, 34, 9)
        s.dot(x+2, 36, 11)
    for x, y in [(7, 51), (57, 48), (61, 43)]:
        leafy_tree(s, x, y, 4, 9, 12, 4, 3)
    s.ellipse(4, 58, 6, 3, 4)
    s.ellipse(58, 56, 5, 2, 5)
    return s


def moonlit_night():
    s = scene([
        "FF142846", "FF1D3657", "FF304C73", "FF587397",
        "FFF5EACA", "FFB7CBE1", "FF4F6682", "FF2D5269",
        "FF123D50", "FF1B303F", "FF78A9BC", "FF7290AE",
    ], [(17, 0), (33, 1), (48, 2), (64, 7)])
    s.ellipse(45, 13, 9, 9, 5)
    s.ellipse(45, 13, 7, 7, 4)
    for x, y, size in [(5, 7, 2), (15, 14, 1), (25, 6, 2),
                       (34, 22, 1), (57, 7, 2), (11, 27, 1),
                       (57, 28, 1), (30, 18, 1), (3, 24, 1)]:
        s.dot(x, y, 4)
        if size > 1:
            s.dot(x-1, y, 11)
            s.dot(x+1, y, 11)
            s.dot(x, y-1, 11)
            s.dot(x, y+1, 11)
    ridge(s, [(0, 46), (12, 27), (23, 43), (37, 26),
              (51, 42), (63, 30)], 6)
    for x, y in [(12, 27), (37, 26), (63, 30)]:
        s.polygon([(x, y), (x-5, y+9), (x, y+7), (x+5, y+9)], 5)
    ridge(s, [(0, 52), (14, 47), (28, 51), (41, 42),
              (55, 50), (63, 47)], 8)
    s.rect(0, 54, 63, 63, 7)
    s.rect(36, 54, 51, 55, 10)
    for y, half in [(56, 4), (59, 7), (62, 11)]:
        for x in range(45-half, 45+half, 5):
            s.line(x, y, x+3, y, 11)
    for x, foot, h in [(1, 59, 24), (9, 63, 21), (20, 58, 14),
                       (53, 60, 21), (63, 63, 28)]:
        conifer(s, x, foot, h, 9, 8, 9)
    s.ellipse(32, 63, 14, 2, 8)
    return s


def wildflower_valley():
    s = scene([
        "FFE6F7FF", "FFB5DCF5", "FFF9FAF4", "FF8EB6C8",
        "FF6F95A7", "FFEEF6F6", "FF91C89C", "FF59AD78",
        "FF3F906B", "FFEAD6A1", "FFF09AC0", "FF9D87DB",
        "FFFFD66B", "FF4F8058", "FFFFF6D8",
    ], [(18, 0), (40, 1), (64, 6)])
    cloud(s, 13, 9, 8, 1, 2)
    cloud(s, 48, 13, 9, 1, 2)
    ridge(s, [(0, 43), (9, 30), (16, 35), (29, 21),
              (43, 37), (56, 25), (63, 38)], 3)
    ridge(s, [(0, 47), (9, 34), (16, 39), (29, 25),
              (43, 42), (56, 29), (63, 41)], 4)
    for x, y in [(9, 30), (29, 21), (56, 25)]:
        s.polygon([(x, y), (x-6, y+10), (x-2, y+7),
                   (x+2, y+9), (x+6, y+11)], 5)
    ridge(s, [(0, 48), (15, 43), (29, 49), (46, 42),
              (57, 46), (63, 44)], 6)
    ridge(s, [(0, 58), (12, 53), (27, 56), (43, 48),
              (54, 52), (63, 50)], 7)
    ridge(s, [(0, 62), (15, 59), (29, 61), (45, 55),
              (57, 59), (63, 56)], 8)
    s.polygon([(34, 49), (39, 49), (36, 54),
               (35, 60), (44, 64), (25, 64), (31, 58)], 9)
    s.polygon([(35, 50), (38, 50), (35, 59),
               (40, 64), (30, 64), (33, 58)], 14)
    for x, y, c in [
        (4, 57, 10), (9, 60, 11), (16, 55, 12),
        (19, 62, 10), (25, 58, 11), (40, 57, 10),
        (46, 61, 12), (51, 55, 11), (57, 59, 10),
        (61, 54, 12), (12, 51, 11), (24, 53, 10),
        (49, 52, 12), (6, 63, 12), (59, 63, 11),
    ]:
        flower(s, x, y, c, 12 if c != 12 else 14, 13)
    for x, y in [(6, 53), (29, 54), (44, 53), (55, 51)]:
        s.line(x, y, x+1, y-2, 13)
    birds(s, 38, 18, 2, 4)
    return s


PICTURES = [
    ("online-landscape-sunset-mountains", "غروب کوهستان",
     "Mountain Sunset", sunset_mountains),
    ("online-landscape-alpine-lake", "دریاچه و جنگل",
     "Alpine Lake and Forest", alpine_lake),
    ("online-landscape-waterfall", "آبشار جنگلی",
     "Forest Waterfall", waterfall),
    ("online-landscape-cottage", "مزرعه و کلبه",
     "Countryside Cottage", cottage_meadow),
    ("online-landscape-golden-desert", "کویر و تپه‌های شنی",
     "Golden Desert Dunes", golden_desert),
    ("online-landscape-tropical-beach", "ساحل و دریا",
     "Tropical Beach", tropical_beach),
    ("online-landscape-misty-forest", "جنگل مه‌آلود",
     "Misty Forest", misty_forest),
    ("online-landscape-river-bridge", "رودخانه و پل سنگی",
     "River and Stone Bridge", river_bridge),
    ("online-landscape-moonlit-night", "آسمان شب و ماه",
     "Moonlit Mountain Night", moonlit_night),
    ("online-landscape-flower-valley", "دشت گل‌ها",
     "Wildflower Valley", wildflower_valley),
]


def create_pack(destination):
    manifest = []
    assets = {}
    for identifier, title_fa, title_en, painter in PICTURES:
        artwork = painter()
        level = {
            "schemaVersion": 2,
            "levelId": identifier,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": artwork.side,
            "height": artwork.side,
            "palette": artwork.palette,
            "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        payload = compact(level)
        stem = f"{identifier}-v1"
        manifest.append({
            "id": identifier,
            "version": 1,
            "title": title_fa,
            "titleEn": title_en,
            "category": "nature",
            "width": artwork.side,
            "height": artwork.side,
            "bytes": len(payload),
            "checksum": level["checksum"],
        })
        assets[f"levels/{stem}.json"] = payload
        assets[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as pack:
        pack.writestr("catalog.json", compact({
            "schemaVersion": 1,
            "pictures": manifest,
        }))
        for name, content in assets.items():
            pack.writestr(name, content)
    print(f"Created {len(manifest)} original 64x64 landscape levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_landscapes_pack.py <content.zip>")
    create_pack(sys.argv[1])
