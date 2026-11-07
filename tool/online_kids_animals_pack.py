#!/usr/bin/env python3
"""Twelve original small animal coloring pages, exclusive to PixelHub Kids.

All artwork is generated from reproducible integer-grid instructions. The PNG
previews and immutable numbered grids are generated as GitHub Release assets,
not committed to the repository or bundled in the APK.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

PREFIX = "online-kids-animal-"
# Paper, outline, yellow, cream, brown, pink, blue, green, white, eye,
# coral, lilac, grey. Keep outlines and eyes high contrast at 16x16.
PALETTE = [
    "FFF5FAFF", "FF344156", "FFF6BC59", "FFFFE5B3", "FFB77653",
    "FFF6A7B8", "FF68B9D3", "FF79B990", "FFFFFFFF", "FF202F45",
    "FFEE826D", "FFB29CCF", "FF8B99A7",
]


def paper(side):
    return Sprite(side, PALETTE)


def eyes(s, x1, x2, y):
    s.dot(x1, y, 9)
    s.dot(x2, y, 9)


def ladybug():
    s = paper(16)
    s.rect(1, 13, 14, 14, 7)
    s.ellipse(8, 8.7, 6.7, 5.7, 1)
    s.ellipse(8, 9, 5.8, 4.7, 10)
    s.ellipse(8, 4, 3, 2.2, 1)
    s.line(8, 5, 8, 13, 1)
    for x, y in ((5, 8), (4, 11), (11, 8), (12, 11)):
        s.ellipse(x, y, 1.1, 1, 9)
    s.line(6, 3, 4, 1, 1)
    s.line(10, 3, 12, 1, 1)
    return s


def snail():
    s = paper(16)
    s.rect(2, 13, 14, 14, 7)
    s.ellipse(8, 11, 6, 3.2, 1)
    s.ellipse(8, 11, 5.3, 2.4, 2)
    s.rect(10, 5, 13, 12, 2)
    s.line(11, 6, 11, 3, 1)
    s.line(13, 6, 13, 3, 1)
    eyes(s, 11, 13, 3)
    s.ellipse(6.5, 9.7, 5.4, 5, 1)
    s.ellipse(6.5, 9.7, 4.5, 4.2, 4)
    s.ellipse(6.5, 9.7, 2.7, 2.8, 3)
    s.line(7, 9, 5, 10, 4)
    return s


def chick():
    s = paper(16)
    s.ellipse(8, 10.5, 6.4, 5.5, 1)
    s.ellipse(8, 10.5, 5.6, 4.8, 2)
    s.ellipse(5, 11, 1.5, 2.4, 3)
    s.ellipse(11, 11, 1.5, 2.4, 3)
    s.ellipse(8, 5, 2.1, 1.8, 2)
    eyes(s, 6, 10, 9)
    s.polygon([(7, 10), (10, 10), (8, 12)], 10)
    s.dot(4, 11, 5)
    s.dot(12, 11, 5)
    s.line(6, 15, 6, 14, 4)
    s.line(10, 15, 10, 14, 4)
    return s


def koala():
    s = paper(24)
    for x in (5, 18):
        s.ellipse(x, 10, 5.1, 5.7, 1)
        s.ellipse(x, 10, 4.1, 4.7, 12)
        s.ellipse(x, 10, 2.5, 3, 5)
    s.ellipse(11.5, 13, 8.2, 8.7, 1)
    s.ellipse(11.5, 13, 7.3, 7.7, 12)
    s.ellipse(11.5, 18, 5.4, 3.4, 8)
    s.ellipse(11.5, 14.7, 2.9, 4.2, 1)
    s.ellipse(11.5, 15, 2.2, 3.2, 9)
    eyes(s, 8, 15, 12)
    s.dot(6, 17, 5)
    s.dot(17, 17, 5)
    return s


def lion():
    s = paper(24)
    for x, y in ((6, 6), (17, 6), (4, 12), (19, 12), (6, 18), (17, 18)):
        s.ellipse(x, y, 4.2, 4, 1)
        s.ellipse(x, y, 3.2, 3, 4)
    s.ellipse(11.5, 12, 9.6, 9.5, 1)
    s.ellipse(11.5, 12, 8.6, 8.5, 4)
    s.ellipse(11.5, 13, 6.2, 6.7, 2)
    s.ellipse(11.5, 17, 4.6, 2.8, 3)
    eyes(s, 9, 14, 12)
    s.polygon([(10, 16), (13, 16), (12, 18)], 9)
    s.line(12, 18, 12, 19, 1)
    s.dot(7, 16, 5)
    s.dot(16, 16, 5)
    return s


def penguin():
    s = paper(24)
    s.ellipse(11.5, 12, 8.5, 10.3, 1)
    s.ellipse(11.5, 12, 7.4, 9.3, 12)
    s.ellipse(11.5, 15, 5.9, 6.5, 8)
    s.ellipse(6, 12, 2.1, 5, 1)
    s.ellipse(17, 12, 2.1, 5, 1)
    s.ellipse(9, 9.7, 2.3, 3, 8)
    s.ellipse(14, 9.7, 2.3, 3, 8)
    eyes(s, 9, 14, 10)
    s.polygon([(10, 12), (14, 12), (12, 15)], 2)
    s.ellipse(8, 14, 1.4, 1, 5)
    s.ellipse(16, 14, 1.4, 1, 5)
    s.ellipse(8, 21, 3.6, 1.7, 2)
    s.ellipse(16, 21, 3.6, 1.7, 2)
    return s


def mouse():
    s = paper(24)
    for x in (5, 18):
        s.ellipse(x, 7, 5, 5, 1)
        s.ellipse(x, 7, 4, 4, 12)
        s.ellipse(x, 7, 2.7, 2.7, 5)
    s.ellipse(11.5, 14, 8.9, 8, 1)
    s.ellipse(11.5, 14, 8, 7, 12)
    s.ellipse(11.5, 17, 4, 3, 8)
    eyes(s, 8, 15, 13)
    s.ellipse(11.5, 16, 1.5, 1.2, 5)
    s.line(12, 17, 12, 19, 1)
    s.line(12, 19, 10, 20, 1)
    s.line(12, 19, 14, 20, 1)
    s.line(2, 17, 7, 18, 1)
    s.line(16, 18, 21, 17, 1)
    return s


def crab():
    s = paper(24)
    s.line(5, 14, 1, 10, 1, radius=1.0)
    s.line(18, 14, 22, 10, 1, radius=1.0)
    for x in (3, 20):
        s.ellipse(x, 8, 3.4, 3.1, 1)
        s.ellipse(x, 8, 2.5, 2.3, 10)
        s.rect(x - 1, 6, x + 1, 7, 0)
    s.ellipse(11.5, 14, 8.6, 6.4, 1)
    s.ellipse(11.5, 14, 7.6, 5.4, 10)
    for x in (5, 8, 15, 18):
        s.line(x, 18, x - (2 if x < 12 else -2), 21, 1)
    s.line(9, 10, 9, 7, 1)
    s.line(15, 10, 15, 7, 1)
    s.ellipse(9, 7, 1.6, 2, 8)
    s.ellipse(15, 7, 1.6, 2, 8)
    eyes(s, 9, 15, 7)
    s.line(10, 16, 14, 16, 1)
    return s


def dolphin():
    s = paper(24)
    s.rect(1, 20, 22, 21, 6)
    s.polygon([(3, 13), (5, 10), (9, 8), (12, 6), (17, 7),
               (20, 10), (22, 11), (18, 13), (13, 16), (8, 16)], 1)
    s.polygon([(4, 13), (7, 10), (12, 8), (17, 9), (20, 11),
               (16, 13), (12, 15), (8, 15)], 6)
    s.polygon([(10, 10), (11, 3), (16, 8)], 1)
    s.polygon([(11, 8), (12, 5), (14, 8)], 6)
    s.polygon([(5, 13), (1, 9), (2, 17)], 1)
    s.polygon([(4, 13), (2, 11), (2, 15)], 6)
    s.polygon([(12, 13), (16, 19), (17, 13)], 1)
    s.polygon([(13, 14), (16, 17), (16, 14)], 6)
    s.dot(18, 10, 9)
    s.line(17, 14, 21, 14, 8)
    return s


def squirrel():
    s = paper(24)
    s.ellipse(17, 10, 6.5, 8, 1)
    s.ellipse(17, 10, 5.5, 7, 4)
    s.ellipse(17, 9, 3.1, 5, 2)
    s.ellipse(10, 16, 7.6, 6.7, 1)
    s.ellipse(10, 16, 6.8, 5.8, 4)
    s.ellipse(10, 18, 4.4, 3.3, 3)
    s.polygon([(4, 10), (3, 3), (10, 8)], 1)
    s.polygon([(5, 9), (5, 5), (8, 8)], 5)
    s.ellipse(7.5, 10, 4.7, 5.3, 1)
    s.ellipse(7.5, 10, 3.8, 4.3, 4)
    s.ellipse(6, 13, 2.8, 1.8, 3)
    s.dot(7, 9, 9)
    s.dot(4, 12, 5)
    s.ellipse(7, 21, 3, 1.2, 1)
    return s


def elephant():
    s = paper(32)
    for x in (6, 25):
        s.ellipse(x, 14, 6, 8, 1)
        s.ellipse(x, 14, 5, 7, 12)
        s.ellipse(x, 14, 3.5, 4.7, 11)
    s.ellipse(15.5, 15, 11, 11.5, 1)
    s.ellipse(15.5, 15, 10, 10.5, 12)
    s.rect(12, 17, 19, 27, 1)
    s.rect(13, 17, 18, 27, 12)
    s.ellipse(15.5, 27, 3.6, 2.7, 1)
    s.ellipse(15.5, 27, 2.7, 1.8, 12)
    eyes(s, 12, 19, 13)
    s.ellipse(7.5, 20, 1.6, 1.5, 5)
    s.ellipse(23.5, 20, 1.6, 1.5, 5)
    s.ellipse(10, 27, 2.3, 1.7, 8)
    s.ellipse(21, 27, 2.3, 1.7, 8)
    return s


def giraffe():
    s = paper(32)
    s.ellipse(16, 26, 9.4, 5, 1)
    s.ellipse(16, 26, 8.4, 4.2, 2)
    s.rect(12, 10, 20, 26, 1)
    s.rect(13, 10, 19, 26, 2)
    for x, y in ((14, 15), (18, 19), (15, 24)):
        s.ellipse(x, y, 1.8, 1.9, 4)
    s.rect(12, 4, 13, 10, 1)
    s.rect(19, 4, 20, 10, 1)
    s.ellipse(12, 4, 2, 2.1, 4)
    s.ellipse(20, 4, 2, 2.1, 4)
    s.ellipse(7, 12, 3.5, 3, 1)
    s.ellipse(25, 12, 3.5, 3, 1)
    s.ellipse(16, 12, 8, 7, 1)
    s.ellipse(16, 12, 7.1, 6.2, 2)
    s.ellipse(16, 16, 5.3, 3, 3)
    eyes(s, 12, 20, 11)
    s.dot(14, 16, 4)
    s.dot(18, 16, 4)
    s.line(14, 18, 18, 18, 1)
    return s


PICTURES = [
    ("ladybug", "کفشدوزک", "Ladybug", ladybug),
    ("snail", "حلزون", "Snail", snail),
    ("chick", "جوجه زرد", "Yellow Chick", chick),
    ("koala", "کوالا", "Koala", koala),
    ("lion", "شیر کوچولو", "Little Lion", lion),
    ("penguin", "پنگوئن", "Penguin", penguin),
    ("mouse", "موش کوچولو", "Little Mouse", mouse),
    ("crab", "خرچنگ", "Crab", crab),
    ("dolphin", "دلفین", "Dolphin", dolphin),
    ("squirrel", "سنجاب", "Squirrel", squirrel),
    ("elephant", "فیل کوچولو", "Little Elephant", elephant),
    ("giraffe", "زرافه", "Giraffe", giraffe),
]


def make_level(name, title_fa, title_en, draw):
    sprite = draw()
    if sprite.side not in (16, 24, 32):
        raise ValueError("Kids animals must use 16, 24 or 32 pixel grids")
    level = {
        "schemaVersion": 2,
        "levelId": PREFIX + name,
        "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": sprite.side,
        "height": sprite.side,
        "palette": sprite.palette,
        "cells": sprite.cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    manifest, assets = [], {}
    for name, title_fa, title_en, draw in PICTURES:
        level = make_level(name, title_fa, title_en, draw)
        body = compact(level)
        ident = level["levelId"]
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1, "title": title_fa,
            "titleEn": title_en, "category": "animals",
            "width": level["width"], "height": level["height"],
            "bytes": len(body), "checksum": level["checksum"],
        })
        assets[f"levels/{stem}.json"] = body
        assets[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, body in assets.items():
            archive.writestr(path, body)
    print(f"Prepared {len(manifest)} Kids-only small animals: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_kids_animals_pack.py <content.zip>")
    create_pack(sys.argv[1])
