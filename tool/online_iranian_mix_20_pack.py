#!/usr/bin/env python3
"""Twenty original Iranian heritage, landscape, and culture pixel-art levels.

Only hand-authored vector drawing recipes are committed. The publishing
workflow creates immutable Release-only JSON grids and PNG previews.
Every new ID has levelVersion 1, independent of any existing online artwork.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


SIZE = 64
# Background, outline, ivory, plaster, turquoise, cobalt, pale tile,
# golden stone, gold, walnut, green, deep green, pomegranate, pink,
# water, white, slate, brick, violet, cream.
PALETTE = [
    "FFE9F6FC", "FF30475A", "FFF8EED7", "FFC6B5A0",
    "FF28A9B6", "FF356998", "FF92D7DB", "FFE5B875",
    "FFF6D276", "FF896750", "FF78A568", "FF42735B",
    "FFC94F58", "FFEAA3B4", "FF66B6D6", "FFFFFFFF",
    "FF7084A1", "FFCD825C", "FF987CA9", "FFFFF7E6",
]


def canvas(background=0):
    s = Sprite(SIZE, PALETTE)
    if background:
        s.rect(0, 0, 63, 63, background)
    return s


def diamond(s, x, y, radius, color):
    s.polygon([(x, y-radius), (x+radius, y),
               (x, y+radius), (x-radius, y)], color)


def sun(s, x, y, radius=5):
    s.ellipse(x, y, radius, radius, 8)
    s.ellipse(x-1, y-1, max(1, radius-2), max(1, radius-2), 19)


def horizon(s, ground=10, at=55):
    s.rect(0, at, 63, 63, ground)
    s.rect(0, at, 63, at+1, 11)


def cypress(s, x, base, height=26):
    s.rect(x-1, base-5, x+1, base, 9)
    s.polygon([(x, base-height), (x-6, base-8),
               (x-4, base-4), (x+4, base-4), (x+6, base-8)], 11)
    s.polygon([(x-1, base-height+4), (x-4, base-9),
               (x, base-6)], 10)
    s.line(x+2, base-height+9, x+3, base-9, 10, radius=1)


def leafy_tree(s, x, base, size=9):
    s.rect(x-1, base-size, x+1, base, 9)
    for dx, dy, ratio in [(-.65, -.8, .72), (.6, -.9, .75), (0, -1.5, .9)]:
        s.ellipse(x+dx*size, base+dy*size, size*ratio, size*.72, 11)
    s.ellipse(x-size*.3, base-size*1.65, size*.6, size*.44, 10)


def portal(s, x, y, width, height, frame=5, inside=1):
    """Simple pointed Persian arch, with legible dark aperture."""
    bottom = y+height
    h = width//2
    s.polygon([(x-h, bottom), (x-h, y+h*.65), (x, y),
               (x+h, y+h*.65), (x+h, bottom)], frame)
    inner = h-2
    s.polygon([(x-inner, bottom), (x-inner, y+h*.65+3),
               (x, y+4), (x+inner, y+h*.65+3),
               (x+inner, bottom)], inside)


def dome(s, x, y, radius, outline=5, fill=4, highlight=6):
    """Round bulbous tiled dome crowned with a finial."""
    s.ellipse(x, y, radius, radius*.83, outline)
    s.ellipse(x, y+1, radius-2, radius*.73, fill)
    s.ellipse(x-3, y-3, radius*.44, radius*.25, highlight)
    s.rect(x-radius, y+2, x+radius, y+radius*.85, outline)
    s.rect(x-radius+1, y+3, x+radius-1, y+radius*.75, fill)
    s.line(x, y-radius*.9-4, x, y-radius*.9, 8, radius=.8)
    s.dot(x, round(y-radius*.9-5), 8)


def minaret(s, x, bottom, top=11):
    s.rect(x-3, top+8, x+3, bottom, 5)
    s.rect(x-2, top+9, x+1, bottom-1, 4)
    for y in range(top+14, bottom-3, 7):
        s.rect(x-3, y, x+3, y+1, 6)
    s.rect(x-5, top+6, x+5, top+8, 5)
    dome(s, x, top+5, 5, 5, 4, 6)


def masonry(s, left, top, right, bottom):
    s.rect(left, top, right, bottom, 9)
    s.rect(left+2, top+2, right-2, bottom-1, 7)
    for yy in range(top+5, bottom, 6):
        s.line(left+2, yy, right-2, yy, 3, radius=.5)


def tiles(s, left, top, right, bottom):
    for yy in range(top, bottom+1, 5):
        for xx in range(left, right+1, 5):
            diamond(s, xx, yy, 2, 6 if (xx+yy)//5 % 2 else 5)
            s.dot(xx, yy, 8)


def tiny_window(s, x, y):
    s.rect(x-3, y-5, x+3, y+4, 1)
    s.rect(x-2, y-4, x+2, y+3, 14)
    s.line(x, y-4, x, y+3, 9, radius=.5)


def flower(s, x, y, petal=12):
    s.dot(x-2, y, petal)
    s.dot(x+2, y, petal)
    s.dot(x, y-2, petal)
    s.dot(x, y+2, petal)
    s.dot(x-1, y-1, petal)
    s.dot(x+1, y+1, petal)
    s.dot(x, y, 8)


def blue_mosque_tabriz():
    s = canvas()
    sun(s, 49, 9, 5)
    horizon(s, 3)
    minaret(s, 10, 52, 13)
    minaret(s, 54, 52, 13)
    masonry(s, 16, 34, 48, 54)
    dome(s, 32, 31, 16)
    s.rect(17, 36, 47, 39, 5)
    portal(s, 32, 39, 16, 16, 5, 1)
    s.polygon([(26, 54), (26, 46), (32, 41),
               (38, 46), (38, 54)], 14)
    tiles(s, 18, 41, 22, 50)
    tiles(s, 42, 41, 46, 50)
    s.rect(6, 54, 58, 57, 7)
    return s


def khaju_bridge():
    s = canvas()
    sun(s, 53, 9, 5)
    s.rect(0, 41, 63, 63, 14)
    for yy in range(47, 63, 5):
        s.line(2, yy, 59, yy, 6, radius=.5)
    masonry(s, 2, 29, 61, 49)
    s.rect(2, 27, 61, 30, 9)
    s.rect(4, 28, 60, 29, 8)
    for x in [9, 18, 27, 36, 45, 54]:
        s.ellipse(x, 43, 3.5, 9, 1)
        s.rect(x-3, 43, x+3, 50, 14)
        s.ellipse(x, 42, 2.7, 7, 14)
    s.rect(22, 17, 42, 27, 7)
    s.rect(20, 15, 44, 17, 9)
    for x in [25, 32, 39]:
        portal(s, x, 19, 6, 8, 9, 1)
    s.rect(28, 11, 36, 15, 7)
    s.polygon([(27, 11), (32, 7), (37, 11)], 9)
    for x in [5, 16, 48, 59]:
        s.rect(x, 23, x+1, 27, 9)
    return s


def ali_qapu():
    s = canvas()
    sun(s, 9, 12)
    horizon(s, 10, 55)
    masonry(s, 12, 28, 54, 54)
    s.rect(12, 26, 54, 29, 9)
    s.rect(15, 15, 50, 27, 7)
    s.rect(13, 12, 52, 15, 9)
    s.rect(30, 5, 47, 13, 7)
    s.rect(31, 5, 46, 7, 9)
    s.polygon([(30, 5), (39, 1), (48, 5)], 9)
    for x in [18, 25, 32, 39, 46]:
        s.rect(x, 16, x+1, 26, 9)
        s.rect(x-1, 25, x+2, 27, 3)
    for x in [20, 31, 42]:
        portal(s, x, 34, 9, 20, 9, 1)
    for x in [17, 26, 35, 44]:
        s.rect(x, 30, x+3, 32, 3)
    s.rect(8, 54, 58, 58, 3)
    return s


def chehel_sotoun():
    s = canvas()
    sun(s, 54, 9, 6)
    horizon(s, 10, 44)
    for x in [5, 58]:
        cypress(s, x, 45, 33)
    s.rect(10, 14, 54, 18, 9)
    s.rect(12, 17, 52, 41, 7)
    s.rect(15, 20, 49, 40, 3)
    s.rect(12, 38, 52, 42, 9)
    s.rect(21, 11, 43, 15, 7)
    s.polygon([(20, 11), (32, 6), (44, 11)], 9)
    for x in [17, 23, 29, 35, 41, 47]:
        s.rect(x, 18, x+1, 39, 9)
        s.rect(x-1, 36, x+2, 38, 8)
    s.rect(12, 44, 52, 63, 14)
    s.polygon([(17, 44), (47, 44), (57, 63), (7, 63)], 5)
    s.polygon([(20, 44), (44, 44), (52, 63), (12, 63)], 6)
    for y in [49, 54, 59]:
        s.line(20-y//8, y, 44+y//8, y, 14, radius=.6)
    return s


def shah_cheragh():
    s = canvas()
    sun(s, 11, 10)
    horizon(s, 3, 56)
    minaret(s, 9, 54, 11)
    minaret(s, 55, 54, 11)
    masonry(s, 17, 36, 47, 55)
    dome(s, 32, 27, 15, 11, 10, 6)
    for x in [23, 41]:
        s.rect(x, 38, x+1, 52, 4)
    portal(s, 32, 40, 16, 16, 5, 1)
    s.polygon([(27, 55), (27, 48), (32, 43),
               (37, 48), (37, 55)], 14)
    tiles(s, 18, 42, 21, 53)
    tiles(s, 43, 42, 46, 53)
    s.rect(4, 55, 60, 57, 8)
    return s


def fin_garden():
    s = canvas()
    s.rect(0, 28, 63, 63, 10)
    s.rect(0, 33, 63, 38, 11)
    masonry(s, 19, 17, 45, 34)
    s.polygon([(16, 17), (32, 10), (48, 17)], 9)
    s.rect(17, 16, 47, 19, 8)
    for x in [23, 32, 41]:
        portal(s, x, 23, 7, 11, 9, 1)
    for x in [5, 12, 52, 59]:
        cypress(s, x, 50, 31 if x % 2 else 24)
    s.polygon([(28, 34), (36, 34), (52, 63), (12, 63)], 3)
    s.polygon([(30, 34), (34, 34), (47, 63), (17, 63)], 14)
    for y, radius in [(42, 3), (51, 5), (59, 7)]:
        s.ellipse(32, y, radius, 1.4, 6)
    s.ellipse(32, 37, 4, 2, 15)
    return s


def eram_garden():
    s = canvas()
    sun(s, 49, 10)
    horizon(s, 10, 55)
    cypress(s, 7, 57, 43)
    cypress(s, 57, 57, 42)
    masonry(s, 14, 23, 50, 54)
    s.rect(12, 21, 52, 24, 9)
    s.rect(20, 13, 44, 22, 7)
    s.rect(19, 11, 45, 14, 5)
    s.polygon([(18, 11), (32, 5), (46, 11)], 7)
    for x in [19, 27, 37, 45]:
        tiny_window(s, x, 35)
        tiny_window(s, x, 47)
    portal(s, 32, 41, 8, 13, 5, 1)
    tiles(s, 23, 16, 41, 18)
    s.rect(24, 54, 40, 62, 14)
    for x in [15, 49]:
        leafy_tree(s, x, 61, 6)
    return s


def masuleh_village():
    s = canvas()
    sun(s, 53, 9)
    s.polygon([(0, 23), (16, 9), (27, 24), (44, 16),
               (63, 29), (63, 63), (0, 63)], 11)
    s.polygon([(0, 36), (11, 25), (22, 33), (39, 25),
               (63, 39), (63, 63), (0, 63)], 10)
    houses = [(3, 33, 17, 46), (22, 25, 35, 39), (39, 34, 58, 48),
              (9, 47, 26, 60), (30, 43, 46, 58), (47, 49, 62, 62)]
    for i, (x0, y0, x1, y1) in enumerate(houses):
        s.rect(x0, y0, x1, y1, 9)
        s.rect(x0+1, y0+2, x1-1, y1-1, 7 if i % 2 else 2)
        s.rect(x0-1, y0, x1+1, y0+2, 17)
        s.rect(x0+3, y0+5, x0+6, y0+10, 5)
        s.rect(x1-6, y0+5, x1-3, y0+10, 4)
        s.rect(x0+2, y1-2, x1-2, y1-1, 3)
    for x,y in [(3, 21), (47, 25), (56, 39)]:
        leafy_tree(s, x, y+17, 6)
    return s


def kandovan_village():
    s = canvas()
    horizon(s, 7, 51)
    sun(s, 51, 9)
    s.polygon([(0, 53), (5, 26), (14, 20), (24, 49),
               (29, 34), (37, 17), (48, 47), (55, 29),
               (63, 43), (63, 63), (0, 63)], 9)
    s.polygon([(1, 52), (7, 28), (14, 24), (21, 51),
               (27, 38), (37, 21), (46, 50), (55, 33),
               (61, 46), (61, 61), (2, 61)], 7)
    for x, y, width in [(13, 21, 10), (37, 19, 12), (54, 31, 7)]:
        s.line(x-width//2, 51, x, y, 3, radius=1)
        s.line(x, y, x+width//2, 51, 3, radius=1)
        s.ellipse(x, 42 if y<25 else 49, 3.5, 5, 1)
        s.rect(x-2, 42 if y<25 else 49, x+2, 54, 9)
        s.ellipse(x-5, 34 if y<25 else 43, 1.3, 1.8, 1)
        s.ellipse(x+5, 34 if y<25 else 43, 1.3, 1.8, 1)
    s.line(1, 55, 62, 55, 3)
    return s


def lut_kaluts():
    s = canvas(19)
    s.rect(0, 28, 63, 63, 7)
    sun(s, 50, 12, 8)
    s.polygon([(0, 52), (16, 48), (34, 54), (53, 47),
               (63, 53), (63, 63), (0, 63)], 17)
    for x, top, width in [(7, 22, 10), (28, 9, 16), (53, 20, 11)]:
        s.polygon([(x-width//2, 54), (x-width//2+2, top+12),
                   (x-2, top+7), (x-4, top), (x+4, top-2),
                   (x+2, top+9), (x+width//2, top+13),
                   (x+width//2+3, 54)], 9)
        s.polygon([(x-width//2+1, 52), (x-width//2+4, top+12),
                   (x, top+4), (x+1, top+12), (x+width//2, 52)], 17)
        for y in range(top+16, 51, 7):
            s.line(x-width//2+2, y, x+width//2-1, y+1, 7, radius=.6)
        s.line(x-2, top+6, x-1, top+12, 3)
    s.polygon([(0, 58), (28, 52), (63, 56), (63, 63), (0, 63)], 7)
    return s


def anzali_lagoon():
    s = canvas()
    sun(s, 50, 9)
    s.rect(0, 35, 63, 63, 14)
    s.rect(0, 34, 63, 36, 10)
    for x in range(0, 63, 9):
        cypress(s, x, 36, 13 if x % 2 else 17)
    s.rect(0, 37, 63, 39, 6)
    for x, y, r in [(11, 47, 6), (49, 49, 8), (26, 57, 5),
                    (55, 58, 4), (6, 58, 4)]:
        s.ellipse(x, y, r, 2.3, 11)
        s.ellipse(x-1, y-1, r-2, 1.4, 10)
    for x, y in [(12, 46), (48, 48), (28, 56)]:
        s.line(x, y, x, y-8, 11, radius=.6)
        flower(s, x, y-9, 13)
    s.polygon([(20, 45), (43, 45), (38, 50), (25, 50)], 9)
    s.rect(31, 36, 32, 45, 1)
    s.polygon([(30, 37), (30, 44), (22, 44)], 15)
    for y in [52, 60]:
        s.line(19, y, 43, y, 6, radius=.7)
    return s


def damavand():
    s = canvas()
    sun(s, 51, 11, 6)
    s.polygon([(0, 47), (10, 36), (20, 42), (35, 13),
               (46, 37), (56, 34), (63, 43), (63, 63), (0, 63)], 16)
    s.polygon([(11, 52), (35, 9), (59, 53), (63, 63), (0, 63)], 5)
    s.polygon([(15, 54), (35, 11), (55, 54), (50, 63),
               (20, 63)], 3)
    s.polygon([(23, 37), (35, 11), (47, 37), (41, 34),
               (37, 39), (31, 31), (27, 39)], 15)
    s.polygon([(29, 35), (35, 13), (41, 34), (38, 30),
               (34, 32)], 2)
    s.polygon([(0, 52), (12, 48), (22, 54), (37, 49),
               (52, 53), (63, 50), (63, 63), (0, 63)], 11)
    s.polygon([(0, 60), (15, 55), (26, 58), (45, 55),
               (63, 58), (63, 63), (0, 63)], 10)
    for x in [7, 14, 53, 60]:
        cypress(s, x, 63, 12)
    return s


def persian_carpet():
    s = canvas(9)
    s.rect(4, 3, 59, 60, 1)
    s.rect(6, 5, 57, 58, 12)
    s.rect(9, 8, 54, 55, 8)
    s.rect(12, 11, 51, 52, 5)
    s.rect(15, 14, 48, 49, 12)
    s.rect(17, 16, 46, 47, 5)
    # Repeated floral motifs along two borders.
    for x in range(9, 56, 7):
        diamond(s, x, 9, 2, 15)
        diamond(s, x, 54, 2, 15)
    for y in range(11, 53, 7):
        diamond(s, 10, y, 2, 15)
        diamond(s, 53, y, 2, 15)
    for x, y in [(20, 19), (44, 19), (20, 45), (44, 45)]:
        flower(s, x, y, 8)
    diamond(s, 32, 31, 16, 8)
    diamond(s, 32, 31, 13, 1)
    diamond(s, 32, 31, 11, 4)
    diamond(s, 32, 31, 8, 19)
    diamond(s, 32, 31, 5, 12)
    flower(s, 32, 31, 8)
    for x in range(8, 56, 4):
        s.rect(x, 1, x, 2, 2)
        s.rect(x, 61, x, 62, 2)
    return s


def minakari_plate():
    s = canvas(19)
    s.ellipse(32, 32, 28, 28, 1)
    s.ellipse(32, 32, 26, 26, 5)
    s.ellipse(32, 32, 23, 23, 6)
    s.ellipse(32, 32, 20, 20, 5)
    s.ellipse(32, 32, 17, 17, 19)
    s.ellipse(32, 32, 13, 13, 4)
    s.ellipse(32, 32, 6, 6, 5)
    for i in range(12):
        ang = 2*math.pi*i/12
        x = int(round(32+21*math.cos(ang)))
        y = int(round(32+21*math.sin(ang)))
        s.ellipse(x, y, 2.5, 2.5, 8 if i % 2 else 15)
    for i in range(8):
        ang = 2*math.pi*i/8
        x = int(round(32+10*math.cos(ang)))
        y = int(round(32+10*math.sin(ang)))
        s.ellipse(x, y, 3.3, 3.3, 6)
        s.ellipse(x, y, 1.5, 1.5, 15)
    flower(s, 32, 32, 8)
    return s


def khatam_box():
    s = canvas(19)
    s.ellipse(32, 54, 26, 3, 3)
    s.polygon([(7, 22), (45, 17), (58, 30), (19, 37)], 1)
    s.polygon([(9, 22), (45, 19), (55, 30), (19, 35)], 9)
    s.polygon([(8, 23), (19, 35), (19, 51), (8, 40)], 1)
    s.polygon([(10, 26), (18, 35), (18, 48), (10, 39)], 17)
    s.polygon([(19, 36), (57, 29), (57, 44), (19, 52)], 1)
    s.polygon([(21, 38), (55, 32), (55, 43), (21, 49)], 9)
    for y in [39, 44]:
        s.line(22, y+1, 53, y-5, 8, radius=.5)
    for x in range(17, 50, 6):
        for y in range(24, 35, 5):
            diamond(s, x+(y-24)//5*2, y, 2, 8)
            s.dot(x+(y-24)//5*2, y, 15)
    s.rect(36, 37, 41, 41, 8)
    s.dot(39, 39, 1)
    s.line(13, 29, 18, 35, 8)
    return s


def samovar_tea():
    s = canvas(19)
    s.ellipse(28, 55, 23, 2.5, 3)
    s.rect(16, 49, 42, 52, 1)
    s.rect(18, 50, 40, 51, 8)
    s.rect(21, 42, 36, 50, 9)
    s.rect(23, 43, 34, 48, 8)
    s.ellipse(28, 30, 15, 18, 1)
    s.ellipse(28, 30, 13.5, 16, 8)
    s.ellipse(25, 25, 5, 11, 7)
    s.ellipse(10, 29, 5, 9, 1)
    s.ellipse(10, 29, 3, 7, 19)
    s.ellipse(46, 29, 5, 9, 1)
    s.ellipse(46, 29, 3, 7, 19)
    s.rect(23, 7, 33, 14, 1)
    s.rect(24, 8, 32, 12, 8)
    s.ellipse(28, 6, 3, 3, 8)
    s.rect(20, 13, 36, 15, 1)
    s.rect(35, 34, 46, 37, 1)
    s.rect(40, 36, 42, 42, 1)
    s.ellipse(41, 43, 2, 2, 8)
    s.rect(46, 40, 58, 54, 1)
    s.rect(48, 42, 56, 51, 12)
    s.rect(49, 42, 55, 44, 8)
    s.rect(46, 53, 59, 55, 9)
    for y in [24, 31, 37]:
        s.line(23, y, 33, y, 7, radius=.5)
    return s


def santur():
    s = canvas(19)
    s.ellipse(30, 54, 27, 2.5, 3)
    s.polygon([(14, 25), (48, 25), (60, 45), (3, 45)], 1)
    s.polygon([(15, 27), (47, 27), (56, 43), (7, 43)], 9)
    s.polygon([(18, 29), (44, 29), (52, 41), (11, 41)], 7)
    for x in range(17, 48, 3):
        s.line(x, 29, x+3, 42, 2, radius=.45)
    s.line(25, 29, 23, 42, 1, radius=1.1)
    s.line(39, 29, 41, 42, 1, radius=1.1)
    for x in [17, 47]:
        diamond(s, x, 36, 3, 1)
        diamond(s, x, 36, 2, 8)
    s.rect(9, 45, 11, 52, 9)
    s.rect(52, 45, 54, 52, 9)
    s.line(16, 15, 35, 33, 9, radius=1)
    s.line(44, 12, 27, 32, 9, radius=1)
    s.ellipse(15, 14, 3, 2, 8)
    s.ellipse(45, 11, 3, 2, 8)
    return s


def tombak():
    s = canvas(19)
    s.ellipse(32, 55, 20, 3, 3)
    s.polygon([(19, 24), (45, 24), (43, 31), (37, 39),
               (38, 48), (45, 53), (19, 53), (26, 48),
               (27, 39), (21, 31)], 1)
    s.polygon([(21, 26), (43, 26), (41, 32), (35, 39),
               (36, 48), (42, 51), (22, 51), (28, 48),
               (29, 39), (23, 32)], 9)
    s.ellipse(32, 23, 18, 8, 1)
    s.ellipse(32, 22, 16, 6.5, 7)
    s.ellipse(32, 21, 14, 4.5, 2)
    for y in [34, 39, 46]:
        s.line(25, y, 39, y, 8, radius=.7)
    for x, y in [(26, 34), (32, 37), (38, 34), (29, 45), (35, 45)]:
        diamond(s, x, y, 2, 8)
    s.rect(19, 53, 45, 56, 1)
    s.rect(21, 54, 43, 55, 8)
    return s


def haft_sin():
    s = canvas(19)
    s.rect(0, 48, 63, 63, 5)
    s.rect(2, 49, 61, 52, 4)
    for x in range(6, 62, 8):
        diamond(s, x, 56, 3, 8)
    s.rect(25, 7, 39, 29, 1)  # mirror
    s.rect(27, 9, 37, 26, 14)
    s.ellipse(32, 12, 4, 4, 15)
    s.rect(30, 24, 34, 27, 9)
    s.rect(16, 24, 23, 42, 9)  # sprouted greens
    s.rect(17, 38, 22, 43, 7)
    for x in [15, 18, 20, 22, 25]:
        s.line(20, 33, x, 22-(x%3), 11, radius=.8)
        s.ellipse(x, 21-(x%3), 2, 4, 10)
    s.ellipse(47, 35, 9, 7, 1)  # goldfish bowl
    s.ellipse(47, 34, 7, 5, 6)
    s.ellipse(47, 36, 3, 1.6, 12)
    s.dot(49, 35, 1)
    s.polygon([(44, 36), (40, 33), (41, 39)], 12)
    s.ellipse(9, 43, 5, 5, 12)  # apple
    s.ellipse(10, 39, 3, 2, 13)
    s.line(9, 39, 11, 35, 9)
    for x in [29, 35, 40]:
        s.ellipse(x, 44, 2.8, 3.5, 2 if x==40 else 8)
    s.rect(50, 44, 59, 48, 8)  # book
    s.rect(51, 44, 58, 45, 15)
    s.ellipse(18, 46, 4, 2, 3)  # garlic / vinegar
    return s


def yalda_pomegranate():
    s = canvas(19)
    s.ellipse(30, 56, 24, 2.5, 3)
    s.ellipse(35, 36, 19, 18, 1)
    s.ellipse(35, 36, 17.5, 16.5, 12)
    s.ellipse(35, 36, 14, 13, 2)
    s.ellipse(35, 36, 12.5, 11.5, 13)
    for y in range(27, 48, 5):
        for x in range(24+(y//5)%2*2, 48, 5):
            if ((x-35)/12)**2+((y-36)/11)**2 < .9:
                s.ellipse(x, y, 2.1, 2.3, 12)
                s.dot(x-1, y-1, 15)
    s.polygon([(28, 18), (30, 12), (34, 16),
               (38, 12), (42, 17), (40, 21)], 12)
    s.ellipse(14, 46, 9, 10, 1)
    s.ellipse(14, 46, 8, 9, 12)
    s.polygon([(9, 37), (8, 31), (13, 35),
               (16, 31), (20, 36)], 12)
    s.polygon([(20, 19), (28, 12), (38, 10), (32, 20)], 11)
    s.polygon([(22, 18), (31, 14), (37, 13), (29, 19)], 10)
    for x,y in [(6, 21), (51, 14), (52, 53)]:
        flower(s, x, y, 13)
    return s


# Older clients accept only nature / animals / objects / patterns / space.
# Architectural scenes use patterns until a versioned category rollout exists.
PICTURES = [
    ("online-iran-blue-mosque-tabriz", "مسجد کبود تبریز",
     "Blue Mosque of Tabriz", "patterns", blue_mosque_tabriz),
    ("online-iran-khaju-bridge", "پل خواجو", "Khaju Bridge",
     "patterns", khaju_bridge),
    ("online-iran-ali-qapu", "عمارت عالی‌قاپو", "Ali Qapu Palace",
     "patterns", ali_qapu),
    ("online-iran-chehel-sotoun", "کاخ چهل‌ستون", "Chehel Sotoun Palace",
     "patterns", chehel_sotoun),
    ("online-iran-shah-cheragh", "شاه‌چراغ", "Shah Cheragh Shrine",
     "patterns", shah_cheragh),
    ("online-iran-fin-garden", "باغ فین کاشان", "Fin Garden",
     "nature", fin_garden),
    ("online-iran-eram-garden", "باغ ارم شیراز", "Eram Garden",
     "nature", eram_garden),
    ("online-iran-masuleh-village", "خانه‌های ماسوله", "Masuleh Village",
     "patterns", masuleh_village),
    ("online-iran-kandovan", "روستای کندوان", "Kandovan Village",
     "patterns", kandovan_village),
    ("online-iran-lut-kaluts", "کلوت‌های کویر لوت", "Lut Desert Kaluts",
     "nature", lut_kaluts),
    ("online-iran-anzali-lagoon", "تالاب انزلی", "Anzali Lagoon",
     "nature", anzali_lagoon),
    ("online-iran-damavand", "قله دماوند", "Mount Damavand",
     "nature", damavand),
    ("online-iran-persian-carpet", "فرش ایرانی", "Persian Carpet Medallion",
     "patterns", persian_carpet),
    ("online-iran-minakari-plate", "بشقاب میناکاری", "Minakari Plate",
     "objects", minakari_plate),
    ("online-iran-khatam-box", "جعبه خاتم‌کاری", "Khatamkari Box",
     "objects", khatam_box),
    ("online-iran-samovar-tea", "سماور و استکان چای",
     "Samovar and Tea Glass", "objects", samovar_tea),
    ("online-iran-santur", "سنتور", "Santur",
     "objects", santur),
    ("online-iran-tombak", "تنبک", "Tombak Drum",
     "objects", tombak),
    ("online-iran-haft-sin", "سفره هفت‌سین", "Haft-Seen Table",
     "objects", haft_sin),
    ("online-iran-yalda-pomegranate", "انار شب یلدا", "Yalda Pomegranate",
     "objects", yalda_pomegranate),
]


def create_pack(destination):
    if len(PICTURES) != 20:
        raise ValueError("Expected exactly twenty original Iranian pictures")
    manifest = []
    files = {}
    for identifier, fa, en, category, painter in PICTURES:
        artwork = painter()
        level = {
            "schemaVersion": 2,
            "levelId": identifier,
            "levelVersion": 1,
            "titles": {"fa": fa, "en": en},
            "width": artwork.side, "height": artwork.side,
            "palette": artwork.palette, "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        content = compact(level)
        if len(content) > 262144:
            raise ValueError(f"Oversized online painting: {identifier}")
        stem = f"{identifier}-v1"
        manifest.append({
            "id": identifier, "version": 1,
            "title": fa, "titleEn": en, "category": category,
            "width": artwork.side, "height": artwork.side,
            "bytes": len(content), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = content
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    output = pathlib.Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "catalog.json", compact({"schemaVersion": 1, "pictures": manifest})
        )
        for path, data in files.items():
            archive.writestr(path, data)
    print(f"Prepared {len(manifest)} original Iranian levels: {output}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 tool/online_iranian_mix_20_pack.py <content.zip>"
        )
    create_pack(sys.argv[1])
