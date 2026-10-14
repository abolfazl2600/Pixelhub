#!/usr/bin/env python3
"""Build 23 original Iranian heritage, nature, wildlife and daily-life paintings.

The release ZIP contains bilingual immutable schema-v2 levels and PNG previews.
Animation recipes are generated deterministically from the exact published
level checksums after the release catalog has been assembled.
"""
import hashlib
import json
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest
from online_starter_pack import Sprite
from pixel_animation_recipes import animation

SIZE = 64
PALETTE = [
    "FFEAF6FC", "FF34495E", "FFF4E8D1", "FFC5AE8D",
    "FF8B6F58", "FF2F8292", "FF67B7BD", "FFE0B75D",
    "FF9BBE8A", "FF50785B", "FFB66E55", "FFD9C7AA",
    "FF6C7D91", "FF9A8BB4", "FF6BA6C9", "FFFFFFFF",
    "FFB64C4C", "FF8C4D3E", "FF4C555D", "FFFFD98A",
]

# IDs are intentionally new and never replace previously published artwork.
SCENES = [
    ("online-iran-pasargadae-cyrus-tomb", "آرامگاه کوروش در پاسارگاد", "Tomb of Cyrus at Pasargadae", "patterns", "cyrus", "sparkle", [0.03, 0.04, 0.97, 0.28]),
    ("online-iran-chogha-zanbil", "زیگورات چغازنبیل", "Chogha Zanbil Ziggurat", "patterns", "ziggurat", "sparkle", [0.03, 0.04, 0.97, 0.25]),
    ("online-iran-saadi-tomb", "آرامگاه سعدی", "Tomb of Saadi", "patterns", "saadi", "glimmer", [0.08, 0.10, 0.92, 0.45]),
    ("online-iran-ferdowsi-tomb", "آرامگاه فردوسی", "Tomb of Ferdowsi", "patterns", "ferdowsi", "sparkle", [0.03, 0.04, 0.97, 0.24]),
    ("online-iran-soltaniyeh-dome", "گنبد سلطانیه", "Soltaniyeh Dome", "patterns", "soltaniyeh", "glimmer", [0.18, 0.12, 0.82, 0.52]),
    ("online-iran-karim-khan-citadel", "ارگ کریم‌خان", "Karim Khan Citadel", "patterns", "citadel", "sparkle", [0.03, 0.04, 0.97, 0.22]),
    ("online-iran-dowlatabad-garden", "باغ دولت‌آباد و بادگیر", "Dowlatabad Garden and Windcatcher", "nature", "dowlatabad", "ripple", [0.03, 0.66, 0.97, 0.91]),
    ("online-iran-borujerdi-house", "خانه بروجردی‌ها", "Borujerdi House", "patterns", "borujerdi", "sparkle", [0.03, 0.04, 0.97, 0.22]),
    ("online-iran-tabatabaei-house", "خانه طباطبایی‌ها", "Tabatabaei House", "patterns", "tabatabaei", "glimmer", [0.15, 0.28, 0.85, 0.60]),
    ("online-iran-vank-cathedral", "کلیسای وانک", "Vank Cathedral", "patterns", "vank", "sparkle", [0.03, 0.04, 0.97, 0.25]),
    ("online-iran-falak-ol-aflak", "قلعه فلک‌الافلاک", "Falak-ol-Aflak Castle", "patterns", "falak", "sparkle", [0.03, 0.04, 0.97, 0.25]),
    ("online-iran-tabriz-bazaar", "بازار تاریخی تبریز", "Tabriz Historic Bazaar", "patterns", "bazaar", "glimmer", [0.15, 0.15, 0.85, 0.55]),
    ("online-iran-yazd-jameh-mosque", "مسجد جامع یزد", "Yazd Jameh Mosque", "patterns", "yazd", "glimmer", [0.15, 0.12, 0.85, 0.42]),
    ("online-iran-gonbad-qabus", "گنبد قابوس", "Gonbad-e Qabus Tower", "patterns", "gonbad", "sparkle", [0.03, 0.04, 0.97, 0.22]),
    ("online-iran-naqsh-e-rostam", "نقش رستم", "Naqsh-e Rostam", "patterns", "naqsh", "sparkle", [0.03, 0.04, 0.97, 0.22]),
    ("online-iran-nature-landscape", "چشم‌انداز کوهستانی ایران", "Iranian Mountain Landscape", "nature", "landscape", "ripple", [0.04, 0.89, 0.96, 0.98]),
    ("online-iran-traditional-architecture", "حیاط خانه سنتی ایرانی", "Traditional Iranian Courtyard", "patterns", "traditional", "sway", [0.03, 0.62, 0.17, 0.96]),
    ("online-iran-native-wildlife", "پلنگ ایرانی در زیستگاه طبیعی", "Persian Leopard in Its Habitat", "animals", "wildlife", "sway", [0.03, 0.68, 0.22, 0.98]),
    ("online-iran-regional-daily-life", "زندگی روزمره در روستای ایرانی", "Daily Life in an Iranian Village", "objects", "daily", "sparkle", [0.03, 0.04, 0.97, 0.24]),
    ("online-iran-taq-e-bostan", "نقش‌برجسته‌های طاق بستان", "Taq-e Bostan Rock Reliefs", "patterns", "taq", "glimmer", [0.18, 0.22, 0.82, 0.65]),
    ("online-iran-behistun-inscription", "کتیبه و نقش‌برجسته بیستون", "Behistun Inscription and Relief", "patterns", "behistun", "sparkle", [0.03, 0.04, 0.97, 0.22]),
    ("online-iran-shahr-e-sukhteh", "محوطه باستانی شهر سوخته", "Shahr-e Sukhteh Archaeological Site", "nature", "shahr", "sparkle", [0.03, 0.04, 0.97, 0.25]),
    ("online-iran-sheikh-lotfollah-mosque", "مسجد شیخ لطف‌الله", "Sheikh Lotfollah Mosque", "patterns", "sheikh", "glimmer", [0.18, 0.18, 0.82, 0.55]),
]

def canvas():
    return Sprite(SIZE, PALETTE)

def sky(s, ground=55):
    s.ellipse(51, 10, 4, 4, 19)
    s.ellipse(50, 9, 2, 2, 15)
    s.ellipse(13, 10, 5, 2.5, 15)
    s.ellipse(18, 9, 4, 2.5, 15)
    s.ellipse(10, 11, 3, 2, 15)
    s.ellipse(42, 16, 3, 1.5, 15)
    s.ellipse(46, 15, 3, 1.5, 15)
    s.rect(0, ground, 63, 63, 11)
    s.line(0, ground, 63, ground, 4, radius=.7)

def mountains(s, color=12):
    s.polygon([(0, 43), (10, 30), (18, 39), (30, 22), (42, 39), (53, 29), (63, 40), (63, 63), (0, 63)], color)
    s.polygon([(23, 31), (30, 22), (37, 32), (32, 29), (29, 31)], 15)
    s.polygon([(0, 50), (15, 43), (29, 48), (45, 41), (63, 49), (63, 63), (0, 63)], 4)

def cypress(s, x, base, height=22):
    s.rect(x-1, base-4, x+1, base, 4)
    s.polygon([(x, base-height), (x-6, base-8), (x-3, base-8), (x-7, base-4), (x+7, base-4), (x+3, base-8), (x+6, base-8)], 9)
    s.polygon([(x, base-height+4), (x-3, base-9), (x+2, base-10)], 8)

def pointed_arch(s, cx, top, bottom, half, outline=1, fill=3, aperture=2):
    s.polygon([(cx-half,bottom),(cx-half,top+half//2),(cx,top),(cx+half,top+half//2),(cx+half,bottom)], outline)
    h=max(1,half-2)
    s.polygon([(cx-h,bottom),(cx-h,top+half//2+2),(cx,top+3),(cx+h,top+half//2+2),(cx+h,bottom)], fill)
    h=max(1,h-3)
    s.polygon([(cx-h,bottom),(cx-h,top+half//2+5),(cx,top+7),(cx+h,top+half//2+5),(cx+h,bottom)], aperture)

def dome(s, cx, cy, rx=12, color=5):
    s.ellipse(cx, cy, rx, rx*.78, 1)
    s.ellipse(cx, cy+1, rx-2, rx*.66, color)
    for x in range(round(cx-rx+4), round(cx+rx-3), 4):
        s.line(x, cy-2, x, cy+2, 6, radius=.5)
    s.rect(cx-rx, cy+3, cx+rx, cy+6, 1)
    s.rect(cx-2, cy-rx-4, cx+2, cy-rx-1, 7)
    s.dot(cx, cy-rx-5, 7)

def tower(s, x, top, bottom, width=7, color=3):
    s.rect(x-width//2, top, x+width//2, bottom, 1)
    s.rect(x-width//2+2, top+2, x+width//2-2, bottom-1, color)
    for y in range(top+6, bottom-2, 7):
        s.rect(x-width//2+1, y, x+width//2-1, y+1, 5)

def birds(s, x=8, y=18, count=3):
    for i in range(count):
        xx=x+i*6; yy=y+(i%2)*3
        s.line(xx-2,yy,xx,yy-1,1,radius=.7)
        s.line(xx,yy-1,xx+2,yy,1,radius=.7)

def scene(kind):
    s=canvas()
    if kind == "cyrus":
        sky(s,54); mountains(s,12)
        s.rect(8,49,56,54,4); s.rect(12,45,52,49,3)
        s.rect(17,41,47,45,4); s.rect(21,37,43,41,3)
        s.polygon([(22,35),(22,28),(27,23),(37,23),(42,28),(42,35)],1)
        s.polygon([(25,33),(25,29),(29,26),(35,26),(39,29),(39,33)],2)
        s.rect(21,34,43,36,1); s.rect(25,36,39,38,4)
        s.rect(0,55,63,57,3); birds(s,8,24,2)
    elif kind == "ziggurat":
        sky(s,56); mountains(s,12)
        for y,x1,x2 in [(25,24,40),(31,19,45),(37,14,50),(43,9,55),(49,4,60)]:
            s.polygon([(x1,y),(x2,y),(x2+3,y+6),(x1-3,y+6)],1)
            s.polygon([(x1+2,y+1),(x2-2,y+1),(x2,y+5),(x1,y+5)],3)
            s.line(x1,y+6,x2,y+6,4,radius=.6)
        s.rect(29,19,35,25,4); s.rect(30,17,34,20,1); birds(s,6,18,3)
    elif kind in ("saadi","ferdowsi"):
        sky(s,56)
        if kind=="saadi":
            s.rect(7,44,57,55,3); s.rect(11,41,53,45,4)
            for x in [14,24,34,44,54]: s.rect(x,31,x+2,44,1)
            dome(s,33,29,12,5); s.rect(20,40,46,43,1)
            s.rect(26,44,40,55,2); s.rect(0,56,63,58,4)
            for x in range(6,59,8): cypress(s,x,56,16)
        else:
            s.rect(8,47,56,55,3); s.rect(12,43,52,48,4)
            s.rect(15,34,49,43,3)
            for x in [18,26,34,42,50]: s.rect(x,31,x+2,43,1)
            s.rect(20,28,44,32,1); s.rect(24,24,40,29,3)
            s.rect(27,19,37,25,1); s.rect(29,17,35,20,3)
            s.rect(0,56,63,58,4); birds(s,7,16,2)
    elif kind=="soltaniyeh":
        sky(s,55)
        s.rect(10,43,54,55,3); s.rect(14,39,50,44,4)
        for x in [17,24,32,40,47]: pointed_arch(s,x,42,54,4,1,5,2)
        s.ellipse(32,25,17,18,1); s.ellipse(32,25,14,15,5)
        s.polygon([(15,26),(20,15),(27,9),(32,7),(37,9),(44,15),(49,26)],1)
        s.polygon([(18,25),(22,16),(28,11),(32,9),(36,11),(42,16),(46,25)],5)
        for x in range(23,43,4): s.line(x,14,x,25,6,radius=.5)
        s.rect(29,6,35,9,7); birds(s,6,16,2)
    elif kind=="citadel":
        sky(s,55)
        s.rect(5,27,58,55,3); s.rect(8,30,55,52,4)
        for x in [7,21,42,56]:
            s.rect(x-5,18,x+5,36,1); s.rect(x-3,20,x+3,34,3)
            for xx in range(x-4,x+5,4): s.rect(xx,16,xx+1,19,1)
            s.rect(x-2,24,x+2,29,2)
        for x in range(14,51,7): s.rect(x,35,x+3,41,1)
        pointed_arch(s,32,37,55,8,1,3,2)
        s.rect(0,56,63,58,4)
    elif kind=="dowlatabad":
        sky(s,59); s.rect(0,60,63,63,5)
        s.rect(5,49,59,59,3); s.rect(7,51,57,57,14)
        for x in range(10,59,12): cypress(s,x,52,22)
        s.rect(27,16,37,49,1); s.rect(29,18,35,48,3)
        for y in range(21,44,6): s.rect(28,y,36,y+1,5)
        s.polygon([(26,16),(27,7),(30,3),(34,3),(37,7),(38,16)],1)
        s.polygon([(29,14),(30,8),(32,6),(35,8),(36,14)],5)
        for x in [24,40]: s.rect(x,18,x+2,45,4)
        s.rect(0,59,63,61,1); birds(s,7,14,2)
    elif kind=="borujerdi":
        sky(s,55)
        s.rect(8,34,56,55,3); s.rect(12,38,52,53,11)
        s.rect(14,31,50,35,4); dome(s,32,29,11,5)
        for x in [18,46]: 
            s.rect(x-4,19,x+4,34,1); s.rect(x-2,21,x+2,33,5)
            s.polygon([(x-5,19),(x-3,12),(x,9),(x+3,12),(x+5,19)],1)
            s.rect(x-2,13,x+2,18,5)
        for x in range(18,48,6): s.rect(x,40,x+2,49,1)
        pointed_arch(s,32,38,55,8,1,3,2)
    elif kind=="tabatabaei":
        sky(s,56)
        s.rect(5,29,59,56,3); s.rect(8,32,56,53,11)
        s.rect(11,27,53,31,4)
        for x in [14,22,30,38,46,54]:
            s.rect(x-2,35,x+2,45,1); s.rect(x-1,36,x+1,44,14)
            s.line(x,36,x,44,5,radius=.5)
        s.rect(14,47,50,52,1)
        for x in [18,26,34,42,50]: s.rect(x,48,x+1,51,7)
        s.polygon([(20,26),(25,19),(32,15),(39,19),(44,26)],1)
        s.polygon([(24,25),(28,20),(32,18),(36,20),(40,25)],5)
    elif kind=="vank":
        sky(s,55)
        s.rect(8,33,56,55,3); s.rect(12,37,52,53,4)
        dome(s,33,28,13,3); s.ellipse(33,28,10,12,5)
        s.rect(23,33,43,38,1)
        for x in [14,49]:
            tower(s,x,20,43,7,3); s.rect(x-5,26,x+5,28,1)
            s.polygon([(x-4,20),(x-3,15),(x,12),(x+3,15),(x+4,20)],1)
        s.rect(29,39,37,55,1); s.rect(31,41,35,54,2)
        for x in range(16,50,6): s.rect(x,44,x+2,50,1)
    elif kind=="falak":
        sky(s,55); mountains(s,12)
        s.polygon([(4,53),(11,38),(21,31),(43,31),(53,39),(60,53)],1)
        s.polygon([(8,52),(14,40),(23,35),(41,35),(50,40),(56,52)],3)
        for x in [17,28,39,49]:
            s.rect(x,37,x+5,49,4); s.rect(x+1,39,x+4,45,1)
        for x in range(13,52,7): s.rect(x,30,x+3,34,1)
        s.rect(0,55,63,57,4); birds(s,7,19,3)
    elif kind=="bazaar":
        sky(s,56)
        s.rect(4,20,60,56,3); s.rect(7,23,57,54,4)
        for x in [14,26,38,50]:
            s.ellipse(x,31,7,9,1); s.ellipse(x,32,4,6,2)
            s.rect(x-7,33,x+7,54,4); s.rect(x-4,38,x+4,54,1)
            s.rect(x-3,40,x+3,52,2)
        s.rect(4,18,60,22,1)
        for x in range(8,59,8): s.rect(x,19,x+3,21,7)
        s.rect(0,56,63,58,4)
    elif kind=="yazd":
        sky(s,56)
        s.rect(10,35,54,56,3); s.rect(15,38,49,53,4)
        pointed_arch(s,32,24,55,14,1,5,2)
        for x in [14,50]:
            tower(s,x,11,37,5,3); s.rect(x-4,15,x+4,17,1)
            s.polygon([(x-3,11),(x,5),(x+3,11)],1)
        for x in range(23,43,5): s.rect(x,39,x+2,45,1)
        for x in range(19,46,6): s.dot(x,31,7)
        s.rect(0,56,63,58,4)
    elif kind=="gonbad":
        sky(s,57)
        s.rect(7,45,57,57,3)
        s.polygon([(13,45),(17,23),(22,18),(42,18),(47,23),(51,45)],1)
        s.polygon([(16,44),(20,25),(24,21),(40,21),(44,25),(48,44)],4)
        for y in range(26,44,4):
            for x in range(21,44,5): s.rect(x,y,x+1,y+2,1)
        s.polygon([(22,18),(26,12),(32,7),(38,12),(42,18)],1)
        s.polygon([(27,17),(32,10),(37,17)],3)
        s.rect(29,44,35,56,1); s.rect(30,46,34,55,2)
        birds(s,5,15,2)
    elif kind=="naqsh":
        sky(s,56); mountains(s,12)
        s.polygon([(0,18),(10,10),(24,13),(37,8),(52,13),(63,9),(63,56),(0,56)],12)
        s.polygon([(12,22),(22,15),(42,15),(52,22),(52,39),(12,39)],1)
        s.polygon([(16,23),(24,18),(40,18),(48,23),(48,36),(16,36)],3)
        for x in [20,28,36,44]: s.rect(x,25,x+2,34,1)
        s.rect(0,56,63,58,4); birds(s,4,7,3)
    elif kind=="landscape":
        sky(s,55); mountains(s,12)
        s.polygon([(0,52),(13,47),(23,51),(35,46),(49,50),(63,45),(63,63),(0,63)],9)
        s.polygon([(0,57),(16,53),(29,58),(45,53),(63,57),(63,63),(0,63)],5)
        s.rect(0,58,63,63,14)
        for x in [7,55]: cypress(s,x,58,16)
        birds(s,13,24,3)
        for x in range(20,49,7): s.line(x,60,x+4,60,15,radius=.6)
    elif kind=="traditional":
        sky(s,56)
        s.rect(6,28,58,56,3); s.rect(10,32,54,53,11)
        s.rect(13,25,51,30,4)
        s.rect(26,8,38,26,1); s.rect(29,11,35,25,5)
        s.polygon([(24,8),(27,3),(37,3),(40,8)],1)
        for x in [15,23,41,49]:
            s.rect(x,36,x+4,45,1); s.rect(x+1,37,x+2,44,14)
        pointed_arch(s,32,36,55,8,1,4,2)
        for x in [6,58]: cypress(s,x,56,17)
        s.rect(0,56,63,58,4)
    elif kind=="wildlife":
        sky(s,56); mountains(s,12)
        # Persian leopard: long body, spotted coat, rounded head and tail.
        s.ellipse(32,43,17,7,1); s.ellipse(32,42,14,5,7)
        s.ellipse(47,38,6,6,1); s.ellipse(47,38,4,4,7)
        s.ellipse(52,40,2,2,1)
        s.line(18,43,10,38,1,radius=1.4); s.line(10,38,7,42,1,radius=1.2)
        for x in [23,29,37,42]: s.rect(x,46,x+2,55,1)
        for x,y in [(24,40),(30,39),(36,43),(41,40),(27,45),(35,46),(44,44)]: s.dot(x,y,1)
        s.ellipse(50,36,1,1,1); s.line(48,37,50,37,18,radius=.5)
        cypress(s,5,56,19); cypress(s,59,56,15)
        for x in [12,17,54]: s.line(x,56,x-2,51,9,radius=.8)
    elif kind=="daily":
        sky(s,56); mountains(s,12)
        s.rect(5,36,33,56,3); s.polygon([(3,36),(19,22),(35,36)],1)
        s.polygon([(8,36),(19,27),(30,36)],4)
        s.rect(13,42,19,53,1); s.rect(22,41,29,46,1); s.rect(23,42,28,45,14)
        # person beside pottery, intentionally small and subordinate to the setting
        s.ellipse(44,37,3,3,1); s.ellipse(44,37,2,2,3)
        s.polygon([(40,41),(48,41),(50,51),(38,51)],5)
        s.line(41,43,35,48,3,radius=1); s.line(47,43,51,47,3,radius=1)
        s.rect(39,51,41,56,1); s.rect(46,51,48,56,1)
        s.ellipse(55,53,4,3,1); s.ellipse(55,52,3,2,7); s.rect(52,54,58,56,1)
        cypress(s,3,56,14)
    elif kind=="taq":
        sky(s,56)
        s.polygon([(7,55),(7,31),(12,21),(22,15),(42,15),(52,21),(57,31),(57,55)],1)
        s.polygon([(13,54),(13,31),(17,24),(24,20),(40,20),(47,24),(51,31),(51,54)],4)
        s.rect(17,31,47,54,1)
        s.ellipse(32,36,12,11,3); s.ellipse(32,36,9,8,11)
        s.rect(20,43,44,51,3)
        for x in [24,31,38]: s.rect(x,43,x+2,49,1)
        s.rect(0,56,63,58,4); birds(s,7,12,2)
    elif kind=="behistun":
        sky(s,56); mountains(s,12)
        s.polygon([(0,18),(14,8),(30,12),(46,6),(63,13),(63,56),(0,56)],12)
        s.rect(13,21,51,35,1); s.rect(15,23,49,33,3)
        # relief panel: a standing ruler and a row of restrained inscription marks
        s.ellipse(21,25,2,2,1); s.rect(20,27,22,31,1); s.line(20,28,17,30,1); s.line(22,28,25,30,1)
        s.line(21,31,19,34,1); s.line(21,31,23,34,1)
        for x in range(28,47,4):
            s.line(x,25,x+2,25,2,radius=.6); s.line(x,28,x+1,28,2,radius=.6); s.line(x,31,x+2,31,2,radius=.6)
        s.rect(0,56,63,58,4)
    elif kind=="shahr":
        sky(s,56); mountains(s,12)
        s.polygon([(0,50),(13,44),(24,48),(40,42),(52,48),(63,44),(63,63),(0,63)],4)
        # excavated low mud-brick walls, no fantasy palaces or intact monuments
        for x,y,w,h in [(5,42,15,10),(23,45,13,8),(39,41,18,12)]:
            s.rect(x,y,x+w,y+h,3); s.rect(x+2,y+2,x+w-2,y+h-2,11)
            for yy in range(y+3,y+h,4): s.line(x+2,yy,x+w-2,yy,4,radius=.5)
        s.rect(0,54,63,56,11); birds(s,8,19,2)
        for x in range(8,60,9): s.line(x,60,x+3,59,4,radius=.5)
    elif kind=="sheikh":
        sky(s,56)
        s.rect(7,35,57,56,3); s.rect(11,38,53,54,4)
        dome(s,33,27,15,5)
        s.polygon([(18,34),(20,23),(25,16),(33,11),(41,16),(46,23),(48,34)],1)
        s.polygon([(21,33),(23,24),(27,18),(33,14),(39,18),(43,24),(45,33)],5)
        for x in range(24,43,4): s.line(x,20,x,32,6,radius=.5)
        pointed_arch(s,33,34,55,10,1,5,2)
        for x in range(17,50,6): s.dot(x,40,7)
        s.rect(0,56,63,58,4)
    return s

def build(destination):
    manifest, files = [], {}
    for ident, fa, en, category, kind, motion, region in SCENES:
        artwork = scene(kind)
        level = {"schemaVersion": 2, "levelId": ident, "levelVersion": 1,
                 "titles": {"fa": fa, "en": en}, "width": SIZE, "height": SIZE,
                 "palette": artwork.palette, "cells": artwork.cells}
        level["checksum"] = checksum(level)
        body = compact(level)
        stem = f"{ident}-v1"
        manifest.append({"id": ident, "version": 1, "title": fa, "titleEn": en,
                         "category": category, "width": SIZE, "height": SIZE,
                         "bytes": len(body), "checksum": level["checksum"]})
        files[f"levels/{stem}.json"] = body
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    output = pathlib.Path(destination); output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({"schemaVersion": 1, "pictures": manifest}))
        for path, data in files.items(): archive.writestr(path, data)
    print(f"Prepared {len(manifest)} Iranian coloring pictures: {output}")

def generate_recipes(online_dir, batch_dir):
    """Derive immutable recipe digests from assembled level JSONs."""
    online_dir, batch_dir = pathlib.Path(online_dir), pathlib.Path(batch_dir)
    recipes = {}
    for ident, _fa, _en, _category, _kind, motion, region in SCENES:
        level_path = online_dir / "levels" / f"{ident}-v1.json"
        if not level_path.exists():
            raise FileNotFoundError(f"Published level missing before animation: {level_path}")
        level = json.loads(level_path.read_text("utf-8"))
        recipe = {"motion": motion, "region": region, "durationMs": 150,
                  "version": 1, "checksum": level["checksum"]}
        rendered = animation(level, recipe)
        rendered_bytes = compact(rendered)
        recipe["animationChecksum"] = hashlib.sha256(rendered_bytes).hexdigest()
        recipes[ident] = recipe
    if len(recipes) > 10:
        # Animation publisher validates at most ten entries per batch.
        chunks = [dict(list(recipes.items())[i:i+10]) for i in range(0, len(recipes), 10)]
    else:
        chunks = [recipes]
    batch_dir.mkdir(parents=True, exist_ok=True)
    for old in batch_dir.glob("online-19*.json"): old.unlink()
    for offset, chunk in enumerate(chunks, start=19):
        (batch_dir / f"online-{offset:02d}.json").write_text(
            json.dumps(chunk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(recipes)} checksum-bound animations in {len(chunks)} batches")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        build(sys.argv[1])
    elif len(sys.argv) == 4 and sys.argv[1] == "recipes":
        generate_recipes(sys.argv[2], pathlib.Path(sys.argv[3]))
    else:
        raise SystemExit("Usage: python3 tool/online_iranian_heritage_23_pack.py <content.zip> | recipes <online-dir> <batch-dir>")
