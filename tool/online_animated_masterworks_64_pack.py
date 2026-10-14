#!/usr/bin/env python3
"""Ten hand-authored 64x64 animated interpretations of distinct public-domain paintings.

No scans, resized reproductions, or third-party artwork assets are embedded.
Only reproducible drawing instructions enter Git; the generated numbered levels,
previews and checksum-bound animation sidecars live in immutable online Releases.
"""
import hashlib
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite

SIDE = 64
PREFIX = "online-classic-animated64-"
FRAME_DURATION_MS = 180


def canvas(colors):
    if len(colors) > 48 or any(len(color) != 8 for color in colors):
        raise ValueError("A valid ARGB palette with up to 48 colors is required")
    return Sprite(SIDE, colors)


def star(s, x, y, color):
    s.dot(x, y, color)
    s.dot(x-1, y, color)
    s.dot(x+1, y, color)
    s.dot(x, y-1, color)
    s.dot(x, y+1, color)


def blossom(s, x, y, petal, center):
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)):
        s.ellipse(x+dx, y+dy, 1.8, 1.7, petal)
    s.ellipse(x, y, 1.4, 1.4, center)


def whistlers_mother():
    """Seated black-dressed profile, white bonnet, print and patterned curtain."""
    s=canvas(["FF9C9C93","FF242528","FF67665E","FFE0DACC","FF414143",
              "FF56473B","FFCEAE91","FF7D644F","FFB0ACA1","FFF7F2E5"])
    s.rect(0,51,63,63,5);s.rect(0,49,63,51,2)
    s.rect(1,0,13,49,1);s.rect(3,0,11,49,2)
    for y in range(3,47,6):
        s.line(4,y,10,y+4,8,radius=.6)
        s.dot(6,y+2,3)
    s.rect(19,5,41,22,1);s.rect(21,7,39,20,9)
    s.rect(23,9,37,18,8)
    s.polygon([(23,16),(28,12),(31,15),(35,11),(37,16)],2)
    s.rect(20,42,47,45,7);s.rect(21,45,23,60,7);s.rect(45,45,47,60,7)
    s.polygon([(35,24),(43,27),(48,38),(55,61),(20,61),
               (14,56),(21,42),(32,32)],1)
    s.polygon([(35,29),(45,34),(50,48),(47,57),(20,57),
               (24,45)],4)
    s.ellipse(41,23,8,11,1);s.ellipse(43,22,6.2,8.5,3)
    s.polygon([(37,13),(45,10),(49,17),(49,23),(45,19),(40,19)],9)
    s.ellipse(44,24,4.0,5.2,6)
    s.polygon([(39,22),(35,25),(40,27),(45,28),(46,24)],6)
    s.dot(40,22,1);s.line(36,26,39,26,5,radius=.6)
    s.polygon([(41,29),(47,31),(51,38),(46,39),(40,35)],3)
    s.polygon([(44,36),(33,38),(29,40),(35,44),(45,42)],3)
    s.line(31,41,38,41,9,radius=1.3)
    return s


def arnolfini_portrait():
    """Oak-paneled room, tall couple, green gown, brass chandelier and convex mirror."""
    s=canvas(["FF73563F","FF2E3028","FF455342","FF66814C","FFA6A36D",
              "FFE1BF89","FFB47C59","FFE7D8AD","FF47382E","FFF8E4A2",
              "FF9D7553","FFACB5A0"])
    s.rect(0,43,63,63,8)
    for y in (48,54,60):
        s.line(0,y,63,y-4,10,radius=.5)
    s.rect(0,8,15,34,1);s.rect(2,10,13,32,11)
    s.rect(3,12,12,31,4)
    for x in (6,10):s.line(x,11,x,31,1)
    s.line(2,21,13,21,1)
    s.ellipse(33,26,8,10,1);s.ellipse(33,26,6.5,8.5,9)
    s.ellipse(33,26,4.5,6.5,11);s.ellipse(33,26,2.5,5,8)
    s.line(28,4,37,4,9,radius=1.3);s.line(33,4,33,12,9,radius=1.2)
    for x in (20,26,33,40,46):
        s.line(33,10,x,13,9,radius=1.0)
        s.ellipse(x,14,2.2,2.3,5)
    # Man on left.
    s.polygon([(17,28),(28,27),(31,48),(27,60),(14,60),(13,45)],1)
    s.polygon([(18,35),(26,33),(24,58),(17,59)],8)
    s.ellipse(23,22,6,8,1);s.ellipse(23,24,4.5,6,6)
    s.rect(17,15,29,19,1);s.rect(19,12,27,16,8)
    s.line(27,35,33,39,6,radius=2.0)
    # Green gown, sleeves and white headdress on right.
    s.polygon([(38,31),(48,32),(54,40),(62,60),(31,61),(32,46)],2)
    s.polygon([(39,35),(48,35),(53,45),(58,58),(35,58)],3)
    for x in (38,43,48,53):
        s.line(x,42,x+4,59,4,radius=.9)
    s.ellipse(43,23,6,8,7);s.ellipse(43,24,4.5,6,6)
    s.polygon([(36,18),(44,14),(49,19),(47,26),(45,20),(39,24)],7)
    s.line(38,36,34,41,6,radius=2)
    s.ellipse(33,43,2,2,6)
    s.ellipse(30,58,6,3,8);s.dot(33,56,9)
    return s


def bedroom_arles():
    """Van Gogh's crooked blue bedroom with prominent yellow/red bed and furniture."""
    s=canvas(["FF8BBDCF","FF3B689C","FFF3D38A","FFDA7C44","FFAA5338",
              "FFDBB15B","FF6B8E82","FF385074","FFF0E9C4","FF6B4834",
              "FFB7D8D9","FFAE754B"])
    s.rect(0,37,63,63,5);s.polygon([(0,42),(63,33),(63,63),(0,63)],11)
    s.line(0,41,63,32,7,radius=1.3);s.line(30,39,31,63,9,radius=.6)
    s.rect(6,9,22,31,7);s.rect(8,11,20,29,10)
    s.line(14,11,14,29,7);s.line(8,21,20,21,7)
    for x,y in ((30,9),(42,8),(52,11)):
        s.rect(x,y,x+8,y+11,9);s.rect(x+2,y+2,x+6,y+8,8)
        s.line(x+2,y+7,x+6,y+3,6,radius=.8)
    s.polygon([(30,39),(52,30),(63,39),(63,52),(39,63),
               (26,55)],4)
    s.polygon([(33,40),(52,33),(61,39),(48,53),(29,54)],2)
    s.polygon([(29,45),(48,37),(61,42),(50,50),(29,56)],5)
    s.polygon([(29,54),(50,47),(58,50),(38,60)],3)
    s.line(52,31,53,54,9,radius=2);s.line(28,42,29,57,9,radius=2)
    s.rect(45,28,56,33,3);s.rect(45,30,56,32,2)
    # Angled chair and bedside table.
    s.rect(6,40,19,45,3);s.line(8,44,5,61,9,radius=1.6)
    s.line(18,44,20,57,9,radius=1.6)
    s.line(8,40,7,32,9,radius=1.4);s.line(18,40,18,34,9,radius=1.4)
    s.rect(22,37,29,44,4);s.line(24,44,22,53,9)
    s.line(28,43,31,51,9)
    return s


def cafe_terrace_night():
    """Yellow awnings and gaslit cafe framing a cobalt-blue starry street."""
    s=canvas(["FF122C63","FF274B88","FF4371A4","FFFFCD60","FFF9E0A0",
              "FFB86B3B","FF423650","FFB2A3A0","FFFDEBBA","FF262C40",
              "FF8E6970","FF588399"])
    s.rect(0,0,27,42,5);s.polygon([(0,0),(23,0),(23,36),(0,44)],3)
    s.rect(3,3,7,30,4);s.rect(11,3,15,31,4)
    s.rect(18,1,22,28,4)
    for y in (9,18,26):
        s.line(0,y,24,y+1,5,radius=.8)
    s.polygon([(0,25),(27,19),(42,24),(13,32)],3)
    s.polygon([(0,27),(27,22),(42,25),(12,34)],4)
    for x in (5,18,31):
        s.line(x,30,x+2,52,9,radius=1.5)
        s.ellipse(x,32,3.6,2.8,8)
    s.polygon([(41,29),(63,24),(63,63),(27,63)],1)
    s.polygon([(51,26),(63,21),(63,63),(48,51)],6)
    s.polygon([(0,48),(29,36),(54,43),(63,63),(0,63)],10)
    s.line(0,48,31,37,11,radius=1)
    for x,y in ((39,5),(47,10),(57,5),(34,16),(51,17),(59,23)):
        star(s,x,y,8)
    for x,y in ((20,41),(28,45),(35,39),(45,47)):
        s.ellipse(x,y,2.1,3.0,9);s.dot(x,y-3,7)
    s.ellipse(11,39,5,2.4,4)
    s.line(12,41,12,50,9,radius=1)
    s.line(8,50,16,50,9,radius=1.2)
    return s


def almond_blossoms():
    """Turquoise sky and crossing dark tree boughs filled with ivory flowers."""
    s=canvas(["FF69B4B9","FF306C7A","FF4B5949","FF8B6D53","FFF9EDD8",
              "FFE9C6C4","FFD89B95","FFFDFBF2","FF98D0CA","FFB89C7C"])
    for x,y in ((8,12),(44,6),(53,34),(10,46)):
        s.ellipse(x,y,11,5,8)
    s.line(-2,59,28,27,2,radius=4.5)
    s.line(25,27,54,2,2,radius=3)
    s.line(20,40,56,46,2,radius=3)
    s.line(17,46,5,9,2,radius=2.7)
    s.line(44,45,61,26,2,radius=2)
    s.line(35,18,59,14,2,radius=1.8)
    for x,y in ((10,12),(14,23),(23,35),(19,47),(8,52),
                (33,21),(42,9),(51,7),(51,17),(55,27),
                (47,39),(39,42),(57,48),(30,47),(8,36),
                (26,16),(36,32),(23,55)):
        blossom(s,x,y,4,6)
        s.dot(x-1,y+1,7)
    for x,y in ((28,30),(46,23),(14,54),(58,9)):
        s.ellipse(x,y,2.6,1.2,9)
    return s


def the_gleaners():
    """Millet's three bent harvesters in broad sunlit wheat fields."""
    s=canvas(["FFF2D79E","FFE0B676","FFBB8A4C","FF8F6B4B","FF645B50",
              "FF356076","FF9B5D50","FFD9BC9D","FFEEE4C9","FFAA8D58",
              "FF6A7C6B","FFFFEBC0"])
    s.rect(0,32,63,63,1);s.rect(0,44,63,63,2)
    s.polygon([(0,34),(11,28),(28,31),(44,26),(63,31),
               (63,40),(0,40)],9)
    for x,y in ((11,31),(38,30),(56,31)):
        s.ellipse(x,y,10,3,1)
        s.line(x-9,y+2,x+9,y+2,3,radius=.7)
    for x in range(2,64,4):
        for y in (49+(x%3),56+(x%4)):
            s.line(x,y+4,x+1,y-2,3,radius=.7)
            s.dot(x,y-2,11)
    # Three harvesting women's bent torsos and kerchiefs.
    for x,y,coat,hat in ((14,37,5,8),(31,35,6,8),(46,39,4,7)):
        s.ellipse(x+2,y,4.4,3.8,hat)
        s.polygon([(x-3,y-1),(x,y-5),(x+6,y-3),(x+8,y)],3)
        s.polygon([(x-4,y+3),(x+3,y+1),(x+9,y+8),
                   (x+7,y+17),(x-6,y+16)],coat)
        s.line(x+5,y+6,x+12,y+13,7,radius=1.7)
        s.line(x-1,y+15,x-5,y+24,3,radius=1.5)
        s.line(x+5,y+15,x+8,y+24,3,radius=1.5)
        s.line(x+12,y+13,x+13,y+20,7,radius=1)
        s.dot(x+13,y+20,8)
    s.ellipse(57,43,5,3,2)
    return s


def fragonard_swing():
    """Pink billowing Rococo dress on a rope swing in a deep green garden."""
    s=canvas(["FF364B38","FF1C382F","FF668460","FF9AA473","FFE6C9AA",
              "FFF1A5A7","FFCF737A","FFF2CD9A","FF6F563D","FFCFD4A4",
              "FFB4C099","FFFBE6D4"])
    for x,y,r in ((5,8,21),(55,5,26),(7,40,15),(56,39,17)):
        s.ellipse(x,y,r,r*.9,1);s.ellipse(x+2,y+3,r*.75,r*.7,2)
    s.line(57,0,50,63,8,radius=5)
    s.line(48,12,9,1,8,radius=3.7)
    s.line(0,57,63,56,2,radius=4.0)
    s.line(26,8,22,35,7,radius=.9)
    s.line(47,8,40,34,7,radius=.9)
    # Airborne figure with dress ballooning around a seated silhouette.
    s.ellipse(34,27,5,6,4);s.polygon([(31,21),(36,17),(39,21),(39,24)],7)
    s.dot(33,25,8)
    s.polygon([(28,31),(42,30),(53,41),(45,51),
               (22,50),(14,43)],6)
    s.polygon([(30,30),(41,29),(49,39),(43,47),(24,48),(17,42)],5)
    for x in (20,27,33,40,46):
        s.line(34,32,x,45,11,radius=.7)
    s.line(29,46,13,36,4,radius=2)
    s.line(41,46,52,40,4,radius=2)
    s.line(15,35,11,32,7,radius=1.4)
    s.line(51,38,57,36,7,radius=1.4)
    s.ellipse(8,52,4,5,8);s.line(7,55,17,62,8,radius=2.4)
    for x,y in ((11,61),(27,59),(44,57),(57,57)):
        blossom(s,x,y,9,5)
    return s


def woman_with_parasol():
    """Monet's low viewpoint, sky, wind-blown white dress and tilted green umbrella."""
    s=canvas(["FF8CC7D7","FFD5E9E3","FFF6F3DF","FF6B9F65","FF386A56",
              "FF46708C","FFB9B5A1","FFEDCCA3","FF454A42","FFBCCBBD",
              "FF76B6CA","FFFFE8B7"])
    for x,y,w in ((5,12,17),(48,13,14),(27,27,20)):
        s.ellipse(x,y,w,7,1);s.ellipse(x+5,y-2,w*.8,5,2)
    s.polygon([(0,45),(20,42),(38,46),(63,37),(63,63),(0,63)],3)
    for x in range(4,63,5):
        s.line(x,59,x+1,51,4,radius=.7)
        s.dot(x+1,51,11)
    # Tilted green umbrella, shaft and billowing veil.
    s.polygon([(10,19),(17,11),(28,7),(42,12),(45,19),
               (34,18),(24,20)],4)
    s.polygon([(12,17),(21,10),(29,9),(41,14),(43,18)],3)
    s.line(32,12,36,35,8,radius=1.2)
    s.polygon([(30,26),(43,25),(52,48),(45,60),(25,57),(19,47)],2)
    s.polygon([(32,29),(40,27),(46,44),(38,56),(27,55),(24,47)],9)
    s.polygon([(22,45),(28,49),(24,62),(17,62)],1)
    s.ellipse(35,23,4.3,5.1,7)
    s.polygon([(31,21),(34,15),(40,19),(41,22)],8)
    s.dot(37,23,8)
    s.line(40,36,36,31,7,radius=1.6)
    s.line(36,31,36,34,8,radius=1)
    return s


def lady_with_ermine():
    """Dark Renaissance portrait, russet sleeves, turned face and pale white ermine."""
    s=canvas(["FF20231F","FF2B2D2C","FF49332D","FF704A3C","FFB98465",
              "FFE4B58C","FFF1DBAE","FF8D968D","FFEAE7D4","FF534842",
              "FFBA9D6B","FFFBF5E6"])
    s.polygon([(17,34),(37,31),(50,39),(61,63),(4,63)],2)
    s.polygon([(22,36),(41,35),(54,48),(56,63),(9,63)],3)
    s.polygon([(23,36),(37,35),(34,57),(17,63),(11,62)],9)
    s.line(18,40,10,58,10,radius=2);s.line(41,41,47,56,10,radius=2)
    s.ellipse(29,20,12,16,2)
    s.ellipse(34,20,8,11,4);s.ellipse(35,20,6.2,10.3,5)
    s.polygon([(19,17),(21,7),(32,4),(41,12),(37,15),(25,13)],1)
    s.polygon([(26,13),(36,9),(42,12),(40,16),(26,17)],2)
    s.line(30,30,31,36,5,radius=2.5)
    s.dot(37,20,1);s.line(38,26,42,26,3,radius=.6)
    s.line(26,29,40,29,10,radius=.8)
    # Heraldic white ermine curves across her arms.
    s.ellipse(38,47,13,8,7);s.ellipse(39,46,11,6.5,8)
    s.ellipse(49,39,6,7,8);s.ellipse(49,38,5,5.7,11)
    s.polygon([(50,34),(53,30),(56,37),(53,39)],8)
    s.dot(51,37,1);s.dot(47,39,1)
    s.line(34,44,45,44,11,radius=.8)
    s.line(31,47,48,57,4,radius=3)
    return s


def bar_folies_bergere():
    """Manet's blonde barmaid, mirrored crowd, bulbs, flowers and bottles."""
    s=canvas(["FF55566A","FF333545","FF91858C","FFEAD7AB","FFF3E5CC",
              "FFB59B7C","FF403E4C","FFB68B64","FFB3C6B8","FFDDD5CC",
              "FF8C5745","FFFFEAAD","FF6E766E"])
    s.rect(0,0,63,24,1)
    for x in (6,15,26,45,56):
        s.ellipse(x,9,4,3,2)
        s.dot(x,7,11)
    for x,y in ((5,28),(13,25),(51,28),(58,25)):
        s.ellipse(x,y,6,9,6);s.ellipse(x,y-7,3,3,5)
    s.rect(0,30,63,34,7)
    # Center barmaid: pale face, blond bangs, black fitted jacket, white lace.
    s.polygon([(25,36),(39,35),(46,46),(46,61),(16,61),(19,44)],6)
    s.polygon([(27,36),(37,35),(39,51),(34,58),(26,52)],3)
    s.ellipse(32,24,10,13,7);s.ellipse(32,26,8,10,3)
    s.polygon([(22,21),(24,12),(38,11),(43,22),(38,20),(27,20)],5)
    s.line(26,20,37,20,7,radius=.9)
    s.dot(29,26,1);s.dot(36,26,1)
    s.line(30,31,35,31,10,radius=.6)
    s.polygon([(23,37),(28,36),(32,47),(35,36),(42,38),(38,51),(29,53)],9)
    s.polygon([(21,40),(28,49),(21,63),(14,62)],6)
    s.polygon([(42,40),(37,49),(45,63),(52,62)],6)
    # Glass marble counter, bouquets, bottles and tangerines.
    s.rect(0,54,63,63,9);s.rect(0,53,63,55,3)
    for x in (4,9,14,49,56):
        s.rect(x,42,x+3,51,12);s.rect(x+1,37,x+2,42,11)
        s.rect(x,45,x+3,46,8)
    s.ellipse(51,55,8,2.5,8)
    for x in (47,51,55):
        s.ellipse(x,52,3,3,10)
    for x,y in ((3,33),(9,30),(56,32),(62,31)):
        s.dot(x,y,11)
    s.rect(1,58,62,59,4)
    return s


# Unique new IDs: these ten works are not in the existing original six or
# subsequent 20-classic online release, and no published content is overwritten.
PICTURES = [
    ("whistlers-mother","مادر ویسلر","Whistler's Mother","James McNeill Whistler",
     whistlers_mother,"Curtain softly shimmers","پرده به‌آرامی موج می‌زند"),
    ("arnolfini-portrait","پرتره آرنولفینی","The Arnolfini Portrait","Jan van Eyck",
     arnolfini_portrait,"Chandelier and convex mirror glow","لوستر و آینه می‌درخشند"),
    ("bedroom-arles","اتاق خواب در آرل","The Bedroom in Arles","Vincent van Gogh",
     bedroom_arles,"Window light moves over the room","نور پنجره در اتاق جابه‌جا می‌شود"),
    ("cafe-terrace-night","تراس کافه در شب","Café Terrace at Night","Vincent van Gogh",
     cafe_terrace_night,"Stars and cafe lights twinkle","ستاره‌ها و چراغ‌های کافه چشمک می‌زنند"),
    ("almond-blossoms","شکوفه‌های بادام","Almond Blossoms","Vincent van Gogh",
     almond_blossoms,"Soft petals float past the branches","گلبرگ‌ها در باد جابه‌جا می‌شوند"),
    ("the-gleaners","خوشه‌چینان","The Gleaners","Jean-François Millet",
     the_gleaners,"Wheat glistens in waves","گندم‌ها زیر نسیم موج می‌زنند"),
    ("the-swing","تاب","The Swing","Jean-Honoré Fragonard",
     fragonard_swing,"Dress and hanging ropes gently sway","لباس و طناب تاب آرام حرکت می‌کنند"),
    ("woman-parasol","زن با چتر آفتابی","Woman with a Parasol","Claude Monet",
     woman_with_parasol,"Clouds shift and green parasol shimmers","ابرها و چتر زیر باد تغییر می‌کنند"),
    ("lady-ermine","بانویی با قاقم","Lady with an Ermine","Leonardo da Vinci",
     lady_with_ermine,"The white ermine blinks","قاقم سفید پلک می‌زند"),
    ("bar-folies-bergere","بار در فولی‌برژر","A Bar at the Folies-Bergère","Édouard Manet",
     bar_folies_bergere,"Mirrored bulbs and bottles glimmer","بازتاب چراغ‌ها و بطری‌ها می‌درخشد"),
]


def motion_frame(base, slug, phase):
    """Make a frame by sparse edits *relative to* the completed original image."""
    image = Sprite(SIDE, base.palette)
    image.cells = base.cells[:]
    if phase == 0:
        return image.cells
    tempo = (0,1,2,3,4,3,2,1)[phase]
    def dot(x,y,color):
        image.dot(x,y,color)
    if slug == "whistlers-mother":
        for y in range(8,47,7):
            dot(4+tempo%4,y,3)
            dot(8+tempo%3,y+2,8)
    elif slug == "arnolfini-portrait":
        for x in (20,26,33,40,46):
            image.ellipse(x,14,2,2,9 if (x+phase)%3 else 5)
        image.ellipse(33,26,1.3+tempo/3,2.0+tempo/3,11)
    elif slug == "bedroom-arles":
        for y in range(13,28,4):
            image.line(9+tempo//2,y,13+tempo//2,y,8,radius=.55)
        for x in range(28,43,4):
            dot(x,49+tempo//2,2)
    elif slug == "cafe-terrace-night":
        for n,(x,y) in enumerate(((39,5),(47,10),(57,5),(34,16),(51,17))):
            dot(x,y,8 if (phase+n)%3 else 3)
        for x in (7,17,26):
            image.ellipse(x,31,1.5+tempo*.2,1.4,8)
    elif slug == "almond-blossoms":
        for i,(x,y) in enumerate(((12,20),(27,35),(47,23),(38,48),(53,38))):
            dot(x+(tempo+i)%3,y+tempo//2,4)
            dot(x+1+(tempo+i)%3,y+1+tempo//2,5)
    elif slug == "the-gleaners":
        for x in range(2,61,6):
            y=53+(x//6+tempo)%4
            dot(x,y,11)
            dot(x+1,y-2,0 if phase%2 else 9)
    elif slug == "the-swing":
        image.line(22+tempo//3,33,21+tempo//2,37,7,radius=.6)
        image.line(40-tempo//3,32,41-tempo//2,37,7,radius=.6)
        for x in (20,28,38,46):
            dot(x+(phase%3)-1,45+(tempo%2),11)
    elif slug == "woman-parasol":
        for x,y in ((17,16),(25,13),(34,15),(41,18)):
            dot(x+tempo//2,y,11 if phase%2 else 1)
        for x in (22,27,31):
            dot(x+tempo//2,55,1)
    elif slug == "lady-ermine":
        dot(51,37,8 if tempo >= 3 else 1)
        dot(47,39,1 if tempo < 3 else 11)
        image.line(35,47,38+tempo//2,47,11,radius=.7)
    elif slug == "bar-folies-bergere":
        for i,x in enumerate((6,15,26,45,56)):
            dot(x,7,11 if (i+phase)%3 else 3)
        for x in (5,10,15,50,57):
            dot(x,42+tempo//2,11)
            dot(x+1,46,8 if phase%2 else 12)
    else:
        raise ValueError("Unknown classic motion: " + slug)
    return image.cells


def animation_frames(artwork, slug):
    before = artwork.cells
    frames = []
    for phase in range(8):
        pose = motion_frame(artwork, slug, phase)
        frames.append({"changes": [[index, color] for index, color in enumerate(pose)
                                   if color != before[index]]})
    return frames


def create_pack(destination):
    if len(PICTURES) != 10:
        raise ValueError("Expected ten distinct classic paintings")
    entries, files, scenarios = [], {}, {}
    for slug, fa, en, artist, draw, motion_en, motion_fa in PICTURES:
        artwork = draw()
        if artwork.side != 64 or len(artwork.cells) != 4096:
            raise ValueError("Invalid 64x64 painting: " + slug)
        level = {
            "schemaVersion": 2,
            "levelId": PREFIX + slug, "levelVersion": 1,
            "titles": {"fa": fa, "en": en},
            "width": 64, "height": 64,
            "palette": artwork.palette, "cells": artwork.cells,
        }
        level["checksum"] = checksum(level)
        level_blob = compact(level)
        frames = animation_frames(artwork, slug)
        animation = {
            "schemaVersion": 1, "levelId": level["levelId"],
            "levelVersion": 1, "levelChecksum": level["checksum"],
            "frameDurationMs": FRAME_DURATION_MS, "frames": frames,
        }
        animation_blob = compact(animation)
        stem = level["levelId"] + "-v1"
        entries.append({
            "id": level["levelId"], "version": 1,
            "title": fa, "titleEn": en, "category": "patterns",
            "width": 64, "height": 64,
            "bytes": len(level_blob), "checksum": level["checksum"],
            "animation": {
                "bytes": len(animation_blob),
                "sha256": hashlib.sha256(animation_blob).hexdigest(),
                "frameCount": len(frames),
            },
        })
        scenarios[level["levelId"]] = {
            "artist": artist, "titleFa": fa, "titleEn": en,
            "frameDurationMs": FRAME_DURATION_MS, "frameCount": 8,
            "motionFa": motion_fa, "motionEn": motion_en,
        }
        files["levels/" + stem + ".json"] = level_blob
        files["previews/" + stem + ".png"] = png(level)
        files["animations/" + stem + ".json"] = animation_blob
    validate_new_pack_manifest(entries)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({"schemaVersion": 1, "pictures": entries}))
        for path, data in files.items():
            archive.writestr(path, data)
        archive.writestr("animation-scenarios.json",
                         compact({"schemaVersion": 1, "scenarios": scenarios}))
    print(f"Created 10 animated 64x64 public-domain masterpiece homages: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_animated_masterworks_64_pack.py <content.zip>")
    create_pack(sys.argv[1])
