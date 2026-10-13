#!/usr/bin/env python3
"""Ten original pixel-art interpretations of landmark buildings in Iran.

Only hand-authored drawing instructions are tracked in Git. A successful main
Web CI run creates a release-only ZIP of downloadable schema-v2 painting grids,
PNG previews and bilingual catalog data. Existing published IDs are untouched.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


def pointed_arch(s, cx, top, bottom, half, rim, inside, thickness=2):
    """Fill a pointed Persian-style arch with a substantial visible border."""
    s.polygon([
        (cx-half, bottom), (cx-half, top+half//2),
        (cx, top), (cx+half, top+half//2), (cx+half, bottom),
    ], rim)
    inner = max(1, half-thickness)
    s.polygon([
        (cx-inner, bottom), (cx-inner, top+half//2+thickness),
        (cx, top+thickness*2), (cx+inner, top+half//2+thickness),
        (cx+inner, bottom),
    ], inside)


def crenels(s, start, stop, y, color, width=3, gap=2):
    for x in range(start, stop, width+gap):
        s.rect(x, y, min(stop-1, x+width-1), y+2, color)


def persepolis():
    s = Sprite(48, [
        "FFE8F5FF", "FF64554E", "FFAE896B", "FFDDC09A",
        "FFF5DCB6", "FF8F7968", "FFE6A76A", "FF94B9C1",
        "FFB5C99A", "FFFAEBD7",
    ])
    s.ellipse(41, 7, 3, 3, 6)
    s.polygon([(0, 34), (8, 30), (18, 34), (30, 28), (48, 35), (48, 48), (0, 48)], 7)
    s.rect(0, 37, 47, 47, 8)
    s.rect(1, 35, 46, 41, 1)
    s.rect(1, 36, 46, 39, 3)
    s.rect(3, 40, 44, 42, 2)
    s.rect(7, 43, 40, 44, 3)
    for x in [5, 16, 27, 38]:
        s.rect(x-4, 34, x+4, 36, 1)
        s.rect(x-3, 33, x+3, 35, 2)
        s.rect(x-2, 14, x+2, 33, 1)
        s.rect(x-1, 14, x+1, 32, 3)
        for y in range(16, 33, 3):
            s.rect(x-1, y, x-1, y+1, 4)
        s.rect(x-4, 12, x+4, 14, 1)
        s.rect(x-3, 11, x+3, 12, 3)
        s.polygon([(x-6, 10), (x-5, 7), (x-2, 8), (x, 10)], 2)
        s.polygon([(x+6, 10), (x+5, 7), (x+2, 8), (x, 10)], 2)
        s.dot(x-5, 8, 1)
        s.dot(x+5, 8, 1)
    s.rect(0, 10, 43, 12, 1)
    s.rect(1, 10, 42, 10, 4)
    for x in range(3, 44, 6):
        s.dot(x, 11, 6)
    for x in range(3, 45, 7):
        s.rect(x, 37, x+2, 38, 5)
    s.rect(3, 45, 44, 46, 1)
    return s


def azadi_tower():
    s = Sprite(48, [
        "FFE1F3FC", "FF566E80", "FFCBD5D9", "FFF5F2E7",
        "FF91B4C3", "FF83AAB2", "FF617E82", "FF98C8A9",
        "FFFCDE9F",
    ])
    s.ellipse(40, 7, 4, 4, 8)
    s.rect(0, 41, 47, 47, 7)
    s.rect(0, 43, 47, 44, 5)
    s.polygon([
        (18, 8), (30, 8), (33, 14), (35, 22),
        (39, 35), (43, 40), (32, 40), (28, 31),
        (20, 31), (16, 40), (5, 40), (9, 35),
        (13, 22), (15, 14),
    ], 1)
    s.polygon([
        (19, 9), (29, 9), (32, 15), (34, 24),
        (39, 39), (33, 39), (29, 29), (19, 29),
        (15, 39), (9, 39), (14, 24), (16, 15),
    ], 2)
    s.polygon([
        (24, 14), (18, 23), (18, 30), (16, 38),
        (32, 38), (30, 30), (30, 23),
    ], 1)
    s.polygon([
        (24, 17), (20, 24), (20, 31), (18, 39),
        (30, 39), (28, 31), (28, 24),
    ], 0)
    s.rect(18, 7, 30, 9, 1)
    s.rect(19, 8, 29, 8, 3)
    s.rect(20, 10, 28, 11, 4)
    for y, xl, xr in [(14, 16, 32), (17, 15, 33), (21, 14, 34)]:
        s.line(xl, y, 21, y+4, 3)
        s.line(xr, y, 27, y+4, 3)
    for x in range(13, 36, 5):
        s.dot(x, 39, 4)
    s.rect(3, 41, 44, 42, 1)
    return s


def milad_tower():
    s = Sprite(48, [
        "FFE1F3FF", "FF496A86", "FFB5CAD7", "FFE9F1EF",
        "FF608DA6", "FF294F6A", "FFF9D19A", "FF8EBC9B",
        "FFDAA8A2",
    ])
    s.ellipse(8, 10, 4, 2, 3)
    s.ellipse(40, 15, 4, 2, 3)
    s.rect(0, 40, 47, 47, 7)
    for x, height in [(0, 35), (7, 37), (13, 34), (33, 37), (40, 33), (45, 36)]:
        s.rect(x, height, x+4, 42, 2)
        s.rect(x+1, height+2, x+1, height+4, 6)
    s.polygon([(20, 23), (28, 23), (26, 42), (22, 42)], 1)
    s.polygon([(22, 23), (26, 23), (25, 41), (23, 41)], 2)
    s.rect(23, 5, 25, 16, 1)
    s.rect(24, 2, 24, 14, 4)
    s.dot(24, 1, 6)
    s.polygon([(16, 17), (32, 17), (29, 22), (19, 22)], 1)
    s.polygon([(17, 17), (31, 17), (28, 21), (20, 21)], 4)
    s.rect(14, 15, 34, 17, 1)
    s.rect(16, 13, 32, 15, 2)
    s.rect(18, 12, 30, 13, 1)
    s.rect(21, 10, 27, 12, 3)
    for x in range(17, 33, 3):
        s.rect(x, 14, x+1, 15, 5)
        s.dot(x, 18, 6)
    s.rect(21, 23, 27, 24, 5)
    s.rect(20, 40, 28, 43, 1)
    s.rect(18, 43, 30, 44, 2)
    s.rect(0, 45, 47, 46, 5)
    return s


def imam_mosque():
    s = Sprite(48, [
        "FFE5F5FF", "FF1D556F", "FF338FA9", "FF74C2D0",
        "FFF5D8A1", "FFE8B777", "FF316CBA", "FFEEE8D9",
        "FF95CDA7", "FF1B3D68", "FFF9F7E8", "FF6BA5B0",
    ])
    s.ellipse(42, 6, 2.6, 2.6, 4)
    s.rect(0, 39, 47, 47, 8)
    for x in (7, 39):
        s.rect(x-3, 12, x+3, 39, 1)
        s.rect(x-2, 13, x+2, 38, 6)
        for y in range(15, 38, 5):
            s.rect(x-2, y, x+2, y+1, 3)
        s.rect(x-4, 11, x+4, 13, 4)
        s.rect(x-3, 8, x+3, 11, 2)
        s.polygon([(x-2, 8), (x, 5), (x+2, 8)], 1)
        s.dot(x, 4, 4)
    s.ellipse(24, 19, 12.5, 12.0, 1)
    s.ellipse(24, 19, 11.5, 11.0, 6)
    s.ellipse(24, 19, 10.2, 10.2, 2)
    for dx in (-7, -3, 1, 5):
        s.line(24+dx, 11, 24+dx+2, 23, 3, radius=0.7)
    s.rect(22, 6, 26, 8, 4)
    s.dot(24, 5, 1)
    s.rect(2, 29, 45, 41, 1)
    s.rect(3, 30, 44, 40, 5)
    s.rect(11, 23, 37, 42, 1)
    s.rect(12, 24, 36, 40, 6)
    s.rect(14, 25, 34, 39, 2)
    pointed_arch(s, 24, 27, 41, 8, 4, 9, 2)
    pointed_arch(s, 24, 32, 41, 4, 3, 9, 1)
    for x in (5, 43):
        pointed_arch(s, x, 33, 40, 3, 2, 9, 1)
    for x in range(14, 36, 4):
        s.dot(x, 25, 4)
    s.rect(21, 42, 27, 47, 3)
    s.rect(22, 43, 26, 47, 11)
    return s


def sio_se_pol():
    s = Sprite(48, [
        "FFE6F5FF", "FF6A6A66", "FFC3986E", "FFE6BD88",
        "FFFFD6A0", "FF558EAC", "FF7FC5D9", "FFB0DCEA",
        "FF94B9A0", "FF444A54",
    ])
    s.ellipse(41, 8, 4, 4, 4)
    s.rect(0, 36, 47, 47, 5)
    s.rect(0, 41, 47, 42, 6)
    for y in (39, 44):
        for x in range((y//2)%5, 48, 7):
            s.line(x, y, x+4, y, 7)
    s.rect(0, 21, 47, 36, 1)
    s.rect(0, 22, 47, 35, 2)
    s.rect(0, 19, 47, 22, 3)
    s.rect(0, 16, 47, 18, 1)
    s.rect(0, 17, 47, 17, 4)
    crenels(s, 0, 48, 14, 2, 4, 2)
    for x in range(2, 48, 6):
        pointed_arch(s, x+1, 24, 36, 2, 1, 9, 1)
        s.rect(x, 37, x+3, 38, 6)
        s.rect(x+1, 39, x+2, 41, 7)
    for x in range(2, 47, 6):
        pointed_arch(s, x+1, 18, 22, 2, 1, 9, 1)
    s.rect(0, 23, 47, 24, 4)
    for x in range(1, 48, 4):
        s.dot(x, 26, 3)
    return s


def nasir_ol_molk():
    s = Sprite(48, [
        "FF473C5D", "FF8A6582", "FFC89B8B", "FFFFE3B4",
        "FFE85C99", "FF5EAFD4", "FF99CA8C", "FFF8C761",
        "FF7349A8", "FFF9E8F2", "FF3E3155",
    ])
    s.rect(0, 0, 47, 47, 0)
    s.rect(0, 0, 47, 8, 1)
    s.rect(0, 9, 47, 33, 2)
    for x in (1, 17, 33):
        pointed_arch(s, x+7, 8, 35, 7, 10, 5, 2)
        for yy in range(17, 34, 4):
            for xx in range(x+2, x+13, 3):
                shade = [4, 5, 6, 7, 8][(xx//3 + yy//4)%5]
                s.rect(xx, yy, xx+2, yy+2, shade)
        s.rect(x+6, 17, x+7, 34, 10)
        s.rect(x+2, 25, x+12, 26, 10)
    for x in (0, 16, 32, 47):
        s.rect(x, 8, x+1, 38, 10)
        s.rect(x, 8, x+1, 12, 3)
    s.polygon([(0, 35), (47, 35), (47, 47), (0, 47)], 8)
    for y in range(36, 48, 3):
        s.line(0, y, 47, y, 4 if y%2 else 7)
    for x in range(2, 48, 5):
        s.line(x, 36, x-3, 47, 7)
        s.line(x+2, 36, x+6, 47, 5)
    for x in range(3, 47, 6):
        s.dot(x, 4, 7)
        s.dot(x+2, 6, 5)
    return s


def arg_e_bam():
    s = Sprite(48, [
        "FFFCEACD", "FF705B4E", "FFB37D54", "FFD3A06B",
        "FFEBC18A", "FFF9DCB0", "FF8B684F", "FFBD916D",
        "FF9EBAA0", "FF9D7355",
    ])
    s.ellipse(40, 8, 5, 5, 5)
    s.polygon([(0, 38), (12, 29), (20, 31), (31, 25),
               (47, 34), (47, 48), (0, 48)], 9)
    s.rect(0, 41, 47, 47, 3)
    s.polygon([(5, 29), (18, 26), (32, 26), (43, 30),
               (46, 42), (2, 42)], 1)
    s.polygon([(5, 30), (18, 27), (32, 27), (43, 31),
               (44, 41), (4, 41)], 2)
    crenels(s, 5, 44, 27, 3, 3, 2)
    s.rect(14, 19, 35, 29, 1)
    s.rect(15, 20, 34, 28, 3)
    crenels(s, 14, 36, 17, 3, 3, 1)
    s.rect(21, 10, 29, 20, 1)
    s.rect(22, 11, 28, 19, 4)
    crenels(s, 20, 31, 8, 2, 3, 1)
    s.rect(26, 5, 28, 8, 1)
    s.rect(27, 4, 27, 5, 4)
    for x in (9, 37):
        s.rect(x-3, 24, x+3, 34, 1)
        s.rect(x-2, 25, x+2, 33, 3)
        crenels(s, x-3, x+4, 22, 2, 2, 1)
    pointed_arch(s, 24, 31, 42, 5, 1, 6, 2)
    for x, y in [(7, 35), (15, 31), (33, 32), (40, 36), (17, 24), (31, 25)]:
        s.rect(x, y, x+2, y+1, 6)
    for x in range(5, 44, 5):
        s.dot(x, 44, 7)
    return s


def hafez_tomb():
    s = Sprite(48, [
        "FFF4EDEB", "FF4A686C", "FF45999C", "FF86C5BF",
        "FFE5B77D", "FFFFDCA4", "FFB58363", "FF5B9078",
        "FFB5D0A1", "FFF8F5E7", "FFB78F8A",
    ])
    s.ellipse(42, 7, 4.3, 4.3, 5)
    s.rect(0, 39, 47, 47, 8)
    for x, y, r in [(5, 27, 7), (44, 31, 6)]:
        s.rect(x-1, y, x+1, 43, 1)
        s.ellipse(x, y, r, 9, 7)
        s.ellipse(x, y-1, r-2, 7, 8)
    s.rect(7, 40, 40, 42, 1)
    s.rect(10, 37, 37, 39, 4)
    s.rect(12, 35, 35, 37, 6)
    for x in (14, 20, 27, 33):
        s.rect(x-1, 22, x+1, 35, 1)
        s.rect(x, 23, x, 34, 9)
        s.rect(x-2, 22, x+2, 23, 4)
        s.rect(x-2, 34, x+2, 35, 4)
    s.polygon([(9, 20), (14, 14), (23, 8), (32, 14),
               (39, 20), (36, 22), (11, 22)], 1)
    s.polygon([(11, 20), (15, 15), (23, 10), (31, 15),
               (37, 20), (34, 20), (12, 20)], 2)
    for x in (14, 19, 24, 29, 34):
        s.line(23, 10, x, 20, 3, radius=0.55)
    s.dot(23, 8, 4)
    s.rect(19, 32, 28, 34, 1)
    s.rect(20, 31, 27, 32, 5)
    s.rect(22, 30, 25, 31, 6)
    for x, y in [(6, 45), (41, 45), (2, 40), (45, 39)]:
        s.dot(x, y, 10)
        s.dot(x+1, y, 5)
    return s


def amir_chakhmaq():
    s = Sprite(48, [
        "FF233650", "FF705B5B", "FFC08D6C", "FFE0B390",
        "FFFFD9A7", "FF337D98", "FF63B9C7", "FF173B53",
        "FFEDBD79", "FFF8E9CB",
    ])
    for x, y in [(4, 4), (41, 6), (30, 3), (14, 8)]:
        s.dot(x, y, 8)
    s.rect(0, 42, 47, 47, 1)
    for x in (5, 41):
        s.rect(x-2, 5, x+2, 39, 1)
        s.rect(x-1, 7, x+1, 38, 2)
        for y in range(9, 38, 5):
            s.rect(x-1, y, x+1, y+1, 4)
        s.rect(x-3, 5, x+3, 7, 3)
        s.rect(x-2, 2, x+2, 5, 2)
        s.dot(x, 1, 8)
    s.rect(9, 16, 37, 42, 1)
    s.rect(10, 17, 36, 41, 2)
    s.rect(14, 11, 32, 20, 1)
    s.rect(15, 12, 31, 20, 3)
    s.rect(20, 7, 26, 15, 1)
    s.rect(21, 8, 25, 15, 2)
    crenels(s, 15, 33, 10, 4, 2, 2)
    for cx, top, bottom, half in [
        (17, 13, 21, 3), (24, 10, 20, 4), (31, 13, 21, 3),
        (15, 22, 33, 4), (24, 19, 33, 5), (33, 22, 33, 4),
        (6, 35, 43, 3), (15, 33, 43, 4), (24, 31, 43, 5),
        (33, 33, 43, 4), (42, 35, 43, 3),
    ]:
        pointed_arch(s, cx, top, bottom, half, 4, 7, 1)
        s.dot(cx, top+half//2+3, 5)
    s.rect(0, 43, 47, 44, 4)
    for x in range(1, 47, 5):
        s.dot(x, 45, 5)
    return s


def golestan_palace():
    s = Sprite(48, [
        "FFE5F3F8", "FF556A73", "FFE6BE8C", "FFFFDCA9",
        "FF4688A6", "FF82C4CC", "FFB46D77", "FFF7F4E9",
        "FF477A65", "FF98BAC5", "FFCAA07C",
    ])
    s.rect(0, 40, 47, 47, 8)
    s.rect(5, 38, 42, 39, 1)
    s.rect(2, 14, 45, 38, 1)
    s.rect(3, 15, 44, 37, 2)
    s.rect(3, 10, 44, 15, 1)
    s.rect(4, 11, 43, 14, 3)
    s.rect(8, 7, 39, 11, 2)
    s.rect(12, 5, 35, 8, 3)
    s.rect(22, 4, 26, 6, 1)
    for x in range(5, 43, 4):
        s.dot(x, 12, 4)
        s.dot(x+1, 13, 6)
    for x in (10, 24, 38):
        pointed_arch(s, x, 18, 37, 6, 4, 1, 2)
        pointed_arch(s, x, 20, 36, 4, 5, 7, 1)
        s.rect(x, 24, x, 36, 1)
        s.rect(x-4, 29, x+4, 30, 1)
        for yy in (23, 26, 32, 35):
            s.dot(x-2, yy, 6)
            s.dot(x+2, yy, 4)
    for x in (3, 17, 31, 44):
        s.rect(x, 15, x+1, 38, 1)
        s.rect(x-1, 16, x+2, 17, 3)
        s.rect(x-1, 37, x+2, 38, 3)
    s.rect(13, 40, 35, 46, 1)
    s.rect(14, 41, 34, 45, 4)
    s.rect(16, 42, 32, 44, 5)
    for x in range(18, 32, 4):
        s.dot(x, 43, 7)
    s.rect(12, 46, 36, 47, 7)
    return s


PICTURES = [
    ("online-iran-persepolis", "تخت جمشید", "Persepolis", persepolis),
    ("online-iran-azadi-tower", "برج آزادی", "Azadi Tower", azadi_tower),
    ("online-iran-milad-tower", "برج میلاد", "Milad Tower", milad_tower),
    ("online-iran-imam-mosque", "مسجد امام اصفهان", "Imam Mosque, Isfahan", imam_mosque),
    ("online-iran-sio-se-pol", "سی‌وسه‌پل", "Si-o-se-pol Bridge", sio_se_pol),
    ("online-iran-nasir-ol-molk", "مسجد نصیرالملک", "Nasir ol-Molk Mosque", nasir_ol_molk),
    ("online-iran-arg-e-bam", "ارگ بم", "Bam Citadel", arg_e_bam),
    ("online-iran-hafez-tomb", "آرامگاه حافظ", "Tomb of Hafez", hafez_tomb),
    ("online-iran-amir-chakhmaq", "میدان امیرچخماق", "Amir Chakhmaq Complex", amir_chakhmaq),
    ("online-iran-golestan-palace", "کاخ گلستان", "Golestan Palace", golestan_palace),
]


def create_pack(destination):
    manifest = []
    assets = {}
    for identifier, title_fa, title_en, painter in PICTURES:
        sprite = painter()
        level = {
            "schemaVersion": 2,
            "levelId": identifier,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": sprite.side,
            "height": sprite.side,
            "palette": sprite.palette,
            "cells": sprite.cells,
        }
        level["checksum"] = checksum(level)
        blob = compact(level)
        stem = f"{identifier}-v1"
        manifest.append({
            "id": identifier,
            "version": 1,
            "title": title_fa,
            "titleEn": title_en,
            "category": "patterns",
            "width": sprite.side,
            "height": sprite.side,
            "bytes": len(blob),
            "checksum": level["checksum"],
        })
        assets[f"levels/{stem}.json"] = blob
        assets[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    destination = pathlib.Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for path, contents in assets.items():
            archive.writestr(path, contents)
    print(f"Generated {len(manifest)} original Iranian landmark coloring levels: {destination}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_iran_landmarks_pack.py <content.zip>")
    create_pack(sys.argv[1])
