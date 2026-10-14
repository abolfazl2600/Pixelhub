#!/usr/bin/env python3
"""Build ten original, easy 8x8 abstract patterns with loopable animations.

Only reproducible authoring instructions are committed. Level JSON, previews,
and animation sidecars are generated into an immutable online Release ZIP.
"""
import hashlib
import json
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

ID_PREFIX = "online-abstract-mini-"

PALETTES = {
    "aurora": ["FFF7F8FF", "FF28334A", "FF5577D8", "FF7DE0C3"],
    "sunset": ["FFFFF5EC", "FF4B3346", "FFED795B", "FFFFC65E"],
    "berry": ["FFFFF2F8", "FF443247", "FFD85A9E", "FF9A80E8"],
    "ocean": ["FFF0FAFF", "FF243F58", "FF2F9FC0", "FF72D6C1"],
    "citrus": ["FFFFFBEA", "FF45402F", "FFE9B83F", "FF83B95A"],
    "orchid": ["FFF8F3FF", "FF40334E", "FF9664D6", "FFE2A3E8"],
    "flame": ["FFFFF4EB", "FF4A3440", "FFF17A42", "FFFFC45B"],
    "lagoon": ["FFF0FBF8", "FF30494C", "FF36A9A1", "FF9BD9A5"],
    "neon": ["FFF4F4FF", "FF34324F", "FF7770E8", "FFFF83B7"],
    "forest": ["FFF4FAEF", "FF344A3D", "FF58A66A", "FFC4D96B"],
}

# Each matrix is exactly eight rows by eight columns. Symbols are palette indexes:
# . = background, x = outline/dark, a = main color, b = accent/highlight.
# These are intentionally simple abstract designs, not object silhouettes.
PATTERNS = [
    ("orbit", "مدارهای رنگی", "Color Orbit", "aurora", "orbit", [
        "........", "..xxxx..", ".xaaaax.", "xa.bb.ax",
        "xa.bb.ax", ".xaaaax.", "..xxxx..", "........"]),
    ("wave", "موج هندسی", "Geometric Wave", "ocean", "wave", [
        "........", "xx......", "aaxx....", "bbaaxx..",
        "..bbaaxx", "....bbaa", "......xx", "........"]),
    ("bloom", "شکوفه پیکسلی", "Pixel Bloom", "berry", "pulse", [
        "...bb...", "..baab..", ".baxxab.", "baaxxxab",
        "baaxxxab", ".baxxab.", "..baab..", "...bb..."]),
    ("spiral", "مارپیچ رنگی", "Color Spiral", "sunset", "spiral", [
        "xxxxxxxx", "xaaaaaax", "xa....ax", "xa.xx.ax",
        "xa.xb.ax", "xa....ax", "xaaaaaax", "xxxxxxxx"]),
    ("bars", "نوارهای شناور", "Floating Bars", "orchid", "bars", [
        "........", "xx..xx..", "aa..aa..", "bb..bb..",
        "..xx..xx", "..aa..aa", "..bb..bb", "........"]),
    ("diamond", "الماس درخشان", "Shimmer Diamond", "citrus", "diamond", [
        "....x...", "...xax..", "..xaaxx.", ".xaabaxx",
        "xaabbaxx", ".xaabaxx", "..xaaxx.", "...xax.."]),
    ("weave", "بافت متقاطع", "Cross Weave", "lagoon", "weave", [
        "x..x..x.", "ax.ax.ax", ".ax.ax.a", "x..x..x.",
        ".x..x..x", "a.ax.ax.", "xa.ax.ax", ".x..x..x"]),
    ("burst", "انفجار ستاره‌ای", "Pixel Burst", "flame", "burst", [
        "...x....", "..xax...", ".xaxax..", "xxaaaxx.",
        ".xaaaxx.", "..xaxax.", "...xax..", "....x..."]),
    ("ripple", "موج‌های هم‌مرکز", "Concentric Ripple", "neon", "ripple", [
        "xxxxxxxx", "x......x", "x.xx..bx", "x.xaa.xb",
        "x.xaa.xb", "x.xx..bx", "x......x", "xxxxxxxx"]),
    ("kaleido", "کالیدوسکوپ", "Pixel Kaleidoscope", "forest", "kaleido", [
        "x..bb..x", ".xa..ax.", "..xbb..x", "b..xx..b",
        "b..xx..b", "x..bb..x", ".xa..ax.", "x..bb..x"]),
]

SCENARIOS = {
    "orbit": ("نقطه روشن روی مدار با حرکت ساعت‌گرد می‌چرخد؛ شکل و پس‌زمینه ثابت می‌مانند.",
              "A bright accent travels clockwise around the orbit; the silhouette and background stay fixed."),
    "wave": ("رنگ موج از چپ به راست حرکت می‌کند و در انتها به نقطه شروع بازمی‌گردد.",
             "A color wave moves left to right and returns to its starting phase."),
    "pulse": ("رنگ‌های روشن به‌آرامی بین دو سطح شدت جابه‌جا می‌شوند؛ بدون تغییر شکل.",
              "Bright cells gently alternate between two intensities without changing the shape."),
    "spiral": ("درخشش در امتداد مسیر مارپیچ پیش می‌رود و به‌آرامی دور می‌زند.",
               "A highlight travels along the spiral path and loops smoothly."),
    "bars": ("نوارهای روشن یک ستون به سمت راست جابه‌جا می‌شوند و پیوسته تکرار می‌شوند.",
             "Highlighted bars advance one column to the right in a seamless loop."),
    "diamond": ("لبه الماس به‌ترتیب روشن و تیره می‌شود؛ هندسه الماس ثابت است.",
                "The diamond's edge shimmers between accent shades while its geometry stays fixed."),
    "weave": ("درخشش از خانه‌های بافت یکی‌درمیان عبور می‌کند و جهت آن رفت‌وبرگشت دارد.",
              "A shimmer travels through alternating weave cells and reverses direction."),
    "burst": ("پرتوهای ستاره‌ای به‌ترتیب رنگ تأکیدی می‌گیرند؛ مرکز و مرز ثابت‌اند.",
              "Starburst rays receive the accent color in sequence; the center and outline remain fixed."),
    "ripple": ("حلقه روشن به سمت بیرون حرکت می‌کند و سپس به حلقه داخلی برمی‌گردد.",
               "A bright ring travels outward and returns inward."),
    "kaleido": ("رنگ تأکیدی در ربع‌های متقارن می‌چرخد و در پایان با فریم آغازین منطبق می‌شود.",
                "Accent colors rotate through symmetric quadrants and return to the opening frame."),
}


def make_level(item):
    slug, title_fa, title_en, palette_name, _motion, rows = item
    if len(rows) != 8 or any(len(row) != 8 for row in rows):
        raise ValueError(f"{slug}: every pattern must be exactly 8x8")
    symbols = {".": 0, "x": 1, "a": 2, "b": 3}
    if any(set(row) - symbols.keys() for row in rows):
        raise ValueError(f"{slug}: unknown matrix symbol")
    cells = [symbols[char] for row in rows for char in row]
    if len(set(cells)) < 3:
        raise ValueError(f"{slug}: use at least three palette indexes")
    level = {
        "schemaVersion": 2,
        "levelId": ID_PREFIX + slug,
        "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": 8,
        "height": 8,
        "palette": PALETTES[palette_name],
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    return level


def animation_frames(level, motion):
    """Eight frames follow a symmetric 0→1→2→3→4→3→2→1 loop."""
    side = level["width"]
    original = level["cells"]
    phases = [0, 1, 2, 3, 4, 3, 2, 1]
    frames = []
    for phase in phases:
        cells = original[:]
        for y in range(side):
            for x in range(side):
                at = y * side + x
                color = original[at]
                if color not in (2, 3):
                    continue
                if motion == "orbit":
                    active = (x + 2 * y + phase) % 8 in (0, 1)
                elif motion == "wave":
                    active = (x - phase) % 4 in (0, 1)
                elif motion == "pulse":
                    active = (phase % 4) >= 2
                elif motion == "spiral":
                    active = (x + y + x * y + phase) % 5 in (0, 1)
                elif motion == "bars":
                    active = (x - phase) % 4 in (0, 1)
                elif motion == "diamond":
                    active = (abs(x - 3.5) + abs(y - 3.5) + phase) % 4 < 2
                elif motion == "weave":
                    active = (x + y + phase) % 3 == 0
                elif motion == "burst":
                    active = (abs(x - 3.5) + abs(y - 3.5) + phase) % 5 < 2
                elif motion == "ripple":
                    active = (x * x + y * y + phase) % 6 < 2
                elif motion == "kaleido":
                    active = ((x + phase) % 4) == (y % 4)
                else:
                    raise ValueError(f"unknown animation motion: {motion}")
                cells[at] = 3 if active else 2
        frames.append({"changes": [[at, color] for at, color in enumerate(cells)
                                   if color != original[at]]})
    return frames


def build(destination):
    manifest = []
    files = {}
    scenarios = {}
    for item in PATTERNS:
        slug, title_fa, title_en, palette_name, motion, _rows = item
        level = make_level(item)
        level_blob = compact(level)
        frames = animation_frames(level, motion)
        animation = {
            "schemaVersion": 1,
            "levelId": level["levelId"],
            "levelVersion": 1,
            "levelChecksum": level["checksum"],
            "frameDurationMs": 180,
            "frames": frames,
        }
        animation_blob = compact(animation)
        stem = f"{level['levelId']}-v1"
        entry = {
            "id": level["levelId"], "version": 1,
            "title": title_fa, "titleEn": title_en,
            "category": "patterns", "width": 8, "height": 8,
            "bytes": len(level_blob), "checksum": level["checksum"],
            "animation": {
                "bytes": len(animation_blob),
                "sha256": hashlib.sha256(animation_blob).hexdigest(),
                "frameCount": len(frames),
            },
        }
        manifest.append(entry)
        files[f"levels/{stem}.json"] = level_blob
        files[f"previews/{stem}.png"] = png(level)
        files[f"animations/{stem}.json"] = animation_blob
        scenario_fa, scenario_en = SCENARIOS[motion]
        scenarios[level["levelId"]] = {
            "titleFa": title_fa, "titleEn": title_en,
            "motion": motion, "frameDurationMs": 180, "frameCount": len(frames),
            "loop": "0→1→2→3→4→3→2→1→0",
            "scenarioFa": scenario_fa, "scenarioEn": scenario_en,
        }

    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": manifest,
        }))
        for name, payload in files.items():
            archive.writestr(name, payload)
        archive.writestr("animation-scenarios.json", compact({
            "schemaVersion": 1, "scenarios": scenarios,
        }))
    print(f"Created {len(manifest)} animated abstract 8x8 patterns: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_abstract_8_pack.py <content.zip>")
    build(sys.argv[1])
