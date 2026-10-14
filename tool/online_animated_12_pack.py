#!/usr/bin/env python3
"""Twenty new 12x12 online pixel pictures with eight-frame companion animations.

Authoring data only: the immutable content ZIP, numbered levels and previews are
created at publish time, never stored in the app bundle or Git history.
"""
import hashlib
import json
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

PREFIX = "online-mini12-"
FRAME_DURATION_MS = 180
SYMBOLS = {".": 0, "#": 1, "o": 2, "*": 3, "+": 4, "=": 5}
PALETTES = {
    "sunset": ["FFFFF5EF", "FF4C3646", "FFEF8063", "FFFFD48A", "FFE5454E", "FF8B79B9"],
    "mint": ["FFF1FBF3", "FF294D4A", "FF6BC0A0", "FFBBE9D4", "FF36A6B9", "FFF8CE68"],
    "blue": ["FFF0F8FF", "FF2F405C", "FF70A9DB", "FFB9DCF7", "FF52BACA", "FFFFDB74"],
    "gold": ["FFFFF9EC", "FF4C3F48", "FFE6B45E", "FFFFD991", "FFFF876A", "FF967BCE"],
    "pink": ["FFFFF3F8", "FF533E57", "FFE884AE", "FFFFC4D9", "FFAB82DC", "FFFFDD88"],
    "purple": ["FFF6F3FF", "FF383958", "FF9B8DDE", "FFD6C8FC", "FF6BC3CD", "FFFFD37D"],
    "forest": ["FFF5F9EF", "FF3A4A3F", "FF75AC74", "FFBCDC98", "FFFFD07D", "FF88BEE1"],
    "rainbow": ["FFFFF8ED", "FF393B58", "FFED7B92", "FFFFCE77", "FF77BBE2", "FF79C59B"],
}

# Each entry defines an independently designed, exact 12x12 static picture.
# The color-by-number level never changes; animation patches are optional overlays.
ARTWORKS = json.loads(r'''[
  {
    "slug": "traffic-light",
    "fa": "چراغ راهنمایی",
    "en": "Traffic Light",
    "category": "objects",
    "theme": "sunset",
    "rows": [
      "....####....",
      "....#oo#....",
      "....#==#....",
      "....#oo#....",
      "....#==#....",
      "....#oo#....",
      "....#==#....",
      "....#oo#....",
      "....####....",
      ".....##.....",
      ".....##.....",
      "....####...."
    ]
  },
  {
    "slug": "battery-charge",
    "fa": "باتری شارژی",
    "en": "Charging Battery",
    "category": "objects",
    "theme": "mint",
    "rows": [
      "............",
      "..########..",
      "..#......#..",
      "..#......###",
      "..#..+...###",
      "..#..+*..#..",
      "..#.+o...#..",
      "..#......#..",
      "..#......#..",
      "..########..",
      "............",
      "............"
    ]
  },
  {
    "slug": "wifi-signal",
    "fa": "علامت وای‌فای",
    "en": "Wi-Fi Signal",
    "category": "objects",
    "theme": "blue",
    "rows": [
      "............",
      ".##########.",
      ".##......##.",
      "..########..",
      "...#....#...",
      "...######...",
      "....#..#....",
      "....####....",
      ".....##.....",
      ".....**.....",
      "............",
      "............"
    ]
  },
  {
    "slug": "ringing-bell",
    "fa": "زنگ اعلان",
    "en": "Notification Bell",
    "category": "objects",
    "theme": "gold",
    "rows": [
      "............",
      ".....##.....",
      "....#oo#....",
      "...#oooo#...",
      "...#oooo#...",
      "...#oooo#...",
      "..#oooooo#..",
      "..########..",
      "....#oo#....",
      ".....##.....",
      "............",
      "............"
    ]
  },
  {
    "slug": "love-envelope",
    "fa": "نامه عاشقانه",
    "en": "Love Letter",
    "category": "objects",
    "theme": "pink",
    "rows": [
      "............",
      "............",
      "..########..",
      "..#*....*#..",
      "..##*..*##..",
      "..#o#**#o#..",
      "..#oo##oo#..",
      "..#oooooo#..",
      "..#oooooo#..",
      "..########..",
      "............",
      "............"
    ]
  },
  {
    "slug": "pixel-pointer",
    "fa": "اشاره‌گر پیکسلی",
    "en": "Pixel Pointer",
    "category": "objects",
    "theme": "purple",
    "rows": [
      "..#.........",
      "..##........",
      "..#o#.......",
      "..#oo#......",
      "..#ooo#.....",
      "..#oooo#....",
      "..#ooooo#...",
      "..#ooo###...",
      "..#o##o#....",
      "..###.#o#...",
      "......###...",
      "............"
    ]
  },
  {
    "slug": "little-candle",
    "fa": "شمع روشن",
    "en": "Glowing Candle",
    "category": "objects",
    "theme": "sunset",
    "rows": [
      ".....*......",
      "....***.....",
      "....*+*.....",
      ".....*......",
      "....####....",
      "....#oo#....",
      "....#oo#....",
      "....#oo#....",
      "....#oo#....",
      "....#oo#....",
      "...######...",
      "............"
    ]
  },
  {
    "slug": "watering-can",
    "fa": "آبپاش کوچک",
    "en": "Watering Can",
    "category": "objects",
    "theme": "mint",
    "rows": [
      "............",
      "............",
      "....####....",
      "...#oooo#...",
      "..##oooo##..",
      ".#.#oooo#.#.",
      ".#.######.#.",
      "..##oooo##..",
      "...#oooo#...",
      "...######...",
      "........##..",
      ".........##."
    ]
  },
  {
    "slug": "mailbox",
    "fa": "صندوق نامه",
    "en": "Mailbox",
    "category": "objects",
    "theme": "pink",
    "rows": [
      "............",
      "....######..",
      "...#oooooo#.",
      "..#oooooooo#",
      "..#oooooooo#",
      "..#oooo#####",
      "..#########.",
      ".....##.....",
      ".....##.....",
      "...######...",
      "............",
      "............"
    ]
  },
  {
    "slug": "tiny-padlock",
    "fa": "قفل کوچک",
    "en": "Little Padlock",
    "category": "objects",
    "theme": "blue",
    "rows": [
      "....####....",
      "...#....#...",
      "..#......#..",
      "..#......#..",
      "..#......#..",
      "..########..",
      "..#oooooo#..",
      "..#oo##oo#..",
      "..#oo##oo#..",
      "..#oooooo#..",
      "..########..",
      "............"
    ]
  },
  {
    "slug": "mini-joystick",
    "fa": "جوی‌استیک",
    "en": "Mini Joystick",
    "category": "objects",
    "theme": "purple",
    "rows": [
      ".....##.....",
      ".....##.....",
      "....#oo#....",
      ".....##.....",
      ".....##.....",
      ".....##.....",
      "..########..",
      ".#oooooooo#.",
      "#oooo##oooo#",
      "#oooo##oooo#",
      ".##########.",
      "............"
    ]
  },
  {
    "slug": "singing-mic",
    "fa": "میکروفون آواز",
    "en": "Singing Microphone",
    "category": "objects",
    "theme": "gold",
    "rows": [
      "....####....",
      "...#oooo#...",
      "...#oooo#...",
      "...#oooo#...",
      "...#oooo#...",
      "....####....",
      "..#......#..",
      "..##....##..",
      "....####....",
      ".....##.....",
      "...######...",
      "............"
    ]
  },
  {
    "slug": "snow-globe",
    "fa": "گوی برفی",
    "en": "Snow Globe",
    "category": "objects",
    "theme": "blue",
    "rows": [
      "....####....",
      "..##....##..",
      ".#..*.....#.",
      ".#.....*..#.",
      "#....oo....#",
      "#...oooo...#",
      "#..o****o..#",
      ".#..oooo..#.",
      "..##....##..",
      "...######...",
      "..########..",
      "............"
    ]
  },
  {
    "slug": "night-tent",
    "fa": "چادر شبانه",
    "en": "Camping Tent",
    "category": "nature",
    "theme": "forest",
    "rows": [
      "..*.......*.",
      "............",
      ".....##.....",
      "....#oo#....",
      "...#oooo#...",
      "..#oooooo#..",
      ".##oooooo##.",
      ".###oooo###.",
      ".##o####o##.",
      "###########.",
      "............",
      "............"
    ]
  },
  {
    "slug": "satellite-dish",
    "fa": "بشقاب ماهواره‌ای",
    "en": "Satellite Dish",
    "category": "space",
    "theme": "purple",
    "rows": [
      "............",
      ".......*....",
      "............",
      "...######...",
      "..#oooooo#..",
      "..##oooo##..",
      "....####....",
      "......##....",
      "......##....",
      "....######..",
      "..########..",
      "............"
    ]
  },
  {
    "slug": "fish-bowl",
    "fa": "تنگ ماهی",
    "en": "Fish Bowl",
    "category": "animals",
    "theme": "blue",
    "rows": [
      "...######...",
      "..#......#..",
      ".#........#.",
      ".#........#.",
      ".#.oooo...#.",
      ".#o*o##...#.",
      ".#.oooo...#.",
      ".#........#.",
      "..#......#..",
      "...######...",
      "....####....",
      "............"
    ]
  },
  {
    "slug": "lighthouse-beam",
    "fa": "فانوس دریایی",
    "en": "Lighthouse Beam",
    "category": "objects",
    "theme": "sunset",
    "rows": [
      ".....##.....",
      "....#**#....",
      "....####....",
      ".....##.....",
      "....#oo#....",
      "....#==#....",
      "....#oo#....",
      "....#==#....",
      "...##oo##...",
      "..########..",
      ".##########.",
      "............"
    ]
  },
  {
    "slug": "spinning-top",
    "fa": "فرفره چرخان",
    "en": "Spinning Top",
    "category": "objects",
    "theme": "pink",
    "rows": [
      ".....##.....",
      ".....##.....",
      "...######...",
      "..#oooooo#..",
      ".#oo****oo#.",
      ".#oo++++oo#.",
      "..#oooooo#..",
      "...######...",
      "....#oo#....",
      ".....##.....",
      ".....##.....",
      "............"
    ]
  },
  {
    "slug": "little-snail",
    "fa": "حلزون کوچولو",
    "en": "Little Snail",
    "category": "animals",
    "theme": "forest",
    "rows": [
      "............",
      ".......#.#..",
      ".......#.#..",
      "......#*#*#.",
      "....######..",
      "...#oooooo#.",
      "..#o****oo#.",
      "..#o*##*oo#.",
      ".##oooooo##.",
      "#oooooooooo#",
      ".##########.",
      "............"
    ]
  },
  {
    "slug": "color-pinwheel",
    "fa": "فرفره رنگی",
    "en": "Color Pinwheel",
    "category": "objects",
    "theme": "rainbow",
    "rows": [
      "............",
      "...##.......",
      "..#oo#...##.",
      "...#oo#.#oo#",
      "....#oo#oo#.",
      "...##o**o##.",
      "..#oo#**#...",
      ".#oo#.#oo#..",
      ".##....#oo#.",
      "........##..",
      ".....##.....",
      ".....##....."
    ]
  }
]''')


def make_level(item):
    rows = item["rows"]
    if len(rows) != 12 or any(len(row) != 12 for row in rows):
        raise ValueError(item["slug"] + ": picture must be exactly 12x12")
    if any(set(row) - SYMBOLS.keys() for row in rows):
        raise ValueError(item["slug"] + ": unknown pixel color")
    cells = [SYMBOLS[c] for row in rows for c in row]
    if len(set(cells)) < 3 or sum(c != 0 for c in cells) < 16:
        raise ValueError(item["slug"] + ": too few visible colors/pixels")
    level = {
        "schemaVersion": 2,
        "levelId": PREFIX + item["slug"],
        "levelVersion": 1,
        "titles": {"fa": item["fa"], "en": item["en"]},
        "width": 12,
        "height": 12,
        "palette": PALETTES[item["theme"]],
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    return level


def animated_cells(level, motion, phase):
    """Return a full pose. Each animation frame is then delta-coded from the base.

    Phase sequence 0,1,2,3,4,5,6,7 -> 0. No mutation of the numbered level.
    Effects remain in the same 12x12 palette and are replayable entirely offline.
    """
    base = level["cells"]
    result = base[:]
    if phase == 0:
        return result

    def dot(x, y, color):
        if 0 <= x < 12 and 0 <= y < 12:
            result[y * 12 + x] = color

    def points(coords, color):
        for x, y in coords:
            dot(x, y, color)

    def rect(x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                dot(x, y, color)

    swing = [0, 1, 2, 3, 4, 3, 2, 1][phase]
    blink = 4 if phase % 2 else 3

    if motion == "traffic-light":
        # A real traffic light sequence: top -> middle -> bottom -> middle.
        active = [2, 2, 5, 8, 8, 5, 2, 2][phase]
        for y in (2, 5, 8):
            dot(5, y, 4 if y == active else 5)
            dot(6, y, 3 if y == active else 2)
    elif motion == "battery-charge":
        # Charging bar grows from left to right, then drains for a clean loop.
        width = [0, 2, 4, 6, 7, 6, 4, 2][phase]
        rect(3, 4, 3 + width - 1, 7, 4)
        dot(3 + min(width, 6), 5, 3)
    elif motion == "wifi-signal":
        for y, dots in ((2, range(2, 10)), (4, range(3, 9)),
                        (6, range(4, 8)), (8, range(5, 7))):
            if (10 - y) // 2 <= swing:
                for x in dots:
                    if base[y * 12 + x] != 0:
                        dot(x, y, 4)
    elif motion == "ringing-bell":
        # Clapper and two ringing arcs pulse outward.
        dot(5 + (phase % 3) - 1, 9, 4)
        if swing >= 1:
            points(((1, 4), (10, 4)), 4)
        if swing >= 2:
            points(((0, 3), (11, 3)), 5)
        if swing >= 3:
            points(((1, 7), (10, 7)), 3)
    elif motion == "love-envelope":
        # A tiny heart rises out of the sealed envelope.
        y = 3 - min(swing, 3)
        points(((5, y), (6, y), (5, y - 1), (6, y - 1)), 4)
        if swing >= 3:
            points(((4, 1), (7, 1)), 3)
    elif motion == "pixel-pointer":
        # Click: gold press point with expanding corner sparkles.
        dot(7, 6, 4)
        if swing >= 1:
            points(((9, 5), (9, 7)), 4)
        if swing >= 2:
            points(((10, 4), (10, 8)), 3)
        if swing >= 3:
            points(((7, 2), (10, 2)), 5)
    elif motion == "little-candle":
        # Flame flickers left/right, glowing softly on the candle body.
        dot(5, 1, 0)
        dot(5 + (-1 if phase % 2 else 1), 1, 4)
        dot(5, 2, blink)
        if swing >= 3:
            points(((3, 2), (8, 2)), 3)
    elif motion == "watering-can":
        # Water droplets fall from the spout into a little puddle.
        y = 7 + (phase % 4)
        points(((10, y), (11, min(y + 1, 11))), 4)
        if swing >= 2:
            points(((9, 11), (10, 11)), 3)
    elif motion == "mailbox":
        # Mail notification: the flag flips up and sparkle appears.
        points(((9, 1), (9, 2), (9, 3)), 1 if swing >= 2 else 3)
        if swing >= 2:
            points(((8, 1), (10, 1)), 4)
        if swing >= 3:
            points(((5, 4), (6, 4)), 5)
    elif motion == "tiny-padlock":
        # The shackle lifts temporarily without changing the base artwork.
        if swing >= 2:
            rect(3, 1, 8, 1, 0)
            points(((3, 0), (4, 0), (7, 0), (8, 0)), 1)
            points(((3, 1), (8, 1)), 2)
        dot(5, 8, blink)
    elif motion == "mini-joystick":
        # Stick tilts: a tiny action icon with left/right emphasis.
        x = [5, 4, 3, 4, 5, 6, 7, 6][phase]
        rect(5, 0, 6, 3, 0)
        points(((x, 1), (x, 2), (x + 1, 1), (x + 1, 2)), 4)
        dot(3 if x < 5 else 8, 9, 5)
    elif motion == "singing-mic":
        # Equalizer-like sound waves emerge symmetrically from the mic.
        if swing >= 1:
            points(((2, 3), (9, 3)), 4)
        if swing >= 2:
            points(((1, 4), (10, 4)), 5)
        if swing >= 3:
            points(((0, 5), (11, 5)), 4)
        dot(5, 2, blink)
    elif motion == "snow-globe":
        # Falling snow, kept inside the transparent globe.
        for x, y in ((4, 3), (7, 4), (5, 6)):
            dot(x, y, 0)
        points(((3 + phase % 3, 2 + phase % 3),
                (8 - phase % 3, 3 + phase % 4)), 3)
        dot(5, 7, blink)
    elif motion == "night-tent":
        # Calm campfire in front of the tent and twinkling stars.
        points(((2, 0), (9, 0)), blink)
        dot(5, 6, 4 if swing >= 2 else 3)
        dot(6, 6, 5 if swing >= 3 else 4)
        if swing >= 3:
            dot(10, 3, 5)
    elif motion == "satellite-dish":
        # Transmission pulses extend away from the dish.
        if swing >= 1:
            points(((8, 2), (9, 2)), 4)
        if swing >= 2:
            points(((9, 1), (10, 2)), 3)
        if swing >= 3:
            points(((10, 0), (11, 1)), 4)
        dot(7, 1, blink)
    elif motion == "fish-bowl":
        # Fish swims gently; translucent bubbles rise.
        rect(2, 4, 8, 7, 0)
        x = [2, 3, 4, 5, 6, 5, 4, 3][phase]
        points(((x, 5), (x + 1, 5), (x + 2, 5),
                (x + 1, 6), (x + 3, 4), (x + 3, 6)), 2)
        dot(x + 1, 5, 3)
        dot(x + 3, 3 - phase % 2, 4)
    elif motion == "lighthouse-beam":
        # Sweeping warm light: left to right and back.
        x = [2, 3, 4, 6, 9, 8, 6, 4][phase]
        points(((x, 1), (x - 1, 2), (x + 1, 2)), 4)
        dot(5, 2, 3)
        if swing >= 3:
            points(((0, 8), (11, 8)), 5)
    elif motion == "spinning-top":
        # Toy's center wobbles with rotating edge sparks.
        x = [5, 4, 5, 6, 6, 5, 4, 5][phase]
        points(((x, 4), (x + 1, 4), (x, 5)), 4)
        dot(2 + (phase % 4) * 2, 7, 5)
        if swing >= 2:
            points(((2, 2), (9, 2)), 3)
    elif motion == "little-snail":
        # Soft antenna wiggle and a glimmer sliding around the shell.
        x = 7 + (phase % 3) - 1
        dot(x, 2, 4)
        dot(9, 3, blink)
        dot(4 + swing, 7, 3)
    elif motion == "color-pinwheel":
        # Four blades alternate color phases; golden center glints.
        for x, y in ((3, 3), (8, 3), (3, 8), (8, 8)):
            dot(x, y, 2 + ((x + y + phase) % 4))
        dot(5, 5, blink)
        dot(6, 5, 4 if phase % 2 else 5)
        if swing >= 3:
            points(((1, 1), (10, 10)), 3)
    else:
        raise ValueError("Unknown motion: " + motion)
    return result


SCENARIOS = {
    "traffic-light": ("چراغ‌ها به ترتیب تغییر می‌کنند.", "The signal cycles between lights."),
    "battery-charge": ("نوار باتری شارژ و خالی می‌شود.", "The battery fills and drains."),
    "wifi-signal": ("سیگنال به شکل موجی تقویت می‌شود.", "Wi-Fi waves radiate out."),
    "ringing-bell": ("زنگ با خطوط لرزش صدا می‌دهد.", "The bell vibrates and rings."),
    "love-envelope": ("قلب کوچکی از نامه بالا می‌رود.", "A little heart floats out of the letter."),
    "pixel-pointer": ("اشاره‌گر با جرقه‌ای کلیک می‌کند.", "A click ripple appears at the pointer."),
    "little-candle": ("شعله شمع به‌آرامی می‌لرزد.", "The candle flame flickers."),
    "watering-can": ("چند قطره آب از آبپاش می‌چکد.", "Water droplets drip from the can."),
    "mailbox": ("پرچم صندوق بالا می‌رود.", "The mailbox flag rises."),
    "tiny-padlock": ("قفل باز و دوباره بسته می‌شود.", "The padlock briefly unlocks."),
    "mini-joystick": ("دسته بازی به چپ و راست می‌رود.", "The joystick tilts left and right."),
    "singing-mic": ("موج صدا از میکروفون پخش می‌شود.", "Sound waves pulse from the mic."),
    "snow-globe": ("دانه‌های برف در گوی شناور می‌مانند.", "Snowflakes drift inside the globe."),
    "night-tent": ("ستاره‌ها بالای چادر چشمک می‌زنند.", "Stars twinkle above the tent."),
    "satellite-dish": ("امواج مخابره از بشقاب پخش می‌شوند.", "Transmission pulses leave the dish."),
    "fish-bowl": ("ماهی در تنگ حرکت می‌کند.", "A fish swims and releases a bubble."),
    "lighthouse-beam": ("نور فانوس به اطراف می‌تابد.", "The lighthouse beam sweeps across the sky."),
    "spinning-top": ("فرفره می‌چرخد و برق می‌زند.", "The spinning top wobbles and sparkles."),
    "little-snail": ("شاخک‌های حلزون تکان می‌خورند.", "The snail's antennae wiggle."),
    "color-pinwheel": ("پره‌های فرفره به نوبت رنگ عوض می‌کنند.", "The pinwheel blades shimmer in rotation."),
}


def animation_frames(level, motion):
    base = level["cells"]
    frames = []
    for phase in range(8):
        pose = animated_cells(level, motion, phase)
        frames.append({"changes": [[pos, value] for pos, value in enumerate(pose)
                                   if value != base[pos]]})
    return frames


def build(destination):
    pictures = []
    assets = {}
    scenarios = {}
    for item in ARTWORKS:
        level = make_level(item)
        motion = item["slug"]
        frames = animation_frames(level, motion)
        animation = {
            "schemaVersion": 1,
            "levelId": level["levelId"],
            "levelVersion": 1,
            "levelChecksum": level["checksum"],
            "frameDurationMs": FRAME_DURATION_MS,
            "frames": frames,
        }
        level_blob = compact(level)
        animation_blob = compact(animation)
        stem = level["levelId"] + "-v1"
        pictures.append({
            "id": level["levelId"], "version": 1,
            "title": item["fa"], "titleEn": item["en"],
            "category": item["category"], "width": 12, "height": 12,
            "bytes": len(level_blob), "checksum": level["checksum"],
            "animation": {
                "bytes": len(animation_blob),
                "sha256": hashlib.sha256(animation_blob).hexdigest(),
                "frameCount": len(frames),
            },
        })
        assets["levels/" + stem + ".json"] = level_blob
        assets["previews/" + stem + ".png"] = png(level)
        assets["animations/" + stem + ".json"] = animation_blob
        fa, en = SCENARIOS[motion]
        scenarios[level["levelId"]] = {
            "titleFa": item["fa"], "titleEn": item["en"],
            "frameDurationMs": FRAME_DURATION_MS, "frameCount": 8,
            "loop": "0→1→2→3→4→5→6→7→0",
            "scenarioFa": fa, "scenarioEn": en,
        }
    validate_new_pack_manifest(pictures)
    destination = pathlib.Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({"schemaVersion": 1, "pictures": pictures}))
        for name, data in assets.items():
            archive.writestr(name, data)
        archive.writestr("animation-scenarios.json", compact({
            "schemaVersion": 1, "scenarios": scenarios,
        }))
    print(f"Created {len(pictures)} animated 12x12 online pictures: {destination}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_animated_12_pack.py <content.zip>")
    build(sys.argv[1])
