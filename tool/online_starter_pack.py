#!/usr/bin/env python3
"""Author and package six original, numbered pixel-art pictures.

This script contains only reproducible drawing instructions; *not* the
generated level JSON or preview PNG assets. The GitHub Pages publication
workflow creates content.zip in a runner and attaches it to a Release.
Release assets are outside Git history and normal git clones.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest


class Sprite:
    """Small opaque, integer-grid pixel-art canvas."""

    def __init__(self, side, palette):
        self.side = side
        self.palette = palette
        self.cells = [0] * (side * side)

    def dot(self, x, y, color):
        if 0 <= x < self.side and 0 <= y < self.side:
            self.cells[y * self.side + x] = color

    def rect(self, x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.dot(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for y in range(self.side):
            for x in range(self.side):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    self.dot(x, y, color)

    def polygon(self, vertices, color):
        """Rasterize a filled polygon using pixel-center intersections."""
        for y in range(self.side):
            for x in range(self.side):
                inside = False
                j = len(vertices) - 1
                for i, (xi, yi) in enumerate(vertices):
                    xj, yj = vertices[j]
                    if (yi > y) != (yj > y):
                        hit = (xj - xi) * (y - yi) / (yj - yi) + xi
                        if x < hit:
                            inside = not inside
                    j = i
                if inside:
                    self.dot(x, y, color)

    def line(self, x0, y0, x1, y1, color, radius=0.5):
        steps = max(abs(x1 - x0), abs(y1 - y0)) * 8 + 1
        for step in range(int(steps) + 1):
            t = step / steps
            cx = x0 + (x1 - x0) * t
            cy = y0 + (y1 - y0) * t
            for y in range(max(0, int(cy - radius - 1)),
                           min(self.side, int(cy + radius + 2))):
                for x in range(max(0, int(cx - radius - 1)),
                               min(self.side, int(cx + radius + 2))):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                        self.dot(x, y, color)


def tulip():
    s = Sprite(16, [
        "FFF0FAF2", "FF345B51", "FF438E64", "FF8ACB70",
        "FFC6487F", "FFF486B3", "FFFFBDCF", "FFFFF0E4",
    ])
    s.ellipse(3, 3, 1.4, 1.4, 7)
    s.ellipse(13, 11, 1.4, 1.4, 7)
    s.rect(7, 8, 8, 14, 1)
    s.rect(8, 9, 8, 14, 2)
    s.polygon([(7, 13), (2, 9), (3, 13), (7, 15)], 1)
    s.polygon([(7, 13), (3, 10), (4, 13), (7, 14)], 3)
    s.polygon([(8, 13), (13, 9), (12, 14), (8, 15)], 1)
    s.polygon([(8, 13), (12, 10), (11, 13), (8, 14)], 2)
    s.polygon([(4, 4), (6, 6), (8, 2), (10, 6), (12, 4),
               (11, 9), (9, 11), (6, 11), (4, 9)], 4)
    s.polygon([(5, 5), (7, 7), (8, 4), (10, 7), (11, 5),
               (10, 9), (8, 10), (6, 9)], 5)
    s.rect(7, 6, 8, 8, 6)
    s.dot(8, 9, 5)
    return s


def mushroom():
    s = Sprite(16, [
        "FFFAF4E9", "FF4C3A43", "FFB93E52", "FFF36A76",
        "FFFFF9E6", "FFDDC49A", "FF74AD72", "FFB8D498",
    ])
    s.ellipse(2, 12, 1.8, 1, 7)
    s.ellipse(13, 13, 1.4, 1, 7)
    s.rect(5, 10, 10, 14, 1)
    s.rect(6, 10, 9, 13, 4)
    s.rect(7, 11, 8, 13, 5)
    s.ellipse(7.5, 7, 6.2, 4.3, 1)
    s.ellipse(7.5, 6.5, 5.2, 3.1, 2)
    s.rect(3, 7, 12, 8, 3)
    s.ellipse(5, 5, 1.1, 1.1, 4)
    s.ellipse(10, 5, 1.5, 1.0, 4)
    s.ellipse(8, 7, 1.1, 1.1, 4)
    s.line(1, 14, 4, 14, 6)
    s.line(11, 14, 14, 14, 6)
    s.dot(1, 8, 7)
    s.dot(14, 4, 7)
    return s


def cat_face():
    s = Sprite(24, [
        "FFF7F6F0", "FF403D51", "FFF0A55C", "FFFFD29A",
        "FFF19AA0", "FFFFEACA", "FF7AB8AE", "FFFFFFFF",
        "FF9F6A4C",
    ])
    s.ellipse(3, 20, 1.5, 1, 5)
    s.ellipse(21, 21, 1.5, 1, 5)
    for pts in [
        [(4, 11), (5, 2), (12, 8), (12, 13)],
        [(12, 8), (19, 2), (20, 11), (13, 13)],
    ]:
        s.polygon(pts, 1)
    s.polygon([(6, 10), (7, 5), (11, 9)], 4)
    s.polygon([(13, 9), (17, 5), (18, 10)], 4)
    s.ellipse(11.5, 14, 9.0, 8.0, 1)
    s.ellipse(11.5, 14, 8.0, 7.0, 2)
    s.ellipse(11.5, 17, 5.6, 3.7, 3)
    s.ellipse(7.5, 13, 1.5, 2.0, 5)
    s.ellipse(15.5, 13, 1.5, 2.0, 5)
    s.rect(8, 12, 9, 14, 1)
    s.rect(15, 12, 16, 14, 1)
    s.dot(9, 12, 7)
    s.dot(16, 12, 7)
    s.ellipse(11.5, 17, 2.8, 2, 5)
    s.polygon([(9, 16), (14, 16), (12, 18)], 4)
    s.line(12, 18, 12, 19, 1)
    s.line(12, 19, 10, 20, 1)
    s.line(12, 19, 14, 20, 1)
    for left, right in [(4, 19), (3, 17), (4, 16)]:
        s.dot(left, right, 8)
        s.dot(23 - left, right, 8)
    s.line(4, 18, 7, 18, 8)
    s.line(16, 18, 19, 18, 8)
    return s


def watermelon():
    s = Sprite(16, [
        "FFF0FAFD", "FF244B4B", "FF35996D", "FF9FDC99",
        "FFF96578", "FFFFA0A8", "FF553644", "FFFFF2CE",
    ])
    s.dot(2, 2, 7)
    s.dot(13, 3, 7)
    s.dot(1, 10, 7)
    s.polygon([(1, 4), (14, 4), (8, 15)], 1)
    s.polygon([(2, 5), (13, 5), (8, 14)], 2)
    s.polygon([(2, 5), (13, 5), (8, 12)], 3)
    s.polygon([(3, 5), (12, 5), (8, 11)], 4)
    s.rect(4, 5, 11, 5, 5)
    for x, y in [(6, 7), (10, 7), (8, 9)]:
        s.dot(x, y, 6)
    return s


def rocket():
    s = Sprite(24, [
        "FF142449", "FF889BD6", "FF2C3D65", "FFF6F5ED",
        "FFF66A74", "FF6DCCE7", "FFFFD06B", "FFFF843E",
        "FFAFBDD4",
    ])
    for x, y in [(2, 3), (6, 2), (19, 4), (21, 11), (3, 15),
                 (18, 19), (5, 21), (20, 22), (17, 2), (2, 9)]:
        s.dot(x, y, 1)
    s.polygon([(10, 17), (14, 17), (15, 20), (12, 23), (9, 20)], 7)
    s.polygon([(11, 18), (13, 18), (13, 21), (12, 23), (11, 21)], 6)
    s.polygon([(8, 13), (5, 20), (10, 18)], 2)
    s.polygon([(16, 13), (19, 20), (14, 18)], 2)
    s.polygon([(8, 14), (6, 18), (10, 17)], 4)
    s.polygon([(16, 14), (18, 18), (14, 17)], 4)
    s.polygon([(12, 2), (17, 9), (16, 19), (8, 19), (7, 9)], 2)
    s.polygon([(12, 4), (16, 10), (15, 18), (9, 18), (8, 10)], 3)
    s.polygon([(12, 2), (17, 9), (7, 9)], 4)
    s.polygon([(12, 4), (15, 8), (9, 8)], 4)
    s.ellipse(12, 12, 4, 4, 2)
    s.ellipse(12, 12, 3, 3, 5)
    s.ellipse(11, 11, 1.5, 1.5, 3)
    s.rect(10, 17, 14, 18, 8)
    return s


def butterfly():
    s = Sprite(24, [
        "FFF8F0FB", "FF363757", "FF9565CE", "FFC19BEE",
        "FFF184BC", "FF70B8E2", "FFFCF6FF", "FFF0C766",
        "FF79C9BF",
    ])
    # Draw mirrored wings before adding antennae and the body.
    for side in (-1, 1):
        top_cx = 11.5 + side * 5.0
        low_cx = 11.5 + side * 5.0
        s.ellipse(top_cx, 8, 5.8, 5.4, 1)
        s.ellipse(top_cx, 8, 4.8, 4.4, 2)
        s.ellipse(11.5 + side * 7, 9, 2.8, 2.6, 3)
        s.ellipse(low_cx, 15, 4.8, 4.2, 1)
        s.ellipse(low_cx, 15, 3.7, 3.2, 4)
        s.ellipse(11.5 + side * 6, 15.4, 1.4, 1.3, 5)
        s.ellipse(11.5 + side * 5, 6.4, 1.3, 1.4, 6)
        s.ellipse(11.5 + side * 7, 11.4, 1.0, 1.0, 8)
    s.line(11, 6, 9, 3, 1)
    s.line(12, 6, 14, 3, 1)
    s.dot(9, 3, 7)
    s.dot(14, 3, 7)
    s.ellipse(11.5, 12, 1.7, 6.2, 1)
    s.ellipse(11.5, 11.4, 0.8, 5.2, 7)
    s.dot(3, 20, 6)
    s.dot(20, 20, 6)
    return s


PICTURES = [
    ("online-tulip", "لاله صورتی", "Pink Tulip", "nature", tulip),
    ("online-mushroom", "قارچ جنگلی", "Forest Mushroom", "nature", mushroom),
    ("online-cat-face", "صورت گربه", "Cat Face", "animals", cat_face),
    ("online-watermelon", "قاچ هندوانه", "Watermelon Slice", "objects", watermelon),
    ("online-rocket", "موشک کوچک", "Little Rocket", "space", rocket),
    ("online-butterfly", "پروانه بنفش", "Purple Butterfly", "animals", butterfly),
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
    print(f"Created online pack with {len(manifest)} original levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_starter_pack.py <content.zip>")
    create_pack(sys.argv[1])
