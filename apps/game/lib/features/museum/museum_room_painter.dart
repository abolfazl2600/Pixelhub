import 'package:flutter/material.dart';

import 'museum_pixel_grid.dart';

/// A crisp 180 × 240 pixel-art room with fine new architectural details.
///
/// Slot placement still uses the original 64 × 86 coordinates in MuseumScreen,
/// so existing layouts, frames and saved arrangements do not need migration.
/// The scenery is static. The sleeping cat and its tail are separate layers.
class MuseumRoomPainter extends CustomPainter {
  const MuseumRoomPainter(this.wall);

  static const int pixelWidth = MuseumPixelGrid.width;
  static const int pixelHeight = MuseumPixelGrid.height;

  final String wall;

  @override
  void paint(Canvas canvas, Size size) {
    final pixels = MuseumPixelGrid(canvas, size);

    // Keep the six original frame locations while snapping old outlines
    // individually to 180×240 grid edges. Fine marks are genuinely new pixels.
    void pixel(int x, int y, int w, int h, Color color) =>
        pixels.legacy(x, y, w, h, color);
    void fine(int x, int y, int w, int h, Color color) =>
        pixels.fine(x, y, w, h, color);

    final plaster = switch (wall) {
      'blue' => const Color(0xffcbdce6),
      'sage' => const Color(0xffc8d3b9),
      'emerald' => const Color(0xff16483c),
      _ => const Color(0xfff1dfc8),
    };
    final plasterShade = switch (wall) {
      'blue' => const Color(0xffb8cbd8),
      'sage' => const Color(0xffb5c4a4),
      'emerald' => const Color(0xff0f352f),
      _ => const Color(0xffe8d1b3),
    };
    final plasterLight = switch (wall) {
      'blue' => const Color(0xffe2ebee),
      'sage' => const Color(0xffdee2cd),
      'emerald' => const Color(0xff286050),
      _ => const Color(0xffffedda),
    };
    const outline = Color(0xff49352c);
    const walnut = Color(0xff69462e);
    const mahogany = Color(0xff925634);
    const timber = Color(0xffad764b);
    const honey = Color(0xffdfaa60);
    const cream = Color(0xffffe5b9);
    const gold = Color(0xfff2ca7d);

    // Masonry texture uses the new 1–3-pixel details, not larger
    // rectangles simply scaled up from the previous low-resolution room.
    pixel(0, 0, 128, 143, plaster);
    for (var row = 17; row < 137; row += 12) {
      final shift = (row ~/ 12).isEven ? 3 : 11;
      for (var x = shift; x < 125; x += 21) {
        pixel(x, row, 8, 1, plasterLight);
        pixel(x + 8, row + 1, 4, 1, plasterShade);
        pixel(x + 17, row + 6, 1, 4, plasterShade);
        pixel(x + 1, row + 5, 2, 1, plasterLight);
      }
    }
    // Raised corner pillars, stepped moldings and an inset ceiling cornice.
    pixel(0, 0, 128, 7, outline);
    pixel(0, 7, 128, 4, walnut);
    pixel(0, 11, 128, 2, honey);
    pixel(0, 13, 128, 2, mahogany);
    pixel(0, 15, 128, 1, plasterShade);
    pixel(0, 0, 5, 144, mahogany);
    pixel(5, 16, 2, 127, honey);
    pixel(7, 16, 1, 127, walnut);
    pixel(120, 16, 1, 127, walnut);
    pixel(121, 16, 2, 127, honey);
    pixel(123, 0, 5, 144, mahogany);
    for (final x in [1, 124]) {
      for (var y = 20; y < 137; y += 15) {
        pixel(x, y, 2, 2, timber);
      }
    }

    // Three faceted, stepped spotlight cones. Each band is a solid color,
    // so no blurred gradients or antialiased rays soften the pixel style.
    for (final cx in [20, 64, 108]) {
      pixel(cx - 5, 16, 10, 2, outline);
      pixel(cx - 4, 18, 8, 2, walnut);
      pixel(cx - 3, 20, 6, 2, honey);
      pixel(cx - 1, 22, 2, 2, cream);
      for (var band = 0; band < 10; band++) {
        final half = 3 + band;
        final yy = 24 + band * 4;
        pixel(cx - half, yy, half * 2, 4, band.isEven ? plasterLight : plaster);
      }
      pixel(cx - 1, 23, 2, 2, gold);
    }

    // Three narrow decorative wall panels, mostly concealed by the art.
    for (final x in [9, 49, 89]) {
      pixel(x, 27, 30, 1, plasterShade);
      pixel(x, 28, 1, 91, plasterShade);
      pixel(x + 29, 28, 1, 91, plasterShade);
      pixel(x + 1, 118, 28, 1, plasterLight);
      for (var y = 32; y <= 112; y += 10) {
        pixel(x + 2, y, 2, 1, plasterLight);
        pixel(x + 26, y + 4, 1, 2, plasterShade);
      }
    }

    // Fine carved wooden skirting and horizontal shadows.
    pixel(0, 138, 128, 2, outline);
    pixel(0, 140, 128, 3, walnut);
    pixel(0, 143, 128, 2, honey);
    pixel(0, 145, 128, 2, mahogany);
    pixel(0, 147, 128, 25, const Color(0xffc18b5d));
    for (var y = 148; y < 172; y += 6) {
      pixel(0, y, 128, 1, timber);
      pixel(0, y + 1, 128, 1, const Color(0xffd5a276));
    }
    for (var row = 0; row < 4; row++) {
      final y = 149 + row * 6;
      for (var x = ((row % 2) * 13); x < 128; x += 26) {
        pixel(x, y + 2, 1, 4, walnut);
        pixel(x + 5, y + 3, 7, 1, timber);
        pixel(x + 16, y + 4, 2, 1, mahogany);
        pixel(x + 1, y + 1, 1, 1, gold);
      }
    }

    // Layered traditional Persian carpet: stepped geometry + fine border.
    const rugDark = Color(0xff573950);
    const rugRed = Color(0xffb35557);
    const rugOrange = Color(0xffdb8e63);
    pixel(18, 157, 92, 13, outline);
    pixel(20, 158, 88, 11, rugDark);
    pixel(22, 159, 84, 9, rugRed);
    pixel(25, 160, 78, 7, rugOrange);
    pixel(28, 161, 72, 5, rugDark);
    pixel(30, 162, 68, 3, const Color(0xffd69e78));
    for (var x = 32; x < 98; x += 8) {
      pixel(x, 160, 3, 1, cream);
      pixel(x + 3, 166, 2, 1, gold);
      pixel(x + 2, 162, 2, 2, rugRed);
    }
    for (final x in [42, 64, 86]) {
      pixel(x, 161, 2, 5, gold);
      pixel(x - 3, 163, 8, 1, gold);
    }
    for (var x = 22; x < 108; x += 6) {
      pixel(x, 170, 2, 1, cream);
    }

    // Detailed wood bench with upholstered seat, edging and curved feet.
    // Its dimensions deliberately leave room above for a readable pixel cat.
    pixel(42, 143, 48, 3, outline);
    pixel(43, 140, 46, 4, walnut);
    pixel(45, 137, 42, 5, const Color(0xffb85f69));
    pixel(47, 136, 38, 2, const Color(0xffe3948c));
    pixel(46, 141, 40, 1, const Color(0xffda8180));
    for (var x = 51; x <= 79; x += 7) {
      pixel(x, 139, 2, 2, gold);
    }
    pixel(44, 145, 45, 3, mahogany);
    pixel(48, 148, 5, 12, walnut);
    pixel(78, 148, 5, 12, walnut);
    pixel(46, 158, 8, 2, outline);
    pixel(77, 158, 8, 2, outline);
    pixel(50, 151, 30, 2, honey);
    pixel(50, 153, 30, 1, walnut);
    pixel(52, 149, 2, 1, honey);
    pixel(77, 149, 2, 1, honey);

    // Variegated leafy plants; each pot has stepped rims and small glints.
    for (final cx in [12, 116]) {
      const stem = Color(0xff356b50);
      const leaf = Color(0xff538e61);
      const leafLight = Color(0xff83b876);
      const leafShade = Color(0xff2e694b);
      const pot = Color(0xff3c7690);
      pixel(cx - 7, 143, 14, 12, pot);
      pixel(cx - 6, 154, 12, 2, const Color(0xff264b61));
      pixel(cx - 8, 141, 16, 3, const Color(0xff8ac6cc));
      pixel(cx - 7, 144, 2, 9, const Color(0xff68aeb7));
      pixel(cx + 4, 145, 2, 7, const Color(0xff315d74));
      pixel(cx - 5, 140, 10, 1, const Color(0xff584535));
      pixel(cx - 1, 118, 2, 24, stem);
      pixel(cx - 2, 122, 2, 3, leafLight);
      pixel(cx - 8, 127, 8, 3, leaf);
      pixel(cx - 11, 124, 7, 4, leafLight);
      pixel(cx - 7, 122, 4, 2, leafShade);
      pixel(cx + 1, 130, 10, 4, leaf);
      pixel(cx + 7, 127, 6, 3, leafLight);
      pixel(cx + 5, 133, 4, 3, leafShade);
      pixel(cx - 5, 117, 7, 3, leaf);
      pixel(cx - 7, 113, 6, 4, leafLight);
      pixel(cx + 1, 114, 6, 5, leafShade);
      pixel(cx - 1, 109, 4, 7, leaf);
      pixel(cx, 111, 2, 3, leafLight);
    }

    // High-resolution architectural pass: wall grain and recessed joins.
    // The old 128×172 drawing remains a layout guide, but these 1px details
    // are authored on the new 180×240 grid, rather than merely upscaled.
    for (var row = 25; row < 191; row += 11) {
      for (var x = 12 + (row ~/ 11 % 3) * 5; x < 171; x += 27) {
        fine(x, row, 5, 1, plasterLight);
        fine(x + 5, row + 1, 2, 1, plasterShade);
        fine(x + 14, row + 4, 1, 3, plasterShade);
        fine(x + 2, row + 7, 2, 1, plasterLight);
      }
    }
    // Chiseled corners, tiny brass inlays and cabinetwork on the pilasters.
    for (final x in [4, 174]) {
      for (var y = 32; y < 193; y += 19) {
        fine(x, y, 2, 4, walnut);
        fine(x + 1, y + 1, 1, 2, gold);
        fine(x, y + 6, 3, 1, honey);
      }
    }
    for (var x = 12; x < 170; x += 9) {
      fine(x, 15, 3, 1, gold);
      fine(x + 2, 19, 2, 1, walnut);
      fine(x + 1, 22, 1, 1, cream);
    }
    // The light fixtures now contain small facets and stepped brass rivets.
    for (final cx in [28, 90, 152]) {
      fine(cx - 6, 25, 12, 1, walnut);
      fine(cx - 4, 26, 8, 2, honey);
      fine(cx - 2, 29, 4, 1, cream);
      fine(cx, 31, 1, 3, gold);
      fine(cx - 9, 39, 2, 2, plasterLight);
      fine(cx + 8, 41, 1, 3, plasterLight);
    }
    // Woodgrain knots and plank joints are visible at this pixel density.
    for (var row = 0; row < 5; row++) {
      final y = 207 + row * 7;
      for (var x = 8 + (row.isEven ? 0 : 12); x < 178; x += 34) {
        fine(x, y, 9, 1, honey);
        fine(x + 12, y + 1, 4, 1, mahogany);
        fine(x + 21, y + 3, 1, 2, walnut);
        fine(x + 23, y + 3, 1, 1, cream);
      }
    }
    // Detailed Persian carpet: fine weave, border stitches and diamonds.
    for (var x = 32; x <= 148; x += 6) {
      fine(x, 221, 2, 1, cream);
      fine(x + 2, 235, 2, 1, honey);
      fine(x + 3, 223, 1, 2, rugDark);
      fine(x, 233, 1, 2, rugOrange);
    }
    for (final cx in [55, 89, 123]) {
      fine(cx, 225, 2, 5, cream);
      fine(cx - 4, 227, 10, 1, cream);
      fine(cx - 2, 226, 6, 3, rugRed);
      fine(cx, 226, 2, 3, gold);
    }
    // Upholstery stitching and carved bench ornamentation.
    for (var x = 68; x < 118; x += 8) {
      fine(x, 192, 1, 2, cream);
      fine(x + 3, 197, 2, 1, honey);
      fine(x + 1, 200, 3, 1, walnut);
    }
    for (final x in [69, 113]) {
      fine(x, 212, 2, 7, mahogany);
      fine(x + 1, 213, 1, 4, honey);
      fine(x - 2, 221, 6, 1, outline);
    }
    // Plants: distinct leaf veins, paired tiny leaves and glazed pots.
    for (final cx in [17, 163]) {
      for (var y = 158; y <= 194; y += 9) {
        fine(cx - 7, y, 8, 2, const Color(0xff6ca76f));
        fine(cx - 6, y + 1, 4, 1, const Color(0xffbbd491));
        fine(cx + 1, y + 4, 7, 2, const Color(0xff366e51));
        fine(cx + 2, y + 4, 4, 1, const Color(0xff9cca8e));
      }
      fine(cx - 6, 203, 12, 1, const Color(0xffbadfe0));
      fine(cx - 7, 207, 1, 8, const Color(0xff74afc5));
      fine(cx + 5, 208, 1, 6, const Color(0xff2d5977));
      fine(cx - 4, 217, 8, 1, outline);
    }
  }

  @override
  bool shouldRepaint(MuseumRoomPainter old) => old.wall != wall;
}
