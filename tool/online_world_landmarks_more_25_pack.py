#!/usr/bin/env python3
"""25 NEW hand-composed famous landmark illustrations at exactly 80x80 cells.

These are separately constructed recognizable pixel-art silhouettes; none is
a resampled 50x50 design or replaces a previously published online level.
The Web Pages workflow emits immutable numbered JSON and PNG preview assets.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 80
PALETTE = [
    "FFE5F4FC",  # 0 daylight sky
    "FF344153",  # 1 dark outline
    "FFF5E9D3",  # 2 white limestone
    "FFDBC19B",  # 3 warm pale stone
    "FFAE8765",  # 4 shadow/stone
    "FFCFAB68",  # 5 golden sandstone
    "FF23684F",  # 6 deep green
    "FF81AE80",  # 7 foliage
    "FF336A9B",  # 8 deep blue
    "FF79C3D9",  # 9 turquoise/bright water
    "FFBD5C4B",  # 10 brick red
    "FFE9A5A3",  # 11 rose
    "FF46566A",  # 12 slate
    "FFFFFFFF",  # 13 bright white
    "FFF0D8AA",  # 14 sand
    "FF835B40",  # 15 timber
    "FF6F668F",  # 16 purple
    "FF9FAFB9",  # 17 grey stone/metal
    "FFF8D879",  # 18 sunlight
    "FFA9CE9C",  # 19 grass
    "FF294A72",  # 20 midnight blue
    "FF3DA8A5",  # 21 teal
    "FFE0B658",  # 22 gold
    "FFBFCFE0",  # 23 cool limestone
    "FF7D4456",  # 24 burgundy
]

# Fresh immutable IDs, with bilingual names and mutually distinct landmarks.
# Unlike the 25-piece 50x50 pack, all items depict NEW world structures.
PICTURES = [
    ("hagia-sophia", "ایاصوفیه استانبول", "Hagia Sophia, Istanbul"),
    ("notre-dame-paris", "کلیسای نوتردام پاریس", "Notre-Dame de Paris"),
    ("arc-de-triomphe", "طاق پیروزی پاریس", "Arc de Triomphe"),
    ("louvre-pyramid", "هرم موزه لوور", "Louvre Pyramid"),
    ("mont-saint-michel", "مون سن میشل", "Mont Saint-Michel"),
    ("empire-state-building", "ساختمان امپایر استیت", "Empire State Building"),
    ("space-needle", "برج اسپیس نیدل", "Space Needle"),
    ("gateway-arch", "طاق دروازه سنت لوئیس", "Gateway Arch"),
    ("cn-tower", "برج سی‌ان تورنتو", "CN Tower, Toronto"),
    ("forbidden-city", "شهر ممنوعه پکن", "Forbidden City, Beijing"),
    ("temple-of-heaven", "معبد آسمان پکن", "Temple of Heaven, Beijing"),
    ("potala-palace", "کاخ پوتالا", "Potala Palace, Lhasa"),
    ("himeji-castle", "قلعه هیمه‌جی", "Himeji Castle"),
    ("fushimi-inari", "دروازه‌های فوشیمی ایناری", "Fushimi Inari Torii Gates"),
    ("gyeongbokgung", "کاخ گیونگ‌بوک‌گونگ", "Gyeongbokgung Palace"),
    ("taipei-101", "برج تایپه ۱۰۱", "Taipei 101"),
    ("petronas-twin-towers", "برج‌های دوقلوی پتروناس", "Petronas Twin Towers"),
    ("lotus-temple", "معبد نیلوفر آبی", "Lotus Temple"),
    ("qutub-minar", "قطب منار دهلی", "Qutub Minar, Delhi"),
    ("sheikh-zayed-mosque", "مسجد شیخ زاید", "Sheikh Zayed Grand Mosque"),
    ("dome-of-the-rock", "قبةالصخره", "Dome of the Rock"),
    ("alhambra", "کاخ الحمرا", "Alhambra Palace"),
    ("florence-cathedral", "کلیسای جامع فلورانس", "Florence Cathedral"),
    ("st-peters-basilica", "کلیسای سن پیترو", "St. Peter's Basilica"),
    ("abu-simbel", "معبد ابوسمبل", "Abu Simbel Temples"),
]


def border_rect(s, left, top, right, bottom, stone=3, rim=1):
    s.rect(left-1, top-1, right+1, bottom+1, rim)
    s.rect(left, top, right, bottom, stone)


def triangle(s, points, fill=3, rim=1):
    s.polygon(points, rim)
    center_x = sum(x for x, _ in points) / len(points)
    center_y = sum(y for _, y in points) / len(points)
    s.polygon([(center_x+(x-center_x)*.88, center_y+(y-center_y)*.88)
               for x, y in points], fill)


def arch(s, center, top, bottom, radius, stone=3, inside=1, border=2):
    s.polygon([(center-radius, bottom), (center-radius, top+radius*.7),
               (center, top), (center+radius, top+radius*.7),
               (center+radius, bottom)], 1)
    r = radius-1
    s.polygon([(center-r, bottom-1), (center-r, top+r*.7+1),
               (center, top+2), (center+r, top+r*.7+1),
               (center+r, bottom-1)], stone)
    r = max(1, radius-border-2)
    s.polygon([(center-r, bottom-1), (center-r, top+r*.72+5),
               (center, top+border+3), (center+r, top+r*.72+5),
               (center+r, bottom-1)], inside)


def window(s, x, y, color=1, length=5):
    s.rect(x-1, y+1, x+1, y+length, color)
    s.ellipse(x, y+1, 1.2, 1.5, color)


def dome(s, x, base, radius, color=2, finial=22):
    s.ellipse(x, base, radius+1, radius*.76, 1)
    s.ellipse(x, base, radius, radius*.76-1, color)
    s.rect(x-radius, base, x+radius, base+4, 1)
    s.rect(x-radius+1, base, x+radius-1, base+3, color)
    s.line(x, base-radius*.74-7, x, base-radius*.74-1, finial, radius=1)
    s.ellipse(x, base-radius*.74-8, 2, 2, finial)


def turret(s, x, top, bottom, width=8, stone=3, roof=12):
    border_rect(s, x-width//2, top+9, x+width//2, bottom, stone)
    triangle(s, [(x-width//2-3, top+10), (x, top),
                 (x+width//2+3, top+10)], roof)
    for y in range(top+15, bottom-5, 7):
        window(s, x, y, 1, 3)


def columns(s, positions, top, bottom, color=2, width=3):
    for x in positions:
        border_rect(s, x-width//2, top, x+width//2, bottom, color)
        s.rect(x-width//2-2, top-1, x+width//2+2, top+1, 4)
        s.rect(x-width//2-2, bottom, x+width//2+2, bottom+1, 4)


def masonry(s, left, top, right, bottom, gap=6, accent=4):
    for y in range(top, bottom+1, gap):
        s.line(left, y, right, y, accent, radius=.35)
        for x in range(left+(gap//2 if (y//gap)%2 else 0), right, gap*2):
            s.line(x, y, x, min(y+gap-2, bottom), accent, radius=.3)


def step_pyramid(s, x, top, bottom, half=28, color=3):
    count = (bottom-top)//4
    for i in range(count):
        xl = x-(half*(i+1)//count)
        xr = x+(half*(i+1)//count)
        y = top+4*i
        border_rect(s, xl+1, y, xr-1, y+3, color, 1)


def scenery(s, kind):
    s.rect(0, 0, 79, 79, 0)
    water = {"louvre", "mont", "gateway", "cn", "petronas",
             "lotus", "sheikh", "dome", "hagia"}
    night = {"taipei", "empire", "space"}
    hills = {"potala", "himeji", "mont", "alhambra"}
    desert = {"abu", "qutub", "alhambra"}
    if kind in night:
        s.rect(0, 0, 79, 79, 20)
        for x,y in ((7,8),(19,16),(29,6),(52,13),(64,5),(74,23),
                    (10,34),(60,32),(36,20)):
            s.dot(x,y,18)
        s.ellipse(65, 13, 6, 6, 18)
    else:
        s.ellipse(66, 12, 5, 5, 18)
        for x,y in ((10, 13), (27, 9), (56, 27)):
            s.ellipse(x, y, 5, 2, 13)
            s.ellipse(x+4, y+1, 4, 2, 13)
    if kind in desert:
        s.rect(0, 65, 79, 79, 14)
        s.line(0,65,79,65,4)
    elif kind in water:
        s.rect(0, 69, 79, 79, 8)
        for y in (71,75,78):
            for x in range(4+(y%7), 75, 13):
                s.line(x,y,x+7,y,9)
    elif kind in hills:
        s.polygon([(0,75),(0,57),(15,48),(25,61),(47,43),
                   (66,56),(79,44),(79,79),(0,79)],7)
        s.rect(0,71,79,79,6)
    else:
        s.rect(0,69,79,79,19)
        s.line(0,69,79,69,6)
    if kind in night:
        for x,y in ((9,62),(18,68),(55,58),(72,66)):
            border_rect(s,x-4,y-6,x+4,69,12,1)
            for yy in range(y-3,69,4):
                s.dot(x,yy,18)


def paint(kind):
    s = Sprite(SIDE, PALETTE)
    scenery(s, kind)

    if kind == "hagia-sophia":
        border_rect(s, 9, 47, 71, 67, 4)
        border_rect(s, 16, 39, 64, 61, 3)
        dome(s,40,39,22,17)
        dome(s,20,47,10,2)
        dome(s,61,47,10,2)
        for x in (8,72):
            turret(s,x,16,65,6,stone=3,roof=17)
            s.line(x,16,x,7,1)
        for x in (23,40,57):
            arch(s,x,48,67,7,stone=3,inside=8)
        for x in (18,62):
            for y in (35,44):
                window(s,x,y,8,3)
        masonry(s, 16, 60, 64, 66)
    elif kind == "notre-dame-paris":
        border_rect(s, 13, 36, 66, 68, 3)
        for x in (19,59):
            border_rect(s,x-8,17,x+8,60,3)
            s.rect(x-9,13,x+9,17,12)
            for y in (24,35,46):
                for dx in (-4,4):
                    window(s,x+dx,y,1,6)
        triangle(s,[(33,37),(40,29),(47,37)],4)
        s.ellipse(40,45,11,11,1)
        s.ellipse(40,45,9,9,8)
        for d in range(0,360,45):
            angle=d*math.pi/180
            s.line(40,45,40+8*math.cos(angle),45+8*math.sin(angle),13)
        arch(s,40,53,69,9,3,1)
        for x in (29,51):
            arch(s,x,58,67,5,3,12)
        for x in (16,64):
            s.line(x,30,x-4 if x==16 else x+4,46,1)
    elif kind == "arc-de-triomphe":
        border_rect(s,17,22,63,68,3)
        s.rect(14,19,66,24,1)
        s.rect(15,20,65,23,2)
        arch(s,40,31,69,16,stone=3,inside=0,border=3)
        for x in (25,55):
            s.rect(x-3,29,x+3,34,4)
            s.line(x-4,38,x+4,38,2)
            for y in (44,52,60):
                s.line(x-2,y,x+2,y,4)
        for x in range(19,63,6):
            s.line(x,26,x,29,1)
        s.rect(10,69,70,71,1)
        s.line(10,74,70,74,4)
    elif kind == "louvre-pyramid":
        s.rect(0,55,79,70,3)
        for x in (3,70):
            border_rect(s,x,42,x+8,62,2)
            for xx in (x+2,x+5):
                window(s,xx,48,12,5)
        s.rect(0,48,79,53,4)
        triangle(s,[(10,65),(40,14),(70,65)],9,1)
        # A rhombus-and-triangle lattice recognizable as glass glazing.
        for y in (28,38,48,57):
            half=round((y-14)*30/51)
            s.line(40-half,y,40+half,y,13,radius=.5)
        for x in (21,31,40,49,59):
            s.line(40,14,x,65,13,radius=.5)
        s.rect(4,65,75,67,1)
        for x in (16,30,48,64):
            s.line(x,69,x+7,69,9)
    elif kind == "mont-saint-michel":
        s.polygon([(2,68),(17,58),(27,51),(45,48),(60,55),
                   (76,67),(79,72),(0,72)],4)
        s.polygon([(9,67),(19,55),(32,55),(40,43),
                   (56,48),(66,67)],3)
        for x,top in ((19,43),(30,37),(50,32),(62,45)):
            border_rect(s,x-5,top+6,x+7,64,3)
            triangle(s,[(x-7,top+7),(x+1,top-1),(x+9,top+7)],12)
            for yy in range(top+13,62,7):
                window(s,x,yy,1,3)
        border_rect(s,35,22,56,49,2)
        triangle(s,[(33,22),(46,8),(58,22)],12)
        s.line(46,8,46,3,22)
        s.rect(42,31,47,48,4)
        for x in (12,70):
            s.ellipse(x,63,5,5,6)
        s.line(1,72,78,72,9)
    elif kind == "empire-state-building":
        border_rect(s,14,57,67,70,12)
        border_rect(s,24,45,57,67,17)
        border_rect(s,30,30,51,67,23)
        border_rect(s,35,17,46,67,17)
        triangle(s,[(33,18),(40,8),(48,18)],17)
        s.line(40,8,40,1,18)
        for y in range(24,66,5):
            for x in range(37 if y<31 else 32 if y<46 else 26,
                           45 if y<31 else 50 if y<46 else 55,4):
                s.rect(x,y,x+1,y+2,18)
        for x in (18,63):
            border_rect(s,x-6,52,x+5,70,12)
            for y in (55,62,67):
                s.dot(x,y,18)
    elif kind == "space-needle":
        s.rect(23,69,58,71,12)
        s.line(33,69,39,35,17,radius=2)
        s.line(47,69,41,35,17,radius=2)
        s.line(31,65,49,65,1,radius=1)
        s.line(34,49,46,49,17,radius=1.5)
        s.rect(38,17,42,52,17)
        s.polygon([(9,32),(17,26),(63,26),(71,32),
                   (60,38),(20,38)],1)
        s.polygon([(12,31),(22,28),(58,28),(68,31),
                   (57,35),(23,35)],8)
        s.ellipse(40,26,27,4,17)
        s.ellipse(40,27,24,2,9)
        s.line(40,17,40,3,17,radius=1)
        s.ellipse(40,2,2,2,18)
        for x in range(20,62,5):
            s.dot(x,33,18)
    elif kind == "gateway-arch":
        s.rect(7,69,73,70,17)
        # Parallel parabolic lines, open center, and continuous steel legs.
        for x in range(8,73):
            norm=(x-40)/32
            y=12+int(57*norm*norm)
            if y<70:
                s.line(x,y,x,y+4,17,radius=1.2)
                s.dot(x,y+4,1)
        s.line(7,69,73,69,12)
        for x in (10,70):
            s.rect(x-2,62,x+2,70,17)
    elif kind == "cn":
        s.rect(20,69,59,72,12)
        s.polygon([(38,9),(42,9),(47,66),(33,66)],1)
        s.polygon([(39,11),(41,11),(45,66),(35,66)],17)
        s.line(40,8,40,1,1)
        s.ellipse(40,37,14,5,1)
        s.ellipse(40,37,12,4,17)
        s.rect(29,37,51,40,8)
        s.ellipse(40,42,9,3,12)
        for x in range(32,50,4):
            s.dot(x,39,9)
        s.rect(25,64,55,69,1)
        for x in (26,53):
            s.rect(x-7,58,x+7,70,23)
    elif kind == "forbidden-city":
        for left,right,top,bottom in ((4,75,48,69),(12,68,36,52),(22,57,27,38)):
            border_rect(s,left,top,right,bottom,3)
            triangle(s,[(left-4,top),(40,top-13),(right+4,top)],10)
            s.rect(left-7,top-1,right+7,top+1,1)
            s.rect(left-6,top,right+6,top,22)
            for x in range(left+5,right-2,8):
                window(s,x,top+5,15,7)
        arch(s,40,55,70,11,3,1)
        for x in (13,66):
            turret(s,x,40,68,6,stone=3,roof=10)
        s.rect(0,71,79,73,4)
    elif kind == "temple-of-heaven":
        for left,right,top in ((11,69,45),(18,62,32),(25,55,20)):
            border_rect(s,left,top,right,68,3)
            s.polygon([(left-8,top+1),(40,top-13),
                       (right+8,top+1),(right+5,top+4),
                       (left-5,top+4)],1)
            s.polygon([(left-6,top+1),(40,top-11),
                       (right+6,top+1),(right+3,top+3),
                       (left-3,top+3)],8)
            s.line(left-4,top+4,right+4,top+4,22,radius=1)
            for x in range(left+5,right-2,9):
                s.rect(x,top+7,x+2,min(top+14,67),15)
        for y in (68,71,74):
            s.line(6-(y-68),y,74+(y-68),y,2)
    elif kind == "potala":
        s.polygon([(0,71),(15,53),(34,47),(55,53),
                   (79,66),(79,78),(0,78)],4)
        border_rect(s,5,48,75,67,2)
        border_rect(s,12,34,68,59,2)
        border_rect(s,20,21,60,52,2)
        border_rect(s,27,15,53,45,10)
        s.rect(19,19,61,21,1)
        s.rect(26,12,54,16,1)
        s.rect(28,13,52,15,22)
        for x0,x1,y0,y1 in ((8,72,51,64),(14,66,37,52),(23,57,25,44)):
            for y in range(y0,y1,7):
                for x in range(x0,x1,7):
                    s.rect(x,y,x+2,y+4,1)
        for y in (62,66,71):
            s.line(0,y,79,y,3)
    elif kind == "himeji":
        border_rect(s,12,52,68,68,2)
        for left,right,top in ((15,65,46),(23,57,34),(28,53,24)):
            border_rect(s,left,top+5,right,top+13,2)
            s.polygon([(left-9,top+6),(40,top-4),
                       (right+9,top+6),(right+5,top+9),
                       (left-5,top+9)],1)
            s.polygon([(left-7,top+6),(40,top-2),
                       (right+7,top+6),(right+4,top+7),
                       (left-4,top+7)],12)
            for x in range(left+5,right,9):
                s.dot(x,top+11,1)
        turret(s,41,12,33,8,stone=2,roof=12)
        for x in (16,64):
            s.ellipse(x,65,7,6,6)
            s.ellipse(x+3,67,5,3,7)
        s.rect(0,69,79,71,4)
    elif kind == "fushimi-inari":
        # A deep procession ofvermillion torii gates, sized by perspective.
        s.polygon([(0,79),(29,56),(51,56),(79,79)],14)
        for level in range(5):
            xspan=7+level*5
            top=35-level*7
            base=58+level*5
            left=40-xspan; right=40+xspan
            width=2+level
            s.rect(left,top,left+width,base,10)
            s.rect(right-width,top,right,base,10)
            s.rect(left-4,top-4,right+4,top,1)
            s.rect(left-3,top-3,right+3,top-1,10)
            s.rect(left+2,top+3,right-2,top+5,15)
            s.rect(left+2,top+6,right-2,top+7,5)
            s.rect(left-2,base,right+2,base+1,1)
        for x in (5,70):
            s.ellipse(x,60,8,10,6)
    elif kind == "gyeongbokgung":
        border_rect(s,7,47,72,68,3)
        border_rect(s,17,32,63,58,2)
        s.polygon([(10,34),(40,18),(70,34),(67,38),
                   (13,38)],1)
        s.polygon([(12,34),(40,21),(68,34),(64,36),
                   (16,36)],8)
        s.line(8,38,72,38,22,radius=1)
        for x in range(21,63,8):
            border_rect(s,x,41,x+3,59,10)
            s.line(x,41,x+3,41,22)
        arch(s,40,50,68,10,3,1)
        s.rect(4,69,75,71,17)
        for x in (11,69):
            s.rect(x-4,58,x+3,67,1)
            s.rect(x-3,59,x+2,65,4)
    elif kind == "taipei":
        s.rect(21,68,59,72,12)
        for i in range(8):
            y=61-i*6
            half=18-(i//3)*2
            s.polygon([(40-half-2,y),(40+half+2,y),
                       (40+half-2,y-5),(40-half+2,y-5)],1)
            s.polygon([(40-half,y-1),(40+half,y-1),
                       (40+half-3,y-4),(40-half+3,y-4)],21)
            s.line(40-half-1,y-5,40+half+1,y-5,22,radius=.6)
            for x in range(40-half+3,40+half-2,5):
                s.dot(x,y-2,18)
        s.rect(37,9,43,15,21)
        s.line(40,9,40,2,22,radius=1)
        s.ellipse(40,2,2,2,18)
        for x in (13,67):
            border_rect(s,x-6,49,x+6,70,12)
            for y in (54,60,66):
                s.dot(x,y,18)
    elif kind == "petronas":
        for cx in (23,57):
            border_rect(s,cx-10,24,cx+10,68,17)
            for stage in range(7):
                y=23+stage*6
                half=max(4,11-stage//2)
                s.rect(cx-half-1,y,cx+half+1,y+2,1)
                s.rect(cx-half,y+1,cx+half,y+1,23)
            s.polygon([(cx-6,24),(cx,8),(cx+6,24)],1)
            s.polygon([(cx-4,24),(cx,12),(cx+4,24)],17)
            s.line(cx,7,cx,1,17)
            for yy in range(31,65,5):
                for xx in (cx-5,cx,cx+5):
                    s.dot(xx,yy,8)
        s.rect(33,39,47,43,1)
        s.rect(34,40,46,42,17)
        s.line(23,43,33,43,12)
        s.line(47,43,57,43,12)
        s.rect(6,70,74,72,12)
    elif kind == "lotus":
        s.rect(4,68,75,71,3)
        for x,r in ((20,18),(30,23),(40,29),(50,23),(60,18)):
            s.polygon([(x-14,65),(x-8,54),(x,68-r),
                       (x+8,54),(x+14,65)],1)
            s.polygon([(x-12,64),(x-6,53),(x,70-r),
                       (x+6,53),(x+12,64)],2)
            s.line(x,70-r,x,62,23,radius=.8)
        for x in (16,28,40,52,64):
            s.polygon([(x-9,66),(x-6,55),(x,46),
                       (x+6,55),(x+9,66)],1)
            s.polygon([(x-7,65),(x-4,56),(x,49),
                       (x+4,56),(x+7,65)],13)
        s.rect(25,66,55,70,2)
        s.ellipse(40,72,27,2,9)
    elif kind == "qutub":
        # Historic tapering brick minaret with alternating fluted balconies.
        border_rect(s,29,13,50,69,10)
        s.polygon([(32,13),(47,13),(51,69),(27,69)],1)
        s.polygon([(33,14),(46,14),(49,68),(29,68)],10)
        for y in (22,32,42,52,62):
            s.rect(27,y,52,y+3,1)
            s.rect(28,y,51,y+2,3)
            for x in range(30,50,5):
                s.dot(x,y+1,22)
        for x in (34,40,46):
            s.line(x,16,x+(x-40)*.3,67,4,radius=.5)
        triangle(s,[(30,13),(40,5),(50,13)],3)
        for x in (12,62):
            border_rect(s,x-7,52,x+8,68,4)
            arch(s,x,56,69,5,3,1)
        for x in range(0,80,12):
            s.line(x,73,x+6,73,4)
    elif kind == "sheikh":
        border_rect(s,6,49,73,67,2)
        border_rect(s,16,40,64,65,13)
        dome(s,40,37,20,2)
        for x in (19,61):
            dome(s,x,47,10,2)
        for x in (6,74):
            turret(s,x,12,64,6,stone=2,roof=2)
        for x in (15,65):
            turret(s,x,23,62,5,stone=2,roof=2)
        for x in (26,40,54):
            arch(s,x,52,68,6,stone=13,inside=8)
        for x in (12,68):
            for y in (29,39):
                s.dot(x,y,22)
        s.rect(3,69,76,72,2)
    elif kind == "dome":
        border_rect(s,12,45,68,65,2)
        border_rect(s,16,36,64,55,8)
        dome(s,40,35,25,22)
        for x in range(17,65,7):
            s.rect(x,40,x+3,48,21)
            s.dot(x+1,42,18)
        for x in (19,61):
            arch(s,x,52,67,6,3,1)
        arch(s,40,52,67,9,2,1)
        for y in (56,61):
            s.line(13,y,67,y,22,radius=.5)
        s.rect(10,68,70,70,3)
    elif kind == "alhambra":
        s.polygon([(0,68),(13,51),(35,52),(56,46),
                   (79,56),(79,78),(0,78)],6)
        border_rect(s,6,38,74,67,4)
        for x,top,bottom in ((13,31,65),(32,24,67),(59,28,65),(70,39,64)):
            border_rect(s,x-7,top,x+7,bottom,3)
            s.rect(x-8,top-2,x+8,top+1,1)
            for y in range(top+8,bottom-3,8):
                window(s,x,y,1,4)
            for xx in range(x-6,x+7,4):
                s.rect(xx,top-5,xx+2,top-2,3)
        for x in (21,44):
            arch(s,x,48,67,8,3,1)
        masonry(s,8,52,70,65,gap=9)
        s.rect(0,69,79,71,4)
    elif kind == "florence":
        border_rect(s,9,40,70,68,3)
        border_rect(s,14,31,59,65,2)
        dome(s,37,28,23,10)
        dome(s,37,25,17,10)
        s.line(37,8,37,3,22)
        border_rect(s,62,18,75,67,2)
        turret(s,68,11,25,10,stone=2,roof=3)
        for y in (31,41,51):
            s.ellipse(68,y,3,3,1)
            s.ellipse(68,y,1.5,1.5,22)
        for x in (18,30,46,55):
            arch(s,x,47,67,5,stone=2,inside=8)
        s.line(10,61,61,61,10)
        s.rect(7,68,76,71,17)
    elif kind == "stpeters":
        border_rect(s,5,49,75,69,2)
        border_rect(s,19,34,61,62,3)
        dome(s,40,33,21,17)
        dome(s,40,31,14,23)
        s.line(40,8,40,1,22)
        s.line(37,4,43,4,22)
        for x in (10,70):
            border_rect(s,x-7,43,x+7,66,3)
            triangle(s,[(x-9,43),(x,34),(x+9,43)],2)
        columns(s, [12,20,28,36,44,52,60,68],54,66,color=2,width=3)
        arch(s,40,48,70,8,3,1)
        s.rect(0,70,79,72,3)
        s.line(11,74,69,74,17)
    elif kind == "abu":
        s.rect(0,16,79,70,4)
        s.polygon([(0,20),(18,13),(34,20),(58,12),
                   (79,18),(79,71),(0,71)],14)
        s.rect(6,24,73,67,3)
        for x,top in ((12,31),(31,27),(49,27),(68,31)):
            s.ellipse(x,top,8,11,1)
            s.ellipse(x,top,6.5,9,5)
            s.rect(x-6,top,x+6,57,5)
            s.ellipse(x-4,top-1,1.6,1.6,13)
            s.ellipse(x+4,top-1,1.6,1.6,13)
            s.polygon([(x-3,top+5),(x+2,top+5),
                       (x+4,top+12),(x-2,top+11)],3)
            s.line(x-5,top+16,x+4,top+16,1)
            s.rect(x-5,57,x+5,65,4)
        arch(s,40,33,69,6,4,1)
        masonry(s,0,60,79,68,gap=8)
        s.rect(0,72,79,79,14)
    else:
        raise ValueError("Unknown landmark: " + kind)
    return s


def make_level(item):
    slug, title_fa, title_en = item
    art = paint(slug)
    level = {
        "schemaVersion": 2,
        "levelId": f"online-world-more-{slug}-80",
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
    if len(PICTURES) != 25 or len({item[0] for item in PICTURES}) != 25:
        raise ValueError("Expected 25 unique world landmarks at 80x80")
    manifest = []
    assets = {}
    for item in PICTURES:
        level = make_level(item)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Over 256 KiB: " + level["levelId"])
        stem = level["levelId"] + "-v1"
        manifest.append({
            "id": level["levelId"], "version": 1,
            "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
            "category": "patterns", "width": SIDE, "height": SIDE,
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
        for name, payload in assets.items():
            archive.writestr(name, payload)
    print("Prepared 25 distinct 80x80 world landmarks:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_world_landmarks_more_25_pack.py <content.zip>")
    create_pack(sys.argv[1])
