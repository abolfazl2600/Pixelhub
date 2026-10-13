#!/usr/bin/env python3
"""Generate 12 original pixel-art coloring levels as one release-only ZIP.

Output is a content.zip with catalog metadata, playable schema-v2 JSON grids,
and tiny PNG previews. The generated assets are never checked into Git.
A successfully verified GitHub Pages workflow publishes this ZIP as a Release.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


def panda():
    s = Sprite(24, [
        "FFE7F8FF", "FF333D50", "FFFFFFFF", "FF768394",
        "FFF6B0C6", "FFA4D6C4", "FFE4EAF1",
    ])
    s.ellipse(3, 20, 1.7, 1.0, 5)
    s.ellipse(20, 20, 1.7, 1.0, 5)
    s.ellipse(6, 7, 3.5, 3.8, 1)
    s.ellipse(17, 7, 3.5, 3.8, 1)
    s.ellipse(11.5, 13, 9, 8.7, 1)
    s.ellipse(11.5, 13, 8.0, 7.6, 2)
    s.ellipse(7.5, 12, 3.0, 4.0, 1)
    s.ellipse(15.5, 12, 3.0, 4.0, 1)
    s.ellipse(8.3, 11.8, 1.3, 1.8, 3)
    s.ellipse(14.7, 11.8, 1.3, 1.8, 3)
    s.dot(8, 11, 2)
    s.dot(15, 11, 2)
    s.ellipse(6, 16, 1.7, 1.0, 4)
    s.ellipse(17, 16, 1.7, 1.0, 4)
    s.ellipse(11.5, 16.1, 4.5, 2.6, 6)
    s.polygon([(10, 15), (13, 15), (12, 17)], 1)
    s.line(12, 17, 12, 18, 1)
    s.line(12, 18, 10, 19, 1)
    s.line(12, 18, 14, 19, 1)
    return s


def bunny():
    s = Sprite(24, [
        "FFFFF5FA", "FF5F5171", "FFF5F1EA", "FFFFC9E0",
        "FFBA8CC6", "FF7A5968", "FFFBDEEC", "FFB7D7AC",
    ])
    s.ellipse(2, 20, 1.7, 1.1, 7)
    s.ellipse(21, 20, 1.7, 1.1, 7)
    s.ellipse(7, 7, 3.1, 6.2, 1)
    s.ellipse(16, 7, 3.1, 6.2, 1)
    s.ellipse(7, 7, 2.0, 5.2, 2)
    s.ellipse(16, 7, 2.0, 5.2, 2)
    s.ellipse(7, 7, 0.9, 4, 3)
    s.ellipse(16, 7, 0.9, 4, 3)
    s.ellipse(11.5, 15, 9, 7.7, 1)
    s.ellipse(11.5, 15, 8, 6.7, 2)
    s.ellipse(7, 15, 1.2, 1.8, 5)
    s.ellipse(16, 15, 1.2, 1.8, 5)
    s.dot(7, 14, 6)
    s.dot(16, 14, 6)
    s.ellipse(5.7, 17.5, 1.8, 1.2, 3)
    s.ellipse(17.3, 17.5, 1.8, 1.2, 3)
    s.ellipse(11.5, 18, 3.4, 2.2, 6)
    s.polygon([(10, 17), (13, 17), (12, 19)], 3)
    s.line(12, 19, 12, 20, 1)
    return s


def turtle():
    s = Sprite(24, [
        "FFE7FAF4", "FF315A56", "FF75B999", "FFBDE7B0",
        "FF528D83", "FF9BC8CB", "FFFFD881", "FFF4F1D6",
    ])
    s.ellipse(3, 3, 1.4, 1.1, 7)
    s.ellipse(20, 21, 1.4, 1.1, 7)
    s.ellipse(7, 19, 3.7, 2.1, 1)
    s.ellipse(7, 19, 2.7, 1.4, 2)
    s.ellipse(14, 19, 3.7, 2.1, 1)
    s.ellipse(14, 19, 2.7, 1.4, 2)
    s.polygon([(4, 15), (1, 13), (3, 17)], 4)
    s.ellipse(18.5, 13.4, 4.2, 4.1, 1)
    s.ellipse(18.5, 13.4, 3.3, 3.2, 2)
    s.ellipse(19.5, 12.4, 0.8, 1.1, 1)
    s.dot(20, 12, 7)
    s.ellipse(6.5, 12.9, 6.5, 6.4, 1)
    s.ellipse(6.5, 12.7, 5.5, 5.4, 4)
    s.ellipse(6.5, 12.7, 4.2, 4.3, 2)
    s.polygon([(6, 9), (9, 11), (9, 15), (6, 17), (3, 15), (3, 11)], 3)
    s.line(6, 9, 6, 17, 4)
    s.line(3, 11, 9, 15, 4)
    s.line(9, 11, 3, 15, 4)
    s.dot(17, 15, 6)
    return s


def owl():
    s = Sprite(24, [
        "FFEDF0FF", "FF383A59", "FF90678B", "FFC49AA4",
        "FFF8E6C0", "FFFFC96B", "FFFFFFFF", "FF4B6474",
        "FFB7CAE9",
    ])
    s.rect(1, 20, 22, 21, 7)
    s.rect(6, 19, 8, 22, 7)
    s.rect(15, 19, 17, 22, 7)
    s.polygon([(4, 9), (5, 2), (11, 6), (17, 2), (19, 9)], 1)
    s.polygon([(5, 10), (6, 5), (11, 8), (17, 5), (18, 10)], 2)
    s.ellipse(11.5, 13, 8.0, 8.0, 1)
    s.ellipse(11.5, 12.7, 7.0, 7.0, 2)
    s.ellipse(11.5, 16, 4.5, 3.8, 3)
    s.ellipse(8, 11.5, 3.4, 3.6, 1)
    s.ellipse(15, 11.5, 3.4, 3.6, 1)
    s.ellipse(8, 11.4, 2.6, 2.8, 6)
    s.ellipse(15, 11.4, 2.6, 2.8, 6)
    s.ellipse(8.3, 11.8, 1.2, 1.5, 1)
    s.ellipse(14.7, 11.8, 1.2, 1.5, 1)
    s.dot(8, 11, 6)
    s.dot(15, 11, 6)
    s.polygon([(10, 14), (13, 14), (12, 16)], 5)
    s.line(9, 20, 9, 21, 5)
    s.line(14, 20, 14, 21, 5)
    s.dot(1, 4, 8)
    s.dot(21, 6, 8)
    return s


def ice_cream():
    s = Sprite(16, [
        "FFEEF8FF", "FF73526A", "FFC88B51", "FFFFDFA6",
        "FFFF96B4", "FFF7CAE0", "FFFDF4E8", "FF7AB9CF",
    ])
    s.dot(2, 3, 7)
    s.dot(13, 9, 7)
    s.polygon([(4, 8), (12, 8), (8, 15)], 1)
    s.polygon([(5, 9), (11, 9), (8, 14)], 2)
    s.line(6, 10, 9, 13, 3)
    s.line(10, 10, 7, 13, 3)
    s.ellipse(8, 7.5, 5.2, 2.1, 1)
    s.ellipse(8, 7, 4.5, 2.1, 4)
    s.ellipse(8, 5, 4.4, 3.6, 1)
    s.ellipse(8, 5, 3.7, 3, 5)
    s.ellipse(7, 4, 2.1, 1.8, 6)
    s.dot(10, 4, 4)
    s.dot(5, 6, 4)
    return s


def donut():
    s = Sprite(24, [
        "FFFFF9F2", "FF704E4D", "FFD8A46C", "FFF29AC2",
        "FFFFD6E7", "FF87BCB1", "FFFFD771", "FF996AD3",
        "FFE5C9A7",
    ])
    s.ellipse(11.5, 12, 9, 8.5, 1)
    s.ellipse(11.5, 12, 8.0, 7.5, 2)
    s.ellipse(11.5, 10.8, 7.5, 6.3, 3)
    s.ellipse(11.5, 13, 7.5, 5.5, 4)
    s.ellipse(11.5, 12, 6.5, 5.5, 3)
    s.ellipse(11.5, 12, 3.5, 3.5, 1)
    s.ellipse(11.5, 12, 2.6, 2.6, 0)
    for x, y, color in [
        (6, 10, 5), (9, 7, 6), (14, 7, 7), (17, 10, 5),
        (7, 15, 6), (11, 18, 7), (16, 15, 6), (14, 5, 5),
    ]:
        s.dot(x, y, color)
        s.dot(x + 1, y, color)
    return s


def coffee():
    s = Sprite(24, [
        "FFF7F2EA", "FF594B55", "FFFAE4CB", "FFC69E82",
        "FF89644F", "FFFFFFFF", "FFD4AAA6", "FF9EC5B1",
    ])
    s.line(8, 3, 7, 6, 6)
    s.line(12, 2, 11, 6, 6)
    s.line(16, 3, 15, 6, 6)
    s.ellipse(11.5, 20.0, 10, 2.1, 1)
    s.ellipse(11.5, 19.8, 9, 1.3, 5)
    s.ellipse(18, 12, 4.5, 4.7, 1)
    s.ellipse(18, 12, 3.5, 3.6, 2)
    s.ellipse(18, 12, 1.5, 1.8, 0)
    s.rect(4, 9, 17, 17, 1)
    s.rect(5, 9, 16, 16, 2)
    s.ellipse(10.5, 9, 6.5, 2.1, 1)
    s.ellipse(10.5, 9, 5.6, 1.2, 4)
    s.rect(6, 13, 15, 14, 3)
    s.ellipse(10.5, 14, 2, 1.2, 5)
    s.rect(6, 17, 15, 18, 1)
    s.rect(7, 17, 14, 17, 3)
    return s


def cactus():
    s = Sprite(24, [
        "FFFFF4DB", "FF55695C", "FF438D70", "FF79B88D",
        "FFC87255", "FFF0A777", "FFFFD36C", "FFF8E7C6",
    ])
    s.rect(2, 20, 21, 21, 7)
    s.polygon([(6, 14), (18, 14), (16, 21), (8, 21)], 1)
    s.polygon([(7, 15), (17, 15), (15, 20), (9, 20)], 4)
    s.rect(6, 14, 18, 16, 1)
    s.rect(7, 14, 17, 15, 5)
    s.ellipse(12, 10, 4.5, 7.4, 1)
    s.ellipse(12, 10, 3.5, 6.5, 2)
    s.rect(11, 5, 12, 14, 3)
    s.ellipse(5, 11, 2.2, 4, 1)
    s.ellipse(5, 11, 1.3, 3.1, 2)
    s.rect(6, 12, 10, 14, 1)
    s.rect(7, 12, 10, 13, 2)
    s.ellipse(19, 10, 2.2, 4, 1)
    s.ellipse(19, 10, 1.4, 3.1, 2)
    s.rect(15, 11, 18, 13, 1)
    s.rect(15, 11, 17, 12, 2)
    s.dot(11, 3, 6)
    s.dot(13, 3, 6)
    s.dot(12, 2, 6)
    return s


def autumn_tree():
    s = Sprite(32, [
        "FFF1F8FF", "FF775142", "FFAB7248", "FFFFC65C",
        "FFF18A4D", "FFD85652", "FFFFE29C", "FF8DAE7E",
        "FF9CC7DA", "FFF9F2E4",
    ])
    s.ellipse(16, 29, 14, 2.2, 7)
    s.ellipse(6, 29, 2, 1.1, 8)
    s.rect(13, 16, 18, 28, 1)
    s.rect(15, 18, 17, 27, 2)
    s.line(15, 20, 9, 14, 1, radius=1.1)
    s.line(17, 20, 23, 13, 1, radius=1.1)
    for cx, cy, rx, ry, shade in [
        (9, 14, 7, 6.5, 4), (22, 14, 7, 6.5, 5),
        (16, 9, 8, 7, 3), (9, 10, 6, 5, 5),
        (23, 10, 6, 5, 4), (16, 15, 9, 7, 3),
        (6, 16, 3, 3, 4), (26, 17, 3, 3, 5),
    ]:
        s.ellipse(cx, cy, rx + .8, ry + .8, 1)
        s.ellipse(cx, cy, rx, ry, shade)
    for cx, cy in [(10, 8), (20, 7), (6, 13), (25, 12), (14, 16)]:
        s.ellipse(cx, cy, 2.2, 1.4, 6)
    for x, y, col in [(5, 26, 4), (10, 30, 5), (24, 28, 3), (28, 24, 4)]:
        s.dot(x, y, col)
        s.dot(x+1, y, col)
    return s


def rain_cloud():
    s = Sprite(24, [
        "FFE9F6FF", "FF637CA2", "FFFFFFFF", "FFCCDFF0",
        "FF66B7E6", "FF9BD6F0", "FFFFD66F", "FF8CAAB4",
    ])
    s.ellipse(4, 4, 1.5, 1.5, 6)
    s.ellipse(20, 5, 1.5, 1.5, 6)
    for cx, cy, rx, ry in [(6, 11, 4, 3), (11, 8, 5, 4.6), (16, 10, 5, 3.5)]:
        s.ellipse(cx, cy, rx+.7, ry+.7, 1)
        s.ellipse(cx, cy, rx, ry, 3)
    s.rect(4, 11, 19, 14, 1)
    s.rect(5, 11, 18, 13, 2)
    s.ellipse(10, 8, 3.0, 2, 2)
    for x, y in [(6, 17), (11, 18), (16, 17), (8, 21), (19, 20)]:
        s.line(x, y, x - 1, y + 2, 4, radius=0.6)
        s.dot(x - 1, y + 1, 5)
    return s


def saturn():
    s = Sprite(32, [
        "FF16213F", "FFABB5DA", "FF405E92", "FFFFD9A0",
        "FFE4A26A", "FFAA6E80", "FFFCE8B7", "FF6885C7",
        "FFFDFBF6",
    ])
    for x, y in [(3,4), (28,4), (5,23), (26,27), (18,3),
                 (3,15), (27,14), (12,27), (9,2)]:
        s.dot(x, y, 8)
    for x, y in [(5,6), (26,6), (24,29)]:
        s.dot(x, y, 7)
    s.line(3, 22, 28, 9, 1, radius=2.5)
    s.line(3, 22, 28, 9, 6, radius=1.3)
    s.ellipse(16, 16, 9.8, 9.8, 1)
    s.ellipse(16, 16, 8.8, 8.8, 3)
    s.rect(9, 14, 23, 16, 4)
    s.rect(11, 19, 21, 20, 4)
    s.ellipse(16, 16, 6.5, 6.5, 3)
    s.rect(10, 14, 22, 15, 4)
    s.rect(11, 19, 21, 20, 4)
    s.ellipse(13, 11, 3, 1.6, 6)
    s.line(4, 25, 28, 12, 1, radius=2)
    s.line(4, 25, 28, 12, 6, radius=0.9)
    return s


def astronaut():
    s = Sprite(32, [
        "FF1B2949", "FF394E74", "FF697E9C", "FFF6F8FB",
        "FFD9E4F1", "FF73C6DC", "FF2B638D", "FFF59E65",
        "FFF9DA76", "FFFFFFFF",
    ])
    for x, y in [(4,5), (27,7), (25,25), (3,26), (16,3),
                 (9,28), (28,18), (5,17), (22,4)]:
        s.dot(x, y, 8)
    s.rect(7, 13, 10, 23, 2)
    s.rect(21, 13, 24, 23, 2)
    s.ellipse(16, 22, 9.0, 8.0, 1)
    s.rect(11, 16, 21, 25, 3)
    s.rect(11, 22, 20, 25, 4)
    s.rect(10, 24, 15, 28, 1)
    s.rect(17, 24, 22, 28, 1)
    s.rect(10, 25, 14, 28, 3)
    s.rect(18, 25, 21, 28, 3)
    s.rect(9, 27, 15, 29, 2)
    s.rect(17, 27, 23, 29, 2)
    s.rect(8, 17, 10, 22, 3)
    s.rect(22, 17, 24, 22, 3)
    s.ellipse(8, 22, 2.5, 2, 1)
    s.ellipse(24, 22, 2.5, 2, 1)
    s.ellipse(8, 22, 1.6, 1.2, 3)
    s.ellipse(24, 22, 1.6, 1.2, 3)
    s.ellipse(16, 11, 9.0, 9.2, 1)
    s.ellipse(16, 11, 8.0, 8.1, 3)
    s.ellipse(16, 11.2, 6.2, 5.8, 1)
    s.ellipse(16, 11.2, 5.4, 5.0, 6)
    s.ellipse(13.5, 8.5, 2.0, 2.1, 5)
    s.rect(13, 19, 19, 23, 1)
    s.rect(14, 20, 18, 22, 2)
    s.dot(15, 20, 7)
    s.dot(18, 20, 5)
    s.dot(15, 22, 8)
    return s


PICTURES = [
    ("online-panda", "پاندای بامزه", "Cute Panda", "animals", panda),
    ("online-bunny", "خرگوش سفید", "White Bunny", "animals", bunny),
    ("online-turtle", "لاک‌پشت سبز", "Green Turtle", "animals", turtle),
    ("online-owl", "جغد کوچک", "Little Owl", "animals", owl),
    ("online-ice-cream", "بستنی توت‌فرنگی", "Strawberry Ice Cream", "objects", ice_cream),
    ("online-donut", "دونات صورتی", "Pink Donut", "objects", donut),
    ("online-coffee", "فنجان قهوه", "Coffee Cup", "objects", coffee),
    ("online-cactus", "کاکتوس گلدانی", "Potted Cactus", "nature", cactus),
    ("online-autumn-tree", "درخت پاییزی", "Autumn Tree", "nature", autumn_tree),
    ("online-rain-cloud", "ابر بارانی", "Rain Cloud", "nature", rain_cloud),
    ("online-saturn", "سیاره زحل", "Planet Saturn", "space", saturn),
    ("online-astronaut", "فضانورد", "Astronaut", "space", astronaut),
]


def create_pack(destination):
    manifest = []
    files = {}
    for ident, title_fa, title_en, category, painter in PICTURES:
        sprite = painter()
        level = {
            "schemaVersion": 2,
            "levelId": ident,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": sprite.side,
            "height": sprite.side,
            "palette": sprite.palette,
            "cells": sprite.cells,
        }
        level["checksum"] = checksum(level)
        body = compact(level)
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1, "title": title_fa,
            "titleEn": title_en, "category": category,
            "width": sprite.side, "height": sprite.side,
            "bytes": len(body), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = body
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, payload in files.items():
            archive.writestr(name, payload)
    print(f"Created collection of {len(manifest)} original levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_collection_pack.py <content.zip>")
    create_pack(sys.argv[1])
