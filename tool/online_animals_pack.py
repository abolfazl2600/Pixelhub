#!/usr/bin/env python3
"""Create ten original animal pixel-art levels for PixelHub online Releases.

The source contains drawing instructions, not bundled assets. On a successful
main-branch Web CI run, the Pages workflow publishes a new immutable Release
containing the numbered JSON levels, PNG previews, and catalog.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


def lion():
    s = Sprite(32, [
        "FFFFF5E6", "FF5A3B38", "FFB96739", "FFE49B46",
        "FFF3C66C", "FFFFDFA0", "FFFFECD1", "FF70434A",
        "FFE69A91", "FF8BA985",
    ])
    s.ellipse(4, 28, 2.5, 1.3, 9)
    s.ellipse(27, 28, 2.5, 1.3, 9)
    for x, y, rx, ry in [
        (9, 8, 6, 6), (23, 8, 6, 6), (6, 16, 5, 7),
        (26, 16, 5, 7), (10, 24, 7, 6), (22, 24, 7, 6),
        (16, 6, 8, 5), (16, 19, 13, 11),
    ]:
        s.ellipse(x, y, rx, ry, 1)
        s.ellipse(x, y, rx - 1, ry - 1, 2)
    s.ellipse(16, 16, 10.8, 12, 3)
    s.ellipse(9, 11, 3.8, 4.0, 1)
    s.ellipse(23, 11, 3.8, 4.0, 1)
    s.ellipse(9, 11, 2.6, 2.9, 8)
    s.ellipse(23, 11, 2.6, 2.9, 8)
    s.ellipse(16, 16.5, 9.0, 10.0, 1)
    s.ellipse(16, 16, 8.0, 9.0, 4)
    s.ellipse(16, 13, 6.1, 4.4, 5)
    s.ellipse(12, 16, 1.5, 2.1, 1)
    s.ellipse(20, 16, 1.5, 2.1, 1)
    s.dot(12, 15, 6)
    s.dot(20, 15, 6)
    s.ellipse(12.5, 22, 4.1, 3.4, 6)
    s.ellipse(19.5, 22, 4.1, 3.4, 6)
    s.polygon([(13, 20), (19, 20), (16, 23)], 7)
    s.line(16, 23, 16, 25, 1)
    s.line(16, 25, 13, 26, 1)
    s.line(16, 25, 19, 26, 1)
    for x, y in [(9, 22), (10, 24), (22, 22), (21, 24)]:
        s.dot(x, y, 7)
    return s


def elephant():
    s = Sprite(32, [
        "FFEAF8F4", "FF425D6D", "FF829EB5", "FFAEC2D0",
        "FFE9AAB2", "FFDFEBED", "FF273F51", "FF8BB79B",
        "FFFFF7DB",
    ])
    s.ellipse(6, 28, 5, 1.6, 7)
    s.ellipse(23, 29, 7, 1.5, 7)
    s.rect(8, 20, 12, 27, 1)
    s.rect(9, 20, 11, 26, 2)
    s.rect(18, 20, 23, 27, 1)
    s.rect(19, 20, 22, 26, 2)
    s.ellipse(13, 19, 10.5, 8.5, 1)
    s.ellipse(13, 18, 9.5, 7.5, 2)
    s.ellipse(21, 13, 8.2, 8.5, 1)
    s.ellipse(21, 12.5, 7.3, 7.6, 3)
    s.line(27, 15, 27, 23, 1, radius=3)
    s.line(27, 15, 27, 23, 2, radius=2.1)
    s.line(27, 23, 24, 25, 1, radius=2.6)
    s.line(27, 23, 24, 24, 2, radius=1.6)
    s.ellipse(17, 15, 6.4, 6.9, 1)
    s.ellipse(16.7, 15, 5.5, 5.8, 4)
    s.ellipse(15, 13, 2.6, 2.7, 3)
    s.ellipse(24, 11, 1.3, 1.6, 6)
    s.dot(24, 10, 8)
    s.polygon([(23, 18), (26, 18), (24, 21)], 8)
    s.line(8, 18, 7, 21, 3)
    return s


def giraffe():
    s = Sprite(32, [
        "FFF0F9FF", "FF66504B", "FFF2B34E", "FFFFD775",
        "FFB87A43", "FFDF966B", "FFFFF5D2", "FF97C4A0",
        "FF41444F",
    ])
    s.rect(0, 29, 31, 31, 7)
    for x0, x1 in [(7, 10), (15, 18)]:
        s.rect(x0, 22, x1, 28, 1)
        s.rect(x0 + 1, 22, x1 - 1, 27, 2)
        s.rect(x0, 28, x1, 29, 4)
    s.ellipse(12, 22, 10.0, 6.4, 1)
    s.ellipse(12, 21.5, 9.0, 5.3, 2)
    s.rect(17, 8, 22, 22, 1)
    s.rect(18, 8, 21, 22, 2)
    s.line(22, 11, 22, 20, 3, radius=0.8)
    s.ellipse(18.5, 8, 4.2, 3.0, 1)
    s.ellipse(18.5, 8, 3.1, 2.0, 2)
    s.ellipse(23.5, 10, 4.7, 3.0, 1)
    s.ellipse(23.5, 10, 3.8, 2.0, 3)
    s.polygon([(16, 7), (13, 4), (18, 5)], 1)
    s.polygon([(16, 6), (14, 4), (17, 5)], 5)
    s.polygon([(22, 7), (25, 4), (25, 8)], 1)
    s.polygon([(23, 6), (24, 5), (24, 7)], 5)
    for x in (17, 21):
        s.line(x, 6, x, 3, 1, radius=0.8)
        s.ellipse(x, 2, 1.6, 1.5, 4)
    s.ellipse(20, 9, 1.0, 1.2, 8)
    s.dot(20, 8, 6)
    s.dot(26, 11, 8)
    for x, y, rx, ry in [
        (7, 20, 2.4, 2), (13, 24, 2.2, 1.8),
        (16, 19, 1.8, 2), (20, 15, 1.3, 2), (19, 10, 1, 1),
    ]:
        s.ellipse(x, y, rx, ry, 4)
    s.line(4, 22, 2, 16, 1)
    s.dot(2, 16, 4)
    return s


def penguin():
    s = Sprite(24, [
        "FFE8F5FF", "FF344B60", "FF283749", "FFFFFFFF",
        "FFD9EDF6", "FFFFB55F", "FFFFD683", "FF83BBD2",
        "FFF7CAD0",
    ])
    s.rect(0, 21, 23, 23, 4)
    s.ellipse(4, 20, 3, 1.2, 7)
    s.ellipse(19, 21, 3, 1.2, 7)
    s.polygon([(6, 11), (1, 15), (5, 19), (8, 17)], 1)
    s.polygon([(18, 11), (22, 15), (19, 19), (16, 17)], 1)
    s.ellipse(11.5, 12.5, 7.7, 9.2, 1)
    s.ellipse(11.5, 12.5, 6.8, 8.3, 2)
    s.ellipse(11.5, 16.0, 5.5, 5.2, 3)
    s.ellipse(8.5, 9.4, 2.8, 3.3, 3)
    s.ellipse(14.5, 9.4, 2.8, 3.3, 3)
    s.ellipse(8.5, 9.2, 1.0, 1.4, 2)
    s.ellipse(14.5, 9.2, 1.0, 1.4, 2)
    s.dot(8, 9, 3)
    s.dot(14, 9, 3)
    s.polygon([(9, 12), (15, 12), (12, 16)], 5)
    s.polygon([(10, 12), (14, 12), (12, 14)], 6)
    s.ellipse(8, 21, 3, 1.3, 5)
    s.ellipse(16, 21, 3, 1.3, 5)
    s.dot(3, 4, 3)
    s.dot(20, 5, 3)
    return s


def dolphin():
    s = Sprite(32, [
        "FFE5F7FF", "FF34647D", "FF499AB7", "FF80C6D8",
        "FFCEEEF1", "FF267DA2", "FFFFFFFF", "FFFFD67D",
        "FF81CBD9",
    ])
    s.rect(0, 26, 31, 31, 5)
    s.line(0, 25, 31, 25, 3)
    s.ellipse(27, 5, 2.8, 2.8, 7)
    s.polygon([(4, 17), (9, 13), (17, 10), (24, 11),
               (28, 13), (30, 14), (27, 16), (22, 16),
               (15, 20), (9, 21)], 1)
    s.polygon([(5, 17), (10, 14), (17, 11), (24, 12),
               (28, 14), (22, 15), (15, 19), (10, 20)], 2)
    s.polygon([(15, 12), (18, 4), (21, 11)], 1)
    s.polygon([(16, 11), (18, 6), (20, 11)], 2)
    s.polygon([(10, 17), (15, 18), (18, 24), (13, 21)], 1)
    s.polygon([(11, 18), (15, 19), (17, 22)], 3)
    s.polygon([(6, 16), (1, 9), (4, 18), (1, 24), (9, 20)], 1)
    s.polygon([(5, 15), (2, 12), (5, 18), (2, 22), (8, 19)], 2)
    s.polygon([(15, 18), (21, 15), (27, 15), (21, 18)], 4)
    s.ellipse(25, 13, 0.9, 0.9, 1)
    s.dot(25, 12, 6)
    s.line(27, 15, 29, 15, 1)
    for x, y in [(6, 26), (11, 24), (20, 25), (26, 23)]:
        s.dot(x, y, 6)
        s.dot(x + 1, y - 1, 8)
    return s


def koala():
    s = Sprite(24, [
        "FFEAF7ED", "FF465960", "FF8A9BA2", "FFC2CCD0",
        "FFF3C5D1", "FFFEFAEC", "FF34424C", "FF7CAC88",
        "FFDFE9E7",
    ])
    s.ellipse(2, 21, 2.6, 1.1, 7)
    s.ellipse(21, 20, 2.6, 1.1, 7)
    s.ellipse(4.5, 8, 4.5, 5, 1)
    s.ellipse(18.5, 8, 4.5, 5, 1)
    s.ellipse(4.5, 8, 3.5, 4.1, 2)
    s.ellipse(18.5, 8, 3.5, 4.1, 2)
    s.ellipse(4.5, 8, 2.4, 3, 4)
    s.ellipse(18.5, 8, 2.4, 3, 4)
    s.ellipse(11.5, 13, 8.2, 8.2, 1)
    s.ellipse(11.5, 13, 7.2, 7.2, 2)
    s.ellipse(11.5, 15, 5.8, 5, 3)
    s.ellipse(8.4, 12.5, 1.4, 1.7, 6)
    s.ellipse(14.6, 12.5, 1.4, 1.7, 6)
    s.dot(8, 12, 5)
    s.dot(14, 12, 5)
    s.ellipse(11.5, 15.5, 2.5, 3.8, 1)
    s.ellipse(11.5, 15.3, 1.7, 3.0, 6)
    s.line(10, 19, 13, 19, 1)
    s.ellipse(6, 17, 1.5, 1.0, 4)
    s.ellipse(17, 17, 1.5, 1.0, 4)
    s.ellipse(11.5, 3.5, 3.5, 1.3, 8)
    return s


def flamingo():
    s = Sprite(32, [
        "FFEDF9F3", "FF6B5C6C", "FFE982A2", "FFF5ADBD",
        "FFFFD6D3", "FFBD5A83", "FFFFF8E8", "FF91C4BD",
        "FF547D84",
    ])
    s.rect(0, 27, 31, 31, 7)
    s.line(0, 27, 31, 27, 8, radius=0.5)
    s.ellipse(19, 19, 9, 5.5, 1)
    s.ellipse(19, 18.5, 8, 4.5, 2)
    s.ellipse(16, 19, 4.8, 3.2, 3)
    s.polygon([(11, 17), (5, 12), (9, 21), (13, 22)], 5)
    s.polygon([(10, 18), (7, 15), (10, 20)], 3)
    s.line(23, 16, 25, 10, 1, radius=2.7)
    s.line(25, 10, 22, 6, 1, radius=2.7)
    s.line(23, 16, 25, 10, 3, radius=1.7)
    s.line(25, 10, 22, 6, 3, radius=1.7)
    s.ellipse(20.5, 6.5, 4.5, 3.5, 1)
    s.ellipse(20.5, 6.3, 3.5, 2.5, 2)
    s.polygon([(17, 7), (12, 8), (13, 11), (15, 10), (18, 9)], 1)
    s.polygon([(17, 7), (13, 8), (14, 9), (18, 8)], 6)
    s.dot(20, 6, 1)
    s.line(17, 22, 17, 29, 1, radius=0.7)
    s.line(22, 22, 22, 26, 1, radius=0.7)
    s.line(22, 26, 18, 28, 1, radius=0.7)
    s.line(15, 29, 19, 29, 1)
    s.line(17, 28, 20, 29, 1)
    for x, y in [(3, 25), (26, 27), (29, 25)]:
        s.dot(x, y, 6)
    return s


def octopus():
    s = Sprite(32, [
        "FFE4F9F8", "FF385B7A", "FF985ECC", "FFC596E8",
        "FFF1D6FF", "FFEF96AC", "FFFFFFFF", "FF61BDBB",
        "FF9DDCD4",
    ])
    s.rect(0, 28, 31, 31, 8)
    s.line(3, 30, 7, 25, 7, radius=1.2)
    s.line(28, 30, 25, 24, 7, radius=1.2)
    for pts in [
        [(10, 19), (5, 20), (3, 25), (5, 27)],
        [(12, 20), (8, 25), (9, 29)],
        [(14, 21), (13, 27), (15, 29)],
        [(18, 21), (18, 27), (20, 29)],
        [(20, 20), (24, 25), (23, 29)],
        [(22, 19), (27, 20), (29, 25), (27, 27)],
    ]:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            s.line(x0, y0, x1, y1, 1, radius=2.1)
            s.line(x0, y0, x1, y1, 2, radius=1.2)
    s.ellipse(16, 13.3, 10, 10.5, 1)
    s.ellipse(16, 13, 9, 9.4, 2)
    s.ellipse(12, 8, 4, 2, 3)
    s.ellipse(12, 16, 1.5, 2, 1)
    s.ellipse(20, 16, 1.5, 2, 1)
    s.dot(12, 15, 6)
    s.dot(20, 15, 6)
    s.ellipse(9, 19, 2.2, 1.5, 5)
    s.ellipse(23, 19, 2.2, 1.5, 5)
    s.line(14, 20, 18, 20, 1)
    for x, y in [(5, 24), (9, 27), (14, 27), (19, 27), (23, 26), (28, 24)]:
        s.dot(x, y, 4)
    for x, y in [(4, 5), (6, 2), (27, 4), (29, 10)]:
        s.ellipse(x, y, 1.5, 1.5, 6)
        s.dot(x, y, 8)
    return s


def deer():
    s = Sprite(32, [
        "FFF9F4E9", "FF5B4646", "FFBD8054", "FFE0A16A",
        "FFF6CA90", "FFFFF0D6", "FF503D3F", "FFDA918D",
        "FF94B298",
    ])
    s.ellipse(3, 28, 3, 1.2, 8)
    s.ellipse(28, 28, 3, 1.2, 8)
    for side in (-1, 1):
        x = 16 + side * 6
        tip = 16 + side * 11
        s.line(x, 12, tip, 2, 1, radius=0.9)
        s.line(16 + side * 9, 7, 16 + side * 7, 2, 1, radius=0.8)
        s.line(16 + side * 8, 8, 16 + side * 12, 6, 1, radius=0.8)
    s.polygon([(10, 13), (3, 7), (5, 16), (11, 19)], 1)
    s.polygon([(22, 13), (29, 7), (27, 16), (21, 19)], 1)
    s.polygon([(9, 13), (5, 10), (6, 15), (11, 17)], 7)
    s.polygon([(23, 13), (27, 10), (26, 15), (21, 17)], 7)
    s.ellipse(16, 20, 9.3, 11.0, 1)
    s.ellipse(16, 19.5, 8.2, 10, 2)
    s.ellipse(16, 24, 5.5, 6, 4)
    s.ellipse(16, 25, 4.3, 4.2, 5)
    for x, y in [(10, 17), (11, 20), (22, 17), (21, 20)]:
        s.dot(x, y, 5)
    s.ellipse(12.4, 18.5, 1.2, 1.6, 6)
    s.ellipse(19.6, 18.5, 1.2, 1.6, 6)
    s.dot(12, 18, 5)
    s.dot(20, 18, 5)
    s.ellipse(16, 25, 2.4, 1.5, 6)
    s.ellipse(16, 24.5, 1.5, 0.9, 1)
    s.line(16, 26, 16, 27, 1)
    s.line(16, 27, 14, 28, 1)
    s.line(16, 27, 18, 28, 1)
    return s


def parrot():
    s = Sprite(32, [
        "FFE7FAEF", "FF344E4D", "FF4EAB70", "FF90D47A",
        "FF3E93C3", "FFFFC654", "FFF47C66", "FFFFFFFF",
        "FF9E744D", "FFB8E8CF",
    ])
    s.line(2, 27, 29, 25, 8, radius=1.7)
    s.line(2, 26, 28, 24, 1, radius=0.5)
    s.polygon([(10, 17), (6, 30), (11, 27), (14, 18)], 1)
    s.polygon([(11, 18), (7, 29), (12, 26), (15, 19)], 4)
    s.polygon([(15, 20), (13, 30), (18, 27), (19, 21)], 1)
    s.polygon([(16, 20), (14, 29), (17, 26), (18, 22)], 5)
    s.ellipse(18, 17, 8.7, 10, 1)
    s.ellipse(18, 17, 7.5, 9.0, 2)
    s.ellipse(16, 17, 5.4, 7.0, 4)
    s.ellipse(16, 18, 3.8, 5.5, 3)
    s.ellipse(22, 9, 5.4, 5.6, 1)
    s.ellipse(22, 9, 4.5, 4.5, 3)
    s.ellipse(22, 8, 3.4, 3.1, 5)
    s.polygon([(18, 6), (17, 2), (21, 5), (22, 1), (24, 6)], 2)
    s.polygon([(24, 11), (31, 11), (28, 16), (24, 14)], 1)
    s.polygon([(25, 12), (30, 12), (27, 15), (25, 14)], 5)
    s.ellipse(23, 8, 1.2, 1.5, 1)
    s.dot(23, 7, 7)
    s.line(17, 24, 16, 26, 1, radius=0.7)
    s.line(21, 24, 20, 26, 1, radius=0.7)
    s.dot(15, 26, 1)
    s.dot(19, 26, 1)
    s.ellipse(5, 6, 3.5, 2, 9)
    s.ellipse(6, 10, 2, 4, 3)
    s.ellipse(28, 20, 2.5, 4, 3)
    return s


PICTURES = [
    ("online-lion", "شیر طلایی", "Golden Lion", lion),
    ("online-elephant", "فیل مهربان", "Gentle Elephant", elephant),
    ("online-giraffe", "زرافه خال‌دار", "Spotted Giraffe", giraffe),
    ("online-penguin", "پنگوئن برفی", "Snowy Penguin", penguin),
    ("online-dolphin", "دلفین بازیگوش", "Playful Dolphin", dolphin),
    ("online-koala", "کوآلای خواب‌آلود", "Sleepy Koala", koala),
    ("online-flamingo", "فلامینگوی صورتی", "Pink Flamingo", flamingo),
    ("online-octopus", "اختاپوس بنفش", "Purple Octopus", octopus),
    ("online-deer", "گوزن جنگلی", "Forest Deer", deer),
    ("online-parrot", "طوطی رنگارنگ", "Colorful Parrot", parrot),
]


def create_pack(destination):
    manifest = []
    files = {}
    for ident, title_fa, title_en, painter in PICTURES:
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
            "titleEn": title_en, "category": "animals",
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
    print(f"Created {len(manifest)} original animal levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_animals_pack.py <content.zip>")
    create_pack(sys.argv[1])
