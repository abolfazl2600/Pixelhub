#!/usr/bin/env python3
"""Twenty *original* 64x64 pixel-art homages to distinct public-domain paintings.

The paintings are recognizable, simplified interpretations drawn with geometric
primitives, not copied scans or original source images. Painting files,
previews and metadata are generated only for GitHub Release publication,
outside the repository and the Android application bundle.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite


SIDE = 64


def painting(palette):
    return Sprite(SIDE, palette)


def hill(s, ridge, color):
    s.polygon([(0, 64)] + ridge + [(63, 64)], color)


def cloud(s, x, y, r, light, shadow):
    s.ellipse(x-r/2, y+2, r*.65, r*.31, shadow)
    s.ellipse(x+r/2, y+1, r*.6, r*.3, shadow)
    s.ellipse(x, y, r*.65, r*.37, light)
    s.ellipse(x-r*.4, y+1, r*.4, r*.25, light)


def person(s, x, y, skin, clothes, ink, scale=1, pose=0):
    """Tiny pictorial figure: y is top of head; arms can be spread or raised."""
    s.ellipse(x, y+3*scale, 3.0*scale, 4*scale, ink)
    s.ellipse(x, y+3*scale, 2.4*scale, 3.2*scale, skin)
    s.polygon([(x-4*scale,y+8*scale),
               (x+4*scale,y+8*scale),
               (x+6*scale,y+23*scale),
               (x-6*scale,y+23*scale)], clothes)
    if pose == 1:
        s.line(x-4*scale,y+10*scale,x-10*scale,y+6*scale,ink,radius=.8*scale)
        s.line(x+4*scale,y+10*scale,x+10*scale,y+6*scale,ink,radius=.8*scale)
    elif pose == 2:
        s.line(x-3*scale,y+10*scale,x-8*scale,y+1*scale,ink,radius=.8*scale)
        s.line(x+3*scale,y+10*scale,x+8*scale,y+1*scale,ink,radius=.8*scale)
    else:
        s.line(x-4*scale,y+10*scale,x-6*scale,y+18*scale,ink,radius=.75*scale)
        s.line(x+4*scale,y+10*scale,x+6*scale,y+18*scale,ink,radius=.75*scale)


def tree(s,x,y,leaf,trunk,highlight):
    s.line(x,y+15,x,y-2,trunk,radius=1.6)
    for dx,dy,r in [(-5,1,7),(3,-3,8),(-1,-10,8)]:
        s.ellipse(x+dx,y+dy,r,r*.78,leaf)
    s.ellipse(x-4,y-10,5,3,highlight)


def petals(s,x,y,petal,center,stem):
    for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        s.ellipse(x+dx,y+dy,1.7,1.7,petal)
    s.dot(x,y,center)
    s.line(x,y+2,x,y+5,stem)


def birth_venus():
    s=painting([
        "FFB5E9E6","FF78BAC2","FF417C9B","FFF3D5AC",
        "FFDDAA79","FFF6E7C5","FF9F653F","FFDBA44E",
        "FFF1C36B","FFC69388","FF448572","FFFFF6DB",
    ])
    s.rect(0,35,63,63,1);s.rect(0,47,63,63,2)
    for x,y in [(4,40),(16,51),(32,44),(49,55)]:
        s.line(x,y,x+10,y,0)
    cloud(s,9,12,9,11,0);cloud(s,52,9,8,11,0)
    # The famous scallop shell, gold hair and central Venus silhouette.
    s.polygon([(13,53),(24,47),(32,50),(40,47),(53,53),
               (49,60),(32,63),(16,60)],6)
    s.polygon([(15,54),(25,49),(32,52),(40,49),(51,54),
               (47,58),(32,61),(18,58)],3)
    for x in (20,25,31,37,43):
        s.line(32,61,x,53,4,radius=.65)
    s.ellipse(31,19,10,13,6)
    s.ellipse(32,20,7,10,7)
    s.ellipse(32,17,6,8,3)
    s.ellipse(33,18,4,6.8,5)
    s.polygon([(27,26),(36,27),(40,45),(34,51),
               (25,51),(24,39)],3)
    s.polygon([(27,31),(36,31),(35,48),(28,48)],5)
    s.line(25,32,23,39,4,radius=1.7)
    s.line(38,32,40,43,4,radius=1.6)
    s.line(22,39,31,42,5,radius=1.3)
    s.line(40,43,35,44,5,radius=1.2)
    for x,y in [(22,26),(23,33),(23,40),(37,26),(40,32),(41,39)]:
        s.ellipse(x,y,2.5,4,7)
    s.line(32,50,29,55,5,radius=1.7)
    s.line(34,50,36,55,5,radius=1.7)
    s.dot(30,18,6);s.dot(35,18,6)
    s.line(32,22,35,23,9)
    for x,y in [(7,30),(11,33),(53,30),(57,26)]:
        s.ellipse(x,y,4,3,9)
    return s


def creation_adam():
    s=painting([
        "FFDAE5D5","FFB0C6B4","FFF1E2C7","FF856D66",
        "FFD9A57E","FFF3D0A8","FF8F4B63","FFB96773",
        "FF526A62","FFBAA68B","FFF9F3E3",
    ])
    cloud(s,17,13,15,10,1);cloud(s,50,12,16,10,1)
    s.polygon([(0,48),(19,40),(32,49),(36,63),(0,63)],8)
    s.polygon([(30,6),(48,1),(63,13),(63,38),
               (45,33),(35,23)],6)
    s.polygon([(35,7),(54,5),(63,13),(63,31),
               (51,27),(38,22)],7)
    # Reclining Adam, the other figure within burgundy drapery.
    s.ellipse(13,31,5,5,3);s.ellipse(13,30,4.3,4.2,4)
    s.polygon([(10,34),(20,34),(30,41),(27,48),
               (15,42),(5,45)],4)
    s.polygon([(9,39),(17,42),(12,53),(5,57)],4)
    s.line(19,36,29,31,4,radius=2.0)
    s.line(29,31,34,29,5,radius=1.0)
    s.line(33,29,39,28,5,radius=.65)
    s.polygon([(13,43),(22,46),(32,51),(26,54),(13,48)],3)
    s.ellipse(52,15,4.9,5.2,3);s.ellipse(52,15,4,4.4,5)
    s.polygon([(49,20),(55,20),(60,34),(46,30)],2)
    s.line(49,23,43,26,4,radius=1.8)
    s.line(43,26,39,27,5,radius=1)
    s.line(41,27,36,28,5,radius=.75)
    for x,y in [(41,13),(60,22),(51,30)]:
        s.ellipse(x,y,3.1,3,5)
        s.dot(x,y-3,3)
    s.line(34,28,36,28,10,radius=.4)
    return s


def last_supper():
    s=painting([
        "FFC1AE93","FF755E56","FFD9C3A4","FF6A858D",
        "FFB5C7B8","FF352F37","FFB67B60","FFEAC69E",
        "FFAF514C","FF477E8C","FFF4E8D1","FF946C54",
    ])
    s.rect(0,0,63,42,2)
    s.polygon([(0,0),(25,13),(38,13),(63,0)],1)
    s.polygon([(0,63),(26,33),(38,33),(63,63)],11)
    for x in (8,28,49):
        s.rect(x,9,x+8,30,1)
        s.rect(x+2,11,x+6,27,3)
        s.rect(x+2,23,x+6,27,4)
    s.line(31,13,31,41,1)
    # Thirteen figures at the long table, central Jesus in blue/red.
    for i,x in enumerate(range(2,63,5)):
        center=i==6
        skin=7; cloth=(8 if i%4==0 else (9 if i%3==0 else 1))
        if center:cloth=9
        s.ellipse(x,33,2.4,3.2,5)
        s.ellipse(x,32,1.8,2.5,skin)
        s.polygon([(x-3,36),(x+3,36),(x+4,43),(x-4,43)],cloth)
        if center:
            s.polygon([(x-3,37),(x+2,37),(x+6,44),(x-4,44)],8)
            s.ellipse(x,31,4.8,5.2,10)
            s.ellipse(x,31,2.2,2.9,7)
        s.line(x-3,40,x-5,44,skin)
        s.line(x+3,40,x+5,44,skin)
    s.rect(1,45,62,51,10)
    s.rect(0,51,63,54,1)
    for x in range(4,61,10):
        s.ellipse(x,47,3,1.3,11)
        s.dot(x+1,46,8)
    s.polygon([(0,54),(63,54),(63,63),(0,63)],2)
    for x in range(0,64,11):
        s.line(x,63,30,54,1,radius=.5)
    return s


def school_athens():
    s=painting([
        "FFEEE3CB","FF7A6D67","FFC5A587","FFF4D1A0",
        "FF4B6079","FF998670","FFD8BC9A","FF9E4D51",
        "FF608A89","FFEAE9DF","FF394157","FFB79E7A",
    ])
    s.rect(0,0,63,63,2)
    s.polygon([(0,0),(16,2),(28,18),(28,50),(0,58)],5)
    s.polygon([(63,0),(47,2),(36,18),(36,50),(63,58)],5)
    s.rect(17,0,46,40,1)
    s.rect(20,4,43,40,9)
    s.ellipse(32,24,20,23,1)
    s.ellipse(32,26,16.5,18,0)
    s.rect(24,22,40,44,4)
    s.rect(26,24,38,44,8)
    for x in (7,14,49,56):
        s.rect(x,13,x+3,50,1)
        s.rect(x+1,14,x+2,48,6)
        s.rect(x-2,12,x+6,14,9)
        s.rect(x-2,48,x+6,51,9)
    for y in (49,55,60):
        s.line(0,y,63,y,1)
    for x in (0,12,52,63):
        s.line(x,63,32,44,1)
    # Plato and Aristotle stand below the central arch.
    person(s,28,27,3,7,10,.72,2)
    person(s,37,27,3,4,10,.72,1)
    for x,y,robe in [(7,36,7),(15,36,8),(48,35,4),(56,33,7),
                     (18,42,10),(44,42,10)]:
        person(s,x,y,3,robe,1,.55)
    s.line(25,31,28,24,3,radius=.8)
    s.line(38,34,44,33,3,radius=.8)
    return s


def night_watch():
    s=painting([
        "FF282A27","FF474235","FF806C4A","FFBC9D62",
        "FFF5CB75","FF5F3D36","FF9C4A3E","FF383B41",
        "FFD7B38B","FFEAD8B6","FFAC976D","FFBFC0A5",
    ])
    s.rect(0,0,63,63,0)
    s.ellipse(31,28,27,27,1)
    s.polygon([(0,63),(0,43),(18,36),(42,38),(63,31),(63,63)],2)
    s.rect(0,53,63,63,0)
    s.rect(2,4,10,43,1);s.rect(48,5,56,40,1)
    # Guards of Rembrandt's company, focal figures brighter.
    for x,y,c in [(10,31,7),(19,29,5),(29,22,7),
                  (42,27,3),(52,32,7)]:
        person(s,x,y,8,c,0,.9)
        s.ellipse(x,y,5,1.7,0)
        s.line(x-6,y+1,x+6,y+1,0,radius=1.4)
    s.polygon([(24,35),(35,34),(40,60),(19,60)],4)
    s.polygon([(25,36),(34,35),(37,56),(22,58)],10)
    s.rect(24,40,34,42,3)
    s.line(36,40,56,17,0,radius=1)
    s.line(36,39,58,18,11,radius=.6)
    s.line(12,36,4,14,0,radius=1)
    s.ellipse(48,35,3,3,8)
    s.polygon([(43,40),(51,38),(57,61),(43,61)],4)
    s.dot(48,38,9)
    for x,y in [(4,52),(58,48),(16,51),(33,48)]:
        s.dot(x,y,3)
    return s


def milkmaid():
    s=painting([
        "FFCFD5C9","FF736B5D","FFE9E1C5","FF92A7A6",
        "FF4E6D87","FFF0C457","FFBA965D","FFE5BC93",
        "FF32557E","FFF4EAD5","FF99704E","FF434A4A",
    ])
    s.rect(0,0,63,63,0)
    s.rect(4,5,30,31,1);s.rect(6,7,28,29,3)
    s.rect(8,9,26,27,2)
    s.line(17,7,17,29,1);s.line(6,17,28,17,1)
    for x,y in [(8,10),(21,14),(24,24)]:s.dot(x,y,9)
    s.rect(0,46,63,63,10)
    s.rect(0,43,63,46,1)
    s.rect(1,45,61,49,2)
    # Vermeer's maid in blue apron and ochre bodice pouring a jug.
    s.polygon([(27,25),(41,25),(49,48),(17,48)],5)
    s.polygon([(27,38),(39,38),(46,62),(18,62)],8)
    s.polygon([(32,38),(43,38),(48,61),(26,61)],4)
    s.ellipse(34,19,7,9,1)
    s.ellipse(34,20,5.8,8,7)
    s.polygon([(27,10),(35,7),(41,13),(36,15),(28,15)],2)
    s.line(27,31,19,41,7,radius=2)
    s.line(40,32,34,40,7,radius=2)
    s.ellipse(21,40,6,4,6)
    s.ellipse(20,39,4,2.8,10)
    s.line(24,41,26,49,9,radius=.8)
    s.ellipse(10,49,7,3,6)
    s.ellipse(54,49,7,3,6)
    for x in (8,13,51,56):s.dot(x,48,9)
    return s


def las_meninas():
    s=painting([
        "FF3F3935","FF6B6054","FF9D8D74","FFD9BFA0",
        "FFF7E3B8","FF3E4F60","FF977154","FFB8A58D",
        "FFAD8D75","FFF7F0DC","FF272C35",
    ])
    s.rect(0,0,63,63,0)
    s.rect(3,5,19,39,1);s.rect(5,7,17,37,5)
    s.rect(39,9,55,35,1);s.rect(41,11,53,32,6)
    s.rect(43,13,50,30,2)
    s.rect(25,8,37,26,10);s.rect(27,10,35,24,1)
    s.rect(29,12,33,21,7)
    s.rect(0,56,63,63,1)
    # Painter with giant canvas on left; standing attendants on right.
    s.polygon([(2,20),(15,16),(18,55),(4,57)],10)
    s.polygon([(4,21),(15,20),(16,54),(6,54)],1)
    person(s,21,25,8,5,10,.75)
    person(s,49,27,8,5,10,.7)
    person(s,58,31,8,10,10,.62)
    # Infanta in a luminous wide crinoline gown.
    s.ellipse(34,30,6,7,1);s.ellipse(34,30,5,5.8,3)
    s.ellipse(34,24,8,3,6)
    s.polygon([(28,36),(40,36),(49,59),(18,59)],7)
    s.ellipse(34,50,16,11,4)
    s.ellipse(34,51,13,8,3)
    for x in (23,27,31,35,40,44):
        s.line(x,47,x+2,56,9,radius=.6)
    s.line(26,39,20,44,3,radius=1.6)
    s.line(42,40,48,43,3,radius=1.6)
    s.ellipse(7,60,5,3,6)
    return s


def third_may():
    s=painting([
        "FF25344A","FF3F4954","FF777065","FFBC9A75",
        "FFF1DEC0","FFCEAF84","FFB7B4AB","FF574A45",
        "FFF8E5A2","FFDAC29C","FF485463",
    ])
    s.rect(0,0,63,63,0)
    hill(s,[(0,36),(14,30),(32,42),(47,31),(63,34)],2)
    hill(s,[(0,49),(12,43),(23,45),(37,41),(63,46)],7)
    s.rect(0,55,63,63,1)
    # Lantern beside a central white-shirted protester with raised arms.
    s.rect(30,38,38,50,7)
    s.rect(31,39,37,47,8)
    s.dot(34,43,4)
    s.ellipse(22,26,5,5,7);s.ellipse(22,27,4,4,9)
    s.polygon([(17,33),(26,33),(29,50),(14,50)],4)
    s.line(18,36,10,22,4,radius=2)
    s.line(26,36,34,22,4,radius=2)
    s.dot(9,21,9);s.dot(35,21,9)
    s.polygon([(17,49),(22,49),(21,62),(15,62)],5)
    s.polygon([(23,49),(28,49),(31,62),(24,62)],5)
    for x,y in [(4,38),(12,42),(29,45)]:
        person(s,x,y,9,1,7,.55)
    # Silhouetted firing line; muskets point to the central figure.
    for x,y in [(46,34),(53,35),(60,36)]:
        person(s,x,y,9,0,10,.75)
        s.line(x-1,44,36,34,10,radius=.75)
    s.ellipse(19,61,13,2.2,2)
    return s


def liberty_leading():
    s=painting([
        "FFADB6BA","FF7F8F94","FFC9AD89","FF594E49",
        "FF26394A","FFB88462","FFF1D49C","FF275B99",
        "FFF6EEE1","FFC73F46","FF846349","FF5E665A",
    ])
    s.rect(0,0,63,63,1)
    cloud(s,12,15,12,2,1);cloud(s,55,22,16,2,1)
    hill(s,[(0,56),(13,50),(33,53),(51,46),(63,53)],10)
    # Windblown French tricolor above a leader and a crowd.
    s.line(33,35,42,4,3,radius=.9)
    s.polygon([(41,3),(50,6),(61,2),(58,19),(47,16),(40,13)],8)
    s.polygon([(41,3),(48,4),(47,16),(40,13)],7)
    s.polygon([(48,4),(55,4),(53,17),(47,16)],8)
    s.polygon([(55,4),(61,2),(58,19),(53,17)],9)
    s.ellipse(30,26,4.6,5.4,3)
    s.ellipse(30,26,3.8,4.5,5)
    s.polygon([(27,30),(33,30),(38,51),(19,53)],6)
    s.polygon([(27,37),(36,39),(39,54),(18,54)],2)
    s.line(32,33,39,18,5,radius=1.4)
    s.line(29,34,18,45,5,radius=1.4)
    s.line(37,19,41,16,5)
    person(s,13,35,5,4,3,.85,1)
    person(s,50,36,5,3,4,.82,2)
    for x,y in [(3,48),(57,49),(7,55),(47,54)]:
        s.ellipse(x,y,4,4,4)
        s.ellipse(x,y,2.8,2.7,5)
    s.line(0,60,63,59,3,radius=1.4)
    return s


def wanderer_fog():
    s=painting([
        "FFC7DAD9","FFA4BEC2","FFDFE4D6","FF889E9C",
        "FF718788","FF536C73","FF3C4F5B","FF243646",
        "FF8E877A","FFB6BBB3","FFEFF0E1",
    ])
    s.rect(0,0,63,63,0)
    cloud(s,11,15,17,2,0);cloud(s,48,10,18,2,0)
    hill(s,[(0,39),(7,27),(14,35),(24,22),
            (35,39),(49,25),(63,33)],3)
    hill(s,[(0,47),(16,36),(30,48),(45,35),(63,47)],4)
    s.rect(0,43,63,46,1)
    cloud(s,16,43,21,2,1);cloud(s,47,46,23,2,1)
    hill(s,[(0,56),(13,51),(28,59),(37,53),(54,57),(63,50)],5)
    s.polygon([(0,63),(14,56),(23,52),(28,61),(36,58),
               (50,53),(63,63)],8)
    # Back-turned traveler with staff looking over mountains.
    s.ellipse(34,24,4.7,5.2,7)
    s.polygon([(29,29),(39,29),(44,51),(24,51)],7)
    s.polygon([(31,30),(38,30),(40,49),(28,49)],6)
    s.line(26,31,23,47,7,radius=2)
    s.line(40,32,44,47,7,radius=1.8)
    s.polygon([(28,49),(33,49),(32,60),(26,60)],7)
    s.polygon([(35,49),(40,49),(42,60),(36,60)],7)
    s.line(46,30,47,62,8,radius=1)
    s.line(44,41,47,39,7,radius=1.4)
    s.line(0,61,63,62,5)
    return s


def fighting_temeraire():
    s=painting([
        "FF8193AE","FFB5BBC5","FFE2BEAE","FFF3AD7D",
        "FFFFD6A0","FFF9E4C0","FF596A87","FF3D4F63",
        "FFA89A83","FF766B6A","FF33434D","FFFAEAC8",
    ])
    s.rect(0,0,63,18,0)
    s.rect(0,18,63,34,2)
    s.rect(0,34,63,63,6)
    s.ellipse(51,32,8,8,3);s.ellipse(51,32,5.4,5.4,4)
    cloud(s,10,14,12,1,0);cloud(s,44,12,12,2,1)
    for y in (44,50,56):
        for x in range(2,63,13):
            s.line(x,y,x+7,y,7)
    # Golden ghost ship is towed by a small dark paddle steamer.
    s.polygon([(5,43),(37,42),(30,48),(11,47)],9)
    s.polygon([(7,43),(34,42),(29,45),(12,45)],8)
    for x,h in [(14,15),(24,7),(30,20)]:
        s.line(x,h,x,43,8,radius=.85)
        s.polygon([(x,h+1),(x+8,h+8),(x+7,35),(x,37)],11)
        s.polygon([(x,h+2),(x+6,h+8),(x+5,34),(x,36)],1)
    s.line(6,43,30,26,8)
    s.line(30,26,34,43,8)
    s.polygon([(38,48),(60,47),(56,54),(41,54)],10)
    s.rect(43,39,57,47,7)
    s.rect(46,36,53,43,10)
    s.rect(49,29,52,38,10)
    s.ellipse(50,24,5,3,9)
    s.ellipse(54,19,7,4,8)
    s.line(31,47,40,48,9,radius=.55)
    return s


def hay_wain():
    s=painting([
        "FFB1D6DF","FFE4EEF0","FF6D8E86","FF4E7654",
        "FF7EAA73","FFB7C38C","FF7A5945","FFC4A078",
        "FFD7C8A8","FF476D88","FF80AFB7","FFF7E5C1",
    ])
    s.rect(0,0,63,63,0)
    cloud(s,14,11,13,1,0);cloud(s,49,14,10,1,0)
    hill(s,[(0,38),(18,33),(37,38),(52,33),(63,36)],4)
    s.rect(0,46,63,63,9)
    for y in (50,55,61):
        for x in range(3,60,12):s.line(x,y,x+5,y,10)
    s.polygon([(0,41),(7,32),(23,34),(28,47),(0,55)],3)
    s.rect(6,23,23,40,7)
    s.polygon([(4,24),(14,16),(26,23)],6)
    s.rect(9,29,15,37,6);s.rect(10,30,14,36,8)
    s.line(22,39,27,46,6)
    tree(s,39,20,3,6,4)
    tree(s,51,25,3,6,4)
    # Cart wheels partly submerged in the shallows.
    s.polygon([(24,42),(44,42),(41,50),(27,49)],6)
    s.polygon([(26,43),(42,43),(40,46),(28,46)],7)
    for x in (29,41):
        s.ellipse(x,49,5,5,6)
        s.ellipse(x,49,3,3,9)
        s.dot(x,49,7)
    s.line(41,46,53,47,6,radius=.8)
    s.ellipse(54,45,6,4,6)
    s.ellipse(54,44,5,3,7)
    for x in (52,58):
        s.line(x,47,x,54,6,radius=.8)
    for x,y in [(3,57),(12,61),(58,57)]:
        s.ellipse(x,y,6,1.8,5)
    return s


def impression_sunrise():
    s=painting([
        "FFB8C5C6","FF8EA9B0","FF778E9A","FF5B7788",
        "FFE78A58","FFFFAA5E","FF3E6575","FFACC2C1",
        "FF456374","FFD8A6A1",
    ])
    s.rect(0,0,63,26,0)
    s.rect(0,26,63,63,2)
    s.rect(0,37,63,63,3)
    for x,h in [(3,14),(9,17),(15,11),(25,18),(41,10),(56,17)]:
        s.rect(x,h,x+3,35,6)
        s.line(x+1,h-6,x+1,h,6)
    s.line(0,31,63,31,1)
    s.ellipse(42,25,6,6,4)
    s.ellipse(42,25,4.7,4.7,5)
    for x,y,w in [(39,35,7),(38,41,10),(40,48,8),(42,56,9)]:
        s.line(x,y,x+w,y,4,radius=.8)
        s.line(x+2,y+2,x+w-2,y+2,9)
    # Two little rowing boats give Monet's composition its silhouette.
    for x,y in [(17,41),(33,49)]:
        s.polygon([(x-6,y),(x+7,y),(x+4,y+4),(x-3,y+4)],6)
        s.line(x,y,x,y-5,6)
        s.ellipse(x,y-6,1.6,2,6)
        s.line(x-1,y-2,x-4,y+4,6)
    for y in (32,39,46,54,60):
        for x in range((y*3)%11,63,13):
            s.line(x,y,x+6,y,7)
    return s


def water_lilies():
    s=painting([
        "FF285A67","FF357D83","FF4B9290","FF7ABAB1",
        "FF94AD75","FF47775A","FF9BBA79","FFD998B5",
        "FFF8C9D9","FFF9EAED","FF5F8C98","FFA4CAC2",
    ])
    s.rect(0,0,63,63,1)
    for y in range(2,63,7):
        for x in range((y*2)%10,64,13):
            s.line(x,y,x+7,y,2,radius=1.3)
            s.line(x+1,y+2,x+5,y+2,3)
    for x,y,r in [(8,14,8),(29,11,9),(49,17,10),
                  (18,34,10),(45,39,9),(9,55,10),
                  (36,57,10),(61,57,8)]:
        s.ellipse(x,y,r,3.2,5)
        s.ellipse(x-1,y-1,r-1,2.4,4)
        s.polygon([(x,y),(x+3,y-4),(x+7,y-2)],1)
        for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            s.ellipse(x+dx,y-3+dy,2.4,2.1,7)
        s.ellipse(x,y-3,2.1,1.8,9)
        s.dot(x,y-3,8)
    for x,y in [(4,25),(34,29),(56,52),(24,59)]:
        s.ellipse(x,y,4,1.5,11)
    return s


def moulin_galette():
    s=painting([
        "FF6F8994","FFB6C9B0","FF325D52","FF527F64",
        "FFEEE0BD","FFB48B7A","FF444C62","FF8C5662",
        "FFF6DCC3","FFD2AB75","FF9EBA9C","FF59666B",
    ])
    s.rect(0,0,63,63,1)
    for x,y in [(4,14),(22,10),(47,13),(59,7)]:
        tree(s,x,y,2,11,3)
    s.rect(0,49,63,63,9)
    for x in range(4,64,13):
        s.ellipse(x,55,4,1.5,5)
    # Dancing couples overlap under sun-dappled leaves.
    for x,y,clothes in [(8,29,6),(23,26,7),(41,26,6),(55,31,7)]:
        person(s,x,y,8,clothes,11,.87,1)
        s.ellipse(x,y+1,4.5,1.5,11)
    for x,y,skirt in [(16,34,4),(33,33,9),(51,38,4)]:
        s.ellipse(x,y,3.2,4,11)
        s.ellipse(x,y,2.7,3.2,8)
        s.polygon([(x-4,y+5),(x+4,y+5),(x+11,y+24),(x-11,y+24)],skirt)
        s.line(x-5,y+8,x-10,y+11,8,radius=1.2)
        s.line(x+5,y+8,x+11,y+11,8,radius=1.2)
    # The famous bright hanging lanterns and speckled patches of daylight.
    for x,y in [(8,13),(32,17),(55,15)]:
        s.line(x,y-9,x,y,11)
        s.ellipse(x,y,3.8,4.5,4)
        s.dot(x,y,9)
    for x,y in [(12,46),(28,51),(42,44),(59,49)]:
        s.ellipse(x,y,6,1.8,10)
    return s


def grande_jatte():
    s=painting([
        "FFC5E1E5","FF8BC3D0","FF427C8B","FF86B985",
        "FF5F9C73","FF3C715D","FFF4EBD1","FF423F53",
        "FFD7B296","FFB77275","FFF8CB72","FFA2C6B0",
    ])
    s.rect(0,0,63,63,0)
    s.rect(0,23,63,37,1)
    s.rect(0,37,63,63,3)
    for x in range(4,63,9):
        s.line(x,29,x+5,29,2)
    for x,h in [(0,18),(11,22),(52,22),(60,18)]:
        tree(s,x,h,5,7,4)
    # Boat in the Seine and park bench.
    s.polygon([(5,34),(21,34),(17,37),(7,37)],7)
    s.line(13,20,13,34,7)
    s.polygon([(13,22),(13,32),(22,32)],6)
    s.rect(9,50,27,52,7)
    s.rect(11,53,12,60,7);s.rect(24,53,25,60,7)
    person(s,37,28,8,9,7,.9)
    s.line(36,30,44,25,7,radius=1)
    # Distinct parasol carrying figures.
    s.ellipse(49,21,11,6.5,7)
    s.ellipse(49,20,10,5.5,10)
    s.line(49,21,50,55,7,radius=.9)
    person(s,50,33,8,7,7,.98)
    s.polygon([(44,46),(53,45),(60,63),(42,63)],7)
    s.polygon([(46,46),(52,46),(57,62),(44,62)],6)
    person(s,25,36,8,7,7,.55)
    s.ellipse(4,59,5,2.2,7)
    s.ellipse(8,57,3,2.5,7)
    s.dot(2,56,7)
    for x,y in [(17,44),(23,58),(33,55)]:
        s.dot(x,y,4)
    return s


def kiss_klimt():
    s=painting([
        "FFB8944D","FFDCB969","FFF8DE95","FFFFEDB1",
        "FF3C3D39","FF977747","FFF2CBAA","FF8E5B4E",
        "FFE6A19B","FF6D9557","FFB6BB6E","FFFDF1CE",
    ])
    s.rect(0,0,63,63,0)
    for y in range(4,63,9):
        for x in range((y*3)%9,64,12):
            s.rect(x,y,x+3,y+5,1)
            s.dot(x+2,y+2,3)
    s.rect(0,53,63,63,9)
    for x in range(3,63,8):
        for y in (55,60):
            s.ellipse(x,y,3,2.2,10)
            s.dot(x,y,8)
    # Embrace as two heads framed by gold mosaic cloaks.
    s.polygon([(18,24),(45,19),(55,52),(48,62),
               (18,62),(10,50)],4)
    s.polygon([(18,26),(43,21),(52,51),(47,60),
               (18,59),(13,49)],1)
    s.ellipse(28,21,9,11,4)
    s.ellipse(26,21,6.6,8.5,7)
    s.ellipse(37,24,7,10,4)
    s.ellipse(38,24,5.3,7.8,6)
    s.line(34,27,30,31,6,radius=1.5)
    s.line(43,31,34,36,6,radius=1.4)
    s.polygon([(20,37),(30,35),(33,62),(12,62)],0)
    s.polygon([(32,37),(47,31),(54,62),(33,62)],2)
    for x,y in [(17,40),(23,46),(28,54),(39,42),(45,51),(40,58)]:
        s.rect(x,y,x+5,y+6,4)
        s.rect(x+1,y+1,x+3,y+4,2)
    for x,y in [(17,53),(28,44),(45,39),(41,56)]:
        s.ellipse(x,y,3,3,8)
        s.dot(x,y,11)
    s.line(25,20,34,25,6)
    return s


def card_players():
    s=painting([
        "FF9C8A75","FF68574D","FFBEA38A","FFE2BE93",
        "FF544A43","FF39616A","FF7C5A52","FFB8805B",
        "FFEBD4AF","FF2C3E47","FFF8E5BA",
    ])
    s.rect(0,0,63,63,0)
    s.rect(0,33,63,63,1)
    s.rect(13,4,51,35,2)
    s.rect(17,8,47,32,0)
    s.ellipse(33,21,7,10,1)
    # Two solemn Provençal card players lean toward the table.
    for x,color,arm in [(17,5,1),(47,6,-1)]:
        s.ellipse(x,24,6,8,4)
        s.ellipse(x,25,4.7,6.7,3)
        s.polygon([(x-9,31),(x+8,31),(x+13,60),(x-11,60)],color)
        s.ellipse(x,19,9,2.5,4)
        s.ellipse(x,19,7,1.2,1)
        s.line(x+arm*5,37,x+arm*10,43,3,radius=2)
        s.line(x+arm*10,43,x+arm*7,48,3,radius=1.5)
        s.dot(x+(3 if x<32 else -3),25,4)
    s.rect(3,47,60,51,7)
    s.rect(5,51,58,56,1)
    s.rect(10,56,13,63,4)
    s.rect(50,56,53,63,4)
    s.polygon([(26,47),(35,47),(33,51),(27,51)],8)
    for x,y in [(29,48),(32,49),(38,48)]:
        s.rect(x,y,x+3,y+1,10)
        s.dot(x+1,y,6)
    s.rect(29,24,33,39,10)
    s.rect(28,23,34,25,4)
    return s


def wheatfield_crows():
    s=painting([
        "FF203C67","FF3C6394","FF6588A6","FFCEB154",
        "FFF5D36A","FFE9B54D","FF92733F","FF4E663E",
        "FF273C4F","FF899F83","FFF7E8B5",
    ])
    s.rect(0,0,63,34,0)
    s.rect(0,9,63,30,1)
    for x in range(2,63,7):
        s.line(x,12,x+4,9,2,radius=1)
        s.line(x,23,x+6,24,0)
    hill(s,[(0,34),(16,31),(29,35),(42,32),(63,34)],7)
    s.rect(0,36,63,63,3)
    s.polygon([(0,38),(15,35),(23,43),(10,63),(0,63)],4)
    s.polygon([(31,39),(44,35),(63,38),(63,63),(38,63)],4)
    s.polygon([(24,36),(32,36),(39,63),(11,63)],6)
    s.polygon([(26,37),(30,37),(34,63),(17,63)],8)
    for x in range(1,63,5):
        for y in (42,50,57):
            if not (x>20 and x<34):
                s.line(x,y,x+1,y-4,5)
                s.dot(x+1,y-4,10)
    # The restless, scattered black crows are the painting's key symbol.
    for x,y in [(8,12),(20,7),(31,19),(43,9),(55,18),
                (12,26),(37,28),(49,23),(59,30)]:
        s.line(x-4,y-2,x,y,8,radius=.9)
        s.line(x,y,x+4,y-2,8,radius=.9)
        s.dot(x,y,8)
    return s


def sleeping_gypsy():
    s=painting([
        "FF21345B","FF425C80","FF6E7194","FFB3A5AB",
        "FFE9DEB8","FFF5E6C3","FFB98957","FF614D3D",
        "FF9A6C55","FF3A344B","FFF2D27E","FF886B76",
    ])
    s.rect(0,0,63,63,0)
    s.rect(0,20,63,46,1)
    s.ellipse(48,14,8,8,4)
    s.ellipse(50,12,7,7,10)
    for x,y in [(8,7),(20,13),(29,6),(57,31),(10,24)]:
        s.dot(x,y,4)
    hill(s,[(0,42),(12,32),(26,37),(42,31),(63,40)],2)
    hill(s,[(0,52),(19,45),(31,50),(47,43),(63,51)],8)
    s.rect(0,53,63,63,6)
    for x in range(3,63,11):
        s.dot(x,58,7)
    # Rousseau's striped resting figure, mandolin and watchful lion.
    s.ellipse(23,50,17,5.5,9)
    s.polygon([(12,45),(38,44),(46,50),(14,53)],3)
    s.polygon([(13,46),(36,45),(43,49),(16,51)],11)
    for x in (17,22,27,32,37):
        s.line(x,46,x+4,50,0)
    s.ellipse(11,45,5.3,5.5,9)
    s.ellipse(12,45,4.3,4.3,8)
    s.line(38,50,48,49,7,radius=1.6)
    s.ellipse(39,54,7,3,7)
    s.ellipse(39,54,5.5,2,6)
    # Maned lion at right with elongated back and tasseled tail.
    s.ellipse(52,40,11,7,7)
    s.ellipse(53,39,9,5.4,6)
    s.ellipse(45,38,5,6,7)
    s.ellipse(45,38,3.8,4.5,6)
    s.ellipse(45,39,2.2,2,4)
    s.dot(44,37,9);s.dot(47,37,9)
    s.ellipse(45,41,1.4,1,9)
    for x in (49,57):
        s.line(x,44,x,53,7,radius=1.5)
    s.line(59,40,63,33,7,radius=1.2)
    s.dot(62,33,9)
    s.line(17,55,38,57,9)
    return s


PICTURES = [
    ("online-classic-birth-venus","زایش ونوس","The Birth of Venus",birth_venus),
    ("online-classic-creation-adam","آفرینش آدم","The Creation of Adam",creation_adam),
    ("online-classic-last-supper","شام آخر","The Last Supper",last_supper),
    ("online-classic-school-athens","مکتب آتن","The School of Athens",school_athens),
    ("online-classic-night-watch","نگهبان شب","The Night Watch",night_watch),
    ("online-classic-milkmaid","زن شیرفروش","The Milkmaid",milkmaid),
    ("online-classic-las-meninas","ندیمه‌ها","Las Meninas",las_meninas),
    ("online-classic-third-may","سوم ماه مه ۱۸۰۸","The Third of May 1808",third_may),
    ("online-classic-liberty-leading","آزادی هدایتگر مردم","Liberty Leading the People",liberty_leading),
    ("online-classic-wanderer-fog","مسافر بر فراز دریای مه","Wanderer above the Sea of Fog",wanderer_fog),
    ("online-classic-fighting-temeraire","تمریر جنگجو","The Fighting Temeraire",fighting_temeraire),
    ("online-classic-hay-wain","گاری علف خشک","The Hay Wain",hay_wain),
    ("online-classic-impression-sunrise","برداشت، طلوع آفتاب","Impression, Sunrise",impression_sunrise),
    ("online-classic-water-lilies","نیلوفرهای آبی","Water Lilies",water_lilies),
    ("online-classic-moulin-galette","رقص در مولن دو لا گالت","Dance at Le Moulin de la Galette",moulin_galette),
    ("online-classic-grande-jatte","یکشنبه در جزیره گراند ژات","A Sunday Afternoon on La Grande Jatte",grande_jatte),
    ("online-classic-klimt-kiss","بوسه","The Kiss",kiss_klimt),
    ("online-classic-card-players","ورق‌بازان","The Card Players",card_players),
    ("online-classic-wheatfield-crows","مزرعه گندم با کلاغ‌ها","Wheatfield with Crows",wheatfield_crows),
    ("online-classic-sleeping-gypsy","کولی خفته","The Sleeping Gypsy",sleeping_gypsy),
]


def create_pack(destination):
    if len(PICTURES) != 20 or len({row[0] for row in PICTURES}) != 20:
        raise ValueError("Twenty distinct masterwork IDs are required")
    catalog = []
    files = {}
    for identifier, title_fa, title_en, painter in PICTURES:
        artwork = painter()
        level = {
            "schemaVersion": 2,
            "levelId": identifier,
            "levelVersion": 1,
            "titles": {"fa": title_fa, "en": title_en},
            "width": artwork.side,
            "height": artwork.side,
            "palette": artwork.palette,
            "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        encoded = compact(level)
        stem = f"{identifier}-v1"
        catalog.append({
            "id": identifier,
            "version": 1,
            "title": title_fa,
            "titleEn": title_en,
            "category": "patterns",
            "width": artwork.side,
            "height": artwork.side,
            "bytes": len(encoded),
            "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = encoded
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(catalog)
    output = pathlib.Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("catalog.json", compact({
            "schemaVersion": 1, "pictures": catalog,
        }))
        for name, payload in files.items():
            bundle.writestr(name, payload)
    print(f"Created {len(catalog)} original 64x64 painting interpretations: {output}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_masterworks_20_pack.py <content.zip>")
    create_pack(sys.argv[1])
