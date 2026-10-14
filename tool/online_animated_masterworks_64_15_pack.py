#!/usr/bin/env python3
"""Build fifteen unique, original 64×64 animated classic painting interpretations.

Only source instructions belong in Git: the preview PNGs, completed numbered
paintings and their immutable animation sidecars are created in CI and shipped
by GitHub Releases to the online catalog, never bundled in the APK.
"""
import hashlib
import pathlib
import sys
import zipfile

from online_animated_masterworks_64_15_designs import PICTURES
from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 64
PREFIX = "online-classic-animated64-"
FRAME_DURATION_MS = 180


def draw_figure(s, x, y, scale, skin, garment, ink, pose):
    """Small human pictogram with an independently placed head, arms and hem."""
    h = 4.0 * scale
    s.ellipse(x, y + h, 3.3 * scale, h, ink)
    s.ellipse(x, y + h, 2.5 * scale, 3.2 * scale, skin)
    s.polygon([
        (x - 3.4*scale, y + 8*scale),
        (x + 3.7*scale, y + 8*scale),
        (x + 6.4*scale, y + 21*scale),
        (x - 6.4*scale, y + 21*scale),
    ], garment)
    s.line(x - 2.5*scale, y + 19*scale,
           x - 3.7*scale, y + 25*scale, ink, radius=max(.6, .85*scale))
    s.line(x + 2.5*scale, y + 19*scale,
           x + 3.7*scale, y + 25*scale, ink, radius=max(.6, .85*scale))
    if pose == 2:
        s.line(x - 3*scale, y + 10*scale,
               x - 8*scale, y + 2*scale, skin, radius=max(.6, scale))
        s.line(x + 3*scale, y + 10*scale,
               x + 8*scale, y + 2*scale, skin, radius=max(.6, scale))
    elif pose == 1:
        s.line(x - 3*scale, y + 11*scale,
               x - 9*scale, y + 13*scale, skin, radius=max(.6, scale))
        s.line(x + 3*scale, y + 11*scale,
               x + 9*scale, y + 13*scale, skin, radius=max(.6, scale))
    else:
        s.line(x - 3*scale, y + 11*scale,
               x - 6*scale, y + 18*scale, skin, radius=max(.6, scale))
        s.line(x + 3*scale, y + 11*scale,
               x + 6*scale, y + 18*scale, skin, radius=max(.6, scale))


def flower(s, x, y, petal, center):
    for dx, dy in ((-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,1)):
        s.ellipse(x+dx, y+dy, 1.7, 1.7, petal)
    s.dot(x,y,center)


def iris(s, x, y, outer, shade, light, center):
    s.ellipse(x-3,y,3.5,2,outer)
    s.ellipse(x+3,y-1,3.5,2.4,outer)
    s.ellipse(x,y-3,2,3.5,shade)
    s.ellipse(x-2,y-2,2.7,1.5,light)
    s.ellipse(x+2,y-3,2.7,1.5,light)
    s.dot(x,y,center)


def draw_scene(scene):
    palette = scene["palette"]
    if len(palette) > 48 or not all(len(color) == 8 and color.startswith("FF")
                                      for color in palette):
        raise ValueError("Invalid ARGB palette for " + scene["slug"])
    s = Sprite(SIDE,palette)
    for instruction in scene["recipe"]:
        op, *values = instruction.split()
        if op == "R":
            a,b,c,d,color = map(int,values)
            s.rect(a,b,c,d,color)
        elif op == "E":
            a,b,c,d,color = values
            s.ellipse(float(a),float(b),float(c),float(d),int(color))
        elif op == "L":
            x0,y0,x1,y1,color,*thickness = values
            s.line(float(x0),float(y0),float(x1),float(y1),
                   int(color),radius=float(thickness[0]) if thickness else .7)
        elif op == "P":
            color,*vertices = values
            s.polygon([tuple(map(float,v.split(","))) for v in vertices],int(color))
        elif op == "D":
            x,y,color = map(int,values)
            s.dot(x,y,color)
        elif op == "T":
            x,y,scale,skin,garment,ink,pose = values
            draw_figure(s,float(x),float(y),float(scale),int(skin),
                        int(garment),int(ink),int(pose))
        elif op == "F":
            x,y,petal,center = map(int,values)
            flower(s,x,y,petal,center)
        elif op == "I":
            x,y,outer,shade,light,center = map(int,values)
            iris(s,x,y,outer,shade,light,center)
        elif op == "C":
            x,y,r,light,shadow = map(int,values)
            s.ellipse(x,y,r,r*.33,shadow)
            s.ellipse(x-r*.3,y-2,r*.70,r*.35,light)
            s.ellipse(x+r*.32,y+1,r*.68,r*.3,light)
        elif op == "B":
            x,y,w,h,wall,window = map(int,values)
            s.rect(x,y,x+w,y+h,wall)
            s.polygon([(x-2,y),(x+w//2,y-5),(x+w+2,y)],wall)
            for row in range(y+3,y+h-1,6):
                for col in range(x+2,x+w-1,5):
                    s.rect(col,row,col+1,row+2,window)
        elif op == "A":
            x,y,w,h,ink = map(int,values)
            s.ellipse(x+w*.5,y+h*.38,w*.48,h*.35,ink)
            s.rect(x,y+h//2,x+w,y+h,ink)
        else:
            raise ValueError("Unknown pixel drawing command: " + instruction)
    return s


def animation_pose(base, slug, phase):
    """Each frame is a complete pose, delta-coded against the pristine level."""
    pose = Sprite(SIDE,base.palette)
    pose.cells = base.cells[:]
    if phase == 0:
        return pose.cells
    wave = (0,1,2,3,4,3,2,1)[phase]
    def dot(x,y,color):
        pose.dot(x,y,color)
    def sparkle(x,y,color):
        dot(x,y,color)
        dot(x-1,y,color)
        dot(x+1,y,color)

    if slug == "primavera":
        for n,(x,y) in enumerate(((5,53),(17,55),(29,60),(45,54),(58,58))):
            dot(x+(phase+n)%3-1,y-wave//2,10)
            dot(x+1+(phase+n)%3,y-wave//2-1,9)
    elif slug == "tower-babel":
        for i,(x,y) in enumerate(((17,48),(24,39),(29,32),(33,25),(37,20))):
            dot(x,y,10 if (i+phase)%3 else 7)
            if wave>=2:
                dot(x+2,y+1,6)
        for x in range(3,13,3):
            dot(x+wave//2,12,10)
    elif slug == "hunters-snow":
        for n,(x,y) in enumerate(((7,10),(17,15),(41,9),(53,21),(32,29),(59,17))):
            dot(x+(n+phase)%3,y+phase%3,8)
        for x in (33,42,50):
            dot(x,55+wave//2,8)
    elif slug == "ophelia":
        for n,(x,y) in enumerate(((9,46),(20,56),(38,58),(51,48),(56,54))):
            dot(x+(phase+n)%4,y+wave//2,10)
            dot(x-1+wave//2,y-1,3)
    elif slug == "lady-shalott":
        for x,y in ((47,28),(52,34)):
            dot(x,y,10 if wave>=2 else 5)
            dot(x+1,y+1,5 if phase%2 else 10)
        for x in (17,29,41,55):
            sparkle(x+wave//2,59,3)
    elif slug == "olympia":
        for y in (6,13,21,31):
            dot(58+wave//2,y,9)
            dot(59,y+phase%3,4)
        for x in (56,59,61):
            dot(x,24+(phase+x)%3,10)
    elif slug == "luncheon-grass":
        for n,(x,y) in enumerate(((8,18),(23,14),(40,20),(55,16),(34,32))):
            dot(x+(phase+n)%3,y+wave//2,9)
            dot(x+1+wave//2,y+1,3)
    elif slug == "childs-bath":
        for x in (29,34,39,44):
            dot(x+(phase+x)%3,47+wave//2,9)
            dot(x+1,49+wave//2,6)
    elif slug == "boating-party":
        for x in (6,17,39,52):
            dot(x+wave//2,54+phase%3,2)
            dot(x+wave//2+1,56+phase%2,0)
        dot(48,45+wave//2,8)
    elif slug == "ballet-class":
        for i,x in enumerate((10,24,30,40,46)):
            dot(x+wave//2,45+i%2,5)
            dot(x+1-wave//2,46+i%2,6)
        for x in (13,26,39):
            dot(x,22+phase%3,4)
    elif slug == "blue-dancers":
        for n,x in enumerate((8,16,24,34,42,49,55)):
            dot(x+wave//2,44+n%3,9)
            dot(x+2-wave//2,46+n%3,5)
    elif slug == "view-delft":
        for n,x in enumerate((6,18,30,44,55)):
            dot(x+wave//2,57+(phase+n)%3,10)
            dot(x,52+n%2,2)
        for x in (13,22,36):
            dot(x+phase%2,10,10)
    elif slug == "astronomer":
        for i,(x,y) in enumerate(((43,25),(48,22),(52,31),(46,34))):
            dot(x,y,9 if (phase+i)%3 else 4)
        for x in (11,15,21):
            dot(x+wave//2,18+phase%2,3)
    elif slug == "irises":
        for n,(x,y) in enumerate(((10,29),(18,31),(24,21),(34,24),
                                  (45,33),(52,26),(59,39))):
            dot(x-2+wave//2,y-2,6)
            dot(x+1+(phase+n)%2,y+1,5)
    elif slug == "red-vineyard":
        for x in range(3,61,6):
            dot(x+wave//2,49+(x//6+phase)%4,5)
        for x in (53,58,62):
            dot(x,36+phase%3,5)
    else:
        raise ValueError("No animation for: " + slug)
    return pose.cells


def animation_frames(base, slug):
    start = base.cells
    return [{"changes": [[i,c] for i,c in enumerate(animation_pose(base,slug,phase))
                         if c != start[i]]} for phase in range(8)]


def create_pack(destination):
    if len(PICTURES) != 15 or len({p["slug"] for p in PICTURES}) != 15:
        raise ValueError("The pack must contain 15 unique painting identifiers")
    manifest, assets, scenarios = [], {}, {}
    for scene in PICTURES:
        slug = scene["slug"]
        artwork = draw_scene(scene)
        if artwork.side != 64 or len(artwork.cells) != 4096:
            raise ValueError("Invalid dimensions: " + slug)
        level = {
            "schemaVersion": 2, "levelId": PREFIX+slug, "levelVersion": 1,
            "titles": {"fa": scene["fa"], "en": scene["en"]},
            "width": 64, "height": 64,
            "palette": artwork.palette, "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        body = compact(level)
        frames = animation_frames(artwork,slug)
        animation = {
            "schemaVersion": 1, "levelId": level["levelId"], "levelVersion": 1,
            "levelChecksum": level["checksum"],
            "frameDurationMs": FRAME_DURATION_MS, "frames": frames,
        }
        anim_body = compact(animation)
        stem = level["levelId"]+"-v1"
        manifest.append({
            "id": level["levelId"], "version": 1,
            "title": scene["fa"], "titleEn": scene["en"],
            "category": "patterns", "width": 64, "height": 64,
            "bytes": len(body), "checksum": level["checksum"],
            "animation": {
                "bytes": len(anim_body),
                "sha256": hashlib.sha256(anim_body).hexdigest(),
                "frameCount": len(frames),
            },
        })
        assets["levels/"+stem+".json"] = body
        assets["previews/"+stem+".png"] = png(level)
        assets["animations/"+stem+".json"] = anim_body
        scenarios[level["levelId"]] = {
            "titleFa": scene["fa"], "titleEn": scene["en"], "artist": scene["artist"],
            "motionFa": scene["motionFa"], "motionEn": scene["motionEn"],
            "frameCount": 8, "frameDurationMs": FRAME_DURATION_MS,
        }
    validate_new_pack_manifest(manifest)
    path = pathlib.Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json",compact({"schemaVersion":1,"pictures":manifest}))
        for name,body in assets.items():
            archive.writestr(name,body)
        archive.writestr("animation-scenarios.json",
                         compact({"schemaVersion":1,"scenarios":scenarios}))
    print("Generated 15 new 64x64 animated classic paintings: "+str(path))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: online_animated_masterworks_64_15_pack.py <content.zip>")
    create_pack(sys.argv[1])
