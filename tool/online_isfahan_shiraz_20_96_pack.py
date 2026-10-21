#!/usr/bin/env python3
"""Twenty hand-composed 96x96 Isfahan and Shiraz pixel-art coloring levels.

Source-only recipes: schema-v2 JSON and PNG previews are built into an
immutable GitHub Release by the Pages workflow, never added to the APK.
These are new views/landmarks, not replacements for previously released IDs.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 96
PALETTE = [
    "FFE7F3F8",  # 0 sky
    "FF304052",  # 1 deep outline
    "FFE8C79E",  # 2 pale limestone
    "FFBD8761",  # 3 brick
    "FF8A5B4B",  # 4 brick shadow
    "FFF9E9C9",  # 5 cream
    "FF126B89",  # 6 dark cobalt tiles
    "FF278EAD",  # 7 turquoise
    "FF80D3D8",  # 8 tile highlights
    "FFDBA54F",  # 9 ochre
    "FF22614A",  # 10 cypress green
    "FF5F9F65",  # 11 leaf green
    "FFA5C783",  # 12 light leaves / grass
    "FF275D80",  # 13 deep water
    "FF68B7CE",  # 14 water
    "FFEA7580",  # 15 blossoms
    "FFB55245",  # 16 ruby brick / flowers
    "FF785F8E",  # 17 violet / glazing
    "FFF1CD59",  # 18 sunlight / gilding
    "FF573E39",  # 19 dark wood
    "FFB2A497",  # 20 rock
    "FFDFE1D8",  # 21 white plaster
    "FFFFFEF5",  # 22 reflections
    "FFDD943B",  # 23 orange fruit
    "FF8EB4C2",  # 24 shadows
    "FF6E8B62",  # 25 shaded foliage
    "FFCEBDD7",  # 26 colored glass
    "FF493B67",  # 27 dark glass
]

# (slug, Persian title, English title, city, drawing recipe)
# Older single-structure views, including Si-o-se-pol, Khaju, Ali Qapu,
# Sheikh Lotfollah, Chehel Sotoun, Jameh Mosque, Hafez, Saadi, Eram,
# Quran Gate, Nasir ol-Molk and Arg-e Karim Khan, are intentionally excluded.
PICTURES = [
    ("naqsh-jahan-square", "میدان نقش جهان اصفهان", "Naqsh-e Jahan Square, Isfahan", "isfahan", "square"),
    ("hasht-behesht", "کاخ هشت بهشت اصفهان", "Hasht Behesht Palace, Isfahan", "isfahan", "hasht"),
    ("menar-jonban", "منارجنبان اصفهان", "Menar Jonban, Isfahan", "isfahan", "menar"),
    ("qeysarie-gate", "سردر قیصریه اصفهان", "Qeysarie Bazaar Gate, Isfahan", "isfahan", "qeysarie"),
    ("chaharbagh-abbasi", "چهارباغ عباسی اصفهان", "Chaharbagh Abbasi Avenue, Isfahan", "isfahan", "chaharbagh"),
    ("shahrestan-bridge", "پل شهرستان اصفهان", "Shahrestan Bridge, Isfahan", "isfahan", "shahrestan"),
    ("marnan-bridge", "پل مارنان اصفهان", "Marnan Bridge, Isfahan", "isfahan", "marnan"),
    ("hakim-mosque", "مسجد حکیم اصفهان", "Hakim Mosque, Isfahan", "isfahan", "hakim"),
    ("pigeon-towers", "کبوترخانه‌های اصفهان", "Historic Pigeon Towers, Isfahan", "isfahan", "pigeons"),
    ("atashgah", "آتشگاه اصفهان", "Atashgah Fire Temple, Isfahan", "isfahan", "atashgah"),
    ("vakil-mosque", "مسجد وکیل شیراز", "Vakil Mosque, Shiraz", "shiraz", "vakil_mosque"),
    ("vakil-bazaar", "بازار وکیل شیراز", "Vakil Bazaar, Shiraz", "shiraz", "vakil_bazaar"),
    ("vakil-bath", "حمام وکیل شیراز", "Vakil Bathhouse, Shiraz", "shiraz", "vakil_bath"),
    ("narenjestan-qavam", "نارنجستان قوام شیراز", "Narenjestan-e Qavam, Shiraz", "shiraz", "qavam"),
    ("afif-abad", "باغ عفیف‌آباد شیراز", "Afif-Abad Garden, Shiraz", "shiraz", "afif"),
    ("delgosha-garden", "باغ دلگشا شیراز", "Delgosha Garden, Shiraz", "shiraz", "delgosha"),
    ("jahan-nama-garden", "باغ جهان‌نما شیراز", "Jahan Nama Garden, Shiraz", "shiraz", "jahan"),
    ("haft-tanan", "باغ‌موزه هفت‌تنان شیراز", "Haft Tanan Museum, Shiraz", "shiraz", "haft"),
    ("khaju-kermani", "آرامگاه خواجوی کرمانی شیراز", "Khaju Kermani Tomb, Shiraz", "shiraz", "khaju"),
    ("shapouri-house", "عمارت شاپوری شیراز", "Shapouri House, Shiraz", "shiraz", "shapouri"),
]


def rect(s, a, b, c, d, fill, rim=1):
    """Architectural rectangle with a one-pixel ink silhouette."""
    s.rect(a - 1, b - 1, c + 1, d + 1, rim)
    s.rect(a, b, c, d, fill)


def sky(s, horizon=74, garden=True):
    s.ellipse(80, 13, 5, 5, 18)
    for x, y in ((7, 12), (44, 8)):
        s.ellipse(x + 7, y, 7, 2, 22)
        s.ellipse(x + 2, y + 1, 5, 2, 22)
    if garden:
        s.rect(0, horizon, 95, 95, 12)
        s.line(0, horizon, 95, horizon, 10, 1)


def masonry(s, x0, y0, x1, y1, color=4, spacing=6):
    for y in range(y0, y1, spacing):
        offset = (spacing // 2) if (y // spacing) % 2 else 0
        for x in range(x0 + offset, x1, spacing * 2):
            s.line(x, y, min(x + spacing, x1), y, color)
            s.dot(x, min(y + 2, y1), color)


def tiles(s, x0, y0, x1, y1, dense=6):
    """Small alternating tile glints, each an editable color-by-number cell."""
    for y in range(y0, y1 + 1, dense):
        for x in range(x0 + ((y // dense) % 2) * (dense // 2), x1 + 1, dense):
            s.dot(x, y, 8)
            if x + 1 <= x1:
                s.dot(x + 1, y + 1, 18)


def pointed(s, x, top, bottom, half, wall=3, opening=1):
    """Three nested pointed arches preserve the recognizable Persian silhouette."""
    s.polygon([(x-half, bottom), (x-half, top + half * .55),
               (x, top), (x+half, top + half * .55), (x+half, bottom)], 1)
    a = half - 2
    s.polygon([(x-a, bottom-1), (x-a, top + a*.55 + 2),
               (x, top+3), (x+a, top + a*.55 + 2), (x+a, bottom-1)], wall)
    a = max(2, half-5)
    s.polygon([(x-a, bottom-2), (x-a, top + a*.57 + 6),
               (x, top+8), (x+a, top + a*.57 + 6), (x+a, bottom-2)], opening)
    for d in (-half+3, half-3):
        s.dot(x+d, min(bottom-3, top+half//2+5), 8)


def arcade(s, left, right, top, bottom, count, stone=3, opening=19):
    step = (right - left) / count
    for i in range(count):
        x = round(left + (i + .5) * step)
        pointed(s, x, top, bottom, max(4, round(step*.46)), stone, opening)


def dome(s, x, center, radius, color=7):
    s.ellipse(x, center, radius + 2, radius*.8, 1)
    s.ellipse(x, center, radius, radius*.77, color)
    s.rect(x-radius-2, center, x+radius+2, center+6, 1)
    s.rect(x-radius, center, x+radius, center+5, color)
    for dx in range(-radius+3, radius, 5):
        y = center - round((1 - (dx / radius)**2)**.5 * radius*.7)
        s.dot(x + dx, y+2, 8)
    s.line(x, center-radius*.8-7, x, center-radius*.8-1, 1)
    s.dot(x, round(center-radius*.8-8), 18)


def minaret(s, x, top, base, width=8, tile=7):
    rect(s, x-width//2, top+7, x+width//2, base, tile)
    s.polygon([(x-width//2-2, top+8), (x, top), (x+width//2+2, top+8)], 1)
    s.polygon([(x-width//2, top+7), (x, top+2), (x+width//2, top+7)], 8)
    s.rect(x-width//2-2, top+13, x+width//2+2, top+15, 1)
    s.rect(x-width//2-1, top+14, x+width//2+1, top+14, 18)
    for y in range(top+21, base-5, 10):
        s.rect(x-1, y, x+1, y+5, 1)
        s.dot(x, y, 8)


def cypress(s, x, base, height=34):
    s.rect(x-1, base-7, x+1, base+1, 19)
    s.polygon([(x, base-height), (x-8, base-9),
               (x-5, base-5), (x+5, base-5), (x+8, base-9)], 10)
    s.polygon([(x, base-height+5), (x-4, base-13),
               (x+1, base-8), (x+3, base-13)], 11)
    for y in range(base-height+12, base-10, 9):
        s.line(x-3, y, x-2, y+3, 25)


def orange_tree(s, x, base, radius=11):
    s.rect(x-1, base-9, x+1, base, 19)
    s.ellipse(x, base-radius-7, radius, radius*.82, 10)
    s.ellipse(x+2, base-radius-9, radius*.75, radius*.65, 11)
    for dx, dy in ((-5, -9), (4, -14), (7, -6), (-2, -18)):
        s.dot(x+dx, base+dy-radius//2, 23)


def water(s, top=77):
    s.rect(0, top, 95, 95, 13)
    for y in range(top+3, 96, 5):
        for x in range((y*3) % 13, 95, 17):
            s.line(x, y, min(x+9, 95), y, 14)
            s.dot(min(x+2, 95), y+1, 8)


def channel(s, start_y=58, end_y=95, width=12):
    s.polygon([(48-width//4, start_y), (48+width//4, start_y),
               (48+width, end_y), (48-width, end_y)], 13)
    s.polygon([(47-width//4, start_y), (48+width//4-1, start_y),
               (47+width-3, end_y), (50-width+3, end_y)], 14)
    for y in range(start_y+5, end_y, 7):
        spread = 2 + (y-start_y)*width/max(1, end_y-start_y)
        s.line(48-spread*.5, y, 48+spread*.5, y, 22)


def windows(s, start, stop, y, count, glass=27):
    step = (stop-start)/(count+1)
    for i in range(count):
        x = round(start+(i+1)*step)
        s.rect(x-2, y, x+2, y+8, 1)
        s.rect(x-1, y+1, x+1, y+6, glass)
        s.dot(x, y+2, 8)


def colonnade(s, left, right, ytop, bottom, count):
    for i in range(count):
        x = round(left+(right-left)*i/max(1, count-1))
        s.rect(x-2, ytop, x+2, bottom, 1)
        s.rect(x-1, ytop+1, x, bottom-1, 5)
        s.rect(x-4, ytop-2, x+4, ytop, 2)
        s.rect(x-4, bottom-2, x+4, bottom, 3)


def bridge(s, top, arches, warm=False):
    wall = 3 if warm else 2
    water(s, 74)
    s.rect(3, top, 92, 76, 1)
    s.rect(4, top+2, 91, 74, wall)
    s.rect(1, top-3, 94, top, 1)
    for i in range(arches):
        x = round(8 + i*79/max(1, arches-1))
        span = 6 if arches < 9 else 4
        pointed(s, x, top+9, 76, span, wall, 13)
    for x in range(6, 93, 5):
        s.rect(x, top-8, x+1, top-3, 4)
        s.dot(x, top-9, 5)
    masonry(s, 4, top+5, 92, top+11, 4)
    for y in (80, 88, 93):
        s.line(5, y, 88, y, 14)


def glass_facade(s, x0, x1, y, panes):
    for i in range(panes):
        x = round(x0+(i+.5)*(x1-x0)/panes)
        s.rect(x-3, y, x+3, y+13, 1)
        s.rect(x-2, y+1, x+2, y+5, 17 if i%2 else 7)
        s.rect(x-2, y+7, x+2, y+11, 26 if i%2 else 16)
        s.line(x, y+1, x, y+12, 18)


def paint(kind):
    s = Sprite(SIDE, PALETTE)
    if kind == "square":
        sky(s, 68)
        s.rect(0, 32, 95, 69, 2)
        arcade(s, 3, 93, 43, 69, 10, 3, 19)
        dome(s, 48, 22, 15, 7)
        minaret(s, 25, 6, 47, 7)
        minaret(s, 71, 6, 47, 7)
        pointed(s, 48, 38, 70, 13, 7, 6)
        tiles(s, 37, 49, 59, 55, 5)
        s.polygon([(0, 72), (95, 72), (90, 95), (5, 95)], 11)
        s.polygon([(37, 72), (59, 72), (69, 95), (27, 95)], 5)
        channel(s, 73, 95, 9)
        for x in (8, 18, 78, 88):
            cypress(s, x, 83, 16)
    elif kind == "hasht":
        sky(s, 77)
        rect(s, 12, 37, 83, 72, 2)
        s.polygon([(8, 38), (47, 26), (87, 38)], 1)
        s.polygon([(14, 37), (47, 29), (81, 37)], 9)
        rect(s, 23, 17, 72, 36, 3)
        windows(s, 23, 72, 21, 6)
        arcade(s, 13, 83, 45, 70, 7, 3, 19)
        colonnade(s, 15, 80, 41, 70, 5)
        s.rect(25, 73, 69, 76, 3)
        channel(s, 78, 95, 17)
        for x in (6, 89): cypress(s, x, 84, 36)
        for x in (15, 80): s.ellipse(x, 80, 8, 4, 11)
    elif kind == "menar":
        sky(s, 81)
        rect(s, 13, 41, 82, 80, 3)
        rect(s, 19, 32, 76, 44, 2)
        minaret(s, 18, 6, 55, 8, 3)
        minaret(s, 77, 6, 55, 8, 3)
        pointed(s, 47, 40, 81, 19, 2, 19)
        pointed(s, 47, 47, 81, 13, 3, 27)
        for x in (26, 69): windows(s, x-7, x+7, 53, 2)
        masonry(s, 22, 33, 74, 40, 4)
        s.rect(0, 82, 95, 95, 20)
        for x in (8, 87): cypress(s, x, 80, 24)
    elif kind == "qeysarie":
        sky(s, 90, False)
        rect(s, 4, 25, 91, 91, 3)
        s.rect(9, 22, 86, 30, 1)
        s.rect(11, 23, 84, 28, 7)
        pointed(s, 48, 31, 92, 31, 6, 19)
        pointed(s, 48, 42, 92, 23, 7, 27)
        for y in (38, 46, 54):
            for x in range(27, 70, 8): s.dot(x, y, 18)
        for x in (12, 84):
            pointed(s, x, 55, 91, 7, 2, 19)
        s.ellipse(48, 18, 9, 9, 1)
        s.ellipse(48, 18, 7, 7, 5)
        s.line(48, 18, 48, 13, 1)
        s.line(48, 18, 52, 20, 1)
        masonry(s, 3, 31, 18, 89)
        masonry(s, 79, 31, 93, 89)
        s.rect(0, 92, 95, 95, 20)
    elif kind == "chaharbagh":
        sky(s, 65)
        s.polygon([(0, 95), (43, 53), (53, 53), (95, 95)], 2)
        s.polygon([(20, 95), (46, 55), (50, 55), (76, 95)], 12)
        channel(s, 59, 95, 10)
        for x, b, h in ((11, 85, 42), (27, 75, 27), (37, 65, 16),
                        (59, 65, 16), (69, 75, 27), (85, 85, 42)):
            orange_tree(s, x, b, max(5, h//3))
        for x in (3, 93): cypress(s, x, 91, 38)
        for y in (71, 81, 91):
            s.line(8, y, 33, y, 9)
            s.line(64, y, 88, y, 9)
    elif kind == "shahrestan":
        sky(s, 81)
        s.polygon([(0, 73), (12, 67), (25, 74), (38, 69),
                   (60, 75), (83, 65), (95, 74), (95, 95), (0, 95)], 25)
        bridge(s, 45, 9)
        s.polygon([(0, 71), (10, 67), (15, 82), (0, 88)], 20)
        s.polygon([(95, 66), (86, 71), (84, 85), (95, 88)], 20)
        for x in (9, 85): cypress(s, x, 66, 24)
    elif kind == "marnan":
        sky(s, 79)
        bridge(s, 51, 11, True)
        s.rect(4, 43, 91, 48, 3)
        for x in (18, 47, 74):
            rect(s, x-2, 34, x+2, 49, 4)
        s.polygon([(0, 71), (12, 67), (22, 74), (20, 91), (0, 95)], 11)
        orange_tree(s, 6, 76, 12)
        for x in range(12, 90, 13): s.line(x, 84, x+5, 84, 8)
    elif kind == "hakim":
        sky(s, 87)
        rect(s, 4, 27, 91, 87, 3)
        rect(s, 22, 17, 74, 85, 2)
        pointed(s, 48, 25, 87, 24, 6, 19)
        pointed(s, 48, 35, 87, 16, 7, 27)
        for x in (11, 84): minaret(s, x, 14, 87, 7, 3)
        tiles(s, 25, 24, 71, 35, 5)
        for x in (11, 85):
            pointed(s, x, 57, 87, 7, 9, 19)
        masonry(s, 25, 61, 30, 84, 4)
        masonry(s, 67, 61, 71, 84, 4)
        s.rect(0, 88, 95, 95, 20)
    elif kind == "pigeons":
        sky(s, 79)
        for cx, radius, top in ((23, 13, 35), (51, 16, 21), (78, 12, 38)):
            rect(s, cx-radius, top+9, cx+radius, 80, 3)
            s.ellipse(cx, top+8, radius+2, 7, 1)
            s.ellipse(cx, top+8, radius, 5, 2)
            s.rect(cx-radius-3, top+13, cx+radius+3, top+16, 4)
            for y in range(top+24, 76, 8):
                for x in range(cx-radius+4, cx+radius-3, 7):
                    s.rect(x, y, x+2, y+3, 1)
            masonry(s, cx-radius+1, top+18, cx+radius-1, top+23, 4)
            s.rect(cx-radius-3, 78, cx+radius+3, 82, 1)
        for x in (5, 90): cypress(s, x, 88, 21)
    elif kind == "atashgah":
        sky(s, 90, False)
        s.polygon([(0, 94), (13, 70), (29, 59), (42, 49),
                   (63, 51), (78, 69), (95, 94)], 1)
        s.polygon([(0, 95), (16, 72), (30, 62), (44, 52),
                   (61, 54), (77, 72), (95, 95)], 20)
        s.polygon([(5, 95), (28, 75), (41, 61), (47, 78),
                   (67, 64), (88, 95)], 4)
        rect(s, 29, 33, 67, 56, 3)
        s.polygon([(25, 32), (48, 20), (72, 32)], 1)
        s.polygon([(30, 31), (48, 23), (67, 31)], 2)
        pointed(s, 48, 36, 58, 8, 2, 19)
        for x in (34, 62): rect(s, x-2, 36, x+2, 53, 2)
        masonry(s, 31, 43, 65, 52)
        for x, y in ((17, 86), (72, 75), (81, 87)):
            s.polygon([(x-5, y+4), (x, y-3), (x+6, y+4)], 4)
    elif kind == "vakil_mosque":
        sky(s, 86)
        rect(s, 7, 36, 88, 86, 3)
        rect(s, 17, 24, 79, 85, 2)
        pointed(s, 48, 30, 87, 24, 7, 19)
        tiles(s, 27, 34, 69, 55, 6)
        s.rect(13, 27, 83, 32, 6)
        s.rect(13, 28, 83, 29, 8)
        for x in (10, 86): minaret(s, x, 14, 85, 7, 7)
        arcade(s, 7, 88, 59, 85, 7, 5, 27)
        s.rect(4, 87, 91, 95, 20)
        for y in (89, 93): s.line(6, y, 90, y, 5)
    elif kind == "vakil_bazaar":
        s.rect(0, 0, 95, 95, 4)
        s.polygon([(0, 95), (29, 57), (67, 57), (95, 95)], 2)
        s.polygon([(0, 0), (95, 0), (73, 58), (22, 58)], 3)
        pointed(s, 48, 5, 79, 43, 3, 19)
        pointed(s, 48, 22, 77, 28, 4, 27)
        pointed(s, 48, 41, 75, 14, 3, 13)
        for y, half in ((13, 36), (26, 30), (40, 22), (51, 15)):
            s.line(48-half, y, 48+half, y, 2)
        for x, y, rad in ((8, 62, 8), (20, 68, 7),
                          (88, 62, 8), (76, 68, 7)):
            rect(s, x-rad//2, y, x+rad//2, 89, 19)
            s.rect(x-rad//2+1, y+4, x+rad//2-1, 77, 16)
            s.line(x-rad//2, y+6, x+rad//2, y+6, 18)
        s.line(0, 95, 38, 68, 1)
        s.line(95, 95, 58, 68, 1)
        for y in (83, 91): s.line(30, y, 66, y, 20)
    elif kind == "vakil_bath":
        s.rect(0, 0, 95, 95, 2)
        s.polygon([(4, 25), (26, 5), (70, 5), (91, 25),
                   (91, 73), (70, 90), (26, 90), (4, 73)], 1)
        s.polygon([(7, 27), (28, 8), (68, 8), (88, 27),
                   (88, 70), (68, 86), (28, 86), (7, 70)], 5)
        dome(s, 48, 29, 25, 3)
        for cx, cy in ((48, 10), (25, 25), (71, 25)):
            s.ellipse(cx, cy, 4, 4, 7)
            s.ellipse(cx, cy, 2, 2, 22)
        for x in (14, 81):
            pointed(s, x, 40, 78, 12, 3, 19)
        colonnade(s, 23, 73, 46, 79, 4)
        s.ellipse(48, 81, 24, 11, 1)
        s.ellipse(48, 80, 21, 8, 14)
        s.ellipse(48, 79, 9, 3, 8)
        for x in range(15, 84, 9): s.dot(x, 91, 9)
    elif kind == "qavam":
        sky(s, 76)
        rect(s, 11, 26, 84, 71, 2)
        s.polygon([(10, 29), (23, 18), (73, 18), (85, 29)], 1)
        s.polygon([(15, 28), (25, 20), (71, 20), (81, 28)], 9)
        dome(s, 48, 17, 12, 6)
        glass_facade(s, 19, 77, 36, 7)
        colonnade(s, 30, 66, 36, 69, 3)
        s.rect(17, 70, 79, 73, 4)
        s.polygon([(18, 95), (35, 73), (61, 73), (78, 95)], 2)
        channel(s, 74, 95, 10)
        for x in (7, 88): orange_tree(s, x, 83, 11)
        for x in (19, 77): s.ellipse(x, 88, 7, 3, 15)
    elif kind == "afif":
        sky(s, 79)
        rect(s, 11, 27, 84, 71, 2)
        rect(s, 19, 17, 76, 32, 3)
        s.polygon([(15, 27), (48, 12), (80, 27)], 1)
        s.polygon([(21, 26), (48, 15), (74, 26)], 9)
        glass_facade(s, 22, 75, 35, 6)
        colonnade(s, 16, 79, 50, 71, 7)
        s.rect(15, 70, 80, 73, 4)
        s.polygon([(0, 95), (31, 73), (64, 73), (95, 95)], 11)
        channel(s, 75, 95, 16)
        for x in (7, 89): cypress(s, x, 86, 34)
        for x in (20, 75): s.ellipse(x, 86, 6, 4, 15)
    elif kind == "delgosha":
        sky(s, 76)
        rect(s, 25, 32, 72, 67, 3)
        rect(s, 32, 22, 65, 36, 2)
        s.polygon([(23, 32), (48, 19), (74, 32)], 1)
        s.polygon([(29, 31), (48, 23), (69, 31)], 9)
        pointed(s, 48, 35, 68, 12, 5, 19)
        for x in (32, 64): windows(s, x-5, x+5, 45, 2, 7)
        s.rect(27, 68, 70, 72, 20)
        s.polygon([(0, 95), (25, 73), (70, 73), (95, 95)], 12)
        channel(s, 74, 95, 13)
        for x, b, r in ((9, 81, 10), (19, 75, 8), (77, 75, 8), (87, 81, 10)):
            orange_tree(s, x, b, r)
    elif kind == "jahan":
        sky(s, 73)
        rect(s, 27, 27, 68, 69, 2)
        s.polygon([(24, 27), (48, 13), (72, 27)], 1)
        s.polygon([(29, 26), (48, 17), (67, 26)], 3)
        for x in (30, 65): minaret(s, x, 19, 67, 5, 3)
        pointed(s, 48, 34, 70, 12, 3, 19)
        s.polygon([(0, 95), (28, 71), (68, 71), (95, 95)], 11)
        channel(s, 73, 95, 12)
        for x in (8, 18, 78, 88): cypress(s, x, 84, 27)
        for x in (27, 68): s.ellipse(x, 85, 7, 4, 15)
    elif kind == "haft":
        sky(s, 83)
        rect(s, 10, 35, 86, 76, 3)
        s.polygon([(7, 37), (48, 23), (89, 37)], 1)
        s.polygon([(12, 36), (48, 26), (84, 36)], 2)
        colonnade(s, 18, 78, 40, 76, 5)
        s.rect(18, 74, 78, 78, 4)
        for x in (30, 42, 54, 66):
            s.rect(x-3, 68, x+3, 75, 9)
        for x in (18, 30, 42, 54, 66, 78, 86):
            s.polygon([(x-4, 89), (x-3, 81), (x+4, 81), (x+5, 89)], 20)
        for x in (5, 90): cypress(s, x, 80, 38)
        s.rect(0, 91, 95, 95, 11)
    elif kind == "khaju":
        sky(s, 91, False)
        s.polygon([(0, 95), (0, 67), (17, 49), (31, 53),
                   (46, 30), (68, 46), (95, 55), (95, 95)], 20)
        s.polygon([(0, 95), (9, 77), (27, 59), (36, 69),
                   (50, 41), (70, 56), (95, 72), (95, 95)], 4)
        rect(s, 31, 25, 65, 58, 2)
        s.polygon([(27, 25), (48, 12), (69, 25)], 1)
        s.polygon([(32, 24), (48, 15), (64, 24)], 9)
        pointed(s, 48, 27, 59, 11, 3, 19)
        s.rect(36, 58, 61, 62, 3)
        s.rect(41, 63, 56, 69, 9)
        s.rect(43, 64, 54, 67, 2)
        cypress(s, 12, 84, 30)
        cypress(s, 86, 85, 36)
        for x, y in ((21, 79), (68, 81), (74, 70)):
            s.polygon([(x-5, y+5), (x, y-4), (x+5, y+5)], 3)
    elif kind == "shapouri":
        sky(s, 79)
        rect(s, 13, 32, 82, 71, 5)
        s.polygon([(9, 34), (48, 13), (87, 34)], 1)
        s.polygon([(16, 33), (48, 17), (80, 33)], 16)
        rect(s, 28, 21, 67, 34, 2)
        glass_facade(s, 20, 76, 39, 7)
        for x in (17, 79): minaret(s, x, 31, 69, 6, 2)
        colonnade(s, 26, 70, 54, 72, 5)
        s.polygon([(42, 71), (54, 71), (70, 91), (26, 91)], 20)
        for y in (76, 81, 86, 91):
            spread = 7 + (y-75)
            s.line(48-spread, y, 48+spread, y, 4)
        for x in (7, 88): orange_tree(s, x, 82, 10)
        s.rect(0, 93, 95, 95, 12)
    else:
        raise ValueError("Unknown landmark recipe: " + kind)
    return s


def make_level(item):
    slug, title_fa, title_en, city, kind = item
    art = paint(kind)
    level = {
        "schemaVersion": 2,
        "levelId": f"online-{city}-{slug}-96",
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
    if (len(PICTURES) != 20 or
            sum(p[3] == "isfahan" for p in PICTURES) != 10 or
            sum(p[3] == "shiraz" for p in PICTURES) != 10):
        raise ValueError("Expected ten unique landmarks per city")
    manifest, assets = [], {}
    seen_pixels = set()
    for item in PICTURES:
        level = make_level(item)
        pixels = tuple(level["cells"])
        if pixels in seen_pixels:
            raise ValueError("Duplicate pixel art: " + level["levelId"])
        seen_pixels.add(pixels)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Online level too large: " + level["levelId"])
        stem = level["levelId"] + "-v1"
        manifest.append({
            "id": level["levelId"], "version": 1,
            "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
            "category": "patterns",  # backward-compatible; app displays Persian architecture
            "width": SIDE, "height": SIDE,
            "bytes": len(body), "checksum": level["checksum"],
        })
        assets["levels/" + stem + ".json"] = body
        assets["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, body in assets.items():
            archive.writestr(name, body)
    print("Prepared 20 original 96x96 Isfahan and Shiraz paintings:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_isfahan_shiraz_20_96_pack.py <content.zip>")
    create_pack(sys.argv[1])
