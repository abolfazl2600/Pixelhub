#!/usr/bin/env python3
"""Ten original exact 15x15, color-by-number object paintings for online-only Releases.

Only reproducible palette-coded recipes live in Git. Numbered JSON and PNG
previews are generated in the Pages publication runner and stored in an
immutable Release, not in the APK. The key and bell are distinct 15x15
redesigns; the existing smaller published paintings are never overwritten.
"""
import pathlib
import sys
import zipfile

from online_release import checksum, compact, png, validate_new_pack_manifest

SIDE = 15
PREFIX = "online-object-detailed15-"
SYMBOLS = {".": 0, "#": 1, "d": 2, "m": 3, "l": 4, "h": 5, "a": 6, "b": 7}
PALETTES = {
    "gold": ["FFFFF8EC","FF523525","FF995B2E","FFE7A83F","FFFFCF61","FFFFF3BB","FFB84240","FFFFFFFF"],
    "regal": ["FFFFF6EF","FF51303B","FF925020","FFE8A533","FFFFD56C","FFFFF4B3","FFB93357","FF4D90D3"],
    "steel": ["FFF1F7FC","FF26354C","FF455E79","FF7794B5","FFB1C9E0","FFF8FCFF","FFDC684F","FFFFD16A"],
    "coral": ["FFFFF5F2","FF3C3949","FF59677B","FF9CAFC5","FFE6ECF4","FFFFFFFF","FFE44A57","FFFF98A3"],
    "ivory": ["FFFFF8F0","FF48342D","FF80573D","FFB5845A","FFE5C69C","FFFFEBD0","FF995C44","FFFFFFFF"],
    "potion": ["FFF4F8FF","FF283C56","FF415F7D","FF92B4D1","FFDAF2FF","FFFFFFFF","FFD93F62","FFFF8A9A"],
    "helm": ["FFF1F5FA","FF303746","FF515F75","FF8497AD","FFC8D8E5","FFFFFFFF","FFE04B52","FFFFCB5C"],
    "torch": ["FFF2F7FC","FF243047","FF45526A","FF78869D","FFB9C6D8","FFFFFFFF","FFF5BA3C","FFFFE58A"],
}

# Each slash separates one 15-cell row, with exactly 15 rows per illustration.
# '.' is the light paper background; all other symbols are paintable colors.
ARTWORKS = [
    ("ornate-gold-key", "کلید طلایی تزئینی", "Ornate Gold Key", "gold",
     ".............../...#####......./..##lll##....../.##lhhhm##...../.#ll###lm#...../.#lh#..#m#...../.#mm#..#d#...../.##m####d##..../..##mmmm##...../...###ml##...../......#mll#..../.......#mll#.../........#ml##../.........#m#d#./..........###.."),
    ("ruby-royal-crown", "تاج سلطنتی یاقوتی", "Ruby Royal Crown", "regal",
     ".......#......./......#a#....../..#...#l#...#../.#l#..#l#..#l#./.#mh#lmmmm#hm#./.#lm#amama#ml#./..#lmaaaaaaml#./..#lmaaaamml#../...#lmmmmml#.../..##mmmmmmm##../.##mambambam##./.#lmabmbabmlm#./.##lmmmmmmml##./..##lllllll##../...#########..."),
    ("antique-golden-bell", "زنگ طلایی کلاسیک", "Antique Golden Bell", "gold",
     "......###....../.....#lhl#...../.....#mdm#...../......#m#....../.....##m##...../....##lll##..../...##lhhll##.../...#llmmmlm#.../..##lmmmmmd##../..#llmmmmmmmd#./.##llmmmmmmmd##/.##lllllllll##./..############./......#md#...../.......##......"),
    ("sailors-steel-anchor", "لنگر فولادی دریایی", "Sailor Steel Anchor", "steel",
     "......###....../.....##l##...../.....#l#l#...../.....##l##...../......#m#....../..####lml####../..#lmmmhmmd#.../..####lml####../......#m#....../......#m#....../.#....#m#....#./.#m...#m#...m#./.##m..#l#..m##./..##mmmlmmm##../....#######...."),
    ("red-handle-scissors", "قیچی دسته‌قرمز", "Red Handle Scissors", "coral",
     "..##.......##../..#mh#...#hm#../...#ml#.#lm#.../....#ml#lm#..../.....#mlm#...../.....#lhl#...../......#d#....../......###....../....###a###..../...##aa#aa##.../..##aab#baa##../..#ab#...#ba#../..#ab#...#ba#../..##aab#baa##../...#########..."),
    ("ivory-chess-knight", "اسب شطرنج عاجی", "Ivory Chess Knight", "ivory",
     "......##......./.....#mh##...../...##mmllm##.../..#hmmlmllm##../..#ml#mmmmmm#../.#ml#dmmlmmd#../.#m###mmmmm#.../.##mmlmmmm#..../...##mmmml#..../....#mmmm#...../....#mml#....../...#mmml##...../..##lllll##..../..#mmmmmmm#..../..#########...."),
    ("ruby-potion-bottle", "شیشه معجون یاقوتی", "Ruby Potion Bottle", "potion",
     "......###....../.....#ddd#...../.....#ddd#...../....##hhh##..../....#llhlh#..../...##laaaml##../..##laaaamm##../..#laaaabammd#./.#hlaaaabammd#./.#hlaaaaaammd#./.#hlaaaaaammd#./..#laaaaaam#.../..##llaaamm##../...#########.../..............."),
    ("silver-open-wrench", "آچار نقره‌ای", "Silver Open Wrench", "steel",
     "..........###../.........#llm#./........#lhmd#./.......#lm##d#./......#lmd#d#../.....#lhm#d#.../....#lhmm##..../...#lhmm#....../..#lhmm#......./.#lhmm#......../.#lhm#........./.#l#m#........./.#l#d#........./.##d#........../..###.........."),
    ("crimson-knight-helmet", "کلاه‌خود شوالیه", "Crimson Knight Helmet", "helm",
     "......aa##...../....#aabaa##.../...#aa#mbbaa#../..#m###mmmm##../..#mllllllmd#../.##lmhhhhmmd##./.#lmhhhlhmmmmd#/.#lmm######mmd#/.#lm#dddddd#m#./.#lmm####ddmm#./.#lml#d#d#mmd#./.#lml#d#d#mmd#./..#lm####mmd#../..##llllllm##../...#########..."),
    ("lit-pocket-flashlight", "چراغ‌قوه جیبی روشن", "Lit Pocket Flashlight", "torch",
     "...........###./..........#abh#/.........#abhb#/........#labhb#/.......##mab##./......##mmd##../.....#lhm##..../....#lhm##...../...#lhm##....../..#lhm##......./.#lhm##......../.#lm##........./.#d##........../.###.........../..............."),
]


def make_level(artwork):
    slug, title_fa, title_en, theme, drawing = artwork
    rows = drawing.split("/")
    if len(rows) != SIDE or any(len(row) != SIDE for row in rows):
        raise ValueError(f"{slug}: expected exactly {SIDE} rows of {SIDE} cells")
    if set("".join(rows)) - SYMBOLS.keys():
        raise ValueError(f"{slug}: unknown palette symbol")
    cells = [SYMBOLS[c] for row in rows for c in row]
    if len(set(cells)) < 5:
        raise ValueError(f"{slug}: insufficient shading/detail")
    level = {
        "schemaVersion": 2, "levelId": PREFIX + slug, "levelVersion": 1,
        "titles": {"fa": title_fa, "en": title_en},
        "width": SIDE, "height": SIDE, "palette": PALETTES[theme],
        "cells": cells,
    }
    level["checksum"] = checksum(level)
    return level


def create_pack(destination):
    if len(ARTWORKS) != 10:
        raise ValueError("Exactly ten 15x15 online objects are required")
    manifest, files, ids = [], {}, set()
    for artwork in ARTWORKS:
        level = make_level(artwork)
        ident = level["levelId"]
        if ident in ids:
            raise ValueError(f"Duplicate level ID: {ident}")
        ids.add(ident)
        body = compact(level)
        if len(body) > 262144:
            raise ValueError(f"Level too large: {ident}")
        stem = f"{ident}-v1"
        manifest.append({
            "id": ident, "version": 1,
            "title": level["titles"]["fa"], "titleEn": level["titles"]["en"],
            "category": "objects", "width": SIDE, "height": SIDE,
            "bytes": len(body), "checksum": level["checksum"],
        })
        files[f"levels/{stem}.json"] = body
        files[f"previews/{stem}.png"] = png(level)
    validate_new_pack_manifest(manifest)
    target = pathlib.Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("catalog.json", compact({"schemaVersion": 1, "pictures": manifest}))
        for path, data in files.items():
            archive.writestr(path, data)
    print(f"Created {len(manifest)} distinct online {SIDE}x{SIDE} levels: {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool/online_objects_detailed_15_pack.py <content.zip>")
    create_pack(sys.argv[1])
