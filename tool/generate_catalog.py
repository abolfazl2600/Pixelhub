#!/usr/bin/env python3
"""Create Pixelhub original geometric V3 art. Existing versioned art is untouched."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'apps/game/assets/levels'
PALETTE = ['FFF7F3E8', 'FF26364A', 'FFEB704A', 'FFF6C953', 'FF43896A', 'FF69A7D3', 'FFDDA0B5']

class Canvas:
    def __init__(self, size):
        self.size = size
        self.cells = [0] * (size * size)
    def draw(self, color, predicate):
        for y in range(self.size):
            for x in range(self.size):
                if predicate((x + .5) / self.size, (y + .5) / self.size):
                    self.cells[y * self.size + x] = color
    def rect(self, x, y, w, h, color):
        self.draw(color, lambda a, b: x <= a <= x + w and y <= b <= y + h)
    def ellipse(self, x, y, rx, ry, color):
        self.draw(color, lambda a, b: ((a-x)/rx)**2 + ((b-y)/ry)**2 <= 1)
    def polygon(self, points, color):
        def inside(x, y):
            hit = False
            last = points[-1]
            for current in points:
                a, b = current
                c, d = last
                if (b > y) != (d > y) and x < (c-a)*(y-b)/(d-b)+a:
                    hit = not hit
                last = current
            return hit
        self.draw(color, inside)
    def line(self, a, b, width, color):
        dx, dy = b[0]-a[0], b[1]-a[1]
        def near(x, y):
            t = max(0, min(1, ((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
            return (x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2 <= width*width
        self.draw(color, near)

def render(kind, n):
    c = Canvas(n)
    if kind in {'flower','tulip'}:
        c.rect(.47,.40,.06,.45,4)
        c.ellipse(.36,.66,.16,.07,4)
        if kind == 'flower':
            for i in range(6):
                angle = i*math.pi/3
                c.ellipse(.5+.15*math.cos(angle),.35+.15*math.sin(angle),.11,.11,6)
            c.ellipse(.5,.35,.10,.10,3)
        else:
            c.polygon([(.25,.20),(.37,.29),(.50,.17),(.63,.29),(.75,.20),(.69,.43),(.50,.52),(.31,.43)],2)
    elif kind == 'cactus':
        c.rect(.40,.23,.20,.52,4); c.ellipse(.5,.23,.10,.10,4)
        c.rect(.23,.38,.10,.20,4); c.rect(.23,.51,.22,.08,4)
        c.rect(.67,.29,.10,.24,4); c.rect(.57,.46,.20,.07,4)
        c.polygon([(.30,.73),(.70,.73),(.64,.89),(.36,.89)],2)
        c.rect(.47,.30,.03,.36,3)
    elif kind == 'mountain':
        c.ellipse(.76,.22,.09,.09,3)
        c.polygon([(.08,.82),(.43,.22),(.78,.82)],1)
        c.polygon([(.37,.32),(.43,.22),(.50,.34),(.46,.40),(.42,.36)],0)
        c.polygon([(.43,.82),(.69,.42),(.93,.82)],5)
        c.rect(.08,.82,.85,.07,4)
    elif kind == 'leaf':
        c.ellipse(.5,.47,.23,.32,4)
        c.line((.5,.22),(.5,.87),.018,1)
        for y in [.36,.48,.60]:
            c.line((.5,y+.06),(.33,y-.02),.014,3)
            c.line((.5,y+.06),(.67,y-.02),.014,3)
    elif kind == 'mushroom':
        c.rect(.41,.42,.18,.39,3)
        c.ellipse(.50,.42,.33,.24,2); c.rect(.17,.42,.66,.08,2)
        for x,y in [(.31,.36),(.51,.27),(.68,.37)]: c.ellipse(x,y,.055,.055,0)
        c.rect(.27,.82,.46,.045,4)
    elif kind in {'apple','cherry','watermelon'}:
        if kind == 'apple':
            c.ellipse(.38,.55,.22,.28,2); c.ellipse(.62,.55,.22,.28,2)
            c.line((.5,.30),(.54,.16),.025,1); c.ellipse(.64,.23,.12,.06,4)
            c.ellipse(.31,.44,.045,.10,0)
        elif kind == 'cherry':
            c.line((.30,.60),(.52,.20),.02,4); c.line((.68,.61),(.52,.20),.02,4)
            c.ellipse(.29,.67,.16,.16,2); c.ellipse(.69,.68,.16,.16,2)
            c.ellipse(.63,.22,.13,.05,4)
        else:
            c.ellipse(.5,.52,.36,.34,4); c.ellipse(.5,.50,.31,.27,0); c.ellipse(.5,.48,.27,.23,2)
            c.rect(.1,.10,.80,.34,0)
            for x,y in [(.32,.50),(.48,.63),(.65,.52)]: c.ellipse(x,y,.02,.035,1)
    elif kind in {'butterfly','bee'}:
        if kind == 'butterfly':
            for x in [.31,.69]:
                c.ellipse(x,.39,.19,.20,6); c.ellipse(x,.65,.14,.16,5)
                c.ellipse(x,.39,.07,.075,3)
            c.rect(.47,.31,.06,.43,1)
            c.line((.49,.34),(.39,.17),.012,1); c.line((.51,.34),(.61,.17),.012,1)
        else:
            c.ellipse(.34,.35,.18,.15,5); c.ellipse(.66,.35,.18,.15,5)
            c.ellipse(.5,.56,.28,.18,3)
            c.draw(1,lambda x,y: ((x-.5)/.28)**2+((y-.56)/.18)**2<=1 and (.34<x<.40 or .51<x<.57))
            c.ellipse(.70,.52,.023,.023,1)
    elif kind in {'bird','fish','turtle'}:
        if kind == 'bird':
            c.ellipse(.46,.57,.27,.20,5); c.ellipse(.67,.36,.15,.15,5)
            c.polygon([(.80,.34),(.93,.40),(.80,.45)],3)
            c.polygon([(.15,.49),(.05,.30),(.36,.52)],5)
            c.ellipse(.47,.58,.15,.09,1); c.ellipse(.70,.33,.025,.025,1)
            c.line((.43,.74),(.40,.87),.018,2); c.line((.56,.74),(.60,.87),.018,2)
        elif kind == 'fish':
            c.polygon([(.69,.5),(.90,.27),(.90,.73)],2)
            c.ellipse(.44,.50,.30,.22,5)
            c.ellipse(.27,.45,.035,.035,1); c.line((.43,.33),(.43,.68),.02,0)
            c.ellipse(.22,.21,.025,.025,5); c.ellipse(.13,.10,.015,.015,5)
        else:
            for x,y in [(.30,.30),(.30,.70),(.65,.30),(.65,.70)]: c.ellipse(x,y,.08,.09,4)
            c.ellipse(.83,.50,.10,.10,4); c.ellipse(.47,.50,.31,.24,4)
            c.ellipse(.47,.50,.23,.17,3); c.line((.47,.35),(.47,.65),.016,4)
            c.line((.27,.50),(.67,.50),.016,4); c.ellipse(.86,.46,.016,.016,1)
    elif kind in {'fox','bunny','owl','dog'}:
        if kind == 'bunny':
            c.ellipse(.35,.26,.095,.22,0); c.ellipse(.65,.26,.095,.22,0)
            c.ellipse(.35,.26,.045,.17,6); c.ellipse(.65,.26,.045,.17,6)
            c.ellipse(.5,.61,.30,.26,6)
        elif kind == 'owl':
            c.ellipse(.5,.57,.30,.32,1)
            c.polygon([(.20,.32),(.20,.12),(.43,.33)],1); c.polygon([(.57,.33),(.80,.12),(.80,.32)],1)
            c.ellipse(.36,.46,.13,.13,3); c.ellipse(.64,.46,.13,.13,3)
        else:
            col = 2 if kind == 'fox' else 3
            c.polygon([(.20,.43),(.18,.15),(.42,.35)],col)
            c.polygon([(.58,.35),(.82,.15),(.80,.43)],col)
            c.ellipse(.5,.57,.31,.27,col)
            c.polygon([(.21,.57),(.5,.82),(.79,.57),(.5,.69)],0)
        c.ellipse(.36,.50,.03,.04,1); c.ellipse(.64,.50,.03,.04,1)
        c.polygon([(.44,.65),(.56,.65),(.50,.72)],1)
    elif kind == 'rocket':
        c.polygon([(.35,.64),(.21,.79),(.25,.53),(.38,.45)],2)
        c.polygon([(.65,.64),(.79,.79),(.75,.53),(.62,.45)],2)
        c.polygon([(.35,.65),(.35,.32),(.50,.10),(.65,.32),(.65,.65)],5)
        c.ellipse(.5,.36,.08,.09,1); c.ellipse(.5,.36,.045,.055,0)
        c.polygon([(.39,.69),(.5,.94),(.61,.69)],3)
    elif kind in {'saturn','ufo','comet','sun'}:
        if kind == 'saturn':
            c.ellipse(.5,.5,.24,.24,3)
            c.draw(5,lambda x,y: .75 <= ((x-.5)/.42)**2+((y-.5-.30*(x-.5))/.11)**2 <= 1.35)
        elif kind == 'ufo':
            c.ellipse(.5,.40,.20,.17,5); c.ellipse(.5,.54,.38,.12,1)
            for x in [.25,.50,.75]: c.ellipse(x,.55,.035,.035,3)
            c.polygon([(.42,.67),(.29,.91),(.71,.91),(.58,.67)],3)
        elif kind == 'comet':
            c.polygon([(.28,.61),(.73,.08),(.66,.46),(.91,.20),(.63,.68)],3)
            c.ellipse(.31,.69,.18,.18,2); c.ellipse(.31,.69,.10,.10,3)
        else:
            for i in range(12):
                a=i*math.pi/6
                c.line((.5+.29*math.cos(a),.5+.29*math.sin(a)),(.5+.40*math.cos(a),.5+.40*math.sin(a)),.017,3)
            c.ellipse(.5,.5,.24,.24,3)
    elif kind == 'lighthouse':
        c.rect(.00,.57,1,.43,5)
        c.polygon([(.16,.95),(.20,.72),(.68,.72),(.83,.95)],1)
        c.polygon([(.36,.75),(.39,.31),(.61,.31),(.65,.75)],0)
        for yy in (.40,.56,.68):
            c.rect(.39,yy,.22,.055,2)
        c.rect(.40,.24,.20,.08,1)
        c.rect(.42,.20,.16,.07,3)
        c.polygon([(.40,.22),(.50,.12),(.60,.22)],2)
    elif kind == 'umbrella':
        c.line((.5,.38),(.5,.80),.025,1); c.ellipse(.43,.80,.09,.09,1); c.ellipse(.43,.77,.045,.07,0)
        c.ellipse(.5,.43,.35,.28,2); c.rect(.12,.44,.76,.13,0)
        c.polygon([(.33,.44),(.50,.17),(.67,.44)],3)
    elif kind == 'cup':
        c.ellipse(.76,.48,.14,.15,1); c.ellipse(.76,.48,.08,.09,0)
        c.rect(.22,.34,.46,.37,5); c.ellipse(.45,.70,.23,.08,5)
        c.ellipse(.45,.34,.23,.045,1)
        c.line((.39,.26),(.42,.12),.015,1); c.line((.54,.26),(.57,.12),.015,1)
        c.ellipse(.45,.82,.34,.04,1)
    elif kind == 'book':
        c.polygon([(.10,.25),(.42,.22),(.50,.28),(.58,.22),(.90,.25),(.90,.77),(.58,.74),(.50,.80),(.42,.74),(.10,.77)],5)
        c.rect(.17,.30,.26,.38,0); c.rect(.57,.30,.26,.38,0); c.line((.5,.30),(.5,.75),.014,1)
        for y in [.38,.48,.58]:
            c.rect(.21,y,.18,.018,1); c.rect(.61,y,.18,.018,1)
    elif kind == 'kite':
        c.polygon([(.5,.12),(.77,.42),(.5,.66),(.23,.42)],2)
        c.polygon([(.5,.12),(.77,.42),(.5,.42)],3)
        c.polygon([(.23,.42),(.5,.42),(.5,.66)],5)
        c.line((.5,.66),(.62,.90),.01,1)
        for x,y in [(.54,.75),(.58,.83)]: c.polygon([(x-.06,y-.03),(x+.06,y+.03),(x+.06,y-.03),(x-.06,y+.03)],6)
    elif kind == 'sailboat':
        c.rect(.48,.16,.025,.55,1)
        c.polygon([(.45,.20),(.16,.61),(.45,.61)],2); c.polygon([(.54,.24),(.78,.61),(.54,.61)],3)
        c.polygon([(.13,.69),(.87,.69),(.71,.82),(.28,.82)],1)
        c.rect(.08,.86,.84,.04,5)
    else:
        c.polygon([(.28,.20),(.72,.20),(.90,.44),(.50,.85),(.10,.44)],5)
        c.polygon([(.28,.20),(.50,.44),(.72,.20)],0)
        c.polygon([(.10,.44),(.50,.44),(.50,.85)],1)
    return c.cells

ITEMS = [
 ('flower','گل بهاری','Spring flower','nature'),('tulip','لاله','Tulip','nature'),
 ('cactus','کاکتوس','Cactus','nature'),('mountain','کوهستان','Mountains','nature'),
 ('leaf','برگ','Leaf','nature'),('mushroom','قارچ','Mushroom','nature'),
 ('apple','سیب','Apple','nature'),('cherry','گیلاس','Cherries','nature'),
 ('watermelon','هندوانه','Watermelon','nature'),('butterfly','پروانه','Butterfly','animals'),
 ('bird','پرنده','Bird','animals'),('fish','ماهی','Fish','animals'),
 ('turtle','لاک‌پشت','Turtle','animals'),('fox','روباه','Fox','animals'),
 ('bunny','خرگوش','Bunny','animals'),('owl','جغد','Owl','animals'),
 ('dog','سگ','Dog','animals'),('bee','زنبور','Bee','animals'),
 ('rocket','موشک','Rocket','space'),('saturn','زحل','Saturn','space'),
 ('ufo','بشقاب پرنده','Flying saucer','space'),('comet','دنباله‌دار','Comet','space'),
 ('sun','خورشید','Sun','space'),('lighthouse','فانوس دریایی','Lighthouse at Sunset','objects'),
 ('umbrella','چتر','Umbrella','objects'),('cup','فنجان','Cup','objects'),
 ('book','کتاب','Book','objects'),('kite','بادبادک','Kite','objects'),
 ('sailboat','قایق بادبانی','Sailboat','objects'),('diamond','الماس','Diamond','patterns')]

# Keep the ten V2 entries and IDs intact.
CATALOG = ['sunflower-v2.json','heart.json','rainbow.json','moon.json','tree.json',
           'star.json','gem.json','cat.json','house.json','planet.json']
CATEGORIES = {'sunflower':'nature','heart':'patterns','rainbow':'nature','moon':'space',
              'tree':'nature','star':'space','gem':'patterns','cat':'animals','house':'objects','planet':'space'}
metadata = {key: {'category': value, 'tags': [value]} for key, value in CATEGORIES.items()}
for i, (name, fa, en, category) in enumerate(ITEMS):
    size = 60 if name == 'lighthouse' else (32 if i % 3 else 16)
    cells = render(name, size)
    used = sorted(set(cells))
    palette = [PALETTE[v] for v in used]
    cells = [used.index(v) for v in cells]
    payload = [2, name, 1, fa, en, size, size, palette, cells]
    checksum = hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    level = dict(schemaVersion=2, levelId=name, levelVersion=1, titles={'fa':fa,'en':en},
                 width=size, height=size, palette=palette, cells=cells, checksum=checksum)
    destination = ROOT / (name+'.json')
    if not destination.exists():
        destination.write_text(json.dumps(level, ensure_ascii=False, separators=(',', ':'))+'\n')
    CATALOG.append(name+'.json')
    metadata[name] = {'category': category, 'tags': [category, name]}
# New offline-only art is authored separately and kept immutable. A subsequent
# V3 catalog regeneration must preserve these assets and their categories.
# The offline list intentionally excludes 'personal': imported pictures belong
# to each user and are not part of the public bundled category catalog.
BUNDLED_OFFLINE_CATEGORY_PACK = {
    'offline-mona-lisa': ('masterpieces', ['mona lisa', 'داوینچی', 'renaissance', 'portrait']),
    'offline-starry-night': ('masterpieces', ['starry night', 'ون گوگ', 'van gogh', 'night']),
    'offline-great-wave': ('masterpieces', ['great wave', 'هوکوسای', 'hokusai', 'sea']),
    'offline-girl-pearl': ('masterpieces', ['girl pearl earring', 'ورمیر', 'vermeer', 'portrait']),
    'offline-azadi-tower': ('persian_architecture', ['azadi tower', 'برج آزادی', 'تهران', 'tehran']),
    'offline-persepolis': ('persian_architecture', ['persepolis', 'تخت جمشید', 'شیراز', 'shiraz']),
    'offline-siosepol': ('persian_architecture', ['si o se pol', 'سی و سه پل', 'اصفهان', 'isfahan']),
    'offline-nasir-molk': ('persian_architecture', ['nasir al molk', 'مسجد نصیرالملک', 'شیراز', 'stained glass']),
    'offline-shamsa': ('patterns', ['shamsa', 'شمسه', 'geometric', 'iranian']),
}
BUNDLED_OFFLINE_FILENAMES = {
    # Keep the artwork ID stable while shipping the redesigned grid as v2.
    'offline-nasir-molk': 'offline-nasir-molk-v2.json',
}
for level_id, (category, tags) in BUNDLED_OFFLINE_CATEGORY_PACK.items():
    filename = BUNDLED_OFFLINE_FILENAMES.get(level_id, f'{level_id}.json')
    if not (ROOT / filename).is_file():
        raise FileNotFoundError(f'Missing immutable offline painting: {filename}')
    CATALOG.append(filename)
    metadata[level_id] = {'category': category, 'tags': [category, *tags]}

(ROOT/'catalog.json').write_text(json.dumps(CATALOG, indent=2)+'\n')
(ROOT/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
