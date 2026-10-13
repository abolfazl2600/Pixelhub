#!/usr/bin/env python3
"""Detailed, original 80x80 pixel-art homage to The Starry Night.

Published as a replacement catalog entry. The original online-starry-night
Release is immutable and its bytes/checksum are never edited.
"""
import math
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

ID = "online-classic-starry-night-detailed"


def draw():
    s = Sprite(80, [
        "FF0C1934",  # 0 blue-black night
        "FF182C5B",  # 1 midnight blue
        "FF234386",  # 2 cobalt
        "FF3864A5",  # 3 vivid blue
        "FF5896C0",  # 4 rolling sky highlights
        "FF83BBD1",  # 5 pale sky accents
        "FFEEE8A3",  # 6 warm light
        "FFF8CE58",  # 7 ochre gold
        "FFFFF2CA",  # 8 luminous centres
        "FF0D2233",  # 9 cypress silhouette
        "FF1B393D",  # 10 cypress facets
        "FF305D5B",  # 11 hillside
        "FF536F82",  # 12 stone buildings
        "FFB0AB8D",  # 13 village highlights
        "FFF6D883",  # 14 windows
        "FF38577D",  # 15 slate roofs
        "FF7898AB",  # 16 slate highlights
    ])
    s.rect(0, 0, 79, 53, 1)
    s.polygon([(0, 0), (31, 0), (52, 15), (79, 3), (79, 0)], 0)
    for y in range(3, 53):
        band = y // 8
        for x in range(80):
            wave = math.sin(x * 0.095 + y * 0.21) * 2.3
            if abs((y + wave) % 12 - 5) < (1.0 if band % 2 else 1.6):
                s.dot(x, y, 2 if band % 2 else 3)
            if abs((y + wave + 4.0) % 17 - 5) < 0.7:
                s.dot(x, y, 4)

    # Brushstroke spirals: separate repeated arcs rather than a filled blob.
    for cx, cy, rx, ry in [(47, 28, 20, 10), (22, 24, 14, 9)]:
        for layer, col in [(0, 4), (1, 3), (2, 5)]:
            r = 1.0 - layer * 0.18
            previous = None
            for step in range(76):
                theta = -0.45 + step * 2.8 * math.pi / 75
                fade = 0.36 + 0.64 * step / 75
                x = cx + rx * r * fade * math.cos(theta)
                y = cy + ry * r * fade * math.sin(theta)
                if previous is not None:
                    s.line(*previous, x, y, col, radius=.75 if layer == 0 else .54)
                previous = (x, y)

    # Radiant individual stars with staggered glows.
    for x, y, r in [
        (11, 9, 3.4), (29, 6, 3.1), (45, 10, 2.9),
        (63, 12, 3.8), (75, 24, 2.7), (10, 31, 3.0),
        (30, 42, 2.5), (54, 42, 2.6), (68, 35, 2.5),
        (39, 18, 2.2),
    ]:
        s.ellipse(x, y, r+2.5, r+2.3, 3)
        s.ellipse(x, y, r+1.25, r+1.25, 5)
        s.ellipse(x, y, r, r, 6)
        s.ellipse(x, y, max(1.05,r-1.25), max(1.05,r-1.25), 7)
        s.ellipse(x-.3, y-.4, .95, .95, 8)
        for dx, dy in [(0, -r-3), (0, r+3), (-r-3, 0), (r+3, 0)]:
            s.dot(int(x+dx), int(y+dy), 6)
    # Large brilliant crescent at upper right.
    s.ellipse(70, 7, 7.4, 7.0, 7)
    s.ellipse(70, 7, 5.9, 5.6, 8)
    s.ellipse(73, 4, 5.7, 5.7, 2)

    # Undulating distant landscape: sky above, hills below.
    s.polygon([(0, 57), (12, 51), (26, 56), (42, 52),
               (55, 55), (69, 50), (79, 52), (79, 79), (0, 79)], 11)
    s.polygon([(0, 65), (16, 58), (33, 63), (52, 59),
               (68, 63), (79, 60), (79, 79), (0, 79)], 10)
    s.line(7, 58, 33, 62, 3, radius=.7)
    s.line(47, 59, 78, 57, 3, radius=.7)
    s.rect(20, 63, 79, 79, 9)

    # Village: varied stepped houses, rooftops, and lit windows.
    for x, top, w in [(22, 62, 9), (33, 60, 12), (49, 63, 8),
                       (60, 59, 10), (71, 64, 8)]:
        s.rect(x, top, min(79,x+w), 75, 12)
        s.polygon([(x-2, top), (x+w/2, top-5),
                   (x+w+2, top)], 15)
        s.line(x, top, x+w, top, 16, radius=.6)
        for wx in range(x+2, min(79,x+w), 4):
            s.rect(wx, top+3, wx+1, top+5, 14)
        s.rect(x+1, top+8, x+2, top+11, 13)
    # Church tower placed on the distant village skyline.
    s.rect(43, 53, 47, 67, 12)
    s.polygon([(41, 54), (45, 45), (49, 54)], 15)
    s.rect(44, 56, 45, 58, 14)
    s.rect(44, 62, 45, 67, 9)
    s.line(45, 45, 45, 41, 16, radius=.5)

    # Iconic cypress: irregular flame-shaped vertical silhouette, foreground.
    s.polygon([(0, 80), (4, 72), (5, 62), (8, 53), (7, 47),
               (10, 35), (10, 24), (14, 13), (16, 24),
               (19, 32), (18, 45), (21, 56), (19, 64),
               (23, 80)], 9)
    s.polygon([(6, 78), (10, 68), (11, 53), (13, 43),
               (12, 29), (15, 35), (16, 53), (18, 70),
               (17, 78)], 10)
    for x,y in [(11,31),(14,40),(10,51),(15,58),(11,68)]:
        s.line(x, y, x+1, y+4, 11, radius=.7)
    s.rect(0, 77, 79, 79, 9)
    return s


def create_pack(destination):
    s = draw()
    level = {
        "schemaVersion": 2,
        "levelId": ID,
        "levelVersion": 1,
        "titles": {"fa": "شب پرستاره", "en": "The Starry Night"},
        "width": s.side,
        "height": s.side,
        "palette": s.palette,
        "cells": s.cells,
    }
    level["checksum"] = checksum(level)
    body = compact(level)
    item = {
        "id": ID, "version": 1,
        "title": level["titles"]["fa"],
        "titleEn": level["titles"]["en"], "category": "patterns",
        "width": s.side, "height": s.side, "bytes": len(body),
        "checksum": level["checksum"],
    }
    validate_new_pack_manifest([item])
    if len(body) > 262144:
        raise ValueError("Detailed painting exceeds the client size limit")
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": [item],
        }))
        archive.writestr(f"levels/{ID}-v1.json", body)
        archive.writestr(f"previews/{ID}-v1.png", png(level))
    print(f"Created detailed 80x80 Starry Night: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_starry_night_replacement_pack.py <content.zip>")
    create_pack(sys.argv[1])
