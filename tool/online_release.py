#!/usr/bin/env python3
"""Build immutable downloadable packs and a Pages catalog, outside git history.

Usage:
  python3 tool/online_release.py sample /tmp/content.zip
  python3 tool/online_release.py assemble /tmp/release-packs /tmp/site/online

Only zip assets attached to pixelhub-content-* Releases are published.
No generated level/preview file is added to the git working tree.
New pictures have unique IDs and levelVersion 1. No content updates by ID.
"""
import hashlib
import json
import math
import pathlib
import re
import struct
import sys
import zipfile
import zlib

PALETTE = [
    "FFF3F8FF",  # pale sky
    "FF313C5B",  # outline
    "FFFF6D77",  # coral
    "FFFFB55C",  # apricot
    "FFFFE8AD",  # warm highlight
    "FF9AD7F0",  # sky accent
    "FFC88C62",  # basket
    "FF8C5D4A",  # ropes
]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def canonical(data):
    return [
        data["schemaVersion"],
        data["levelId"],
        data["levelVersion"],
        data["titles"]["fa"],
        data["titles"]["en"],
        data["width"],
        data["height"],
        data["palette"],
        data["cells"],
    ]


def checksum(data):
    return hashlib.sha256(compact(canonical(data))).hexdigest()


def png(level):
    width, height = level["width"], level["height"]
    palette = [bytes.fromhex(value[2:]) + bytes.fromhex(value[:2]) for value in level["palette"]]
    scanlines = b"".join(
        b"\x00" + b"".join(palette[level["cells"][y * width + x]] for x in range(width))
        for y in range(height)
    )

    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload +
                struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))

    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">2I5B", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(scanlines, 9)) + chunk(b"IEND", b""))


# The *only* historical exception, published before immutable-ID policy.
# Both released ZIPs remain untouched. The original v1 and redesigned v2
# assets retain their existing paths and checksums so prior downloads work.
LEGACY_AZADI_ID = "online-iran-azadi-tower"
LEGACY_AZADI_V1 = ("pixelhub-content-iran-landmarks-10-v1", 1)
LEGACY_AZADI_V2 = ("pixelhub-content-iran-z-architecture-11-v1", 2)


def valid_online_id(ident):
    return isinstance(ident, str) and re.fullmatch(
        r"online-[a-z0-9-]{1,64}", ident
    ) is not None


def validate_new_pack_manifest(pictures):
    """Require a fresh, single-publication ID and levelVersion=1 per entry.

    Cross-Release ID uniqueness is enforced by assemble(), which reads every
    published pack; a standalone generator cannot know remote Release IDs.
    """
    seen = set()
    for item in pictures:
        ident = item["id"]
        version = item["version"]
        if not valid_online_id(ident):
            raise ValueError(f"Invalid new online content ID: {ident}")
        if type(version) is not int or version != 1:
            raise ValueError(f"New picture must have levelVersion 1: {ident}")
        if ident in seen:
            raise ValueError(f"Duplicate online content ID in pack: {ident}")
        seen.add(ident)


def validate_archived_azadi_pack_manifest(pictures):
    """Reproduce the existing v2 Release, never use it for new designs."""
    legacy = [item for item in pictures if item["id"] == LEGACY_AZADI_ID]
    if len(legacy) != 1 or legacy[0]["version"] != 2:
        raise ValueError("Archived Azadi pack must contain only the legacy v2")
    validate_new_pack_manifest(
        [item for item in pictures if item["id"] != LEGACY_AZADI_ID]
    )


def sample(destination):
    side = 24
    cells = [0] * (side * side)

    def set_cell(x, y, color):
        if 0 <= x < side and 0 <= y < side:
            cells[y * side + x] = color

    # A fully original pixel-art hot-air balloon with numbered colors.
    for y in range(1, 17):
        for x in range(4, 20):
            dx = (x - 11.5) / 7.3
            dy = (y - 8.0) / 8.0
            distance = dx * dx + dy * dy
            if distance <= 1.0:
                if distance >= 0.78:
                    color = 1
                elif x < 8:
                    color = 3
                elif x < 12:
                    color = 2
                elif x < 16:
                    color = 3
                else:
                    color = 2
                if 6 <= x <= 8 and 4 <= y <= 6:
                    color = 4
                set_cell(x, y, color)
    for y in (16, 17):
        for x in range(10, 14):
            set_cell(x, y, 1)
    for y in range(18, 21):
        set_cell(9, y, 7)
        set_cell(14, y, 7)
    for y in range(20, 23):
        for x in range(9, 15):
            set_cell(x, y, 1 if x in (9, 14) or y == 22 else 6)
    for x, y in [(2, 5), (3, 5), (2, 6), (21, 12), (22, 12),
                 (21, 13), (3, 16), (4, 16)]:
        set_cell(x, y, 5)

    level = {
        "schemaVersion": 2,
        "levelId": "online-balloon",
        "levelVersion": 1,
        "titles": {"fa": "بالن رنگی", "en": "Colorful balloon"},
        "width": side,
        "height": side,
        "palette": PALETTE,
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    blob = compact(level)
    item = {
        "id": level["levelId"], "version": 1,
        "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
        "category": "objects", "width": side, "height": side,
        "bytes": len(blob), "checksum": level["checksum"],
    }
    validate_new_pack_manifest([item])
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({"schemaVersion": 1, "pictures": [item]}))
        archive.writestr("levels/online-balloon-v1.json", blob)
        archive.writestr("previews/online-balloon-v1.png", png(level))


def assemble(pack_dir, output_dir):
    root = pathlib.Path(pack_dir)
    destination = pathlib.Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    images = {}
    origins = {}
    for pack in sorted(root.glob("*/content.zip")):
        with zipfile.ZipFile(pack) as archive:
            manifest = json.loads(archive.read("catalog.json"))
            if manifest.get("schemaVersion") != 1:
                raise ValueError(f"Unsupported pack format: {pack}")
            for item in manifest["pictures"]:
                ident = item["id"]
                version = item["version"]
                if not valid_online_id(ident):
                    raise ValueError(f"Invalid online content ID: {ident}")
                origin = (pack.parent.name, version)
                previous = origins.get(ident)
                if ident == LEGACY_AZADI_ID and origin not in (
                    LEGACY_AZADI_V1, LEGACY_AZADI_V2
                ):
                    raise ValueError(f"Reserved historical online ID: {ident}")
                if previous is not None:
                    # Do not permit upgrades, even to higher levelVersion.
                    # Preserve exactly the one pre-policy Azadi v1->v2 pair.
                    if not (ident == LEGACY_AZADI_ID and
                            previous == LEGACY_AZADI_V1 and
                            origin == LEGACY_AZADI_V2):
                        raise ValueError(f"Duplicate online content ID: {ident}")
                elif type(version) is not int or version != 1:
                    raise ValueError(
                        f"New picture must have levelVersion 1: {ident}"
                    )
                stem = f"{ident}-v{version}"
                level_path = f"levels/{stem}.json"
                preview_path = f"previews/{stem}.png"
                body = archive.read(level_path)
                preview = archive.read(preview_path)
                data = json.loads(body)
                if (data["levelId"] != ident or data["levelVersion"] != version or
                    data["schemaVersion"] != 2 or
                    len(data["cells"]) != data["width"] * data["height"] or
                    any(not isinstance(c, int) or c < 0 or c >= len(data["palette"])
                        for c in data["cells"]) or
                    len(data["palette"]) > 48 or
                    data["checksum"] != checksum(data) or
                    data["checksum"] != item["checksum"] or
                    len(body) != item["bytes"] or
                    data["width"] != item["width"] or
                    data["height"] != item["height"] or
                    not preview.startswith(b"\x89PNG\r\n\x1a\n") or
                    len(body) > 262144):
                    raise ValueError(f"Invalid level or preview: {ident}")
                images[ident] = item
                origins[ident] = origin
                for name, payload in ((level_path, body), (preview_path, preview)):
                    file = destination / name
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_bytes(payload)
    catalog = {"schemaVersion": 1, "pictures": list(images.values())}
    (destination / "catalog.json").write_bytes(compact(catalog))
    print(f"Published {len(images)} online pictures.")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "sample":
        sample(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "assemble":
        assemble(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("Usage: online_release.py sample <zip> | assemble <pack-dir> <out-dir>")
