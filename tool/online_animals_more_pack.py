#!/usr/bin/env python3
"""Twenty original 48x48 animal color-by-number drawings for the online gallery.

Only the reproducible drawing source is tracked in git. The Pages workflow
assembles downloadable schema-v2 levels, bilingual metadata and PNG previews
into an immutable GitHub Release, without adding anything to the APK.
These species are distinct from the existing starter, collection and animals packs.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


N = 48


def board(palette):
    return Sprite(N, palette)


def ground(s, color):
    s.ellipse(24, 43, 21, 2.2, color)


def eyes(s, left, right, y, dark, glint):
    for x in (left, right):
        s.ellipse(x, y, 2.1, 2.7, dark)
        s.dot(x-1, y-1, glint)


def nose(s, x, y, dark):
    s.polygon([(x-3, y), (x+3, y), (x, y+3)], dark)


def stars(s, color):
    for x,y in ((6,8),(39,6),(43,20),(7,30)):
        s.dot(x,y,color)


def fox():
    s=board(["FFF7F4DE","FF543B3A","FFC16B3D","FFF39A52",
             "FFFFC07E","FFFCEBDD","FF705258","FF88B296","FFFFFFFF"])
    ground(s,7)
    # Triangular ears and an expressive white-cheeked red fox.
    for poly in ([(10,20),(7,3),(21,14)],[(27,14),(41,3),(38,20)]):
        s.polygon(poly,1)
    for poly in ([(11,15),(10,7),(17,15)],[(31,15),(38,7),(37,15)]):
        s.polygon(poly,4)
    s.polygon([(5,19),(13,13),(24,11),(35,13),(43,19),
               (40,31),(31,39),(24,42),(17,39),(8,31)],1)
    s.polygon([(7,20),(14,15),(24,13),(34,15),(41,20),
               (38,30),(31,37),(24,40),(17,37),(10,30)],2)
    s.polygon([(11,25),(23,33),(24,40),(17,36),(9,30)],5)
    s.polygon([(37,25),(25,33),(24,40),(31,36),(39,30)],5)
    s.ellipse(24,32,6,4.5,5)
    eyes(s,17,31,24,1,8)
    nose(s,24,33,1)
    s.line(24,36,24,38,1)
    s.line(24,38,20,39,1)
    s.line(24,38,28,39,1)
    for x,y in ((12,33),(35,33)):
        s.dot(x,y,4)
    return s


def wolf():
    s=board(["FFE9F2F5","FF394555","FF667789","FF93A7B4",
             "FFD4DEE0","FFF9FAF7","FF425868","FFAFBFCA","FFFFFFFF"])
    ground(s,7)
    for poly in ([(9,20),(6,3),(21,14)],[(27,14),(42,3),(39,20)]):
        s.polygon(poly,1)
    for poly in ([(11,16),(9,7),(18,15)],[(30,15),(39,7),(37,16)]):
        s.polygon(poly,3)
    s.polygon([(5,19),(14,12),(24,15),(34,12),(43,19),
               (39,33),(31,41),(24,44),(17,41),(9,33)],1)
    s.polygon([(8,20),(15,15),(24,18),(33,15),(40,20),
               (37,32),(30,39),(24,42),(18,39),(11,32)],2)
    s.polygon([(14,27),(24,31),(34,27),(32,39),(24,44),(16,39)],4)
    s.ellipse(24,34,8,5,5)
    s.polygon([(17,23),(22,25),(17,27)],1)
    s.polygon([(31,23),(26,25),(31,27)],1)
    eyes(s,17,31,26,1,8)
    nose(s,24,35,1)
    s.line(24,38,24,40,1)
    for x in (13,35):
        s.line(x,19,x+(-2 if x<24 else 2),26,3)
    return s


def brown_bear():
    s=board(["FFF3E9D7","FF523B33","FF85543B","FFAE7452",
             "FFD3A079","FFF5DAB6","FFB98D72","FFFFFFFF","FF89B69C"])
    ground(s,8)
    for x in (12,36):
        s.ellipse(x,13,8,9,1)
        s.ellipse(x,13,6,7,2)
        s.ellipse(x,13,3.8,4.8,6)
    s.ellipse(24,27,18,18.5,1)
    s.ellipse(24,27,16,16,2)
    s.ellipse(23,24,12.5,12,3)
    s.ellipse(15,28,5,6,3)
    s.ellipse(33,28,5,6,3)
    s.ellipse(24,35,9,7,5)
    eyes(s,17,31,26,1,7)
    s.ellipse(24,35,3.5,2.4,1)
    s.ellipse(24,39,4,1.3,6)
    s.dot(8,40,4);s.dot(39,39,4)
    return s


def zebra():
    s=board(["FFF0F5E8","FF252F3D","FFFFFFFF","FFBBC9C9",
             "FF8AADB3","FF526C70","FFDAAC9D","FF9BB78B"])
    ground(s,7)
    s.polygon([(19,16),(13,4),(12,19)],1)
    s.polygon([(29,16),(35,4),(36,19)],1)
    s.polygon([(18,16),(14,8),(15,18)],6)
    s.polygon([(30,16),(34,8),(33,18)],6)
    s.ellipse(24,25,13,17,1)
    s.ellipse(24,25,11,15,2)
    s.ellipse(24,36,7.5,7,3)
    s.ellipse(24,37,6.5,5.5,2)
    # Different diagonal bands on each cheek.
    for points in (
        [(14,17),(21,21),(19,25),(13,22)],
        [(12,27),(19,30),(18,34),(13,32)],
        [(34,17),(27,21),(29,25),(35,22)],
        [(36,27),(29,30),(30,34),(35,32)],
        [(22,10),(26,10),(24,18)],
        [(21,20),(27,18),(25,24)]
    ):
        s.polygon(points,1)
    s.rect(22,10,25,17,1)
    eyes(s,19,29,27,1,2)
    for x in (21,27):
        s.dot(x,39,1)
    s.line(20,42,28,42,1)
    return s


def tiger():
    s=board(["FFFBEED6","FF3D3835","FFBA592A","FFF19A46",
             "FFFFC271","FFFBE8CE","FFF6FCFA","FFDA8F84","FF94B18A"])
    ground(s,8)
    for x in (11,37):
        s.ellipse(x,12,7,8,1)
        s.ellipse(x,12,5.5,6,3)
        s.ellipse(x,12,3.4,4,7)
    s.ellipse(24,27,18,17,1)
    s.ellipse(24,27,16.5,15.5,3)
    for x in (12,36):
        for yy in (19,29):
            if x<24:
                s.polygon([(8,yy-3),(20,yy+1),(13,yy+4)],1)
            else:
                s.polygon([(40,yy-3),(28,yy+1),(35,yy+4)],1)
    s.polygon([(18,13),(24,22),(30,13)],1)
    s.polygon([(22,16),(24,20),(26,16)],4)
    s.ellipse(16,34,7,6,5)
    s.ellipse(32,34,7,6,5)
    s.ellipse(24,36,7.5,5.5,6)
    eyes(s,17,31,27,1,6)
    nose(s,24,34,1)
    s.line(24,37,24,39,1)
    s.line(24,39,20,40,1)
    s.line(24,39,28,40,1)
    for x in (11,37):
        s.dot(x,35,5)
    return s


def cheetah():
    s=board(["FFF9F3D8","FF59483C","FFCE9A55","FFF6C779",
             "FFFFE2A1","FFFFFFFF","FF6D564D","FFBF885B","FF8EB997"])
    ground(s,8)
    s.polygon([(11,17),(8,5),(20,14)],1)
    s.polygon([(37,17),(40,5),(28,14)],1)
    s.polygon([(12,15),(10,8),(18,15)],7)
    s.polygon([(36,15),(38,8),(30,15)],7)
    s.ellipse(24,27,16.5,18,1)
    s.ellipse(24,27,15,16.5,2)
    s.ellipse(24,33,10,10,3)
    for x,y in [(13,18),(18,14),(30,14),(35,18),
                (10,28),(15,37),(33,37),(38,28),
                (21,11),(26,11),(13,32),(35,32)]:
        s.ellipse(x,y,1.7,1.4,1)
    eyes(s,17,31,25,1,5)
    for x,tilt in [(16,-1),(32,1)]:
        s.line(x,28,x+tilt,36,1,radius=1)
        s.dot(x+tilt,37,1)
    s.ellipse(24,38,6.5,4.3,4)
    nose(s,24,36,1)
    s.line(24,39,24,41,1)
    s.line(24,41,21,42,1)
    s.line(24,41,27,42,1)
    return s


def kangaroo():
    s=board(["FFFBEFD9","FF513E37","FFB57848","FFE0A36F",
             "FFF5CC9D","FFFFE4BA","FFD88E9B","FF89B592","FFFFFFFF"])
    ground(s,7)
    s.ellipse(24,34,15,11,1)
    s.ellipse(24,33,13.5,10,2)
    s.ellipse(24,36,8,6.4,4)
    for vertices in (
        [(12,22),(10,2),(19,12),(21,23)],
        [(27,22),(29,2),(37,15),(35,25)]
    ):
        s.polygon(vertices,1)
    s.polygon([(14,20),(13,7),(18,15)],6)
    s.polygon([(31,20),(31,7),(35,16)],6)
    s.ellipse(24,24,14,14,1)
    s.ellipse(24,24,12.5,12.5,3)
    s.ellipse(24,30,7.5,6.5,4)
    eyes(s,17,31,23,1,8)
    s.ellipse(24,29,3,2.2,1)
    s.ellipse(24,33,4.4,2,5)
    s.rect(16,42,21,44,1)
    s.rect(27,42,32,44,1)
    s.dot(12,37,5); s.dot(36,37,5)
    return s


def hippopotamus():
    s=board(["FFEAF6F6","FF3D4E57","FF77848B","FF9EA9AD",
             "FFC4B5B0","FFF8E8DB","FF9A6A7D","FF8FC5BB","FFFFFFFF"])
    ground(s,7)
    for x in (12,36):
        s.ellipse(x,16,7,7,1)
        s.ellipse(x,16,5.4,5.5,2)
        s.ellipse(x,16,3.0,3.5,6)
    s.ellipse(24,23,17,16,1)
    s.ellipse(24,23,15.5,14.5,2)
    s.ellipse(24,34,19,11,1)
    s.ellipse(24,34,17.5,9.8,3)
    s.ellipse(24,34,14,7.4,4)
    eyes(s,16,32,23,1,8)
    for x in (15,33):
        s.ellipse(x,34,3.3,2.8,2)
        s.dot(x+1,34,1)
    s.line(16,39,32,39,1)
    s.dot(18,40,5);s.dot(30,40,5)
    return s


def rhinoceros():
    s=board(["FFE5F2EE","FF3D4D53","FF829A9E","FFB1C3C1",
             "FFD3DFD5","FFF0E8CF","FF7A8E94","FF91B4A2","FFFFFFFF"])
    ground(s,7)
    for x in (12,36):
        s.ellipse(x,16,7,10,1)
        s.ellipse(x,17,5.5,8.5,2)
        s.ellipse(x,13,3.5,5,6)
    s.ellipse(24,26,17,17,1)
    s.ellipse(24,26,15.5,16,2)
    s.ellipse(24,35,12.5,10,3)
    s.ellipse(24,34,9.2,6.6,4)
    # Centerpiece elongated horn and a smaller nasal horn.
    s.polygon([(23,33),(21,11),(29,28)],1)
    s.polygon([(24,30),(23,15),(27,28)],5)
    s.polygon([(24,36),(20,27),(29,33)],1)
    s.polygon([(24,34),(23,28),(27,32)],5)
    eyes(s,16,32,27,1,8)
    s.ellipse(19,39,2.0,1.6,1)
    s.ellipse(29,39,2.0,1.6,1)
    s.line(18,42,30,42,6)
    return s


def crocodile():
    s=board(["FFE3F7F3","FF294D46","FF4B9171","FF70B68C",
             "FFB4D7A0","FFF2E9BC","FF5C805D","FF8FCACB","FFFFFFFF"])
    s.rect(0,39,47,47,7)
    s.line(1,42,45,42,4)
    s.ellipse(24,30,21,10,1)
    s.ellipse(24,29,20,9,2)
    s.ellipse(24,33,20,5.5,3)
    for x in (11,37):
        s.ellipse(x,20,7,7,1)
        s.ellipse(x,20,5.7,5.7,3)
        s.ellipse(x,19,2.4,2.8,5)
        s.dot(x+1,19,1)
        s.dot(x+1,18,8)
    s.polygon([(3,33),(9,27),(18,25),(30,26),(40,28),
               (46,33),(43,37),(8,38)],1)
    s.polygon([(4,33),(11,29),(19,27),(30,28),(39,30),
               (44,33),(41,35),(8,36)],3)
    for x in range(8,44,5):
        s.polygon([(x,24),(x+2,20),(x+4,25)],1)
        s.polygon([(x,25),(x+2,22),(x+4,25)],4)
    s.line(5,36,44,36,1)
    for x in range(10,42,5):
        s.polygon([(x,36),(x+2,39),(x+4,36)],5)
    for x in (6,42):
        s.dot(x,32,1)
    return s


def toucan():
    s=board(["FFEAF8EC","FF293E42","FF3B4A50","FFEDF3EB",
             "FFFFC85D","FFF58A4C","FFDB5E57","FF6CBE92",
             "FF8BD2BE","FFFFFFFF","FF9B7051"])
    s.line(1,40,46,38,10,radius=1.8)
    s.line(1,39,46,37,1)
    s.polygon([(14,33),(8,45),(17,40),(23,32)],1)
    s.ellipse(22,28,12,14,1)
    s.ellipse(22,28,10,12,2)
    s.ellipse(20,29,6,9,1)
    s.ellipse(20,31,4,6,3)
    s.ellipse(27,15,9,10,1)
    s.ellipse(27,15,7.5,8.5,2)
    # Overlarge tropical beak, curved to a striking burnt-orange tip.
    s.polygon([(27,13),(44,9),(47,12),(42,20),(27,22)],1)
    s.polygon([(28,14),(43,10),(46,12),(41,18),(28,20)],4)
    s.polygon([(39,11),(46,12),(41,18),(38,18)],5)
    s.line(30,18,43,18,6)
    s.ellipse(26,15,2,2,9)
    s.dot(26,15,1)
    for x in (19,26):
        s.line(x,38,x-1,41,1)
    s.ellipse(8,9,5,4,8)
    s.ellipse(4,18,3,6,7)
    return s


def peacock():
    s=board(["FFF1F9EC","FF274F60","FF267E81","FF47B5A2",
             "FF77CD90","FF3257A1","FFE0B762","FFB9E8A5",
             "FFFFFFFF","FF94B69C","FF54A1D4"])
    ground(s,9)
    # Radial fan feathers; eye spots are individually visible.
    for x,y in ((6,16),(11,9),(20,5),(28,5),(37,9),(42,16),
                (5,26),(43,26),(11,33),(37,33)):
        s.line(24,35,x,y,1,radius=1.8)
        s.line(24,35,x,y,3,radius=1)
        s.ellipse(x,y,4.6,6.5,2)
        s.ellipse(x,y,3.5,5,4)
        s.ellipse(x,y,2.5,3.4,5)
        s.ellipse(x,y,1.2,1.8,6)
    s.ellipse(24,32,8,12,1)
    s.ellipse(24,32,6.6,10.5,5)
    s.ellipse(24,25,5.5,6.4,2)
    s.ellipse(24,24,4.2,5.3,3)
    s.polygon([(23,27),(29,29),(23,31)],6)
    s.dot(26,24,1)
    s.dot(26,23,8)
    for xx in (21,24,27):
        s.line(24,20,xx,14,1)
        s.dot(xx,14,6)
    s.line(21,42,21,46,1)
    s.line(27,42,27,46,1)
    return s


def hedgehog():
    s=board(["FFF8F1E8","FF544039","FF8B6048","FFC18C63",
             "FFE6B68A","FFFBE7C8","FFAD8E79","FF9BBA8D","FFFFFFFF"])
    ground(s,7)
    # Large dark spines around the back and side silhouette.
    spines=[(2,25),(7,17),(13,10),(19,8),(28,8),
            (36,13),(42,20),(45,31),(39,37),(9,38)]
    s.polygon(spines+[(2,35)],1)
    for cx,cy,r in ((13,21,9),(24,19,12),(34,25,10)):
        s.ellipse(cx,cy,r,r-1,2)
    for x,y in ((8,17),(16,11),(23,8),(31,11),(39,19),(43,28)):
        s.polygon([(x-5,y+6),(x,y-4),(x+5,y+6)],1)
        s.polygon([(x-2,y+5),(x,y),(x+2,y+5)],3)
    s.ellipse(24,31,16,12,1)
    s.ellipse(24,31,14.5,10.8,4)
    s.ellipse(24,35,11.5,7.5,5)
    s.ellipse(12,29,4,5,1)
    s.ellipse(12,29,2.8,3.5,3)
    s.ellipse(36,29,4,5,1)
    s.ellipse(36,29,2.8,3.5,3)
    eyes(s,17,31,30,1,8)
    nose(s,24,36,1)
    s.line(24,39,20,40,1)
    s.line(24,39,28,40,1)
    s.dot(14,38,3);s.dot(34,38,3)
    return s


def raccoon():
    s=board(["FFF2F1E9","FF34434B","FF65737A","FF9EA7A7",
             "FFD2D3C9","FFFDF2E1","FF80756C","FFB9A9A2","FFFFFFFF"])
    ground(s,7)
    s.polygon([(11,21),(5,5),(21,14)],1)
    s.polygon([(37,21),(43,5),(27,14)],1)
    s.polygon([(11,17),(8,8),(18,15)],6)
    s.polygon([(37,17),(40,8),(30,15)],6)
    s.ellipse(24,27,18,18,1)
    s.ellipse(24,27,16.5,16.2,3)
    # Broad dark raccoon eye mask with pale eyebrow band.
    s.ellipse(16,27,9,6,1)
    s.ellipse(32,27,9,6,1)
    s.ellipse(16,26,7,4.5,2)
    s.ellipse(32,26,7,4.5,2)
    s.ellipse(24,34,10,9,4)
    s.ellipse(24,36,7.7,6.2,5)
    eyes(s,17,31,26,1,8)
    nose(s,24,35,1)
    s.line(24,38,24,40,1)
    s.line(24,40,21,41,1)
    s.line(24,40,27,41,1)
    for x in (11,37):
        s.dot(x,34,5)
    return s


def sloth():
    s=board(["FFF2F7E9","FF514944","FF907358","FFC1A17C",
             "FFE2CB9F","FFF3E8D4","FF6D6158","FF8AB18A","FFFFFFFF"])
    s.line(5,7,42,9,1,radius=2.3)
    s.line(5,6,42,8,2,radius=1)
    s.ellipse(24,29,16,17,1)
    s.ellipse(24,28,14.6,15.5,2)
    s.ellipse(24,24,12,12,3)
    s.ellipse(24,25,9.2,9,4)
    for x in (10,38):
        s.ellipse(x,30,5.5,8,1)
        s.ellipse(x,30,4,6.5,2)
        s.line(x-2,34,x-4,40,1)
        s.line(x,35,x,41,1)
        s.line(x+2,34,x+4,40,1)
    s.ellipse(16,24,4.4,7,6)
    s.ellipse(32,24,4.4,7,6)
    s.ellipse(17,24,3,5,5)
    s.ellipse(31,24,3,5,5)
    eyes(s,17,31,24,1,8)
    s.ellipse(24,31,3.3,2.5,1)
    s.line(21,35,27,35,1)
    for x in (17,31):
        s.dot(x,37,4)
    return s


def seal():
    s=board(["FFE8F5FC","FF46596D","FF8299A7","FFC3D0D7",
             "FFE6EBE7","FFFFFFFF","FF6C7E8C","FF8DC7D4","FFB5DCE8"])
    s.rect(0,39,47,47,7)
    for y in (40,44):
        for x in range(3,46,9):
            s.line(x,y,x+5,y,8)
    s.ellipse(24,32,18.5,12.8,1)
    s.ellipse(24,32,17,11.3,2)
    s.ellipse(24,34,13,9,3)
    for x in (15,33):
        s.ellipse(x,12,5.6,5.1,1)
        s.ellipse(x,12,4.3,3.8,2)
    s.ellipse(24,24,13,15,1)
    s.ellipse(24,24,11.6,13.5,3)
    s.ellipse(24,32,8.5,8,4)
    eyes(s,18,30,23,1,5)
    nose(s,24,31,1)
    s.line(24,34,24,36,1)
    s.line(24,36,20,37,1)
    s.line(24,36,28,37,1)
    for side in (-1,1):
        s.line(24,35,24+side*12,34,6)
        s.line(24,37,24+side*11,39,6)
    return s


def whale():
    s=board(["FFE5F9FB","FF254E66","FF3882AC","FF64B4D0",
             "FF96D7E1","FFE8F9F4","FF86C9D2","FF3F7092","FFFFFFFF"])
    s.rect(0,39,47,47,6)
    for x in (8,18,28,38):
        s.line(x,42,x+5,42,4)
    s.ellipse(23,28,18,13,1)
    s.ellipse(23,27,16.5,11.5,2)
    s.ellipse(23,33,16.3,6,4)
    s.ellipse(23,35,12.5,4.8,5)
    # Forked tail extends right and has two triangular lobes.
    s.polygon([(36,27),(43,15),(47,21),(44,27),
               (47,34),(42,39),(35,31)],1)
    s.polygon([(39,27),(43,19),(46,22),(43,27),
               (46,33),(42,36)],2)
    s.polygon([(19,18),(24,9),(29,19)],1)
    s.polygon([(21,18),(24,12),(27,18)],3)
    s.ellipse(13,28,2.3,2.6,1)
    s.dot(12,27,8)
    s.line(9,34,17,35,1)
    s.line(23,16,23,10,7)
    s.line(20,12,23,10,7)
    s.line(26,12,23,10,7)
    for x,y in ((18,8),(28,7),(24,4)):
        s.dot(x,y,3)
    return s


def shark():
    s=board(["FFE7F8FC","FF294C66","FF718DA1","FFA7C4CD",
             "FFE4F3F0","FF4B8FA8","FF90D4E1","FFBADCE3","FFFFFFFF"])
    s.rect(0,40,47,47,6)
    for x in range(3,47,8):
        s.line(x,43,x+4,43,7)
    # Long torpedo shape and a high triangular dorsal fin.
    s.polygon([(5,29),(14,22),(26,21),(36,24),
               (42,21),(45,15),(47,19),(45,29),
               (47,37),(43,34),(38,32),(25,36),
               (13,35)],1)
    s.polygon([(7,29),(16,24),(27,23),(37,26),
               (41,25),(40,29),(36,31),(25,34),(14,33)],2)
    s.polygon([(18,23),(26,9),(31,23)],1)
    s.polygon([(21,23),(26,13),(29,23)],2)
    s.polygon([(17,35),(22,43),(26,34)],1)
    s.polygon([(17,34),(21,40),(23,35)],3)
    s.line(8,33,30,34,1)
    s.line(10,33,27,33,4)
    for x in (11,15,19,23,27):
        s.polygon([(x,34),(x+2,37),(x+4,34)],8)
    s.ellipse(12,27,2.2,2,1)
    s.dot(11,26,8)
    for xx in (26,29,32):
        s.line(xx,29,xx+1,32,1)
    return s


def frog():
    s=board(["FFE8F7E1","FF355C43","FF5B9D56","FF8AC76D",
             "FFC3E69B","FFFFE2A2","FFB9D9D1","FFFFFFFF","FF9AB792"])
    ground(s,8)
    for x in (13,35):
        s.ellipse(x,17,9,9,1)
        s.ellipse(x,17,7.4,7.5,3)
        s.ellipse(x,17,5.2,5.5,7)
        s.ellipse(x,17,3.1,4.1,1)
        s.dot(x-1,15,7)
    s.ellipse(24,31,19,14,1)
    s.ellipse(24,31,17.3,12.6,2)
    s.ellipse(24,30,13,9.5,3)
    s.ellipse(24,36,10,6.5,4)
    s.ellipse(16,32,2,1.7,1)
    s.ellipse(32,32,2,1.7,1)
    s.line(17,38,31,38,1)
    s.line(17,38,20,40,1)
    s.line(31,38,28,40,1)
    for x in (8,40):
        s.ellipse(x,39,6,4,1)
        s.ellipse(x,39,4.7,3,3)
        for dx in (-4,0,4):
            s.dot(x+dx,42,3)
    s.dot(11,30,4);s.dot(36,29,4)
    return s


def chameleon():
    s=board(["FFF0F8E9","FF395948","FF69A961","FF9ACB6C",
             "FFC5DA86","FFFFDA87","FF7FBCA9","FF95B08C","FFFFFFFF"])
    s.line(1,41,46,38,1,radius=2)
    s.line(1,40,46,37,7,radius=1)
    # Curled tail is a sequence of nested loops with a colored center.
    s.ellipse(13,31,12,11,1)
    s.ellipse(13,31,10,9,2)
    s.ellipse(13,31,7.5,7,3)
    s.ellipse(13,31,5,4.7,1)
    s.ellipse(13,31,3.2,2.8,0)
    s.ellipse(14,30,1.6,1.6,5)
    s.ellipse(25,27,13,12,1)
    s.ellipse(25,27,11.5,10.5,2)
    s.ellipse(24,29,8,7,3)
    s.polygon([(27,22),(32,13),(42,16),(45,23),
               (42,31),(31,29)],1)
    s.polygon([(30,22),(33,16),(41,18),(43,23),
               (40,29),(32,27)],3)
    s.ellipse(37,19,4.4,4.4,1)
    s.ellipse(37,19,3.2,3.2,8)
    s.ellipse(38,19,1.7,1.7,1)
    s.dot(38,18,8)
    s.line(36,28,42,29,1)
    s.line(22,35,20,41,1,radius=.8)
    s.line(31,34,30,41,1,radius=.8)
    s.dot(20,42,1);s.dot(30,42,1)
    for x,y in ((22,23),(26,30),(31,25),(18,29)):
        s.dot(x,y,5)
        s.dot(x+1,y,4)
    return s


PICTURES=[
    ("online-fox","روباه نارنجی","Red Fox",fox),
    ("online-wolf","گرگ خاکستری","Gray Wolf",wolf),
    ("online-brown-bear","خرس قهوه‌ای","Brown Bear",brown_bear),
    ("online-zebra","گورخر راه‌راه","Striped Zebra",zebra),
    ("online-tiger","ببر نارنجی","Orange Tiger",tiger),
    ("online-cheetah","یوزپلنگ خال‌دار","Spotted Cheetah",cheetah),
    ("online-kangaroo","کانگوروی بازیگوش","Playful Kangaroo",kangaroo),
    ("online-hippopotamus","اسب آبی","Hippopotamus",hippopotamus),
    ("online-rhinoceros","کرگدن خاکستری","Gray Rhinoceros",rhinoceros),
    ("online-crocodile","تمساح سبز","Green Crocodile",crocodile),
    ("online-toucan","توکان رنگارنگ","Colorful Toucan",toucan),
    ("online-peacock","طاووس پرنقش","Bright Peacock",peacock),
    ("online-hedgehog","جوجه‌تیغی","Hedgehog",hedgehog),
    ("online-raccoon","راکون نقاب‌دار","Masked Raccoon",raccoon),
    ("online-sloth","تنبل درختی","Tree Sloth",sloth),
    ("online-seal","فک دریایی","Harbor Seal",seal),
    ("online-whale","نهنگ آبی","Blue Whale",whale),
    ("online-shark","کوسه اقیانوس","Ocean Shark",shark),
    ("online-frog","قورباغه سبز","Green Frog",frog),
    ("online-chameleon","آفتاب‌پرست","Chameleon",chameleon),
]


def create_pack(destination):
    if len(PICTURES) != 20 or len(set(row[0] for row in PICTURES)) != 20:
        raise ValueError("This pack must hold twenty unique animal level IDs")
    manifest=[]
    files={}
    for ident,title_fa,title_en,painter in PICTURES:
        sprite=painter()
        level={
            "schemaVersion":2,
            "levelId":ident,
            "levelVersion":1,
            "titles":{"fa":title_fa,"en":title_en},
            "width":sprite.side,
            "height":sprite.side,
            "palette":sprite.palette,
            "cells":sprite.cells,
        }
        level["checksum"]=checksum(level)
        payload=compact(level)
        stem=f"{ident}-v1"
        manifest.append({
            "id":ident,"version":1,"title":title_fa,"titleEn":title_en,
            "category":"animals","width":sprite.side,"height":sprite.side,
            "bytes":len(payload),"checksum":level["checksum"],
        })
        files[f"levels/{stem}.json"]=payload
        files[f"previews/{stem}.png"]=png(level)
    validate_new_pack_manifest(manifest)
    target=pathlib.Path(destination)
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json",compact({
            "schemaVersion":1,"pictures":manifest,
        }))
        for name,data in files.items():
            archive.writestr(name,data)
    print(f"Created {len(manifest)} original 48x48 animal pictures: {target}")


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python3 tool/online_animals_more_pack.py <content.zip>")
    create_pack(sys.argv[1])
