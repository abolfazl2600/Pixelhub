#!/usr/bin/env python3
"""Twenty original 10x10 country flag icons as immutable online levels.

The 10x10 grid contains a ten-by-six flag centered on a neutral background
(except Switzerland, shown as a centered six-by-six square). Small emblems,
stars, and inscriptions are necessarily simplified at this resolution.
This file contains drawing instructions only; published JSON/PNG assets live
in a separate GitHub Release rather than in Git or the Android application.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

SIZE = 10
COLORS = {
    ".": "FFE9EDF2",  # neutral framing background
    "w": "FFFFFFFF",  # white
    "r": "FFCE2838",  # red
    "g": "FF23965D",  # Iranian green
    "b": "FF2556A5",  # royal blue
    "n": "FF19335F",  # navy blue
    "k": "FF20242C",  # black
    "y": "FFF3C340",  # yellow
    "o": "FFF19432",  # saffron / orange
    "c": "FF71BCE7",  # light blue
    "d": "FF167440",  # Brazilian green
    "m": "FFAD2135",  # Turkish red
}

# Country, bilingual labels. Fresh IDs do not overlap earlier published levels.
COUNTRIES = [
    ("iran", "ایران", "Iran"),
    ("france", "فرانسه", "France"),
    ("germany", "آلمان", "Germany"),
    ("italy", "ایتالیا", "Italy"),
    ("russia", "روسیه", "Russia"),
    ("ukraine", "اوکراین", "Ukraine"),
    ("netherlands", "هلند", "Netherlands"),
    ("poland", "لهستان", "Poland"),
    ("japan", "ژاپن", "Japan"),
    ("turkey", "ترکیه", "Turkey"),
    ("united-states", "ایالات متحده آمریکا", "United States"),
    ("united-kingdom", "بریتانیا", "United Kingdom"),
    ("canada", "کانادا", "Canada"),
    ("brazil", "برزیل", "Brazil"),
    ("india", "هند", "India"),
    ("china", "چین", "China"),
    ("sweden", "سوئد", "Sweden"),
    ("norway", "نروژ", "Norway"),
    ("finland", "فنلاند", "Finland"),
    ("switzerland", "سوئیس", "Switzerland"),
]


def flag_cells(country):
    """Return 100 palette symbols in row-major order, no scaling or antialias."""
    pixels = [["."] * SIZE for _ in range(SIZE)]

    def dot(x, y, color):
        if 0 <= x < SIZE and 0 <= y < SIZE:
            pixels[y][x] = color

    def rect(x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                dot(x, y, color)

    def fill(color):
        rect(0, 2, 9, 7, color)

    def horizontal(colors):
        for y in range(2, 8):
            rect(0, y, 9, y, colors[(y - 2) * len(colors) // 6])

    def vertical(colors):
        for x in range(10):
            rect(x, 2, x, 7, colors[x * len(colors) // 10])

    if country == "iran":
        horizontal(("g", "w", "r"))
        # Red central emblem represented by four discrete pixels.
        for x, y in ((4, 4), (5, 4), (4, 5), (5, 5)):
            dot(x, y, "r")
    elif country == "france":
        vertical(("b", "w", "r"))
    elif country == "germany":
        horizontal(("k", "r", "y"))
    elif country == "italy":
        vertical(("g", "w", "r"))
    elif country == "russia":
        horizontal(("w", "b", "r"))
    elif country == "ukraine":
        horizontal(("b", "y"))
    elif country == "netherlands":
        horizontal(("r", "w", "b"))
    elif country == "poland":
        horizontal(("w", "r"))
    elif country == "japan":
        fill("w")
        for y in range(2, 8):
            for x in range(10):
                if (x - 4.5) ** 2 + (y - 4.5) ** 2 <= 4.3:
                    dot(x, y, "r")
    elif country == "turkey":
        fill("m")
        for y in range(2, 8):
            for x in range(10):
                if (x - 3.5) ** 2 + (y - 4.5) ** 2 <= 5.1:
                    dot(x, y, "w")
                if (x - 4.6) ** 2 + (y - 4.0) ** 2 <= 2.0:
                    dot(x, y, "m")
        # One-point star is a deliberate 10x10 simplification.
        for x, y in ((7, 4), (8, 5), (7, 6)):
            dot(x, y, "w")
    elif country == "united-states":
        for y in range(2, 8):
            rect(0, y, 9, y, "r" if (y - 2) % 2 == 0 else "w")
        rect(0, 2, 4, 5, "n")
        for x, y in ((1, 2), (3, 2), (2, 3), (1, 4), (3, 4), (2, 5)):
            dot(x, y, "w")
    elif country == "united-kingdom":
        fill("n")
        for x in range(10):
            dot(x, 2 + round(x * 5 / 9), "w")
            dot(x, 7 - round(x * 5 / 9), "w")
        rect(4, 2, 5, 7, "w")
        rect(0, 4, 9, 5, "w")
        rect(4, 2, 4, 7, "r")
        rect(0, 4, 9, 4, "r")
    elif country == "canada":
        fill("w")
        rect(0, 2, 1, 7, "r")
        rect(8, 2, 9, 7, "r")
        for x, y in ((4, 3), (3, 4), (5, 4), (2, 5), (4, 5), (6, 5),
                     (3, 6), (4, 6), (5, 6), (4, 7)):
            dot(x, y, "r")
    elif country == "brazil":
        fill("d")
        for y in range(2, 8):
            for x in range(10):
                if abs(x - 4.5) / 4.3 + abs(y - 4.5) / 2.7 <= 1:
                    dot(x, y, "y")
                if (x - 4.5) ** 2 + (y - 4.5) ** 2 <= 2.7:
                    dot(x, y, "b")
        dot(3, 4, "w")
        dot(4, 4, "w")
    elif country == "india":
        horizontal(("o", "w", "g"))
        for x, y in ((4, 4), (5, 4), (4, 5), (5, 5)):
            dot(x, y, "n")
    elif country == "china":
        fill("r")
        for x, y in ((1, 3), (2, 3), (1, 4), (2, 4),
                     (4, 2), (5, 3), (5, 5), (4, 6)):
            dot(x, y, "y")
    elif country == "sweden":
        fill("b")
        rect(3, 2, 4, 7, "y")
        rect(0, 4, 9, 4, "y")
    elif country == "norway":
        fill("r")
        rect(3, 2, 5, 7, "w")
        rect(0, 4, 9, 5, "w")
        rect(4, 2, 4, 7, "n")
        rect(0, 4, 9, 4, "n")
    elif country == "finland":
        fill("w")
        rect(3, 2, 4, 7, "b")
        rect(0, 4, 9, 5, "b")
    elif country == "switzerland":
        rect(2, 2, 7, 7, "r")
        rect(4, 3, 5, 6, "w")
        rect(3, 4, 6, 5, "w")
    else:
        raise ValueError("Unsupported flag country: " + country)

    return [color for row in pixels for color in row]


def make_level(item):
    country, title_fa, title_en = item
    symbols = flag_cells(country)
    used = [symbol for symbol in COLORS if symbol in symbols]
    palette = [COLORS[symbol] for symbol in used]
    cells = [used.index(symbol) for symbol in symbols]
    level = {
        "schemaVersion": 2,
        "levelId": "online-flag-" + country + "-10",
        "levelVersion": 1,
        "titles": {"fa": "پرچم " + title_fa, "en": title_en + " Flag"},
        "width": SIZE,
        "height": SIZE,
        "palette": palette,
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(COUNTRIES) != 20 or len({c[0] for c in COUNTRIES}) != 20:
        raise ValueError("Expected 20 distinct country flags")
    manifest, assets = [], {}
    for item in COUNTRIES:
        level = make_level(item)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError("Online level too large: " + level["levelId"])
        stem = level["levelId"] + "-v1"
        manifest.append({
            "id": level["levelId"],
            "version": 1,
            "title": level["titles"]["fa"],
            "titleEn": level["titles"]["en"],
            "category": "patterns",
            "width": SIZE,
            "height": SIZE,
            "bytes": len(body),
            "checksum": level["checksum"],
        })
        assets["levels/" + stem + ".json"] = body
        assets["previews/" + stem + ".png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1,
            "pictures": manifest,
        }))
        for name, body in assets.items():
            archive.writestr(name, body)
    print("Prepared 20 distinct 10x10 country flags:", target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_flags_20_pack.py <content.zip>")
    create_pack(sys.argv[1])
