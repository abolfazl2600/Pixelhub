#!/usr/bin/env python3
"""Twenty original, 32x32 Persian numeral coloring levels for PixelHub Kids.

The immutable artwork is authored as per-cell pixels, not screenshots. Digit
stencils are pinned in this source (no machine fonts or Pillow at build time).
Generated JSON, PNG and content.zip are release-only assets, never APK assets.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

SIDE = 32
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
PREFIX = "online-kids-persian-number-"

# Persian-style numeral silhouettes. # is a filled pixel; . is transparent.
# Rasterized once from a bold Persian-capable glyph and pinned for reproducibility.
GLYPHS = {
    "۰": "........../....##..../....###.../...#####../..#######./.#########/..#######./...#####../....###.../.....#..../..........",
    "۱": "....../####../####../.####./.####./.####./.####./.####./.####./.####./..###./..####/..####/..####/..####/..####",
    "۲": ".........../####...####/####...####/.#########./.#########./.########../.####....../.####....../.####....../..###....../..###....../..###....../..###......",
    "۳": "..#......#./####.##.###/###########/.##########/.#####.###./.###......./.###......./.###......./.####....../.####....../..###....../..###......",
    "۴": "..##..####./####.#####./####.####../.###.###.../.#########./.##########/.#########./.####....../.####....../..###....../..###....../..###....../..###......",
    "۵": ".........../....##...../...####..../...#####.../...######../..#######../.####.####./.###...###./.###...####/###..##.###/###########/.#########./..###.###..",
    "۶": "...####.../..#####.../.######.../#######.../####....../####....../#####..#../.########./..#######./...######./..######../.######.../.#####..../#####...../.###....../...#......",
    "۷": "..#.....#../###.....###/.###...####/.###...###./.###...###./..###.###../..###.###../..###.###../...#####.../...#####.../...#####.../....###..../....##.....",
    "۸": ".........../....###..../....####.../...#####.../...#####.../...######../..###.###../..###.###../.####..###./.###...###./.###...###./###.....###/..#.....#..",
    "۹": "...#####.../..#######../.########../.#########./####..####./#####.####./.#########./.#########./..########./.......###./.......####/.......####/.......####/...........",
}

# A consistent playful palette. Indices: paper, border, corner, dark outline,
# numeral fill, highlight, decorations, sparkle, additional confetti.
THEMES = [
    ("FFFDF5EF", "FFFF9BBB", "FFF378A1", "FF342D49", "FFFF526F", "FFFFA0AE", "FFFFD55E", "FFFFF2AC", "FFFFB7CA"),
    ("FFFFF9F1", "FF7ACCEB", "FF46B7E7", "FF322D48", "FFFFB72F", "FFFFE46B", "FF4EC7F0", "FFFFFFFF", "FFFFDA7D"),
    ("FFFFFAF3", "FF91DEA6", "FF59C87F", "FF38294A", "FFAB59D6", "FFDC94F2", "FF5FCB7E", "FFFFFFCE", "FFDFBAF3"),
    ("FFFFFAEF", "FFFFD27C", "FFFFB950", "FF302E4A", "FF38A9ED", "FF79D5FF", "FFFFB52A", "FFFFE88D", "FF8FCDF4"),
    ("FFFFF9F8", "FFC1A6EE", "FF9A73DF", "FF34413C", "FF71C849", "FFB2EC80", "FFCE8CFF", "FFFFC4E9", "FFFFE7B4"),
    ("FFFFFAEF", "FFFFD97B", "FFFFBA3E", "FF393142", "FFFF647A", "FFFFA7A7", "FFFFAE32", "FFFFFFB4", "FF9ADDF5"),
    ("FFFFF8F4", "FFFFA0BA", "FFFB7BA0", "FF30434E", "FF36C6CB", "FF8DE7E6", "FFFFA8C8", "FFFFF0B5", "FFF7C4D9"),
    ("FFF5FBFF", "FF8DCDF4", "FF5AB6EF", "FF402F3C", "FFFF9034", "FFFFCB60", "FF73D3FB", "FFFFFFFF", "FFB7EAFF"),
]
# Repeated colors are intentional, but each numeral has its own layout.
PALETTE_INDEXES = (0, 1, 2, 3, 4, 5, 6, 7, 2, 6, 4, 3, 0, 2, 5, 7, 3, 4, 0, 2)


def persian_number(number):
    return "".join(PERSIAN_DIGITS[int(ch)] for ch in str(number))


def _raster(number):
    """Generate 1024 color-by-number cells in a square, with crisp hard edges."""
    theme = PALETTE_INDEXES[number - 1]
    pixels = [[0] * SIDE for _ in range(SIDE)]

    def put(x, y, value):
        if 0 <= x < SIDE and 0 <= y < SIDE:
            pixels[y][x] = value

    def rect(x1, y1, x2, y2, value):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                put(x, y, value)

    # Chunky double-line frame with chamfered corners and a warm center.
    rect(1, 1, 30, 30, 1)
    rect(3, 3, 28, 28, 0)
    for x, y in ((1, 1), (30, 1), (1, 30), (30, 30)):
        put(x, y, 0)
    for x, y in ((3, 3), (4, 3), (3, 4), (27, 3), (28, 3),
                 (28, 4), (3, 27), (3, 28), (4, 28),
                 (27, 28), (28, 27), (28, 28)):
        put(x, y, 2)

    # Tiny heart/star/flower decorations in otherwise empty corners.
    if theme % 3 == 0:
        for dx, dy in ((-1, 0), (1, 0), (-2, 1), (-1, 1), (0, 1),
                       (1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (0, 3)):
            put(6 + dx, 6 + dy, 6)
            put(25 + dx, 25 + dy, 6)
    elif theme % 3 == 1:
        for x, y in ((6, 6), (25, 25)):
            for dx, dy in ((0, -2), (0, -1), (-2, 0), (-1, 0), (0, 0),
                           (1, 0), (2, 0), (0, 1), (0, 2)):
                put(x + dx, y + dy, 7 if dx == dy == 0 else 6)
    else:
        for x, y in ((6, 6), (25, 25)):
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                put(x + dx, y + dy, 6)
            put(x, y, 7)

    for x, y in ((25, 6), (6, 25), (4, 17), (27, 15)):
        put(x, y, 8)
    for x, y in ((23, 5), (8, 27)):
        put(x, y, 7)

    numeral = persian_number(number)
    # Slightly narrower for two-digit numbers; never use an image upscaler.
    glyph_parts = []
    for digit in numeral:
        rows = GLYPHS[digit].split("/")
        if len(numeral) == 1:
            width = 9 if digit == "۱" else (9 if digit == "۰" else 14)
            height = 20 if digit != "۰" else 12
        else:
            width = 6 if digit == "۱" else (7 if digit == "۰" else 10)
            height = 18 if digit != "۰" else 10
        glyph_parts.append((rows, width, height))

    gap = 3 if len(glyph_parts) > 1 else 0
    total_width = sum(part[1] for part in glyph_parts) + gap
    start_x = (SIDE - total_width) // 2
    filled = set()
    for rows, width, height in glyph_parts:
        source_h = len(rows)
        source_w = len(rows[0])
        if any(len(row) != source_w for row in rows):
            raise ValueError("Inconsistent Persian numeral glyph width")
        start_y = 16 - height // 2
        for yy in range(height):
            source_y = min(source_h - 1, yy * source_h // height)
            for xx in range(width):
                source_x = min(source_w - 1, xx * source_w // width)
                if rows[source_y][source_x] == "#":
                    filled.add((start_x + xx, start_y + yy))
        start_x += width + gap

    # One-pixel outline around the actual Persian-shaped glyphs.
    outline = {(x + dx, y + dy) for x, y in filled
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    for x, y in outline - filled:
        put(x, y, 3)
    for x, y in filled:
        put(x, y, 5 if (y + x) % 7 < 2 else 4)

    return [pixel for row in pixels for pixel in row]


def make_level(number):
    if not 1 <= number <= 20:
        raise ValueError("Expected a Persian numeral from 1 through 20")
    title = persian_number(number)
    level = {
        "schemaVersion": 2,
        "levelId": f"{PREFIX}{number:02d}",
        "levelVersion": 1,
        "titles": {"fa": f"عدد {title}", "en": f"Persian number {number}"},
        "width": SIDE,
        "height": SIDE,
        "palette": list(THEMES[PALETTE_INDEXES[number - 1]]),
        "cells": _raster(number),
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    pictures, files = [], {}
    for number in range(1, 21):
        level = make_level(number)
        body = compact(level)
        stem = f"{level['levelId']}-v1"
        pictures.append({
            "id": level["levelId"], "version": 1,
            "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
            # A legacy public category, already allowed by Kids.
            "category": "patterns", "width": SIDE, "height": SIDE,
            "bytes": len(body), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = body
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(pictures)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": pictures,
        }))
        for name, body in files.items():
            bundle.writestr(name, body)
    print(f"Prepared 20 Kids-only Persian numeral paintings: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_kids_persian_numbers_pack.py <content.zip>")
    create_pack(sys.argv[1])
