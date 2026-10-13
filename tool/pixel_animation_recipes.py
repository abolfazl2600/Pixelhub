#!/usr/bin/env python3
"""Deterministic palette-only motion; each sparse frame patches the original."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSES = [0, 1, 2, 1, 0, -1, -2, -1, 0, 0, 0, 0]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def animation(level, recipe):
    w, h = level["width"], level["height"]
    original = level["cells"]
    palette = [tuple(bytes.fromhex(c[2:])) for c in level["palette"]]
    motion = recipe["motion"]
    region = recipe.get("region", [0.12, 0.12, 0.88, 0.88])
    x0, y0, x1, y1 = region
    selected = [(x, y) for y in range(h) for x in range(w)
                if x0 <= (x + .5) / w <= x1 and y0 <= (y + .5) / h <= y1
                and original[y * w + x] != 0]
    frames = []
    for index, pose in enumerate(POSES):
        cells = original[:]
        if pose and motion in {"sway", "float", "pulse", "flap", "spin"}:
            for x, y in selected:
                cells[y * w + x] = 0
            if motion in {"pulse", "flap", "spin"}:
                # Inverse sampling fills every destination pixel. Forward
                # scaling/rotation leaves holes between enlarged source cells.
                cx, cy = w * .5, h * .5
                scale = 1 + pose * .065 if motion == "pulse" else 1 - abs(pose) * .12
                angle = -pose * .055
                for y in range(h):
                    for x in range(w):
                        dx, dy = x - cx, y - cy
                        if motion == "spin":
                            sx = round(cx + dx * math.cos(angle) - dy * math.sin(angle))
                            sy = round(cy + dx * math.sin(angle) + dy * math.cos(angle))
                        else:
                            sx = round(cx + dx / scale)
                            sy = round(cy + dy / scale) if motion == "pulse" else y
                        if (0 <= sx < w and 0 <= sy < h and
                                x0 <= (sx + .5) / w <= x1 and
                                y0 <= (sy + .5) / h <= y1 and original[sy * w + sx] != 0):
                            cells[y * w + x] = original[sy * w + sx]
            else:
                for x, y in selected:
                    px, py = x, y
                    if motion == "sway":
                        px += round(pose * max(1, round(w / 48)) *
                                    (y1 - (y + .5) / h) / max(.1, y1 - y0))
                    else:
                        py += round(pose * max(1, h / 64))
                    if 0 <= px < w and 0 <= py < h:
                        cells[py * w + px] = original[y * w + x]
        elif motion == "blink" and index in [3, 4]:
            for x, y in selected:
                nx, ny = (x + .5) / w, (y + .5) / h
                eyes = recipe.get("eyes")
                inside = any(((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 <= 1
                             for cx, cy, rx, ry in eyes) if eyes else (
                    (.29 <= nx <= .42 or .58 <= nx <= .71) and .38 <= ny <= .55)
                if inside:
                    r, g, b = palette[original[y * w + x]]
                    if max(r, g, b) < 110:
                        above = original[max(0, y - max(1, h // 32)) * w + x]
                        if above != 0 and max(palette[above]) >= 110:
                            cells[y * w + x] = above
        elif motion in {"ripple", "glimmer", "flame", "steam", "rain", "sparkle"} and pose:
            if motion == "ripple":
                for x, y in selected:
                    r, g, b = palette[original[y * w + x]]
                    if b > r * 1.12 and b > 80 and (y + index) % max(3, h // 12) == 0:
                        sx = max(0, min(w - 1, x + (1 if pose > 0 else -1)))
                        cells[y * w + x] = original[y * w + sx]
            elif motion == "flame":
                for x, y in selected:
                    r, g, b = palette[original[y * w + x]]
                    if r > 180 and r > b * 1.4:
                        cells[y * w + x] = original[max(0, y - (1 if pose > 0 else 2)) * w + x]
            elif motion == "glimmer":
                bright = max(range(1, len(palette)), key=lambda c: sum(palette[c]))
                for x, y in selected:
                    r, g, b = palette[original[y * w + x]]
                    if sum((r, g, b)) > 400 and (x + y + index * 3) % 19 == 0:
                        cells[y * w + x] = bright
            elif motion == "steam":
                dark = min(range(1, len(palette)), key=lambda c: sum(palette[c]))
                for x, y in selected:
                    if (y + .5) / h < .32 and original[y * w + x] == dark:
                        cells[y * w + x] = 0
                        nx = max(0, min(w - 1, x + (1 if pose > 0 else -1)))
                        ny = max(0, y - abs(pose))
                        cells[ny * w + nx] = dark
            else:
                color = max(range(1, len(palette)), key=lambda c: sum(palette[c]))
                for k in range(4):
                    x = round(w * (.15 + k * .21))
                    y = round(h * (.12 + ((index + k * 3) % 9) * .075))
                    if 0 <= x < w and 0 <= y < h and original[y * w + x] == 0:
                        cells[y * w + x] = color
        frames.append({"changes": [[at, color] for at, color in enumerate(cells)
                                   if color != original[at]]})
    if not any(f["changes"] for f in frames):
        raise ValueError(f"Motion has no visible frames: {level['levelId']} ({motion})")
    return {"schemaVersion": 1, "levelId": level["levelId"],
            "levelVersion": level["levelVersion"], "levelChecksum": level["checksum"],
            "frameDurationMs": recipe.get("durationMs", 150), "frames": frames}


def write_bundled(recipes):
    source = ROOT / "apps/game/assets/levels"
    target = ROOT / "apps/game/assets/animations"
    target.mkdir(exist_ok=True)
    catalog = json.loads((target / "catalog.json").read_text()) if (target / "catalog.json").exists() else {}
    for filename in json.loads((source / "catalog.json").read_text()):
        level = json.loads((source / filename).read_text())
        ident = level["levelId"]
        if ident not in recipes:
            continue
        stem = f"{ident}-v{level['levelVersion']}.json"
        (target / stem).write_bytes(compact(animation(level, recipes[ident])))
        catalog[ident] = stem
    (target / "catalog.json").write_bytes(compact(catalog))
