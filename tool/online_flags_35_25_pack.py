#!/usr/bin/env python3
"""Twenty-five NEW country flags as distinct 35x35 online coloring levels.

Flags are rasterized directly to a discrete 35x35 pixel grid (not upscaled
10x10 icons). Their emblem/lettering details are necessarily stylized.
Only deterministic drawing instructions are tracked by Git; the numbered JSON
and preview PNG assets are published in an immutable GitHub Release.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite
from online_flags_20_pack import COUNTRIES as FIRST_TWENTY

SIDE = 35
TOP = 6
BOTTOM = 28

# Single stable opaque ARGB palette: background, white, scarlet, dark red,
# cobalt, navy, sky blue, green, dark green, yellow, orange, black, gold, grey.
PALETTE = [
    "FFEAF0F4",  # 0 neutral margin
    "FFFFFFFF",  # 1 white
    "FFCF293C",  # 2 red
    "FF98243D",  # 3 dark red
    "FF285AA3",  # 4 blue
    "FF172E59",  # 5 navy
    "FF73BEE3",  # 6 sky blue
    "FF208A53",  # 7 green
    "FF116D3D",  # 8 dark green
    "FFF4D04C",  # 9 yellow
    "FFF18E39",  # 10 orange
    "FF1E2935",  # 11 black
    "FFCB9D4C",  # 12 gold
    "FFB5B7BF",  # 13 grey
]

# Country ISO name in our immutable ID, fa, en, variant.
# These are intentionally absent from the earlier 20-country 10x10 pack.
COUNTRIES = [
    ("spain", "اسپانیا", "Spain"),
    ("portugal", "پرتغال", "Portugal"),
    ("belgium", "بلژیک", "Belgium"),
    ("austria", "اتریش", "Austria"),
    ("denmark", "دانمارک", "Denmark"),
    ("greece", "یونان", "Greece"),
    ("ireland", "ایرلند", "Ireland"),
    ("czechia", "چک", "Czechia"),
    ("slovakia", "اسلواکی", "Slovakia"),
    ("hungary", "مجارستان", "Hungary"),
    ("romania", "رومانی", "Romania"),
    ("bulgaria", "بلغارستان", "Bulgaria"),
    ("croatia", "کرواسی", "Croatia"),
    ("serbia", "صربستان", "Serbia"),
    ("south-korea", "کره جنوبی", "South Korea"),
    ("australia", "استرالیا", "Australia"),
    ("new-zealand", "نیوزیلند", "New Zealand"),
    ("mexico", "مکزیک", "Mexico"),
    ("argentina", "آرژانتین", "Argentina"),
    ("chile", "شیلی", "Chile"),
    ("colombia", "کلمبیا", "Colombia"),
    ("peru", "پرو", "Peru"),
    ("south-africa", "آفریقای جنوبی", "South Africa"),
    ("egypt", "مصر", "Egypt"),
    ("saudi-arabia", "عربستان سعودی", "Saudi Arabia"),
]


def flag(name):
    s = Sprite(SIDE, PALETTE)
    s.rect(0, 0, 34, 34, 0)

    def band(colors):
        count = len(colors)
        for y in range(TOP, BOTTOM + 1):
            s.rect(0, y, 34, y, colors[(y - TOP) * count // 23])

    def stripes(colors):
        count = len(colors)
        for x in range(35):
            s.rect(x, TOP, x, BOTTOM, colors[x * count // 35])

    def line(x0, y0, x1, y1, color, size=0.7):
        s.line(x0, y0, x1, y1, color, radius=size)

    def poly(points, color):
        s.polygon(points, color)

    def disk(x, y, r, color):
        s.ellipse(x, y, r, r, color)

    def star(x, y, r, color, rays=5):
        pts = []
        for t in range(2 * rays):
            a = -math.pi / 2 + t * math.pi / rays
            rr = r if t % 2 == 0 else r * .43
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        poly(pts, color)

    def shield(x, y, color=2):
        poly([(x-4,y-5),(x+4,y-5),(x+4,y+3),
              (x,y+7),(x-4,y+3)], color)

    def crest(x, y):
        # Vivid stylized crest for flags whose heraldic seal cannot fit
        # faithfully at 35px: shield, upper gold crown and inner marks.
        shield(x, y, 2)
        s.rect(x-3, y-4, x+3, y-1, 9)
        s.rect(x-3, y, x+3, y+3, 1)
        s.rect(x-1, y, x+1, y+2, 4)
        s.rect(x-5, y-7, x+5, y-6, 12)
        for dx in (-4, 0, 4):
            s.dot(x+dx, y-8, 12)

    def uk_canton(width=15, height=11):
        s.rect(0, TOP, width-1, TOP+height-1, 5)
        for x in range(width):
            y = TOP + round(x * (height-1)/(width-1))
            z = TOP + height-1 - round(x * (height-1)/(width-1))
            s.dot(x, y, 1)
            s.dot(x, z, 1)
        s.rect(width//2-1, TOP, width//2+1, TOP+height-1, 1)
        s.rect(0, TOP+height//2-1, width-1, TOP+height//2+1, 1)
        s.rect(width//2, TOP, width//2, TOP+height-1, 2)
        s.rect(0, TOP+height//2, width-1, TOP+height//2, 2)

    if name == "spain":
        s.rect(0, TOP, 34, BOTTOM, 9)
        s.rect(0, TOP, 34, TOP+5, 2)
        s.rect(0, BOTTOM-5, 34, BOTTOM, 2)
        crest(13, 18)
    elif name == "portugal":
        stripes((7, 2, 2, 2, 2))
        disk(14, 17, 7.5, 9)
        disk(14, 17, 5.7, 1)
        shield(14, 17, 2)
        for x, y in ((12,16),(16,16),(14,18),(12,20),(16,20)):
            s.dot(x, y, 4)
    elif name == "belgium":
        stripes((11, 9, 2))
    elif name == "austria":
        band((2, 1, 2))
    elif name == "denmark":
        s.rect(0, TOP, 34, BOTTOM, 2)
        s.rect(12, TOP, 15, BOTTOM, 1)
        s.rect(0, 16, 34, 19, 1)
    elif name == "greece":
        band((4, 1, 4, 1, 4, 1, 4, 1, 4))
        s.rect(0, TOP, 13, TOP+12, 4)
        s.rect(5, TOP, 7, TOP+12, 1)
        s.rect(0, TOP+5, 13, TOP+7, 1)
    elif name == "ireland":
        stripes((7, 1, 10))
    elif name == "czechia":
        band((1, 2))
        poly([(0,TOP),(0,BOTTOM),(17,17)],4)
    elif name == "slovakia":
        band((1, 4, 2))
        shield(11, 18)
        line(11, 13, 11, 22, 1, 1.0)
        line(7, 16, 15, 16, 1, 1.0)
        line(9, 19, 13, 19, 1, 1.0)
        poly([(8,23),(11,20),(14,23)],4)
    elif name == "hungary":
        band((2, 1, 7))
    elif name == "romania":
        stripes((4, 9, 2))
    elif name == "bulgaria":
        band((1, 7, 2))
    elif name == "croatia":
        band((2, 1, 4))
        shield(17, 17, 2)
        for yy in range(13, 20, 3):
            for xx in range(14, 21, 3):
                s.rect(xx, yy, xx+2, yy+2, 1 if ((xx-14)//3+(yy-13)//3)%2 else 2)
        for xx in (13,16,19,22):
            s.dot(xx, 11, 4)
    elif name == "serbia":
        band((2, 4, 1))
        shield(12, 18, 1)
        s.rect(9, 15, 15, 17, 12)
        disk(12, 20, 2, 2)
        line(12, 14, 12, 24, 2)
        line(10, 21, 14, 21, 2)
        s.rect(8, 12, 16, 13, 12)
    elif name == "south-korea":
        s.rect(0, TOP, 34, BOTTOM, 1)
        disk(17,17,7,2)
        # Divide the yin-yang medallion into two intertwined halves.
        for yy in range(17, 25):
            for xx in range(9, 25):
                if (xx-17)**2+(yy-17)**2<=49:
                    s.dot(xx, yy, 4)
        disk(14, 17, 3.5, 2)
        disk(20, 17, 3.5, 4)
        for xx, yy, split in ((7,11,False),(27,11,True),
                              (7,23,True),(27,23,False)):
            for i in range(3):
                if split:
                    s.rect(xx-2, yy+i*2, xx-1, yy+i*2, 11)
                    s.rect(xx+1, yy+i*2, xx+2, yy+i*2, 11)
                else:
                    s.rect(xx-2, yy+i*2, xx+2, yy+i*2, 11)
    elif name == "australia":
        s.rect(0, TOP, 34, BOTTOM, 5)
        uk_canton()
        for x,y,r in ((23,11,2.4),(27,17,2.2),(22,24,2.3),
                      (30,24,2.2),(17,19,2.0),(8,24,2.6)):
            star(x,y,r,1,7)
    elif name == "new-zealand":
        s.rect(0, TOP, 34, BOTTOM, 5)
        uk_canton()
        for x,y in ((24,10),(29,16),(26,24),(18,19)):
            star(x,y,3.2,1)
            star(x,y,2.0,2)
    elif name == "mexico":
        stripes((7,1,2))
        # Simplified eagle perched on a cactus within the white stripe.
        disk(18,15,4.1,12)
        disk(18,15,2.7,8)
        poly([(15,17),(21,15),(20,20),(17,22)],11)
        line(15,23,20,23,8,1.5)
        line(18,19,18,24,8,1.2)
        line(15,24,21,24,12,1.1)
    elif name == "argentina":
        band((6,1,6))
        disk(17,17,3.2,9)
        for i in range(12):
            a=2*math.pi*i/12
            line(17+4*math.cos(a),17+4*math.sin(a),
                 17+5.8*math.cos(a),17+5.8*math.sin(a),9)
    elif name == "chile":
        band((1,2))
        s.rect(0,TOP,13,17,4)
        star(6,11.5,4,1)
    elif name == "colombia":
        s.rect(0,TOP,34,17,9)
        s.rect(0,18,34,23,4)
        s.rect(0,24,34,BOTTOM,2)
    elif name == "peru":
        stripes((2,1,2))
    elif name == "south-africa":
        s.rect(0,TOP,34,17,2)
        s.rect(0,18,34,BOTTOM,4)
        s.rect(0,16,34,19,1)
        poly([(0,TOP),(0,BOTTOM),(21,17)],1)
        poly([(0,TOP+2),(0,BOTTOM-2),(17,17)],9)
        poly([(0,TOP+5),(0,BOTTOM-5),(13,17)],11)
        poly([(0,TOP+7),(0,BOTTOM-7),(11,17)],11)
        s.rect(13,15,34,20,1)
        s.rect(12,16,34,19,7)
        poly([(0,TOP+3),(0,TOP+6),(12,17),(12,15)],7)
        poly([(0,BOTTOM-3),(0,BOTTOM-6),(12,17),(12,19)],7)
    elif name == "egypt":
        band((2,1,11))
        s.ellipse(17,18,2.3,5.5,12)
        line(14,16,20,16,12,1.1)
        line(15,21,19,21,12,1.1)
        s.dot(17,14,11)
    elif name == "saudi-arabia":
        s.rect(0,TOP,34,BOTTOM,8)
        # Respectfully abstracted calligraphic motif: not actual Shahada text.
        for x0,y0,x1,y1 in ((7,13,11,12),(12,12,16,13),
                             (17,13,22,12),(23,12,27,13),
                             (9,16,15,15),(16,16,23,15),
                             (8,18,13,17),(18,17,26,18)):
            line(x0,y0,x1,y1,1,0.65)
        line(8,22,27,22,1,0.9)
        line(26,22,29,20,1,0.7)
        s.dot(9,21,1)
    else:
        raise ValueError("Unknown country: " + name)

    return s


def make_level(item):
    slug, title_fa, title_en = item
    art = flag(slug)
    level = {
        "schemaVersion": 2,
        "levelId": "online-flag-" + slug + "-35",
        "levelVersion": 1,
        "titles": {"fa": "پرچم " + title_fa, "en": title_en + " Flag"},
        "width": SIDE,
        "height": SIDE,
        "palette": art.palette,
        "cells": art.cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(COUNTRIES) != 25:
        raise ValueError("Pack must have exactly 25 country flags")
    slugs = {item[0] for item in COUNTRIES}
    if len(slugs) != 25 or slugs.intersection({item[0] for item in FIRST_TWENTY}):
        raise ValueError("Duplicate country within or across 10x10 / 35x35 packs")
    manifest, assets = [], {}
    for item in COUNTRIES:
        level = make_level(item)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Flag exceeds online download limit: " + item[0])
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
        for path, body in assets.items():
            archive.writestr(path, body)
    print("Prepared 25 original 35x35 country flags:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_flags_35_25_pack.py <content.zip>")
    create_pack(sys.argv[1])
