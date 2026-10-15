#!/usr/bin/env python3
"""Fifteen original 70x70 pixel-art coloring levels of NEW world landmarks.

Hand-authored drawing recipes produce schema-v2, checksum-bound online levels.
Only recipes are committed. Numbered JSON and PNG previews are published in
an immutable GitHub Release, never bundled inside the Android application.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 70
PALETTE = [
    "FFE7F5FC",  # 0 sky
    "FF34465C",  # 1 ink
    "FFF4E6D0",  # 2 bright stone
    "FFD5B994",  # 3 stone
    "FFAA8466",  # 4 stone shadow
    "FFDEBA6B",  # 5 golden masonry
    "FF246D53",  # 6 trees
    "FF89B789",  # 7 foliage
    "FF306B92",  # 8 deep water / blue tile
    "FF79C6D9",  # 9 bright water
    "FFBE5947",  # 10 brick red
    "FFE7A8B3",  # 11 rose
    "FF4B5367",  # 12 slate
    "FFFFFFFF",  # 13 white
    "FFF3D59D",  # 14 sand
    "FF835842",  # 15 earth
    "FF826A9C",  # 16 mauve
    "FF9EABB6",  # 17 silvery stone
    "FFFBDD8C",  # 18 sun
    "FFA5CD94",  # 19 grass
    "FF2B4268",  # 20 dark navy
    "FF31A3A2",  # 21 turquoise
    "FFE5B448",  # 22 gold
    "FFB9CFE0",  # 23 bluish stone
    "FF8A4851",  # 24 burgundy
]

# Unlike the first two world-landmark packs, these are fifteen new subjects.
# (slug, Persian title, English title, location)
PICTURES = [
    ("belem-tower", "برج بلم لیسبون", "Belém Tower", "Portugal"),
    ("pena-palace", "کاخ پنا", "Pena Palace", "Portugal"),
    ("prague-astronomical-clock", "ساعت نجومی پراگ", "Prague Astronomical Clock", "Czechia"),
    ("charles-bridge", "پل چارلز پراگ", "Charles Bridge", "Czechia"),
    ("hungarian-parliament", "پارلمان مجارستان", "Hungarian Parliament Building", "Hungary"),
    ("edinburgh-castle", "قلعه ادینبرو", "Edinburgh Castle", "United Kingdom"),
    ("milan-cathedral", "کلیسای جامع میلان", "Milan Cathedral", "Italy"),
    ("blue-mosque", "مسجد آبی استانبول", "Blue Mosque, Istanbul", "Türkiye"),
    ("galata-tower", "برج گالاتا", "Galata Tower", "Türkiye"),
    ("borobudur", "معبد بوروبودور", "Borobudur Temple", "Indonesia"),
    ("prambanan", "معبد پرامبانان", "Prambanan Temple", "Indonesia"),
    ("shwedagon-pagoda", "پاگودای شوداگون", "Shwedagon Pagoda", "Myanmar"),
    ("wat-arun", "معبد وات آرون", "Wat Arun", "Thailand"),
    ("gateway-of-india", "دروازه هند بمبئی", "Gateway of India, Mumbai", "India"),
    ("hassan-ii-mosque", "مسجد حسن دوم", "Hassan II Mosque", "Morocco"),
]


def block(s, x0, y0, x1, y1, color=3, rim=1):
    """Filled pixel rectangle with one-cell visible contour."""
    s.rect(x0-1, y0-1, x1+1, y1+1, rim)
    s.rect(x0, y0, x1, y1, color)


def triangle(s, vertices, fill=3, rim=1):
    s.polygon(vertices, rim)
    cx = sum(p[0] for p in vertices) / len(vertices)
    cy = sum(p[1] for p in vertices) / len(vertices)
    s.polygon([(cx+(x-cx)*.88, cy+(y-cy)*.88) for x, y in vertices], fill)


def window(s, x, y, fill=1):
    s.rect(x-1, y, x+1, y+4, fill)
    s.dot(x, y-1, fill)


def pointed_arch(s, x, top, bottom, half, stone=3, opening=1):
    s.polygon([(x-half, bottom), (x-half, top+half*.6),
               (x, top), (x+half, top+half*.6),
               (x+half, bottom)], 1)
    a = max(1, half-1)
    s.polygon([(x-a, bottom-1), (x-a, top+a*.65+1),
               (x, top+2), (x+a, top+a*.65+1),
               (x+a, bottom-1)], stone)
    a = max(1, half-4)
    s.polygon([(x-a, bottom-1), (x-a, top+a*.7+5),
               (x, top+6), (x+a, top+a*.7+5),
               (x+a, bottom-1)], opening)


def onion_dome(s, x, center_y, r, fill=22):
    # Layered domed silhouette with tiered tip, not a scaled bitmap.
    s.ellipse(x, center_y, r, r*.85, 1)
    s.ellipse(x, center_y, r-1, r*.85-1, fill)
    s.polygon([(x-r, center_y), (x+r, center_y),
               (x+r-1, center_y+5), (x-r+1, center_y+5)], 1)
    s.rect(x-r+1, center_y, x+r-1, center_y+4, fill)
    s.line(x, center_y-r*.9-6, x, center_y-r*.8, 1)
    s.dot(x, round(center_y-r*.9-7), 18)


def minaret(s, x, top, base, wall=2, width=5):
    block(s, x-width//2, top+7, x+width//2, base, wall)
    s.polygon([(x-width//2-2, top+7), (x, top),
               (x+width//2+2, top+7)], 1)
    s.polygon([(x-width//2, top+6), (x, top+2),
               (x+width//2, top+6)], wall)
    s.rect(x-width//2-1, top+10, x+width//2+1, top+12, 1)
    for y in range(top+16, base-3, 8):
        window(s, x, y, 1)


def scenery(s, mode="grass"):
    s.rect(0, 0, 69, 69, 0)
    if mode == "evening":
        s.rect(0, 0, 69, 69, 23)
    if mode == "water":
        s.rect(0, 60, 69, 69, 8)
        for y in (62, 65, 68):
            for x in range(4+(y%4), 67, 13):
                s.line(x, y, x+6, y, 9)
    elif mode == "desert":
        s.rect(0, 60, 69, 69, 14)
        s.line(0,60,69,60,4)
    else:
        s.rect(0, 63, 69, 69, 19)
        s.line(0,63,69,63,6)
    s.ellipse(61, 9, 4, 4, 18)
    for x, y in ((7,12), (42,9)):
        s.ellipse(x, y, 5, 2, 13)
        s.ellipse(x+3, y+1, 3, 1.5, 13)


def paint(slug):
    s = Sprite(SIDE, PALETTE)
    background = ("water" if slug in {"belem-tower", "charles-bridge",
                                      "wat-arun", "hassan-ii-mosque"} else
                  "desert" if slug in {"borobudur", "prambanan",
                                      "gateway-of-india"} else
                  "evening" if slug in {"prague-astronomical-clock",
                                        "shwedagon-pagoda"} else "grass")
    scenery(s, background)

    if slug == "belem-tower":
        # Manueline river fortress, polygonal bulwark and patterned watchtowers.
        s.polygon([(4,47),(15,44),(55,44),(66,47),(63,60),(7,60)],1)
        s.polygon([(6,48),(18,45),(52,45),(64,48),(60,58),(10,58)],3)
        block(s,17,25,53,52,2)
        block(s,22,14,48,36,3)
        for x in (16,54):
            block(s,x-5,35,x+5,53,3)
            s.polygon([(x-5,35),(x,29),(x+5,35)],1)
            window(s,x,40)
        for x in (22,47):
            block(s,x-4,12,x+4,24,3)
            s.rect(x-5,10,x+5,12,1)
            for xx in (x-4,x,x+4):
                s.rect(xx,8,xx+2,11,3)
        for x in range(24,47,6):
            window(s,x,20)
            window(s,x,33)
        pointed_arch(s,35,39,59,9,stone=3,opening=8)
        for x in range(12,61,6):
            s.dot(x,48,1)
        s.line(0,60,69,60,9)

    elif slug == "pena-palace":
        # Distinctive yellow-and-red Romanticist terraces and conical towers.
        s.polygon([(0,63),(0,48),(19,41),(38,44),
                   (57,35),(69,44),(69,69),(0,69)],6)
        block(s,8,38,61,59,22)
        block(s,20,26,48,56,10)
        for x, top, fill in ((14,20,22),(36,13,10),(55,23,22)):
            minaret(s,x,top,58,fill,width=9)
            s.polygon([(x-8,top+8),(x,top-3),(x+8,top+8)],12)
            s.polygon([(x-6,top+7),(x,top-1),(x+6,top+7)],fill)
        s.polygon([(17,26),(34,17),(51,26)],1)
        s.polygon([(20,26),(34,20),(48,26)],10)
        for x in (22,31,42,53):
            for y in (39,48):
                window(s,x,y)
        pointed_arch(s,36,43,60,9,stone=10,opening=1)
        s.rect(4,60,65,62,4)
        s.ellipse(5,59,4,7,6)

    elif slug == "prague-astronomical-clock":
        # Orloj: a richly divided astronomical dial plus separate calendar.
        block(s,13,13,57,64,3)
        s.rect(11,9,59,14,1)
        for x in range(14,58,5):
            s.rect(x,8,x+2,11,3)
        s.ellipse(35,30,16,16,1)
        s.ellipse(35,30,14,14,22)
        s.ellipse(35,30,12,12,8)
        s.ellipse(35,30,9.5,9.5,21)
        s.ellipse(35,30,6,6,20)
        for i in range(12):
            a=2*math.pi*i/12
            xx=round(35+12*math.sin(a))
            yy=round(30-12*math.cos(a))
            s.dot(xx,yy,13)
        s.line(35,30,43,26,18,radius=1)
        s.line(35,30,32,22,13,radius=1)
        s.ellipse(35,53,8,8,1)
        s.ellipse(35,53,6,6,22)
        for x in (19,51):
            for y in (22,43,54):
                window(s,x,y)
        triangle(s,[(11,13),(35,3),(59,13)],12)
        s.line(9,64,61,64,1)

    elif slug == "charles-bridge":
        # Multiple robust bridge spans, gothic towers, statues and reflections.
        s.rect(0,0,69,60,0)
        for x,top in ((12,23),(57,19)):
            block(s,x-6,top+8,x+6,49,3)
            triangle(s,[(x-8,top+8),(x,top-1),(x+8,top+8)],12)
            for y in (top+14,top+24,top+30):
                window(s,x,y)
        s.rect(0,47,69,54,1)
        s.rect(0,48,69,51,4)
        for x in (9,27,45,63):
            pointed_arch(s,x,48,60,8,stone=3,opening=8)
        s.rect(0,45,69,47,3)
        for x in (5,19,34,50,64):
            s.rect(x,37,x+2,45,12)
            s.ellipse(x+1,36,3,4,1)
            s.ellipse(x+1,35,2,3,17)
        s.rect(0,57,69,59,1)
        for y in (62,66):
            for x in range(5,63,11):
                s.line(x,y,x+5,y,9)

    elif slug == "hungarian-parliament":
        # Neo-Gothic river facade with central dome and matching spires.
        block(s,3,44,66,59,3)
        block(s,12,34,58,54,2)
        onion_dome(s,35,31,13,12)
        for x in (8,62):
            minaret(s,x,18,57,3,6)
        for x in (18,52):
            minaret(s,x,23,52,2,5)
        for x in (25,45):
            minaret(s,x,29,51,3,4)
        for x in range(7,65,6):
            for y in (47,54):
                window(s,x,y,1)
        s.polygon([(18,38),(35,28),(52,38)],1)
        s.polygon([(20,38),(35,31),(50,38)],2)
        pointed_arch(s,35,44,61,6,stone=3,opening=1)
        s.rect(0,60,69,62,4)
        for x in range(3,69,9):
            s.dot(x,62,18)

    elif slug == "edinburgh-castle":
        s.polygon([(0,62),(8,48),(16,43),(26,45),(37,37),
                   (48,42),(58,45),(69,60),(69,69),(0,69)],12)
        s.polygon([(0,65),(12,50),(28,48),(38,42),
                   (54,48),(69,63),(69,69),(0,69)],4)
        block(s,11,31,59,52,3)
        block(s,21,22,50,45,4)
        for x,top,bot in ((15,22,50),(34,14,48),(56,25,51)):
            block(s,x-6,top,x+6,bot,3)
            for xx in range(x-7,x+7,4):
                s.rect(xx,top-4,xx+2,top,4)
            for y in range(top+8,bot-3,8):
                window(s,x,y)
        triangle(s,[(20,22),(34,13),(49,22)],12)
        pointed_arch(s,36,39,56,7,stone=3,opening=1)
        s.line(3,59,66,59,1)
        s.ellipse(65,61,5,8,6)

    elif slug == "milan-cathedral":
        # Rich Gothic facade: dozens of pointed spires and lancet windows.
        block(s,8,33,61,64,2)
        s.polygon([(8,34),(35,23),(62,34)],1)
        s.polygon([(11,34),(35,26),(59,34)],2)
        for x,top in ((10,18),(18,12),(26,20),(35,4),
                      (44,20),(52,12),(60,18)):
            minaret(s,x,top,61,2,4 if x!=35 else 6)
            s.line(x,top-1,x,top-6,1)
            s.dot(x,top-7,22)
        pointed_arch(s,35,36,65,8,stone=2,opening=12)
        for x in (14,24,46,56):
            pointed_arch(s,x,43,63,4,stone=2,opening=8)
        for y in (38,48,57):
            s.line(8,y,61,y,4,radius=.4)
        s.rect(4,65,66,67,17)

    elif slug == "blue-mosque":
        # Distinctive six minarets and stacked blue-grey domes.
        block(s,7,44,63,62,2)
        onion_dome(s,35,36,17,17)
        onion_dome(s,21,44,10,23)
        onion_dome(s,49,44,10,23)
        for x,top in ((6,18),(14,11),(56,11),(64,18)):
            minaret(s,x,top,61,2,4)
        for x in (18,52):
            minaret(s,x,23,57,2,4)
        for x in (13,26,35,44,57):
            pointed_arch(s,x,49,63,5,stone=2,opening=8)
        for y in (55,60):
            s.line(9,y,61,y,8,radius=.3)
        s.rect(1,63,68,65,3)

    elif slug == "galata-tower":
        # Dominant stone cylindrical mass with a conical pointed dark roof.
        s.ellipse(35,60,20,7,1)
        block(s,20,22,50,61,3)
        s.polygon([(19,23),(35,5),(51,23)],1)
        s.polygon([(22,22),(35,8),(48,22)],12)
        s.rect(18,22,52,26,1)
        s.rect(20,23,50,24,4)
        for x in (24,31,39,46):
            window(s,x,29)
            for y in (42,52):
                window(s,x,y)
        s.rect(17,36,53,38,4)
        for x in range(19,52,5):
            s.rect(x,34,x+1,38,1)
        s.rect(15,62,55,65,1)
        s.rect(16,63,54,64,4)
        s.ellipse(7,61,6,6,6)
        s.ellipse(63,60,5,7,7)

    elif slug == "borobudur":
        # Concentric terraced Buddhist monument with lattice stupas.
        for tier in range(6):
            left=6+tier*4
            right=63-tier*4
            top=57-tier*6
            block(s,left,top,right,top+5,3)
            for x in range(left+4,right-1,7):
                s.rect(x,top-2,x+3,top,4)
        for x,y,r in ((18,31,5),(35,23,8),(52,31,5),
                      (25,35,4),(45,35,4)):
            s.ellipse(x,y,r,r*.8,1)
            s.ellipse(x,y,r-1,r*.7,17)
            s.rect(x-r,y,x+r,y+4,1)
            for dx in (-2,1):
                s.dot(x+dx,y+2,8)
        minaret(s,35,12,35,wall=17,width=6)
        s.rect(2,63,67,66,4)

    elif slug == "prambanan":
        # Tall staggered Hindu prasada shrines with ribbed tapering tops.
        for x,top,bottom,width in ((11,25,61,12),(27,14,62,15),
                                    (44,4,62,16),(59,25,60,12)):
            block(s,x-width//2,top+18,x+width//2,bottom,3)
            s.polygon([(x-width//2-2,top+19),(x,top),
                       (x+width//2+2,top+19)],1)
            s.polygon([(x-width//2,top+18),(x,top+3),
                       (x+width//2,top+18)],4)
            for y in range(top+7,top+20,4):
                half=max(2,(y-top)*width//45)
                s.rect(x-half,y,x+half,y+1,2)
            for y in range(top+26,bottom-2,7):
                window(s,x,y)
            s.rect(x-width//2-2,bottom-4,x+width//2+2,bottom-2,1)
        for x in (17,36,53):
            s.rect(x-2,63,x+2,65,15)
        s.rect(0,66,69,68,14)

    elif slug == "shwedagon-pagoda":
        # Giant tiered golden stupa; surrounding golden temple bells.
        block(s,4,54,65,63,5)
        for k in range(7):
            half=26-k*3
            y=53-k*5
            block(s,35-half,y,35+half,y+3,22 if k%2 else 5)
        s.polygon([(29,22),(35,7),(41,22)],1)
        s.polygon([(31,22),(35,10),(39,22)],22)
        s.line(35,7,35,2,18)
        s.ellipse(35,2,3,2,18)
        for x in (9,60):
            minaret(s,x,32,63,wall=22,width=6)
            s.ellipse(x,29,6,6,22)
        for y in (25,35,45,55):
            s.line(12,y,58,y,18,radius=.3)
        s.rect(0,64,69,66,4)

    elif slug == "wat-arun":
        # Multi-tiered Khmer-influenced prang and four small satellite spires.
        for x,top,bottom,width in ((11,30,58,9),(25,26,60,9),
                                   (45,26,60,9),(59,30,58,9)):
            block(s,x-width//2,top+8,x+width//2,bottom,2)
            triangle(s,[(x-width//2-2,top+9),(x,top),
                         (x+width//2+2,top+9)],17)
            for y in range(top+12,bottom-2,5):
                s.line(x-width//2,y,x+width//2,y,21)
        for i in range(9):
            y=59-i*5
            half=15-i
            s.polygon([(35-half,y+4),(35+half,y+4),
                       (35+half-2,y),(35-half+2,y)],1)
            s.polygon([(35-half+2,y+3),(35+half-2,y+3),
                       (35+half-3,y+1),(35-half+3,y+1)],2 if i%2 else 17)
            s.line(35-half+1,y+3,35+half-1,y+3,21,radius=.5)
        triangle(s,[(31,17),(35,5),(39,17)],22)
        s.line(35,6,35,1,18)
        s.rect(3,61,66,64,3)
        for x in range(4,65,7):
            s.dot(x,63,22)

    elif slug == "gateway-of-india":
        # Yellow basalt Indo-Saracenic arch on Mumbai's harborfront.
        block(s,11,30,58,60,3)
        for x in (14,56):
            block(s,x-6,23,x+6,60,4)
            onion_dome(s,x,20,7,3)
            for y in (35,45,53):
                window(s,x,y)
        block(s,17,24,53,31,3)
        for x in range(20,52,7):
            s.rect(x,20,x+3,25,4)
            s.ellipse(x+1,19,2,2,5)
        pointed_arch(s,35,29,62,12,stone=3,opening=0)
        for x in (22,48):
            pointed_arch(s,x,40,59,4,stone=3,opening=1)
        s.rect(6,60,64,63,1)
        s.rect(9,61,61,62,3)
        s.line(1,65,69,65,4)

    elif slug == "hassan-ii-mosque":
        # Atlantic-side Casablanca complex with its unusually tall minaret.
        block(s,4,45,65,61,2)
        block(s,12,38,53,60,3)
        for x in (12,58):
            onion_dome(s,x,37,7,5)
        minaret(s,43,9,62,wall=5,width=12)
        s.rect(36,11,50,15,1)
        s.rect(37,12,49,14,21)
        for y in (20,29,38,48):
            s.rect(37,y,49,y+2,21)
            for x in (39,44,47):
                s.dot(x,y+1,18)
        s.rect(38,7,48,10,22)
        s.line(43,7,43,2,18)
        for x in (9,18,26,57):
            pointed_arch(s,x,46,62,5,stone=2,opening=8)
        s.rect(2,62,67,64,3)
        for y in (66,68):
            for x in range(4,65,12):
                s.line(x,y,x+7,y,9)

    else:
        raise ValueError("Unknown landmark: " + slug)
    return s


def make_level(item):
    slug, title_fa, title_en, _country = item
    art = paint(slug)
    level = {
        "schemaVersion": 2,
        "levelId": f"online-world-new-{slug}-70",
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
    if len(PICTURES) != 15 or len({p[0] for p in PICTURES}) != 15:
        raise ValueError("Expect exactly 15 unique landmark recipes")
    manifest, assets = [], {}
    for item in PICTURES:
        level = make_level(item)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Over 256 KiB: " + level["levelId"])
        stem = level["levelId"] + "-v1"
        manifest.append({
            "id": level["levelId"],
            "version": 1,
            "title": level["titles"]["fa"],
            "titleEn": level["titles"]["en"],
            "category": "patterns",
            "width": SIDE, "height": SIDE,
            "bytes": len(body),
            "checksum": level["checksum"],
        })
        assets["levels/" + stem + ".json"] = body
        assets["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    dest = pathlib.Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, payload in assets.items():
            archive.writestr(path, payload)
    print("Prepared 15 original 70x70 world landmarks:", dest)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_world_landmarks_15_70_pack.py <content.zip>")
    create_pack(sys.argv[1])
