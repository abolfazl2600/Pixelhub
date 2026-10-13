#!/usr/bin/env python3
"""Six hand-drawn, simplified pixel-art interpretations of classic paintings.

No painting scans, photographs, or third-party images are used. The generated
schema-v2 color-by-number JSON and PNG previews live only in a GitHub Release,
not in source control or the application binary.

All six entries use the existing 'patterns' category deliberately: published
Android clients validate the category allowlist and would reject an entire
catalog containing a new, unknown 'masterworks' category.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png
from online_starter_pack import Sprite


def mona_lisa():
    """Landscape horizon, dark hair, subtle smile and folded hands."""
    s = Sprite(32, [
        "FF594C36",  # 0 aged dark olive backdrop
        "FF292D25",  # 1 near-black outlines and hair
        "FF66775A",  # 2 misty trees
        "FFACB39A",  # 3 distant landscape
        "FF9B7657",  # 4 shadow skin
        "FFDAB58B",  # 5 warm face and hands
        "FFF1CE9D",  # 6 skin highlight
        "FF443F30",  # 7 dress
        "FF807450",  # 8 embroidered folds
        "FF42372B",  # 9 earth shadow
        "FFEEE0B8",  # 10 pale sky
    ])
    s.rect(0, 0, 31, 10, 3)
    s.rect(0, 10, 31, 15, 2)
    s.polygon([(0, 9), (7, 6), (13, 10), (19, 7), (31, 10),
               (31, 14), (0, 14)], 2)
    s.line(0, 12, 10, 13, 10, radius=.6)
    s.line(23, 11, 31, 10, 10, radius=.6)
    s.polygon([(3, 32), (5, 23), (10, 18), (13, 17),
               (19, 17), (24, 21), (29, 32)], 1)
    s.polygon([(4, 31), (7, 23), (13, 19), (19, 19),
               (25, 23), (28, 31)], 7)
    s.polygon([(6, 28), (11, 21), (15, 23), (11, 32), (4, 32)], 8)
    s.polygon([(26, 28), (21, 21), (17, 23), (21, 32), (29, 32)], 8)
    s.ellipse(16, 13, 9.0, 12.2, 1)
    s.ellipse(16, 13, 7.1, 10.2, 9)
    s.ellipse(16, 12.2, 5.6, 7.7, 4)
    s.ellipse(16, 12, 4.7, 7.0, 5)
    s.polygon([(11, 9), (12, 5), (18, 4), (21, 10),
               (20, 8), (17, 7), (13, 8)], 1)
    s.ellipse(14, 14, 1.5, 2.3, 6)
    s.dot(13, 12, 1)
    s.dot(18, 12, 1)
    s.line(13, 16, 18, 16, 4, radius=.55)
    s.dot(15, 16, 6)
    s.dot(17, 16, 6)
    s.line(12, 18, 13, 21, 1, radius=.7)
    s.line(19, 18, 20, 21, 1, radius=.7)
    s.polygon([(11, 22), (17, 23), (21, 26), (15, 27),
               (8, 26)], 4)
    s.polygon([(12, 23), (18, 24), (19, 25), (14, 26), (10, 25)], 5)
    s.polygon([(21, 24), (26, 25), (21, 28), (13, 28),
               (12, 27)], 4)
    s.polygon([(19, 25), (24, 26), (21, 27), (15, 27)], 5)
    s.line(6, 30, 25, 30, 9, radius=.5)
    return s


def starry_night():
    """Cobalt night, spiral brush rhythms, moon and hillside village."""
    s = Sprite(32, [
        "FF122548",  # 0 deep blue
        "FF253D7F",  # 1 ultramarine
        "FF4164AE",  # 2 blue strokes
        "FF7DB5D6",  # 3 light blue strokes
        "FFFFE98A",  # 4 pale star glow
        "FFFDBF45",  # 5 sunflower yellow
        "FFF4F0C9",  # 6 moon
        "FF101D30",  # 7 trees, cypress
        "FF487164",  # 8 dark rolling hills
        "FF667C95",  # 9 village
        "FFF0CE79",  # 10 lit windows
    ])
    s.rect(0, 0, 31, 5, 1)
    s.rect(0, 13, 31, 20, 1)
    for points in [
        [(0, 4), (5, 7), (12, 7), (19, 3), (25, 5), (31, 4)],
        [(0, 11), (7, 9), (14, 12), (21, 10), (31, 12)],
        [(1, 17), (8, 15), (18, 18), (28, 14), (31, 14)],
    ]:
        for a, b in zip(points, points[1:]):
            s.line(*a, *b, 2, radius=1.0)
    s.ellipse(17, 13, 7, 5, 2)
    s.ellipse(17, 13, 5.7, 3.9, 0)
    s.ellipse(17, 13, 4.3, 2.8, 3)
    s.ellipse(17, 13, 3.3, 1.7, 1)
    s.line(15, 13, 21, 12, 5, radius=.7)
    for x, y, radius in [(4, 5, 2.6), (10, 3, 2.1), (24, 5, 2.5),
                         (27, 12, 1.7), (7, 15, 1.8), (14, 7, 1.8)]:
        s.ellipse(x, y, radius + 1.1, radius + 1.1, 2)
        s.ellipse(x, y, radius, radius, 4)
        s.ellipse(x, y, max(.65, radius - 1), max(.65, radius - 1), 5)
    s.ellipse(28, 3, 4, 4, 4)
    s.ellipse(29, 2.5, 3, 3.5, 6)
    s.polygon([(0, 21), (8, 20), (17, 23), (24, 21), (31, 22),
               (31, 32), (0, 32)], 8)
    s.rect(9, 24, 31, 31, 7)
    for a, b, c in [(10, 25, 12), (15, 25, 18), (22, 24, 26)]:
        s.polygon([(a, 26), (b, 23), (c, 26)], 7)
        s.rect(a + 1, 26, c - 1, 30, 9)
        s.dot(a + 2, 28, 10)
    s.polygon([(0, 32), (2, 26), (1, 20), (4, 12),
               (3, 5), (6, 9), (8, 18), (7, 22), (10, 32)], 7)
    s.line(4, 13, 5, 30, 1, radius=.9)
    return s


def the_scream():
    """Orange fjord sky, oblique bridge and terrified foreground silhouette."""
    s = Sprite(32, [
        "FFF4A45A",  # 0 sunset
        "FFC65353",  # 1 crimson sky
        "FFF2CE89",  # 2 bright sky
        "FF385A6D",  # 3 fjord
        "FF172C3E",  # 4 dark hills
        "FF8C6855",  # 5 bridge boards
        "FF4E3D3A",  # 6 railing and figure
        "FFE7D7AC",  # 7 face
        "FFF5E7C8",  # 8 highlights
        "FF1D2630",  # 9 eyes and scream
        "FF8FADAF",  # 10 water glimmer
    ])
    s.rect(0, 0, 31, 3, 1)
    for y, col in [(5, 2), (8, 1), (12, 2), (15, 1)]:
        s.line(0, y, 31, y - 2, col, radius=1.4)
    s.polygon([(0, 15), (10, 13), (19, 16), (31, 13),
               (31, 23), (0, 25)], 4)
    s.polygon([(0, 19), (13, 17), (20, 19), (31, 17),
               (31, 27), (0, 27)], 3)
    for y in (20, 22, 24):
        s.line(17, y, 31, y - 1, 10, radius=.7)
    s.polygon([(0, 18), (7, 21), (31, 31), (0, 31)], 5)
    s.line(0, 18, 31, 31, 6, radius=1.2)
    s.line(0, 23, 31, 31, 6, radius=1.1)
    s.line(2, 21, 1, 28, 6, radius=.9)
    s.line(15, 25, 15, 30, 6, radius=.9)
    s.ellipse(15.5, 25, 5.7, 10.2, 6)
    s.polygon([(9, 32), (11, 22), (15, 20), (19, 22), (23, 32)], 6)
    s.ellipse(16, 12.4, 5.8, 9.0, 6)
    s.ellipse(16, 12.4, 4.7, 7.6, 7)
    s.ellipse(13.8, 11, 1.1, 1.7, 9)
    s.ellipse(18.2, 11, 1.1, 1.7, 9)
    s.ellipse(16, 16, 2.2, 3.3, 9)
    s.ellipse(16, 15.8, 1.0, 2.0, 4)
    s.line(10, 16, 13, 20, 7, radius=1.3)
    s.line(22, 16, 19, 20, 7, radius=1.3)
    s.ellipse(11, 17, 1.8, 2.8, 7)
    s.ellipse(21, 17, 1.8, 2.8, 7)
    return s


def sunflowers():
    """Van Gogh-inspired bouquet of several golden blooms in a ceramic vase."""
    s = Sprite(24, [
        "FFDED5A8",  # 0 ochre room
        "FF675A3A",  # 1 contours
        "FF8B9C5E",  # 2 stems
        "FFF4C653",  # 3 yellow petals
        "FFF8E48A",  # 4 light petals
        "FF956B3E",  # 5 dark center
        "FFC89B58",  # 6 vase
        "FFF0D3A0",  # 7 vase highlights
        "FF8F754D",  # 8 table
        "FFB8A96C",  # 9 green-gold leaves
    ])
    s.rect(0, 17, 23, 23, 8)
    s.rect(0, 16, 23, 16, 1)
    for a, b in [((12, 15), (12, 5)), ((12, 15), (6, 8)),
                 ((12, 15), (18, 8)), ((12, 15), (6, 13)),
                 ((12, 15), (18, 13))]:
        s.line(*a, *b, 2, radius=.7)
    s.polygon([(11, 11), (6, 10), (8, 14), (12, 15)], 9)
    s.polygon([(13, 11), (19, 10), (16, 15), (12, 15)], 9)
    for cx, cy, radius in [(12, 4, 2.0), (5, 8, 1.8),
                           (18, 8, 1.8), (6, 13, 1.4), (18, 13, 1.4)]:
        s.ellipse(cx, cy, radius + 1.5, radius + 1.5, 1)
        s.ellipse(cx, cy, radius + 1.0, radius + 1.0, 3)
        for dx, dy in [(0, -radius - 1), (0, radius + 1),
                       (-radius - 1, 0), (radius + 1, 0)]:
            s.ellipse(cx + dx, cy + dy, 1.2, 1.2, 4)
        s.ellipse(cx, cy, radius, radius, 5)
        s.dot(round(cx), round(cy), 1)
    s.polygon([(6, 15), (18, 15), (17, 21), (14, 23),
               (10, 23), (7, 21)], 1)
    s.polygon([(7, 16), (17, 16), (16, 21), (14, 22),
               (10, 22), (8, 21)], 6)
    s.rect(9, 17, 10, 21, 7)
    s.rect(8, 16, 16, 16, 7)
    return s


def girl_pearl():
    """A turban with blue-yellow folds, profile face and single white pearl."""
    s = Sprite(32, [
        "FF171D25",  # 0 shadow
        "FF1C2B38",  # 1 navy backdrop
        "FFBE884F",  # 2 facial shadow
        "FFEAC18E",  # 3 gold skin
        "FFF6DAAD",  # 4 face highlight
        "FF33538C",  # 5 cobalt blue turban
        "FF668EB6",  # 6 blue cloth shine
        "FFECC762",  # 7 ochre cloth
        "FFF7E6A1",  # 8 yellow cloth highlight
        "FF463027",  # 9 hair and collar
        "FFFFFFFF",  # 10 pearl
        "FF9CB6BD",  # 11 pearl shadow
    ])
    s.rect(0, 0, 31, 31, 1)
    s.ellipse(29, 26, 5.5, 5, 0)
    s.polygon([(3, 32), (7, 23), (15, 21),
               (20, 22), (29, 32)], 9)
    s.polygon([(9, 32), (14, 24), (21, 24), (28, 32)], 2)
    s.ellipse(16, 16, 8.0, 10.0, 9)
    s.ellipse(17, 16.3, 6.4, 8.3, 2)
    s.ellipse(17.2, 16, 5.4, 7.3, 3)
    s.polygon([(16, 11), (23, 12), (23, 19),
               (19, 23), (14, 22), (12, 19)], 3)
    s.ellipse(21, 15, 2.2, 3.2, 4)
    s.polygon([(22, 16), (26, 19), (21, 20)], 3)
    s.dot(24, 18, 2)
    s.line(17, 13, 21, 13, 9, radius=.6)
    s.dot(19, 14, 0)
    s.line(20, 21, 23, 21, 9, radius=.65)
    s.polygon([(8, 12), (9, 5), (17, 3), (24, 7),
               (22, 12), (16, 11)], 5)
    s.polygon([(9, 9), (12, 4), (18, 4), (22, 8),
               (18, 10), (13, 9)], 6)
    s.polygon([(17, 5), (23, 6), (27, 13),
               (25, 22), (22, 20), (23, 12)], 7)
    s.polygon([(20, 6), (23, 8), (26, 14),
               (25, 20), (23, 17), (24, 12)], 8)
    s.polygon([(12, 23), (16, 24), (13, 29)], 9)
    s.ellipse(13, 24, 2.3, 2.8, 11)
    s.ellipse(13, 24, 1.6, 2.1, 10)
    s.dot(12, 23, 4)
    return s


def great_wave():
    """A sweeping indigo breaker with white foam, boats and distant Fuji."""
    s = Sprite(32, [
        "FFDFE9D9",  # 0 pale sky
        "FF253D58",  # 1 deep indigo contour
        "FF2E6490",  # 2 ocean blue
        "FF5D91B2",  # 3 crest blue
        "FFA3CAD4",  # 4 pale sea foam
        "FFF8F4E6",  # 5 white foam
        "FFB9C7C6",  # 6 distant mountain
        "FF71879A",  # 7 shaded wave
        "FF9F8064",  # 8 boat
    ])
    s.rect(0, 14, 31, 31, 2)
    s.line(0, 15, 31, 14, 1, radius=.55)
    s.polygon([(19, 15), (23, 8), (26, 12), (29, 16)], 6)
    s.polygon([(22, 13), (23, 9), (24, 11), (25, 10), (26, 13)], 5)
    s.line(20, 16, 30, 16, 1, radius=.65)
    for x, y in [(4, 24), (17, 27), (21, 22)]:
        s.line(x, y, x + 8, y - 2, 8, radius=.8)
        s.line(x, y + 1, x + 8, y - 1, 1, radius=.5)
    s.polygon([(0, 32), (0, 11), (2, 6), (7, 3),
               (12, 4), (16, 8), (18, 13), (14, 13),
               (11, 10), (8, 9), (6, 13), (5, 19),
               (9, 23), (16, 25), (24, 23), (32, 18),
               (32, 32)], 1)
    s.polygon([(0, 31), (1, 12), (3, 7), (7, 5),
               (11, 6), (14, 9), (15, 11), (12, 9),
               (8, 8), (5, 13), (4, 19), (8, 24),
               (16, 26), (25, 25), (31, 21), (31, 31)], 2)
    s.polygon([(1, 18), (3, 10), (6, 6), (9, 5),
               (13, 8), (15, 11), (13, 11), (11, 9),
               (7, 10), (5, 15), (5, 19)], 3)
    s.polygon([(3, 11), (5, 7), (8, 5), (12, 7),
               (15, 10), (17, 12), (14, 12), (11, 9),
               (9, 8), (6, 10), (5, 14)], 5)
    for ax, ay, bx, by in [
        (12, 8, 16, 11), (9, 6, 10, 10),
        (6, 7, 5, 11), (16, 11, 18, 13),
        (13, 12, 16, 15), (3, 12, 2, 16),
    ]:
        s.line(ax, ay, bx, by, 5, radius=.65)
    s.polygon([(0, 23), (5, 22), (9, 26), (18, 29),
               (26, 27), (31, 24), (31, 32), (0, 32)], 7)
    for x, y in [(3, 25), (10, 27), (19, 28), (25, 26), (28, 30)]:
        s.line(x, y, x + 3, y - 1, 4, radius=.8)
        s.dot(x + 3, y - 1, 5)
    return s


PICTURES = [
    ("online-mona-lisa", "مونالیزا", "Mona Lisa", mona_lisa),
    ("online-starry-night", "شب پرستاره", "The Starry Night", starry_night),
    ("online-the-scream", "جیغ", "The Scream", the_scream),
    ("online-sunflowers", "آفتابگردان‌ها", "Sunflowers", sunflowers),
    ("online-girl-pearl", "دختر با گوشواره مروارید",
     "Girl with a Pearl Earring", girl_pearl),
    ("online-great-wave", "موج بزرگ", "The Great Wave", great_wave),
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
        blob = compact(level)
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1, "title": title_fa,
            "titleEn": title_en, "category": "patterns",
            "width": sprite.side, "height": sprite.side,
            "bytes": len(blob), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = blob
        files[f"previews/{stem}.png"] = png(level)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, payload in files.items():
            archive.writestr(name, payload)
    print(f"Created six classic masterwork interpretations: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_masterworks_pack.py <content.zip>")
    create_pack(sys.argv[1])
