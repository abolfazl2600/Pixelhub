#!/usr/bin/env python3
"""Original Persian architectural abstractions and the redesigned Azadi Tower.

This script authors drawings in source code, not repository-bundled level assets.
Web CI publishes an immutable content.zip Release holding bilingual schema-v2
levels, numbered painting cells, their checksums, and miniature PNG previews.

The Azadi v2 is an archived, pre-policy exception. Reproduce only the
existing Release; all future redesigns need fresh IDs and levelVersion 1.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_archived_azadi_pack_manifest
from online_starter_pack import Sprite


SIZE = 64


def canvas(palette, color=0, size=SIZE):
    s = Sprite(size, palette)
    if color:
        s.rect(0, 0, size - 1, size - 1, color)
    return s


def diamond(s, x, y, radius, color):
    s.polygon([(x, y-radius), (x+radius, y),
               (x, y+radius), (x-radius, y)], color)


def star(s, x, y, outer, inner, color, points=8, offset=-math.pi/2):
    coords = []
    for i in range(points * 2):
        angle = offset + i * math.pi / points
        radius = outer if i % 2 == 0 else inner
        coords.append((x + math.cos(angle)*radius,
                       y + math.sin(angle)*radius))
    s.polygon(coords, color)


def border(s, inner=4, dark=1, light=2, accent=3):
    last = s.side-1
    s.rect(0, 0, last, 2, dark)
    s.rect(0, last-2, last, last, dark)
    s.rect(0, 0, 2, last, dark)
    s.rect(last-2, 0, last, last, dark)
    for x in range(4, last-3, 6):
        s.rect(x, 1, x+2, 2, light)
        s.rect(x, last-2, x+2, last-1, light)
        s.dot(x+3, 1, accent)
        s.dot(x+3, last-1, accent)
    for y in range(4, last-3, 6):
        s.rect(1, y, 2, y+2, light)
        s.rect(last-2, y, last-1, y+2, light)
        s.dot(1, y+3, accent)
        s.dot(last-1, y+3, accent)


def arch(s, cx, top, bottom, half, outline, face, aperture, thickness=3):
    """A deeply framed, distinctly pointed Iranian iwan/mihrab."""
    vertices = [(cx-half, bottom), (cx-half, top+half//2),
                (cx-half//2, top+3), (cx, top),
                (cx+half//2, top+3), (cx+half, top+half//2),
                (cx+half, bottom)]
    s.polygon(vertices, outline)
    h = half-thickness
    s.polygon([(cx-h, bottom), (cx-h, top+half//2+thickness),
               (cx-h//2, top+thickness+5), (cx, top+thickness),
               (cx+h//2, top+thickness+5),
               (cx+h, top+half//2+thickness), (cx+h, bottom)], face)
    h2 = max(1, h-thickness)
    s.polygon([(cx-h2, bottom), (cx-h2, top+half//2+thickness*2),
               (cx, top+thickness*2+3),
               (cx+h2, top+half//2+thickness*2), (cx+h2, bottom)], aperture)


def geometric_tiles(s, left, top, right, bottom, base, highlight, point):
    for y in range(top, bottom+1, 6):
        for x in range(left, right+1, 6):
            shade = base if (x+y)//6 % 2 else highlight
            diamond(s, x+2, y+2, 2, shade)
            s.dot(x+2, y+2, point)


def azadi_tower_v2():
    """80x80, with authentic splayed marble piers and a pointed open arch."""
    s = canvas([
        "FFE6F5FC",  # 0 open sky
        "FFC4E6F3",  # 1 low sky
        "FF476678",  # 2 marble outline
        "FFABBCC8",  # 3 shadow on marble
        "FFEEEFE9",  # 4 lit marble
        "FFFFFFFF",  # 5 marble highlights
        "FF91B5C5",  # 6 distant city
        "FF398F9E",  # 7 turquoise bands
        "FF1D657C",  # 8 rich blue tile
        "FF7CBDBB",  # 9 pale glazed tile
        "FF668D80",  # 10 garden
        "FFA8C4B2",  # 11 lawn
        "FFDBD6C9",  # 12 plaza
        "FFB7ACA0",  # 13 stone paving
        "FFFBE6B1",  # 14 pale sun
        "FF758B9B",  # 15 structural lines
    ], size=80)
    s.rect(0, 49, 79, 68, 1)
    s.ellipse(66, 14, 7, 7, 14)
    for x, h in [(0, 62), (5, 60), (12, 64), (66, 62), (72, 59), (77, 63)]:
        s.rect(x, h, min(79,x+5), 68, 6)
        s.rect(x+1, h+2, min(79,x+1), h+3, 0)
    s.rect(0, 69, 79, 79, 12)
    s.rect(0, 71, 79, 72, 13)
    s.polygon([(0, 70), (27, 68), (53, 68), (79, 70),
               (79, 75), (0, 75)], 11)
    # Stepped, tapering tower with two dramatic flared supporting legs.
    outer = [(29, 10), (51, 10), (55, 17), (56, 26), (59, 39),
             (66, 55), (75, 68), (76, 70), (57, 70),
             (52, 56), (47, 44), (44, 36), (36, 36), (33, 44),
             (28, 56), (23, 70), (4, 70), (5, 68), (14, 55),
             (21, 39), (24, 26), (25, 17)]
    s.polygon(outer, 2)
    s.polygon([
        (30, 11), (50, 11), (54, 18), (55, 26), (58, 39),
        (65, 55), (73, 68), (58, 68), (53, 54), (48, 42),
        (45, 34), (35, 34), (32, 42), (27, 54), (22, 68),
        (7, 68), (15, 55), (22, 39), (25, 26), (26, 18),
    ], 3)
    s.polygon([
        (31, 12), (49, 12), (53, 18), (54, 27), (57, 41),
        (62, 54), (70, 67), (59, 67), (52, 51), (47, 38),
        (44, 31), (36, 31), (33, 38), (28, 51), (21, 67),
        (10, 67), (18, 54), (23, 41), (26, 27), (27, 18),
    ], 4)
    # Negative-space apex and tall arch: visually open through the tower.
    opening = [(40, 30), (36, 35), (34, 42), (30, 52), (25, 63),
               (23, 69), (57, 69), (55, 63), (50, 52),
               (46, 42), (44, 35)]
    s.polygon(opening, 2)
    s.polygon([(40, 33), (37, 38), (35, 45), (31, 55),
               (26, 68), (54, 68), (49, 55), (45, 45),
               (43, 38)], 0)
    # Four recessed curves define the distinctive crossing vault.
    for a, b, c, d in [
        (29, 44, 16, 65), (51, 44, 64, 65),
        (31, 48, 21, 67), (49, 48, 59, 67),
    ]:
        s.line(a, b, c, d, 15, radius=.55)
    s.line(26, 18, 31, 29, 5)
    s.line(54, 18, 49, 29, 5)
    s.line(24, 35, 16, 55, 5)
    s.line(56, 35, 64, 55, 5)
    # Upper 3-level glazed bridge and diamond lattice.
    s.rect(28, 10, 52, 13, 2)
    s.rect(30, 11, 50, 12, 4)
    s.rect(27, 15, 53, 17, 2)
    s.rect(28, 16, 52, 16, 9)
    s.rect(29, 18, 51, 25, 8)
    s.rect(30, 19, 50, 24, 7)
    for x in range(31, 51, 4):
        s.line(x, 19, x+3, 24, 9)
        s.line(x+3, 19, x, 24, 5)
    s.rect(30, 26, 50, 27, 2)
    s.rect(31, 26, 49, 26, 5)
    s.polygon([(35, 28), (40, 33), (45, 28)], 8)
    s.polygon([(37, 28), (40, 31), (43, 28)], 9)
    # The inner piers catch light, while panel seams follow their slope.
    for yy, xl, xr in [(36, 30, 50), (42, 28, 52), (49, 24, 56),
                       (56, 19, 61), (63, 14, 66)]:
        s.line(xl-3, yy, xl, yy+1, 3)
        s.line(xr, yy+1, xr+3, yy, 3)
    # Plaza, green lawns and perspective paving.
    s.rect(0, 69, 16, 71, 10)
    s.rect(63, 69, 79, 71, 10)
    for xx in range(3, 80, 10):
        s.line(xx, 76, xx-2, 79, 13)
        s.dot(xx, 73, 13)
    s.line(0, 75, 79, 75, 13)
    s.line(0, 78, 79, 78, 13)
    return s


def muqarnas_turquoise():
    s = canvas([
        "FFF8F1DE", "FF1E5170", "FF257F99", "FF52ADBA",
        "FF8ED2CB", "FFDDC389", "FFF2DFB5", "FF386F87",
        "FFB4DCD8", "FF17435B",
    ])
    border(s, dark=1, light=5, accent=3)
    s.rect(5, 5, 58, 58, 9)
    s.rect(7, 7, 56, 56, 7)
    s.polygon([(7, 12), (32, 5), (56, 12), (56, 56),
               (7, 56)], 1)
    for tier in range(8):
        yy = 9+tier*6
        count = 3+tier if tier < 4 else 10-tier
        count = max(3, count)
        spacing = 45/(count-1)
        for j in range(count):
            xx = round(9+j*spacing)
            width = 5 if tier < 4 else 4
            s.polygon([(xx, yy), (xx-width, yy+5),
                       (xx, yy+10), (xx+width, yy+5)], 2 if tier%2 else 3)
            s.polygon([(xx, yy+2), (xx-3, yy+5),
                       (xx, yy+8), (xx+3, yy+5)], 4)
            s.dot(xx, yy+5, 6)
    s.rect(9, 56, 54, 57, 5)
    star(s, 32, 32, 8, 4, 1)
    star(s, 32, 32, 5, 2, 6)
    s.dot(32, 32, 3)
    return s


def geometric_persian_dome():
    s = canvas([
        "FFF8EDD9", "FF164D69", "FF246F94", "FF399DB3",
        "FF82CFCD", "FFCCE7D8", "FFF5DC98", "FFB98355",
        "FF2E7086", "FFFFF4D3",
    ])
    border(s, dark=1, light=7, accent=6)
    s.rect(8, 46, 55, 55, 1)
    s.rect(10, 45, 53, 52, 2)
    s.rect(12, 48, 51, 51, 3)
    s.ellipse(32, 46, 23, 25, 1)
    s.ellipse(32, 46, 21, 23, 2)
    s.polygon([(11, 45), (11, 36), (16, 26), (24, 16),
               (32, 8), (40, 16), (48, 26), (53, 36),
               (53, 45)], 1)
    s.polygon([(13, 45), (13, 36), (18, 27), (25, 18),
               (32, 11), (39, 18), (46, 27), (51, 36),
               (51, 45)], 3)
    s.polygon([(18, 44), (20, 31), (25, 20), (32, 12),
               (39, 20), (44, 31), (46, 44)], 4)
    for dx in (-17, -11, -5, 5, 11, 17):
        s.line(32, 13, 32+dx, 43, 1, radius=.65)
    for yy in (27, 34, 41):
        for xx in range(17, 48, 6):
            s.dot(xx, yy, 9)
    s.rect(30, 5, 34, 8, 7)
    s.dot(32, 4, 6)
    for xx in range(12, 53, 8):
        s.rect(xx, 48, xx+3, 51, 5)
        s.dot(xx+1, 49, 6)
    s.rect(9, 55, 55, 58, 7)
    s.rect(11, 56, 53, 56, 6)
    return s


def orsi_stained_glass():
    s = canvas([
        "FFEEE1CA", "FF563F45", "FF9B5B50", "FFD7A77B",
        "FF194A67", "FF5EA5C0", "FFDB507A", "FFF4C258",
        "FF7DBF83", "FF9966AF", "FFFFE8C5", "FF26475C",
    ])
    border(s, dark=1, light=3, accent=7)
    s.rect(6, 8, 57, 57, 1)
    s.rect(8, 10, 55, 55, 2)
    for cx in (17, 32, 47):
        arch(s, cx, 11, 53, 7, 1, 3, 11, 2)
        # Backlit glass is arranged as stars and rhombi.
        for yy in range(22, 51, 6):
            for xx in range(cx-4, cx+5, 4):
                shade = [4, 5, 6, 7, 8, 9][(xx+yy)//3 % 6]
                diamond(s, xx, yy, 3, shade)
                s.dot(xx, yy, 10)
        s.line(cx, 21, cx, 52, 1, radius=.6)
        s.line(cx-5, 35, cx+5, 35, 1)
        s.line(cx-5, 44, cx+5, 44, 1)
        star(s, cx, 19, 4, 1.8, 7)
        s.dot(cx, 19, 10)
    s.rect(6, 54, 57, 58, 1)
    s.rect(8, 55, 55, 56, 3)
    return s


def eslimi_tile_scroll():
    s = canvas([
        "FFF6EFE2", "FF185470", "FF236D92", "FF48A9AA",
        "FF86CFB8", "FFDEAF65", "FFF5DCA6", "FF9C6C9E",
        "FF8FBED6", "FF17435B",
    ])
    border(s, dark=1, light=5, accent=3)
    s.rect(5, 5, 58, 58, 8)
    for cx, cy, turn in [(19, 19, 1), (45, 19, -1),
                         (19, 45, -1), (45, 45, 1)]:
        # Deliberate stepped spirals rather than a flat all-over checker.
        coords = []
        for i in range(24):
            angle = turn * (i*math.pi/6)
            radius = 2+i*.56
            coords.append((cx+math.cos(angle)*radius,
                           cy+math.sin(angle)*radius))
        for (xa, ya), (xb, yb) in zip(coords, coords[1:]):
            s.line(xa, ya, xb, yb, 1, radius=1.5)
            s.line(xa, ya, xb, yb, 3, radius=.6)
        s.ellipse(cx, cy, 3, 3, 5)
        s.dot(cx, cy, 6)
    for cx, cy in [(32, 12), (12, 32), (52, 32), (32, 52)]:
        s.ellipse(cx, cy, 5, 3.5, 1)
        s.ellipse(cx, cy, 3.5, 2.5, 4)
        s.dot(cx, cy, 5)
    star(s, 32, 32, 11, 5, 1)
    star(s, 32, 32, 9, 4, 4)
    star(s, 32, 32, 5, 2, 5)
    s.dot(32, 32, 9)
    return s


def perspective_iwans():
    s = canvas([
        "FFF4E5C6", "FF254C63", "FF3A7A93", "FF64AFB3",
        "FFA9DBCA", "FFEAC68E", "FFBD8566", "FF7397A2",
        "FF193B58", "FFF9F2DC",
    ])
    border(s, dark=1, light=5, accent=3)
    s.rect(5, 5, 58, 58, 6)
    s.rect(7, 7, 56, 56, 2)
    arch(s, 32, 7, 58, 24, 1, 3, 8, 3)
    arch(s, 32, 15, 58, 19, 1, 5, 7, 3)
    arch(s, 32, 23, 58, 14, 1, 3, 8, 3)
    arch(s, 32, 31, 58, 9, 1, 4, 8, 2)
    s.polygon([(26, 58), (38, 58), (41, 63), (23, 63)], 5)
    for x in range(10, 55, 7):
        s.dot(x, 11, 9)
        s.dot(x, 53, 9)
    for y in range(16, 53, 6):
        s.dot(9, y, 5)
        s.dot(55, y, 5)
    star(s, 32, 44, 5, 2.5, 5)
    s.dot(32, 44, 3)
    return s


def windcatcher_geometry():
    s = canvas([
        "FFF9EBD6", "FF30566B", "FFB4835F", "FFE7B98A",
        "FFF9DAA9", "FF308DA2", "FF8DD2C4", "FFB7D3C6",
        "FF795C61", "FFF3F6E2",
    ])
    border(s, dark=1, light=2, accent=5)
    s.rect(5, 50, 58, 58, 2)
    s.rect(8, 45, 56, 52, 3)
    s.rect(10, 14, 54, 45, 1)
    s.rect(12, 16, 52, 44, 3)
    s.rect(16, 10, 47, 44, 1)
    s.rect(18, 12, 45, 43, 4)
    s.rect(19, 8, 45, 12, 2)
    s.rect(22, 6, 42, 9, 3)
    for xx in (21, 29, 37):
        s.rect(xx, 16, xx+6, 33, 1)
        s.rect(xx+1, 17, xx+5, 32, 5)
        s.rect(xx+2, 18, xx+4, 31, 6)
        s.rect(xx+3, 21, xx+3, 32, 9)
    s.rect(20, 34, 44, 37, 2)
    s.rect(21, 35, 43, 36, 7)
    for xx in (15, 49):
        arch(s, xx, 35, 45, 4, 1, 5, 8, 1)
    for x in range(11, 54, 6):
        s.dot(x, 42, 5)
        s.dot(x+1, 43, 6)
    s.polygon([(12, 53), (52, 53), (57, 58), (7, 58)], 1)
    s.polygon([(15, 54), (49, 54), (52, 57), (12, 57)], 4)
    return s


def eight_point_shamsa():
    s = canvas([
        "FFFAEDDA", "FF143F62", "FF266D95", "FF4FABC3",
        "FF8ED8D1", "FFDFBC7A", "FFF8E6B9", "FF9F8AB3",
        "FF317F88", "FFF9F6E9",
    ])
    border(s, dark=1, light=5, accent=3)
    s.rect(5, 5, 58, 58, 2)
    for cx in (10, 54):
        for cy in (10, 54):
            star(s, cx, cy, 9, 4, 1)
            star(s, cx, cy, 6, 2.5, 4)
            s.dot(cx, cy, 6)
    diamond(s, 32, 32, 27, 1)
    diamond(s, 32, 32, 24, 3)
    star(s, 32, 32, 25, 10, 1)
    star(s, 32, 32, 22, 9, 5)
    star(s, 32, 32, 18, 7, 8)
    star(s, 32, 32, 15, 6, 4)
    star(s, 32, 32, 11, 4, 2)
    star(s, 32, 32, 7, 3, 6)
    diamond(s, 32, 32, 4, 1)
    s.dot(32, 32, 5)
    for x, y in [(32, 6), (58, 32), (32, 58), (6, 32)]:
        diamond(s, x, y, 4, 6)
        s.dot(x, y, 1)
    return s


def symmetrical_mosque():
    s = canvas([
        "FFF4EEDC", "FF214D6B", "FF2D85A5", "FF56B2BD",
        "FF9DD8CF", "FFE4BE7F", "FFF9E2AD", "FF1D5473",
        "FF9C735C", "FFFFF3D5",
    ])
    border(s, dark=1, light=5, accent=2)
    s.rect(5, 38, 58, 57, 1)
    s.rect(6, 39, 57, 55, 5)
    for cx in (12, 52):
        s.rect(cx-4, 14, cx+4, 54, 1)
        s.rect(cx-3, 15, cx+3, 53, 2)
        s.rect(cx-2, 11, cx+2, 14, 3)
        s.polygon([(cx-3, 11), (cx, 7), (cx+3, 11)], 1)
        s.dot(cx, 6, 5)
        for yy in range(18, 53, 5):
            s.rect(cx-3, yy, cx+3, yy+1, 4)
            s.dot(cx, yy, 6)
    s.polygon([(16, 36), (21, 25), (27, 19), (32, 14),
               (37, 19), (43, 25), (48, 36)], 1)
    s.polygon([(18, 37), (23, 25), (28, 20), (32, 17),
               (36, 20), (41, 25), (46, 37)], 2)
    for xx in (25, 32, 39):
        s.line(32, 18, xx, 35, 4)
    s.rect(30, 12, 34, 15, 5)
    s.dot(32, 11, 1)
    s.rect(18, 36, 46, 55, 1)
    s.rect(19, 37, 45, 54, 2)
    arch(s, 32, 34, 56, 11, 5, 3, 7, 2)
    for cx in (22, 42):
        arch(s, cx, 44, 56, 3, 1, 4, 7, 1)
    for xx in range(19, 47, 5):
        s.dot(xx, 38, 6)
    s.rect(6, 57, 57, 59, 8)
    s.rect(10, 58, 54, 58, 6)
    return s


def brick_and_tile():
    s = canvas([
        "FFF8EAD7", "FF734C48", "FFC18D67", "FFE6BA88",
        "FFF5D5A2", "FF246B82", "FF4DACC0", "FF9ADAD3",
        "FFEDC992", "FF2B586D",
    ])
    border(s, dark=1, light=3, accent=5)
    s.rect(5, 5, 58, 58, 1)
    for yy in range(6, 59, 6):
        shift = 0 if (yy//6) % 2 == 0 else 5
        for xx in range(6-shift, 59, 11):
            s.rect(max(5, xx), yy, min(58, xx+9), yy+4, 2)
            s.rect(max(5, xx)+1, yy+1, min(58, xx+8), yy+3, 3)
            if (xx+yy)//5 % 4 == 0:
                diamond(s, xx+5, yy+2, 2, 4)
    # Contrasting turquoise eight-sided medallions set into the brick.
    for cx, cy in [(19, 19), (45, 19), (19, 45), (45, 45)]:
        star(s, cx, cy, 11, 6, 1)
        star(s, cx, cy, 9, 5, 5)
        star(s, cx, cy, 7, 3, 6)
        s.dot(cx, cy, 7)
    star(s, 32, 32, 10, 5, 9)
    star(s, 32, 32, 7, 3, 7)
    diamond(s, 32, 32, 3, 1)
    return s


def abstract_iwan_courtyard():
    s = canvas([
        "FFF9F0DC", "FF23506D", "FF347F9C", "FF63B9BC",
        "FFB2DFCE", "FFE0B879", "FFF5DBA5", "FFB88162",
        "FF3F657C", "FFF9F9E6",
    ])
    border(s, dark=1, light=5, accent=3)
    s.rect(5, 5, 58, 58, 7)
    s.rect(8, 7, 55, 47, 1)
    arch(s, 32, 8, 49, 22, 5, 2, 8, 4)
    arch(s, 32, 15, 49, 16, 1, 3, 8, 3)
    arch(s, 32, 22, 48, 11, 5, 4, 1, 3)
    arch(s, 32, 30, 47, 6, 2, 9, 8, 2)
    for y in (12, 19, 26):
        for xx in (10, 16, 48, 54):
            s.dot(xx, y+10, 6)
    for cx in (12, 52):
        for yy in (17, 27, 37):
            diamond(s, cx, yy, 3, 6)
            s.dot(cx, yy, 3)
    # A stylized rectangular reflecting pool in courtyard perspective.
    s.polygon([(23, 49), (41, 49), (54, 58), (10, 58)], 1)
    s.polygon([(24, 50), (40, 50), (50, 57), (14, 57)], 3)
    s.polygon([(28, 51), (36, 51), (42, 55), (22, 55)], 4)
    for yy, xa, xb in [(53, 24, 39), (55, 20, 43), (57, 15, 49)]:
        s.line(xa, yy, xb, yy, 9)
    return s


PICTURES = [
    ("online-iran-azadi-tower", 2, "برج آزادی - بازطراحی",
     "Azadi Tower - Redesigned", azadi_tower_v2),
    ("online-iran-abstract-muqarnas", 1, "مقرنس فیروزه‌ای",
     "Turquoise Muqarnas", muqarnas_turquoise),
    ("online-iran-abstract-dome", 1, "گنبد هندسی ایرانی",
     "Geometric Persian Dome", geometric_persian_dome),
    ("online-iran-abstract-orsi", 1, "پنجره ارسی رنگی",
     "Colorful Orsi Window", orsi_stained_glass),
    ("online-iran-abstract-eslimi", 1, "کاشی‌کاری اسلیمی",
     "Arabesque Tile Scroll", eslimi_tile_scroll),
    ("online-iran-abstract-arches", 1, "قوس‌های متقارن ایرانی",
     "Receding Persian Arches", perspective_iwans),
    ("online-iran-abstract-windcatcher", 1, "هندسه بادگیر",
     "Windcatcher Geometry", windcatcher_geometry),
    ("online-iran-abstract-shamsa", 1, "شمسه هشت‌پر",
     "Eight-Point Shamsa", eight_point_shamsa),
    ("online-iran-abstract-mosque", 1, "نمای هندسی مسجد ایرانی",
     "Symmetrical Persian Mosque", symmetrical_mosque),
    ("online-iran-abstract-brickwork", 1, "آجر و کاشی ایرانی",
     "Persian Brick and Tile Weave", brick_and_tile),
    ("online-iran-abstract-iwan", 1, "ایوان و حیاط ایرانی",
     "Abstract Iwan Courtyard", abstract_iwan_courtyard),
]


def create_pack(destination):
    manifest = []
    assets = {}
    for identifier, version, fa, en, paint in PICTURES:
        sprite = paint()
        level = {
            "schemaVersion": 2,
            "levelId": identifier,
            "levelVersion": version,
            "titles": {"fa": fa, "en": en},
            "width": sprite.side,
            "height": sprite.side,
            "palette": sprite.palette,
            "cells": sprite.cells,
        }
        level["checksum"] = checksum(level)
        payload = compact(level)
        stem = f"{identifier}-v{version}"
        manifest.append({
            "id": identifier, "version": version,
            "title": fa, "titleEn": en,
            "category": "patterns",
            "width": sprite.side, "height": sprite.side,
            "bytes": len(payload),
            "checksum": level["checksum"],
        })
        assets[f"levels/{stem}.json"] = payload
        assets[f"previews/{stem}.png"] = png(level)
    validate_archived_azadi_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as pack:
        pack.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, payload in assets.items():
            pack.writestr(path, payload)
    print(f"Created {len(manifest)} Iranian architecture levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_iran_architecture_pack.py <content.zip>")
    create_pack(sys.argv[1])
