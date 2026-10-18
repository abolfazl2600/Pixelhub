#!/usr/bin/env python3
"""Publish detailed, immutable replacements for three online animal paintings.

The artwork was converted from the approved pixel-art references into opaque
color-by-number grids. New IDs preserve the checksum-bound historical releases.
"""
import base64
import pathlib
import sys
import zipfile
import zlib

from online_release import checksum, compact, png, validate_new_pack_manifest

ARTWORKS = (
    (
        "online-elephant-detailed", "فیل مهربان", "Gentle Elephant", 48,
        [
            "FFE3F7F2", "FF8EA3B2", "FF708CA3", "FF99B3C9",
            "FFF4A5AF", "FF59738C", "FFB2C7D4", "FF516471",
            "FF354E62", "FF6A9A5B", "FF9DC968", "FFADD1A1",
            "FF87B46A", "FFDA7790", "FF24384D", "FFC7DFB6",
        ],
        "eNrtVdGSpDAIBCIBTUz+/2+vSdRx7pzdfbyqO6waTWygaYhD9N/+UmMR5h8hMy42lZQy5x8EVmFxBRqm33lk4RxIMcTHA39NKgMVvDklM8kR/KsMWZMo7ftOlNKkRCSf8ZaE9gW2E9BpOnxmxJx4WSZ+8J9Ff8SDzQHfzwTwIHmuQMyO6GHUovRoQtZn2XN6w7sAbg4H4SfqhEB6wfcdBRhbKJtsAn6DIz3d8ChAAeRJSN4axwq9E8ZgoQu/gx1Twy7ekum9cUMLRFC7E1oWRr2cBhfVl66iKY9ZEfWLEuIjyBxTINny1WiUBpqRAA7tbJlBTdAWRJJEWJy6cuODDw6J+sHJXKHn4AoHjC3bSccxCAN+d2jukYyiBpSQkxx4yCYHejCaDgjvLohLJTIgnvFZbZMDOxMA6INMANhwNDnF9qGlC1xjNOOIIyLeKGQJreaZ8NiwQx21ljErowLRQEOXaKq4n4IrcrweUZPqSDDxcB6SuD4MJiSwGOWTOhLHtyGmvqn9OZi52ezYCB9Mven4NAz9HwY5piiHciLeQhizQQjO/HhSqGP6QpoBzzGLmAEixNfHo1soRiVzAx0b/Q6BElazpVt5Q5ey2qQTEUHZPM5tfLDQwVKpUuk3h1qBwzhBK4hkayxTfHN94b6GweeybcOGa++MuHWtZuYG3rg8sHht+D05lRqLul62TUB9rbe1bqvVF/9e4IEqgIonYLfYqPiJaLj3Up50KkNc+HTcqMPg+C//yf4CGRoT9w=="
    ),
    (
        "online-penguin-detailed", "پنگوئن برفی", "Snowy Penguin", 48,
        [
            "FFACDAF9", "FFE8F3F9", "FF1F3253", "FF32496F",
            "FF557094", "FF708AA6", "FF98B5D0", "FF969DAC",
            "FF0E1B37", "FFEEA656", "FFF79831", "FF3B5988",
            "FF475973", "FFE2762D", "FFF1D0AD", "FFFECC67",
        ],
        "eNq9ldm2IiEMRRMIFMWg//+3fQI1QIF6nzoPLsGdcDKARP/Z+Mf6lzvzn8L++GEI4121mVnyToyatVn8HwRLAJpsEoGf/1marHi16uAWKXD3BfihJonBMWbm+zRESdscrLEZn98kuWAcMt/aGRsi4ZAvfK44sztwmJw5r/oWFBeAkCRwUxcjiz63RTakUPCqCB9bdToO4Dln/XlzHJoSdpytHuBW41B5yBFnTh61hfeSP7LV+FsA/4KBt96D/9Rlq6Jrlnt87xEOvhYouHV/0ZyNtRDA39WhFjQdgq4CDXy1Eve97EcW6VMC6OXh8CrxxAVz4T/MprkceKcLV/n8FFM3vM6+59sIfavZXjwPfdbJFLp53zb6W9g5eOgZ8OqQbof+5Fqf1DrQGWogZ3145F0Sqx0eDBJFkNNIc70kModvB4jl2XTb5Glbi5ysTPvOSrLnZA5xgj4vnZxWU5OsXciBoHAecLdBeeBhxeM+aJn50V5tzNjci7fZXPw1pw533RzPw9AxAdtGroJ3u5iCSXOZkS9aT32yd63T8wBCkRdFOyw/xgdy0hdcFclT/dTbfpQoU4zn6rXHEtyCpuvbDouFNvIoSIm4xvvrOcm3m8fD8HrDQ5JghkHrO7HRYv7bfSwIGWMpvsUvdbGtYJ7+Z7H20Ofni/K8mmcfaaWc+pu/KsMclx5FbWFornnPjI/Lx8T4H+rfDoY="
    ),
    (
        "online-parrot-detailed", "طوطی رنگارنگ", "Colorful Parrot", 48,
        [
            "FFDCF5EB", "FF5BA254", "FF70AD96", "FFAEDACB",
            "FF9ACEB4", "FF265C55", "FF98CE4C", "FF125DA4",
            "FF2A99D9", "FF5C6261", "FF8F5439", "FF163157",
            "FF5B3429", "FF91AEA2", "FFF2E958", "FFA36B4A",
        ],
        "eNqtVtuS6jAMs504l6ah//+3R3IKSwsPZ2c2CzvQyjdZdhH5s5N/idcCm/QbvKpp+b8wcGxeioqUebNI32K6qJgoTiky786YZsrvySZHQoqcSnk8vhic5+eSBVbkwXMzSC/8K0L/uUsDvcAtJ8M7pWcAc+RC7yLH2BjA3vBmkyVEDen07k76H5GYfOCz2CV5ma4reRA1EMRmesdLtku1ZAfEhOPR5fA++zsVNElM6wVXFhABkNToOBeGFt7ST7NWQkEOLvTuV3ymjdlZrbrT5jTwAYNxxcNzPvEgp0IkFgyd3fALQaduo4CMe61FV5begJ6o4JsoGQXBG/F4RQmMMT8EJG+RgU6AN1RBDVGjH7BnN9Kgb8CtWVEPVr8IOuVzCLw2ZgOwlVLRNCmPQnlehwTwVXHAG+DAkyDKP/yvEUlrvjgq/Dxrk1rD/Vnvg3gwDHcwyNGpAOM7vrQqhNNLbdUjn8LBZMIrB3Y1nyM5Kk5r1WgYC4XlqqdnDqupbGtacOZTa8DHor+UmLUcbnO4jwBMATgWTAso6FwOdB9iNNPTfeApkDtcuSPshDO9ZEudqNYqAwCObgZc1uuZDVsNdeGDGtJKycdgQoDUUHO8HDkn+mcvcGs7tm3rygHwgQiA1zZiYDjzztZChklDrBn4A+O8qVknHD3C+wkPaSZuM/ZOA79thxwH/u3DUSg4Bcy9e5wcmwBCX8WL7DtMIgYXJkroHZdQZOcYd0tprT0oVEnLxO0dBscBRljxxvRg0He2rHcWq/3oCqPV444g+x7wOnaaIiSggqgdgzj7tu09q84lIhCKa044cke0Df6x1QBHTeRv2+ckB8oQ5DIzNvlxjC+j7RJmW+jk2Jk95Udhuma0zykfIeGtjtlZ9bYOucCfUa8F5LrlaDGGBboZNaQM4kmELAJBACcY4s5UMrm1ROGjudJGej5/M0jayYegApjoeiavjQHte/Gn+9dDNaYmwQQRLBbLJPx07yj5ugngrUATx/7acEx+zSvcy7g9Xalpbup+vP9OYLFwP2LIr6tJ48F6P5H3R/ZhMFnofR0ye/TqtrY/fwH8A33mGko="
    ),
)


def decode_cells(side, encoded):
    cells = list(zlib.decompress(base64.b64decode(encoded)))
    if len(cells) != side * side:
        raise ValueError(f"Invalid cell count for {side}x{side} artwork")
    return cells


def create_pack(destination):
    manifest = []
    files = {}
    for ident, title_fa, title_en, side, palette, encoded in ARTWORKS:
        cells = decode_cells(side, encoded)
        if not palette or max(cells, default=0) >= len(palette):
            raise ValueError(f"Invalid palette indexes for {ident}")
        level = {
            "schemaVersion": 2,
            "levelId": ident,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": side,
            "height": side,
            "palette": palette,
            "cells": cells,
        }
        level["checksum"] = checksum(level)
        body = compact(level)
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident,
            "version": 1,
            "title": title_fa,
            "titleEn": title_en,
            "category": "animals",
            "width": side,
            "height": side,
            "bytes": len(body),
            "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = body
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({
            "schemaVersion": 1,
            "pictures": manifest,
        }))
        for name, payload in files.items():
            archive.writestr(name, payload)
    print(f"Created {len(manifest)} detailed animal replacements: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_animal_redesigns_pack.py <content.zip>")
    create_pack(sys.argv[1])
