#!/usr/bin/env python3
"""Five manually redrawn 96x96 classic artworks, generated as pixel-grid recipes.

This source contains geometry and ARGB palettes, not scans or pre-rendered
pictures. The release job produces the level JSON, PNG thumbnails, and the four
originally supported animated companions. The mobile app version is unchanged.

Recipe commands: R=filled rectangle, E=ellipse, P=filled polygon,
L=pixel line, D=single pixel. Draw order is significant.
"""
import hashlib
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 96
PREFIX = "online-classic-detailed96-"
FRAME_DURATION_MS = 180

WORKS = (
    ("girl-pearl", "دختر با گوشواره مروارید", "Girl with a Pearl Earring",
     "Johannes Vermeer", "درخشش مروارید", "Pearl softly glows", False),
    ("boating-party", "مهمانی قایق‌سواری", "The Boating Party",
     "Mary Cassatt", "انعکاس آب و حرکت ملایم قایق",
     "Water glimmers and the boat rocks gently", True),
    ("childs-bath", "حمام کودک", "The Child's Bath",
     "Mary Cassatt", "درخشش و موج‌های ظریف آب",
     "Delicate ripples in the wash basin", True),
    ("whistlers-mother", "مادر ویسلر", "Whistler's Mother",
     "James McNeill Whistler", "حرکت نور روی پرده",
     "Soft light moves across the curtain", True),
    ("woman-parasol", "زن با چتر آفتابی", "Woman with a Parasol",
     "Claude Monet", "حرکت ابرها و نور روی چتر",
     "Clouds pass as the parasol shimmers", True),
)

# Each multiline block begins with its deliberately limited ARGB palette,
# followed by ordered raster instructions. These are editable source drawings.
DRAWINGS = {
"girl-pearl": """20222C 151D27 293A45 334D6B 1D4169 3D74A4 6BA7BE D3A331 E7BE49 F6D36A FFE99A 704737 986344 BA835E D5A177 EBC099 F5D2A7 FFE4BE 352C33 1D2A39 F8F7E7 C6D9D2 506677 D18F76
R0,0,95,95,0
R0,5,95,89,1
E50,45,35,47,0
P18:17,95;24,78;36,72;42,69;62,69;71,77;87,95
P4:14,95;28,76;39,74;61,77;76,84;86,95
P3:26,95;35,81;46,78;59,81;71,95
L29,83,68,91,5,1.3
L26,91,62,95,2,0.8
P18:30,30;31,53;27,68;38,78;56,78;69,67;72,46;57,25
E51,51,24,29,11
E54,51,20,26,12
P13:34,35;37,64;47,75;63,69;72,54;68,34;46,27
P14:43,30;39,43;41,62;48,68;55,70;57,58;53,40
P15:59,37;67,43;67,58;62,68;54,70;60,54
P15:45,39;48,53;47,64;55,67;62,62;62,42
E65,50,6,10,16
P15:49,39;60,36;67,41;70,52;74,57;67,59;64,67;55,71;47,65;45,48
P16:56,42;67,40;68,47;63,45
L67,47,70,53,13,0.8
L71,54,75,55,12,0.9
L75,55,72,58,12,0.8
D72,57,16
L56,47,64,46,18,0.75
L57,50,64,50,18,0.75
R60,50,62,52,1
D61,50,21
D64,50,16
L57,65,65,65,11,0.8
L60,67,65,66,22,0.7
D67,61,17
D55,57,16
D45,56,12
P4:29,36;31,24;44,12;57,13;61,25;45,38
P5:29,35;37,22;51,15;57,14;52,29;37,42
P6:33,29;45,17;53,17;46,23;37,37
P3:30,39;34,44;32,57;28,67;25,65
L29,40,36,33,21,0.8
L35,27,46,18,21,0.8
P7:39,19;54,9;73,7;88,16;90,27;77,29;69,37;50,38;39,31
P9:43,20;57,12;72,10;85,18;87,24;73,26;67,32;50,34
P10:47,16;61,12;73,12;80,16;70,17;59,16
P8:53,33;69,31;78,29;73,34;66,38;55,40
L42,30,49,34,8,0.8
L55,35,69,33,8,0.8
L72,25,85,23,8,0.8
P14:45,69;45,77;55,82;64,78;61,70
P17:35,78;43,80;54,83;64,78;69,85;59,91;39,89
L42,79,54,84,19,1.1
E41,72,4.3,4.7,21
E40,71,2.9,3.1,20
D39,70,19
D40,76,22
L40,78,43,82,18,0.7""",
"boating-party": """7BB5C7 B0D3D5 E8E3C9 FAF1D8 4C89A7 296987 1B465F 9C613C C88659 DCB387 E9D9B4 FFF3D5 D5BB98 EEC9A4 B77F5B 253C46 2C5268 496E7A E9563E 704F3A CBA17C F4E9CF 789CAA
R0,0,95,95,0
P3:64,0;95,0;95,60;81,46;67,33
P2:64,0;67,34;83,47;90,50;95,0
R0,51,95,95,4
R0,58,95,95,5
L3,66,21,65,0,1.0
L28,61,40,60,0,1.0
L64,72,84,71,0,1.0
L76,90,93,89,0,1.0
L0,90,25,89,0,1.0
L9,75,23,76,22,0.85
L42,67,58,68,22,0.85
L74,65,90,66,22,0.85
L53,87,69,88,22,0.85
P7:2,63;20,72;81,69;95,63;82,87;62,95;24,95;10,83
P8:5,66;26,76;84,73;91,66;78,85;58,90;28,90;13,80
P9:10,74;37,81;68,81;83,77;72,88;34,90
L6,68,26,76,19,1.2
L26,76,78,73,19,1.2
L24,89,64,90,19,1.2
L19,79,29,84,19,1.2
L59,88,72,84,19,1.2
L24,81,27,82,12,0.7
L35,85,38,86,12,0.7
L49,85,52,86,12,0.7
L62,84,65,85,12,0.7
L72,80,75,81,12,0.7
P15:67,40;79,38;88,50;91,69;82,70;73,61;63,57
P16:70,43;77,42;84,50;87,67;78,66;72,57;63,55
P17:73,45;78,44;79,58;76,59
E73,33,5.7,8.0,13
E74,32,4.2,7,9
R67,26,80,28,15
R71,21,78,26,16
R68,23,78,25,17
D76,32,15
L75,37,78,39,14,0.6
L77,52,89,59,15,2.2
L84,59,92,63,13,1.8
L78,64,84,78,15,2.3
L85,78,92,82,15,1.1
P10:18,41;34,42;44,63;46,77;11,76;9,58
P11:17,45;28,43;37,61;38,74;14,72
P2:14,55;17,52;16,68;11,75;8,67
P3:31,54;35,64;41,76;34,74
E25,36,7.7,9.4,13
E26,35,6,8,9
E26,29,11.8,3.5,10
P6:18,27;22,20;32,20;37,28
P17:18,27;20,22;31,22;35,27
D31,34,18
L28,41,33,43,14,0.7
P11:40,55;51,52;61,64;66,78;34,77
P3:43,59;50,56;57,68;60,75;42,75
E47,50,5.7,7,13
E47,49,4.5,5.7,9
P18:41,46;43,41;51,41;53,46
D49,50,15
D49,55,14
L42,58,37,67,13,2.2
L53,60,63,63,13,2.4
L61,63,72,58,13,1.6
L68,58,95,85,6,1.2
P15:86,75;95,83;95,88;90,85
L4,61,87,64,19,1.15
L5,62,89,65,8,0.8
L90,5,90,59,15,1.7
L90,12,96,18,15,0.9""",
"childs-bath": """9693A4 B9AFC0 715C69 573C44 9B6F66 CB9479 E0B39A F2D2B3 F8E2C9 FFF1D9 D1C4B7 52506A 77728D 9D8196 F3E8D5 6D596F 7B4B43 E8D8B8 7D9B9E BFDDDB 4B5660 DCA993
R0,0,95,95,0
P4:0,63;95,55;95,95;0,95
R0,64,95,72,3
R0,67,95,69,5
R0,74,95,77,2
R0,77,12,84,5
R25,77,37,84,5
R50,77,62,84,5
R75,77,87,84,5
R0,86,95,89,2
R8,89,20,96,5
R33,89,45,96,5
R58,89,70,96,5
R83,89,95,96,5
R17,18,80,79,2
R20,20,76,76,14
R20,24,78,28,4
R21,43,77,45,5
P11:27,32;45,30;53,46;65,61;82,86;27,91;14,73;20,52
P12:28,37;43,35;51,49;68,76;56,83;27,85;20,70
P15:29,43;38,44;35,66;21,78;20,71
P1:39,57;46,63;59,79;70,85;58,86;38,70
L25,76,43,80,2,0.8
L30,84,52,85,2,0.8
L47,62,57,79,2,0.8
L62,80,73,86,2,0.8
E42,26,12,15,3
E44,28,10,13,6
P2:32,28;31,17;38,10;52,11;57,17;56,21;46,20;37,28
P4:31,23;36,16;44,14;55,18;56,20;41,20
P7:46,24;55,23;56,33;49,39;43,35
L45,36,50,38,5,1.0
D50,29,3
L51,33,54,33,21,0.75
P9:38,40;48,38;57,45;65,58;55,62;44,53
P8:47,42;57,46;63,56;54,54
L47,44,55,50,17,1.2
E58,69,27,15,3
E58,66,25,13,19
E58,64,21,9,18
E57,65,17,5.5,9
L32,68,36,75,19,1.3
L81,69,79,75,19,1.3
E63,47,11,10,6
E64,46,9,8.5,7
P4:54,42;57,37;65,35;72,39;76,44;70,41;62,40
D71,46,3
L68,52,73,53,21,0.8
E61,59,8.5,11,7
E60,58,6.5,8,8
L59,64,50,70,7,3.3
L57,69,48,70,7,2.5
L65,65,72,69,7,3.0
L72,69,73,73,21,2
L50,54,51,63,6,3.0
L51,63,56,71,7,2.1
L55,54,68,61,7,3.3
L68,61,65,67,6,2.0
D51,70,21
D53,71,21
D55,70,21
L40,69,47,68,19,0.85
L69,67,77,68,19,0.85
L52,74,62,74,19,0.85
L41,76,48,77,19,0.85
L35,80,48,83,14,1.0
L65,81,78,79,14,1.0""",
"whistlers-mother": """99998D ACAAA0 696960 4F504F 242427 323235 444348 5B534D 786354 E4DED0 F9F2DF CBB9A6 F3DFC2 8E8175 D2C8BB 635447 3C3938 B2B1A6
R0,0,95,95,0
R0,76,95,95,7
R0,75,95,77,2
R0,0,19,76,5
R0,0,9,75,2
R9,0,12,75,3
R17,0,19,76,6
L2,5,8,9,9,0.85
L8,9,4,13,9,0.85
D11,8,13
L2,15,8,19,9,0.85
L8,19,4,23,9,0.85
D11,18,13
L2,25,8,29,9,0.85
L8,29,4,33,9,0.85
D11,28,13
L2,35,8,39,9,0.85
L8,39,4,43,9,0.85
D11,38,13
L2,45,8,49,9,0.85
L8,49,4,53,9,0.85
D11,48,13
L2,55,8,59,9,0.85
L8,59,4,63,9,0.85
D11,58,13
L2,65,8,69,9,0.85
L8,69,4,73,9,0.85
D11,68,13
R33,10,67,39,4
R36,13,64,36,10
R40,16,61,33,1
P2:41,29;45,27;48,29;53,24;57,27;62,22;62,33;41,33
L40,34,64,34,13,0.7
R24,61,66,66,15
R25,65,28,90,15
R61,65,64,90,15
P4:39,45;47,44;56,55;67,76;64,87;43,87;22,76
P5:34,54;46,48;57,57;65,79;53,85;28,82;24,73
P4:43,45;55,51;59,65;77,89;21,89;14,80;26,64
P5:39,50;49,50;55,64;64,84;28,85;23,76
P6:38,54;32,64;26,79;36,82
P6:54,57;67,76;70,88;61,85
L29,78,42,80,16,0.8
L44,84,60,84,16,0.8
L49,59,55,76,16,0.8
E55,92,8,2,3
P10:40,31;48,19;57,20;64,31;58,40;47,40
E48,32,12,12,9
E51,30,9,11,10
P10:39,28;42,21;47,18;55,20;60,24;55,30;45,31
L39,28,46,22,14,1.0
L48,22,55,24,14,1.0
L57,26,60,30,14,1.0
P11:48,31;60,31;65,37;61,42;54,44;48,39
P12:55,30;63,35;65,37;61,39;58,35
D59,35,4
L62,39,65,39,13,0.65
L54,43,57,46,13,0.65
P10:46,43;53,45;60,52;55,57;46,52
P9:49,50;57,49;63,58;57,63;45,58
L48,53,56,54,14,0.9
L52,57,58,59,14,0.9
P10:48,59;59,59;65,64;60,69;47,66
E59,64,6,3.2,11
E63,63,3,2.7,12
L45,65,58,68,15,0.85""",
"woman-parasol": """88C7D7 B4DFE4 E4F1E9 FCF6DF 569A78 3F805E 2B614C 72A76C 9CB66E C3C6B7 E8E7D6 FFF7E9 657D76 A6BEB8 E9C79E C99775 3B443F 6C8669 DADDC9 91C1C8 FFDFA9
R0,0,95,95,0
E11,17,26,8,2
E6,20,23.4,5,3
E47,25,26,8,2
E42,28,23.4,5,3
E82,14,22,8,2
E77,17,19.8,5,3
E73,39,20,8,2
E68,42,18,5,3
D5,11,3
D18,8,3
D61,16,3
D84,5,3
P4:0,65;18,64;43,68;64,62;95,58;95,95;0,95
P7:0,80;20,76;43,78;69,73;95,68;95,95;0,95
L2,95,3,88,5,0.8
D3,88,8
L8,95,9,82,5,0.8
L14,95,15,88,5,0.8
D15,88,8
L20,95,21,82,5,0.8
L26,95,27,88,5,0.8
D27,88,8
L32,95,33,82,5,0.8
L38,95,39,88,5,0.8
D39,88,8
L44,95,45,82,5,0.8
L50,95,51,88,5,0.8
D51,88,8
L56,95,57,82,5,0.8
L62,95,63,88,5,0.8
D63,88,8
L68,95,69,82,5,0.8
L74,95,75,88,5,0.8
D75,88,8
L80,95,81,82,5,0.8
L86,95,87,88,5,0.8
D87,88,8
L92,95,93,82,5,0.8
E80,57,3,4,14
P10:77,62;83,61;88,73;77,72
L82,72,80,78,16,1.2
P2:48,33;61,33;76,51;77,65;66,60;61,45
P1:56,37;65,41;70,57;65,51
P6:12,38;18,26;34,16;51,16;64,23;68,37;54,35;42,39;29,38
P4:14,36;22,25;37,18;53,20;63,28;66,36;53,33;42,36;28,35
P7:16,35;30,23;44,20;46,34;29,36
P5:45,21;54,22;64,30;58,34;47,32
L40,18,43,36,5,0.8
L43,36,17,37,5,0.8
L43,36,66,36,5,0.8
L44,26,50,71,16,1.0
L44,26,46,32,20,0.65
P10:36,48;55,45;69,58;80,79;70,94;23,95;30,78;26,62
P3:36,52;49,50;61,66;66,85;49,92;23,94;32,77
P18:51,52;60,55;72,79;68,91;57,84
P2:29,63;38,58;36,76;24,92;17,95;21,83
P9:43,68;53,70;60,92;40,95;35,88
L29,74,33,82,13,0.9
L37,79,41,88,13,0.9
L48,74,53,90,13,0.9
L56,64,67,84,13,0.9
L21,90,29,86,1,1.0
L41,94,58,93,1,1.0
L61,89,68,85,1,1.0
P14:40,41;45,40;50,47;47,52;44,52
E44,40,6,8,15
E45,40,4.5,6.5,14
P16:37,34;41,30;47,30;53,35;54,39;38,39
D48,40,16
L46,45,51,46,15,0.65
P3:40,50;47,50;52,59;46,63;40,57
P16:43,50;47,53;50,63;48,67;42,57
L51,56,52,65,14,2.3
L52,65,49,69,15,1.5
L29,70,34,73,2,0.75
L35,65,40,68,2,0.75
L59,73,64,76,2,0.75
L65,82,70,85,2,0.75
L43,88,48,91,2,0.75
L73,90,78,93,2,0.75"""
}


def draw_scene(slug):
    """Recreate the reference artwork from its ordered vector pixel recipe."""
    source = DRAWINGS[slug].splitlines()
    palette = ["FF" + rgb for rgb in source[0].split()]
    if len(palette) > 48 or not all(len(color) == 8 for color in palette):
        raise ValueError("Invalid classic-art color palette")
    canvas = Sprite(SIDE, palette)
    for instruction in source[1:]:
        kind, parameters = instruction[0], instruction[1:]
        if kind == "P":
            paint, coords = parameters.split(":", 1)
            vertices = [tuple(map(int, pair.split(","))) for pair in coords.split(";")]
            canvas.polygon(vertices, int(paint))
        elif kind == "R":
            canvas.rect(*map(int, parameters.split(",")))
        elif kind == "D":
            canvas.dot(*map(int, parameters.split(",")))
        elif kind == "E":
            x, y, rx, ry, color = map(float, parameters.split(","))
            canvas.ellipse(x, y, rx, ry, int(color))
        elif kind == "L":
            x0, y0, x1, y1, color, thickness = map(float, parameters.split(","))
            canvas.line(x0, y0, x1, y1, int(color), radius=thickness)
        else:
            raise ValueError(f"Unknown pixel drawing operation: {kind}")
    return canvas


# Sparse highlight movements, without modifying the permanent base artwork.
MOTION = {
    "boating-party": [(9, 65, 0), (35, 61, 22), (79, 72, 0),
                      (14, 90, 22), (86, 89, 0)],
    "childs-bath": [(44, 69, 19), (73, 69, 9), (55, 75, 19),
                    (75, 77, 19), (58, 68, 18)],
    "whistlers-mother": [(4, 13, 9), (6, 27, 14), (7, 47, 9),
                         (4, 63, 14), (10, 58, 9)],
    "woman-parasol": [(16, 18, 3), (31, 21, 2), (64, 29, 7),
                      (51, 68, 2), (83, 17, 3)],
}


def animation_frames(artwork, slug):
    if slug not in MOTION:
        return None
    result = []
    before = artwork.cells
    for phase in range(8):
        changes = []
        if phase:
            for i, (x, y, color) in enumerate(MOTION[slug]):
                dx = (phase + i) % 3 - 1
                dy = (phase + 2 * i) % 2
                at = (y + dy) * SIDE + x + dx
                if before[at] != color:
                    changes.append([at, color])
        result.append({"changes": changes})
    return result


def create_pack(destination):
    entries, files, scenarios = [], {}, {}
    for slug, fa, en, artist, fa_motion, en_motion, animated in WORKS:
        artwork = draw_scene(slug)
        ident = PREFIX + slug
        level = {
            "schemaVersion": 2, "levelId": ident, "levelVersion": 1,
            "titles": {"fa": fa, "en": en},
            "width": SIDE, "height": SIDE,
            "palette": artwork.palette, "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        level_bytes = compact(level)
        if len(level_bytes) > 262144:
            raise ValueError("Detailed picture is too large: " + ident)
        stem = ident + "-v1"
        entry = {
            "id": ident, "version": 1, "title": fa, "titleEn": en,
            "category": "patterns", "width": SIDE, "height": SIDE,
            "bytes": len(level_bytes), "checksum": level["checksum"],
        }
        files[f"levels/{stem}.json"] = level_bytes
        files[f"previews/{stem}.png"] = png(level)
        if animated:
            frames = animation_frames(artwork, slug)
            payload = compact({
                "schemaVersion": 1, "levelId": ident, "levelVersion": 1,
                "levelChecksum": level["checksum"],
                "frameDurationMs": FRAME_DURATION_MS, "frames": frames,
            })
            files[f"animations/{stem}.json"] = payload
            entry["animation"] = {
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "frameCount": 8,
            }
            scenarios[ident] = {
                "artist": artist, "titleFa": fa, "titleEn": en,
                "frameDurationMs": FRAME_DURATION_MS, "frameCount": 8,
                "motionFa": fa_motion, "motionEn": en_motion,
            }
        entries.append(entry)
    validate_new_pack_manifest(entries)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json",
                         compact({"schemaVersion": 1, "pictures": entries}))
        for path, body in files.items():
            archive.writestr(path, body)
        archive.writestr("animation-scenarios.json",
                         compact({"schemaVersion": 1, "scenarios": scenarios}))
    print(f"Generated five detailed 96x96 classic artworks: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_classics_detailed_96_5_pack.py <content.zip>")
    create_pack(sys.argv[1])
