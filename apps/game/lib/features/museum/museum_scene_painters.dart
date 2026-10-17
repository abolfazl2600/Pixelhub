import 'package:flutter/material.dart';

/// Each museum design paints a separate architectural scene. The completed
/// paintings, labels, six hit targets and animated cat are Flutter overlays.
/// Nothing in the background contains a baked-in or fake completed painting.
abstract class MuseumScenePainter extends CustomPainter {
  const MuseumScenePainter(this.wall);

  static const pixelWidth = 256;
  static const pixelHeight = 352;

  final String wall;

  @override
  bool shouldRepaint(covariant MuseumScenePainter oldDelegate) =>
      oldDelegate.runtimeType != runtimeType || oldDelegate.wall != wall;
}

MuseumScenePainter museumSceneFor(String theme, String wall) => switch (theme) {
  'royal' => MuseumRoyalScenePainter(wall),
  'sky' => MuseumSkyScenePainter(wall),
  'botanical' => MuseumBotanicalScenePainter(wall),
  _ => MuseumClassicScenePainter(wall),
};

/// Integer aligned 256 × 352 canvas. Shapes never use gradients or smoothing.
class MuseumScenePixels {
  MuseumScenePixels(this.canvas, this.size);

  static const width = MuseumScenePainter.pixelWidth;
  static const height = MuseumScenePainter.pixelHeight;

  final Canvas canvas;
  final Size size;
  final Paint _brush = Paint()..isAntiAlias = false;

  void rect(int x, int y, int w, int h, Color color) {
    if (w <= 0 || h <= 0) return;
    _brush.color = color;
    canvas.drawRect(
      Rect.fromLTWH(
        x * size.width / width,
        y * size.height / height,
        w * size.width / width,
        h * size.height / height,
      ),
      _brush,
    );
  }

  void trim(int x, int y, int w, int h, Color outside, Color inside) {
    rect(x, y, w, h, outside);
    rect(x + 2, y + 2, w - 4, h - 4, inside);
  }

  void floor(Color base, Color seam, Color highlight) {
    rect(0, 285, 256, 67, base);
    for (var row = 0; row < 9; row++) {
      final y = 286 + row * 8;
      rect(0, y, 256, 1, seam);
      rect(0, y + 1, 256, 1, highlight);
      for (var x = row.isEven ? 6 : 23; x < 256; x += 41) {
        rect(x, y + 2, 1, 6, seam);
        rect(x + 7, y + 4, 10, 1, highlight);
        rect(x + 21, y + 5, 5, 1, seam);
      }
    }
  }

  void lamp(int cx, int top, Color bronze, Color gold, Color glow) {
    rect(cx - 9, top, 18, 3, bronze);
    rect(cx - 5, top + 3, 10, 2, gold);
    rect(cx - 4, top + 5, 8, 4, bronze);
    rect(cx - 6, top + 9, 12, 2, gold);
    rect(cx - 4, top + 11, 8, 2, glow);
    rect(cx - 1, top + 13, 2, 4, gold);
    for (var i = 0; i < 4; i++) {
      rect(cx - 6 - i * 2, top + 17 + i * 4, 12 + i * 4, 1, glow);
    }
  }

  void persianRug(Color border, Color field, Color accent, Color light) {
    rect(25, 323, 206, 26, border);
    rect(29, 326, 198, 20, light);
    rect(34, 329, 188, 14, field);
    rect(40, 331, 176, 10, accent);
    rect(46, 333, 164, 6, field);
    for (var x = 38; x < 220; x += 8) {
      rect(x, 328, 3, 1, border);
      rect(x + 3, 343, 2, 1, border);
      rect(x, 335, 2, 3, light);
    }
    for (final cx in [74, 128, 182]) {
      rect(cx - 2, 329, 4, 12, light);
      rect(cx - 9, 335, 18, 2, light);
      rect(cx - 6, 332, 12, 8, field);
      rect(cx - 3, 334, 6, 4, accent);
      rect(cx - 1, 334, 2, 4, light);
    }
    for (var x = 33; x < 225; x += 9) {
      rect(x, 349, 3, 2, light);
    }
  }

  void plant(
    int cx, {
    required Color pot,
    required Color rim,
    required Color leaf,
    required Color shade,
    required Color light,
    int reach = 44,
  }) {
    rect(cx - 11, 301, 22, 24, pot);
    rect(cx - 13, 299, 26, 4, rim);
    rect(cx - 9, 324, 18, 3, shade);
    rect(cx - 8, 305, 3, 13, rim);
    rect(cx + 7, 306, 2, 11, shade);
    rect(cx - 2, 303 - reach, 4, reach + 1, shade);
    for (var y = 270; y > 302 - reach; y -= 9) {
      final side = (y ~/ 9).isEven ? -1 : 1;
      rect(cx + side * 3 - 8, y, 13, 4, leaf);
      rect(cx + side * 7 - 7, y - 4, 11, 5, shade);
      rect(cx + side * 5 - 4, y - 3, 6, 2, light);
    }
    rect(cx - 6, 279 - reach, 12, 10, leaf);
    rect(cx - 2, 275 - reach, 5, 8, light);
  }

  void bench({
    required Color wood,
    required Color shadow,
    required Color fabric,
    required Color sheen,
    required Color decoration,
    bool rattan = false,
  }) {
    // Seat is positioned underneath the independent sleeping cat sprite.
    rect(58, 289, 141, 7, shadow);
    rect(60, 286, 137, 7, wood);
    rect(65, 280, 127, 8, fabric);
    rect(68, 278, 121, 2, sheen);
    for (var x = 72; x < 190; x += 14) {
      rect(x, 284, 3, 2, decoration);
    }
    rect(63, 295, 131, 10, shadow);
    rect(69, 296, 119, 5, wood);
    rect(70, 304, 11, 23, shadow);
    rect(177, 304, 11, 23, shadow);
    rect(72, 306, 6, 15, wood);
    rect(179, 306, 6, 15, wood);
    rect(68, 325, 16, 2, shadow);
    rect(175, 325, 16, 2, shadow);
    if (rattan) {
      rect(81, 300, 95, 12, wood);
      for (var x = 83; x < 177; x += 5) {
        rect(x, 302, 2, 9, shadow);
        rect(x + 2, 305, 2, 2, decoration);
      }
    } else {
      rect(83, 304, 92, 4, sheen);
      rect(85, 310, 88, 2, shadow);
    }
  }
}

/// Warm classic gallery: vaulted dark-wood cornice, champagne plaster,
/// brass lamps, carved wall pilasters and a traditional Persian carpet.
class MuseumClassicScenePainter extends MuseumScenePainter {
  const MuseumClassicScenePainter(super.wall);

  @override
  void paint(Canvas canvas, Size size) {
    final p = MuseumScenePixels(canvas, size);
    const walnut = Color(0xff593423);
    const dark = Color(0xff38271f);
    const gilded = Color(0xffbc813c);
    const lightGold = Color(0xffffd98c);
    final plaster = switch (wall) {
      'blue' => const Color(0xffd2e4ea),
      'sage' => const Color(0xffd9dec6),
      'emerald' => const Color(0xff356355),
      _ => const Color(0xffffedcf),
    };
    p.rect(0, 0, 256, 285, plaster);
    // High carved ceiling, stepped cornice and central decorative crest.
    p.rect(0, 0, 256, 24, dark);
    p.rect(10, 4, 236, 12, walnut);
    for (var x = 20; x < 243; x += 20) {
      p.rect(x, 5, 12, 2, gilded);
      p.rect(x + 3, 11, 5, 2, const Color(0xff855032));
    }
    p.rect(0, 24, 256, 4, gilded);
    p.rect(0, 28, 256, 2, lightGold);
    p.rect(7, 31, 242, 2, const Color(0xffca985b));
    for (var x = 24; x < 242; x += 16) {
      p.rect(x, 26, 4, 1, lightGold);
      p.rect(x + 2, 30, 2, 2, walnut);
    }
    for (final x in [0, 248]) {
      p.rect(x, 0, 8, 285, walnut);
      p.rect(x + 2, 34, 2, 249, gilded);
      for (var y = 44; y < 283; y += 29) {
        p.rect(x + 1, y, 6, 8, dark);
        p.rect(x + 2, y + 1, 4, 5, gilded);
        p.rect(x + 3, y + 2, 2, 3, lightGold);
      }
    }
    // Reliefs are placed behind the dynamic artwork, never baked into it.
    for (var row = 0; row < 14; row++) {
      final y = 40 + row * 17;
      for (var x = 19 + (row.isEven ? 0 : 9); x < 247; x += 22) {
        p.rect(x, y, 7, 1, const Color(0xffefd6b1));
        p.rect(x + 8, y + 5, 1, 5, const Color(0xffdec3a2));
        p.rect(x + 4, y + 10, 3, 1, const Color(0xfffff7e0));
      }
    }
    for (final cx in [48, 128, 208]) {
      p.lamp(cx, 33, walnut, gilded, lightGold);
      p.rect(cx - 5, 137, 10, 2, gilded);
      p.rect(cx - 2, 139, 4, 3, lightGold);
    }
    p.rect(0, 280, 256, 4, walnut);
    p.rect(0, 284, 256, 2, gilded);
    p.floor(
      const Color(0xffb9794d),
      const Color(0xff7a492d),
      const Color(0xffe0a777),
    );
    for (final x in [25, 231]) {
      p.plant(
        x,
        pot: const Color(0xfff1d3a4),
        rim: const Color(0xff835338),
        leaf: const Color(0xff539460),
        shade: const Color(0xff2f6546),
        light: const Color(0xff90c48b),
        reach: 45,
      );
    }
    p.bench(
      wood: const Color(0xffab683c),
      shadow: dark,
      fabric: const Color(0xffa34d5e),
      sheen: const Color(0xffe48a82),
      decoration: lightGold,
    );
    p.persianRug(
      const Color(0xff503148),
      const Color(0xff7c263f),
      const Color(0xffc06d46),
      lightGold,
    );
  }
}

/// Regal emerald gallery: deep patterned green damask, dark coffered timber,
/// richly gilded columns and lamps, velvet bench and jewel-toned rug.
class MuseumRoyalScenePainter extends MuseumScenePainter {
  const MuseumRoyalScenePainter(super.wall);

  @override
  void paint(Canvas canvas, Size size) {
    final p = MuseumScenePixels(canvas, size);
    const walnut = Color(0xff321d17);
    const gold = Color(0xffc99134);
    const highlight = Color(0xffffda73);
    const deep = Color(0xff032e28);
    final green = switch (wall) {
      'cream' => const Color(0xffefe0c2),
      'blue' => const Color(0xff3b6574),
      'sage' => const Color(0xff70836b),
      _ => const Color(0xff075044),
    };
    p.rect(0, 0, 256, 285, green);
    // Gilded coffered roof; unlike the classic room its cornice is square.
    p.rect(0, 0, 256, 27, walnut);
    p.rect(9, 2, 238, 17, const Color(0xff603921));
    for (var x = 22; x < 234; x += 54) {
      p.trim(x, 3, 41, 15, walnut, const Color(0xff3c241b));
      p.rect(x + 2, 5, 37, 1, gold);
      p.rect(x + 5, 15, 31, 1, const Color(0xff835222));
    }
    p.rect(0, 21, 256, 3, gold);
    p.rect(0, 24, 256, 2, highlight);
    p.rect(0, 27, 256, 3, walnut);
    // Velvet damask: heraldic motifs and pinstripe stems between frames.
    for (var y = 43; y < 276; y += 33) {
      for (var x = 19 + ((y ~/ 33).isEven ? 0 : 17); x < 242; x += 34) {
        p.rect(x + 4, y, 4, 12, const Color(0xff176253));
        p.rect(x, y + 4, 12, 3, const Color(0xff1e6a55));
        p.rect(x + 2, y + 2, 8, 7, deep);
        p.rect(x + 5, y + 3, 2, 6, const Color(0xffa18038));
        p.rect(x + 3, y + 5, 6, 2, const Color(0xffa18038));
      }
    }
    for (final x in [0, 247]) {
      p.rect(x, 0, 9, 285, walnut);
      p.rect(x + 2, 30, 2, 254, gold);
      p.rect(x + 5, 30, 1, 254, highlight);
      for (var y = 39; y < 276; y += 23) {
        p.rect(x + 1, y, 7, 3, gold);
        p.rect(x + 3, y + 1, 3, 1, highlight);
      }
    }
    for (final cx in [48, 128, 208]) {
      p.lamp(cx, 31, walnut, gold, highlight);
      p.rect(cx - 3, 142, 6, 2, gold);
      p.rect(cx - 1, 144, 2, 2, highlight);
    }
    p.rect(0, 278, 256, 5, walnut);
    for (var x = 14; x < 245; x += 20) {
      p.rect(x, 280, 12, 2, gold);
    }
    p.floor(
      const Color(0xff734023),
      const Color(0xff402315),
      const Color(0xffae6a36),
    );
    for (final x in [23, 233]) {
      p.plant(
        x,
        pot: const Color(0xff076454),
        rim: highlight,
        leaf: const Color(0xff397c48),
        shade: const Color(0xff123e31),
        light: const Color(0xff8fbe63),
        reach: 53,
      );
      p.rect(x - 7, 311, 14, 3, gold);
      p.rect(x - 3, 315, 6, 6, highlight);
    }
    p.bench(
      wood: gold,
      shadow: walnut,
      fabric: const Color(0xff731e44),
      sheen: const Color(0xffd15d72),
      decoration: highlight,
    );
    p.rect(124, 300, 8, 6, highlight);
    p.rect(126, 302, 4, 2, deep);
    p.persianRug(
      const Color(0xff38192c),
      const Color(0xff075147),
      const Color(0xff8c2642),
      highlight,
    );
  }
}

/// Open sky gallery: panoramic skylight, airy slate-blue plaster, crisp white
/// panels, understated furniture and cool blue geometric woven rug.
class MuseumSkyScenePainter extends MuseumScenePainter {
  const MuseumSkyScenePainter(super.wall);

  @override
  void paint(Canvas canvas, Size size) {
    final p = MuseumScenePixels(canvas, size);
    final plaster = switch (wall) {
      'sage' => const Color(0xffd2e2ce),
      'emerald' => const Color(0xff37676d),
      'cream' => const Color(0xfff3e5d0),
      _ => const Color(0xffcfe6f2),
    };
    const cream = Color(0xfffcf7ea);
    const blue = Color(0xff80bedc);
    const slate = Color(0xff729db1);
    p.rect(0, 0, 256, 285, plaster);
    // The large blue skylight replaces the wooden coffered ceiling.
    p.rect(0, 0, 256, 8, const Color(0xff967053));
    p.rect(7, 2, 242, 39, cream);
    p.rect(12, 4, 232, 31, blue);
    p.rect(12, 4, 232, 5, const Color(0xffb8e5f4));
    for (final x in [67, 128, 189]) {
      p.rect(x - 2, 3, 4, 35, cream);
      p.rect(x, 3, 1, 35, const Color(0xff9ec8d5));
    }
    for (final cx in [37, 101, 163, 221]) {
      p.rect(cx - 12, 15, 16, 3, const Color(0xfff6faf5));
      p.rect(cx - 6, 12, 9, 3, const Color(0xfff6faf5));
      p.rect(cx + 6, 19, 7, 2, const Color(0xffd9eef0));
    }
    p.rect(0, 36, 256, 5, cream);
    p.rect(0, 41, 256, 2, slate);
    p.rect(0, 44, 256, 3, const Color(0xffeaf3f0));
    // Recessed tall panels, no carved wood and far more negative space.
    for (final x in [11, 90, 169]) {
      p.rect(x, 57, 76, 215, const Color(0xffb5d5e1));
      p.rect(x + 2, 59, 72, 211, plaster);
      p.rect(x + 4, 62, 68, 207, const Color(0xffdef1f6));
      p.rect(x + 5, 64, 66, 202, plaster);
    }
    for (var y = 55; y < 276; y += 21) {
      for (var x = 15 + (y.isEven ? 2 : 7); x < 241; x += 25) {
        p.rect(x, y, 9, 1, const Color(0xffeaf6fb));
        p.rect(x + 7, y + 7, 2, 3, const Color(0xffb7d4df));
      }
    }
    for (final x in [0, 247]) {
      p.rect(x, 0, 9, 287, const Color(0xffd7e0dc));
      p.rect(x + 2, 48, 2, 235, cream);
      p.rect(x + 6, 51, 1, 228, slate);
    }
    for (final cx in [48, 128, 208]) {
      p.lamp(cx, 45, const Color(0xff7c634d), const Color(0xffd6ae66), cream);
    }
    p.rect(0, 280, 256, 6, const Color(0xffe7eeeb));
    p.floor(
      const Color(0xffd3ae88),
      const Color(0xffa07d60),
      const Color(0xfff0d4ad),
    );
    for (final x in [22, 234]) {
      p.plant(
        x,
        pot: const Color(0xff9ad1de),
        rim: cream,
        leaf: const Color(0xff559977),
        shade: const Color(0xff326f63),
        light: const Color(0xff8bc2a0),
        reach: 39,
      );
    }
    p.bench(
      wood: const Color(0xff9d7657),
      shadow: const Color(0xff5f554d),
      fabric: const Color(0xff86bacf),
      sheen: cream,
      decoration: const Color(0xffc7e1e3),
    );
    p.persianRug(
      const Color(0xff91b6ca),
      cream,
      const Color(0xff99cbe1),
      const Color(0xff5788ad),
    );
  }
}

/// Botanical gallery: wood-beamed pergola, hanging vines and amber pendants,
/// sage plaster, rattan bench, woven baskets and a floral olive-green rug.
class MuseumBotanicalScenePainter extends MuseumScenePainter {
  const MuseumBotanicalScenePainter(super.wall);

  @override
  void paint(Canvas canvas, Size size) {
    final p = MuseumScenePixels(canvas, size);
    const wood = Color(0xff945b31);
    const woodShade = Color(0xff5b3826);
    const honey = Color(0xffd4a269);
    const foliage = Color(0xff437b45);
    const leafLight = Color(0xff83b75d);
    const cream = Color(0xffffe8b1);
    final plaster = switch (wall) {
      'blue' => const Color(0xffc8dedc),
      'cream' => const Color(0xffe8dcc1),
      'emerald' => const Color(0xff4d7158),
      _ => const Color(0xffd5dfb5),
    };
    p.rect(0, 0, 256, 285, plaster);
    // Overhanging pergola with wooden rafters and a carved botanical plaque.
    p.rect(0, 0, 256, 16, woodShade);
    for (var x = 0; x < 256; x += 35) {
      p.rect(x, 0, 12, 22, wood);
      p.rect(x + 2, 3, 2, 19, honey);
      p.rect(x + 9, 5, 2, 15, woodShade);
    }
    p.rect(0, 21, 256, 5, wood);
    p.rect(0, 26, 256, 2, honey);
    p.trim(94, 12, 68, 19, woodShade, wood);
    p.rect(100, 17, 56, 11, honey);
    p.rect(117, 19, 22, 4, foliage);
    p.rect(126, 15, 5, 9, cream);
    p.rect(124, 17, 9, 4, const Color(0xfff8f4dc));
    p.rect(127, 18, 3, 3, const Color(0xffeeb86b));
    for (final x in [0, 248]) {
      p.rect(x, 0, 8, 285, wood);
      p.rect(x + 2, 32, 2, 248, honey);
      for (var y = 40; y < 278; y += 24) {
        p.rect(x + 5, y, 3, 11, woodShade);
        p.rect(x + 1, y + 5, 4, 2, honey);
      }
    }
    // Leafy hanging vines with light blossoms, visible around the artwork.
    for (final cx in [13, 42, 83, 176, 214, 243]) {
      p.rect(cx, 8, 2, 39, const Color(0xff456542));
      for (var y = 12; y < 51; y += 9) {
        final side = (y ~/ 9).isEven ? -1 : 1;
        p.rect(cx + side * 2 - 4, y, 10, 4, foliage);
        p.rect(cx + side * 3 - 3, y + 2, 6, 3, leafLight);
        if (cx == 13 || cx == 243) {
          p.rect(cx + side * 2, y + 5, 3, 3, cream);
        }
      }
    }
    // Delicate leafy reliefs and warm sun patches on the sage wall.
    for (var y = 54; y < 280; y += 15) {
      for (var x = 12 + (y % 3) * 6; x < 246; x += 28) {
        p.rect(x, y, 6, 2, const Color(0xffdce5b8));
        p.rect(x + 8, y + 6, 3, 1, const Color(0xffa5bd89));
        p.rect(x + 4, y + 10, 2, 4, const Color(0xffc1d29e));
      }
    }
    for (final cx in [48, 128, 208]) {
      p.rect(cx - 1, 28, 2, 7, woodShade);
      p.lamp(cx, 33, woodShade, wood, cream);
    }
    // A carved wainscot separates the wall from the natural timber floor.
    p.rect(0, 278, 256, 7, woodShade);
    for (var x = 10; x < 249; x += 20) {
      p.rect(x, 280, 15, 2, wood);
      p.rect(x + 2, 283, 11, 1, honey);
    }
    p.floor(
      const Color(0xffb78655),
      const Color(0xff805436),
      const Color(0xffdfad78),
    );
    for (final x in [22, 234]) {
      p.plant(
        x,
        pot: const Color(0xffe6cf9f),
        rim: wood,
        leaf: foliage,
        shade: const Color(0xff245a35),
        light: leafLight,
        reach: 59,
      );
      for (var y = 307; y < 320; y += 4) {
        for (var bx = x - 8; bx < x + 9; bx += 5) {
          p.rect(bx, y, 2, 2, wood);
        }
      }
    }
    p.bench(
      wood: wood,
      shadow: woodShade,
      fabric: const Color(0xff7f9d6b),
      sheen: const Color(0xffc8d7ab),
      decoration: cream,
      rattan: true,
    );
    p.persianRug(
      const Color(0xff5b653c),
      const Color(0xff79945c),
      const Color(0xff345d3f),
      cream,
    );
    // Daisy motifs on the rug; tiny ivory petals read as botanical embroidery.
    for (final cx in [56, 110, 166, 207]) {
      p.rect(cx, 331, 3, 10, cream);
      p.rect(cx - 4, 335, 11, 2, cream);
      p.rect(cx - 2, 333, 7, 6, const Color(0xff668653));
      p.rect(cx, 335, 3, 2, const Color(0xffebad63));
    }
  }
}
