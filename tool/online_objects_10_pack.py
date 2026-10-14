#!/usr/bin/env python3
"""Twenty hand-authored, exact 10x10 object icons for an online Release pack.

The source stores compact cell matrices, never enlarged reference sheets. Every
row is ten cells wide and every level is generated at exactly 10x10.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

# Four colors per image: clear background, dark outline, main color, highlight.
PALETTES = {
    "red": ["FFFFF5F2", "FF493845", "FFE84D5B", "FFFFB35C"],
    "yellow": ["FFFFFAE8", "FF493845", "FFF4C542", "FFFFEAA0"],
    "green": ["FFF1FAEF", "FF344B45", "FF53A76A", "FFB9DF78"],
    "blue": ["FFF0F8FF", "FF34435D", "FF4D8FD0", "FF9FD9F2"],
    "purple": ["FFF8F2FF", "FF493845", "FF9564C8", "FFD8B6F0"],
    "pink": ["FFFFF2F6", "FF493845", "FFE66F9B", "FFFFB7CF"],
    "orange": ["FFFFF6E9", "FF493845", "FFF08A37", "FFFFC66A"],
    "teal": ["FFF0FAF8", "FF344B45", "FF3DADB0", "FF9DE0D8"],
}

# '.' = background, 'x' = outline, 'a' = main fill, 'b' = highlight.
# Alternate variants of common motifs are intentionally distinct: a balloon
# bouquet, bitten sprinkle donut, ice-cream bar, and whole watermelon fruit.
PICTURES = [
    ("heart", "قلب قرمز", "Red Heart", "red", [
        "..........", "...xx.xx..", "..xxxxxxx.", ".xxxxxxxxx",
        ".xxaxaxxx.", ".xxaaaaxx.", "..xxaaaxx.", "...xxaxx..",
        "....xxx...", ".....x...."]),
    ("star", "ستاره زرد", "Yellow Star", "yellow", [
        ".....x....", "....xxx...", "....xbx...", "xxxxxxxxxx",
        ".xxxxxxxx.", "..xxxxxx..", "..xx..xx...", ".xx....xx..",
        ".x......x..", ".........."]),
    ("apple-leaf", "سیب با برگ", "Apple with Leaf", "red", [
        "....bb....", "...bbb....", "....x.....", "..xxxxxx..",
        ".xxaaaaxx.", "xxaaaaaaxx", "xxaaaaaaxx", ".xxaaaaxx.",
        "..xxxxxx..", "...xxxx..."]),
    ("cherry-pair", "دو گیلاس", "Pair of Cherries", "pink", [
        "...x..x...", "...x..x...", "....xx....", "....xx....",
        "...xxxx...", "..xxaaxx..", ".xxaaaxxx.", ".xxaaaxxx.",
        "..xxaaxx..", "...xxxx..."]),
    ("banana", "موز زرد", "Yellow Banana", "yellow", [
        "..........", ".......xx.", ".....xxaa.", "...xxaaax.",
        ".xxaaaxxx.", "xxaaaxxx...", ".xxaxxx....",
        "..xxxx.....", "..........", ".........."]),
    ("gold-key", "کلید طلایی", "Golden Key", "yellow", [
        "..........", "..xxxx....", ".xxbbxx...", ".xxbbxx...",
        "..xxxx....", "...x......", "...x.xx....",
        "...xxxx....", "...x.xx....", "...x......"]),
    ("balloon-bouquet", "دسته بادکنک‌ها", "Balloon Bouquet", "red", [
        "..xx..xx..", ".xaxxxax..", "xaaaaxxx..", ".xaxxxxx..",
        "..xx.x.....", "...xx......", "...x.......", "...x.......",
        "..x.x......", ".xx..xx...."]),
    ("envelope", "پاکت نامه", "Envelope", "blue", [
        "..........", ".xxxxxxxx.", ".xaaaaaax.", ".xxaaaaxx.",
        ".xxxaxxxx.", ".xxxxaxxx.", ".xxxxxaax.", ".xxxxxxxx.",
        ".xxxxxxxx.", ".........."]),
    ("gift-box", "جعبه هدیه", "جعبه هدیه", "purple", [
        "...xx.....", "..xbbx.....", ".xxxxxxx..", ".xaxxxax..",
        ".xaxxxax..", ".xxxxxxxx.", ".xaxxxax..", ".xaxxxax..",
        ".xxxxxxxx.", ".........."]),
    ("ice-cream-bar", "بستنی چوبی", "Ice Cream Bar", "pink", [
        "..........", "...xxxx...", "..xaaaax...", "..xabbax...",
        "..xaaaax...", "..xabbax...", "..xaaaax...", "...xxxx...",
        "....xx.....", "....xx....."]),
    ("strawberry", "توت‌فرنگی", "Strawberry", "red", [
        "...bb.....", "..bxxb....", ".xxxxxxx..", ".xaxaxaxx.",
        "xxaxaxaxxx", "xxaaaaaaxx", ".xxaaaaxx.", "..xxaxx...", "...xxx....",
        ".........."]),
    ("carrot", "هویج", "Carrot", "orange", [
        "....bb....", "...bbb....", "....x.....", "...xx.....",
        "..xxax....", "..xxaaxx...", "...xxaxx..", "...xxax....",
        "....xx.....", ".....x...."]),
    ("umbrella", "چتر", "Umbrella", "blue", [
        "...xxxx...", "..xbbbxx..", ".xbbbbbbx.", "xxxxxxxxxx",
        "...x..x....", "...x..x....", "...x.......",
        "...xxxx....", "..........", ".........."]),
    ("coffee-cup", "فنجان", "Coffee Cup", "teal", [
        "....xx....", "...xbx....", "...xbx....", "..xxxxxx..",
        ".xaaaaaax.", ".xaaaaaax.x", ".xaaaaaaxxx",
        "..xxxxxx..", "...xxxx...", ".........."]),
    ("candle", "شمع روشن", "Lit Candle", "yellow", [
        "....b.....", "...bxb....", "....b.....", "....x.....",
        "...xxxx...", "...xax....", "...xax....", "...xax....",
        "...xxxx...", ".........."]),
    ("sprinkle-donut", "دونات رنگی", "Sprinkle Donut", "pink", [
        "..xxxxxx..", ".xaaaaaax.", "xxabaaaaxx", "xxaaaxabxx",
        "xxaaxxaaax", "xxaaaaaaxx", ".xaaaaxaxx.", "..xxxxxx..",
        "..........", ".........."]),
    ("wrapped-candy", "آبنبات کاغذپیچ", "Wrapped Candy", "purple", [
        "..........", "...xx..xx..", "..xaxxxax..", ".xxaaaxxx..",
        "xxaabbbaxx.", ".xxaaaxxx..", "..xaxxxax..",
        "...xx..xx..", "..........", ".........."]),
    ("whole-watermelon", "هندوانه کامل", "Whole Watermelon", "green", [
        "..........", "...xxxx...", "..xaaaaax..", ".xaaaaaaxx.",
        "xxaabaaaaxx", "xxaaaabaxx.", ".xxaaaaxx..",
        "..xxxxxx...", "...xx......", ".........."]),
    ("light-bulb", "لامپ", "Light Bulb", "yellow", [
        "....xxxx...", "...xaaaax..", "..xaaaaaax.", "..xaaaaaax.",
        "..xaaaaaax.", "...xaaaax..", "....xxxx...", ".....xx....",
        "....xxxx...", "....xxxx..."]),
    ("cupcake", "کاپ‌کیک", "Cupcake", "purple", [
        "....xxxx...", "...xbbbxx..", "..xbbbbbx..", ".xxabbbaxx.",
        ".xxxxxxxxx.", "...xxxx....", "..xaaaaax..",
        "..xaaaaax..", "...xxxx....", ".........."]),
]


def make_level(item):
    slug, title_fa, title_en, palette_name, rows = item
    if len(rows) != 10 or any(len(row) != 10 for row in rows):
        raise ValueError(f"{slug}: every picture must be exactly 10x10")
    symbols = {".": 0, "x": 1, "a": 2, "b": 3}
    if any(set(row) - symbols.keys() for row in rows):
        raise ValueError(f"{slug}: unknown matrix symbol")
    cells = [symbols[cell] for row in rows for cell in row]
    if len(set(cells)) < 3:
        raise ValueError(f"{slug}: use at least three visible colors")
    level = {
        "schemaVersion": 2,
        "levelId": f"online-object-mini-{slug}",
        "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": 10,
        "height": 10,
        "palette": PALETTES[palette_name],
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    manifest, files = [], {}
    for item in PICTURES:
        level = make_level(item)
        body = compact(level)
        stem = f"{level['levelId']}-v1"
        manifest.append({
            "id": level["levelId"], "version": 1,
            "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
            "category": "objects", "width": 10, "height": 10,
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
    print(f"Created online pack with {len(manifest)} exact 10x10 levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_objects_10_pack.py <content.zip>")
    create_pack(sys.argv[1])
