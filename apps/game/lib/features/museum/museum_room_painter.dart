import 'package:flutter/material.dart';

/// Lightweight, fully procedural pixel room: no network images, textures,
/// raster uploads, filters or continuously animated background.
class MuseumRoomPainter extends CustomPainter {
  const MuseumRoomPainter(this.wall);
  final String wall;

  @override
  void paint(Canvas canvas, Size size) {
    final cell = size.width / 64;
    final yCell = size.height / 86;
    final p = Paint()..isAntiAlias = false;

    void rect(num x, num y, num w, num h, Color color) {
      p.color = color;
      canvas.drawRect(
        Rect.fromLTWH(
          x * cell,
          y * yCell,
          w * cell,
          h * yCell,
        ),
        p,
      );
    }

    final base = switch (wall) {
      'blue' => const Color(0xffcbdce6),
      'sage' => const Color(0xffc8d3b9),
      _ => const Color(0xfff1dfc8),
    };
    final shadow = switch (wall) {
      'blue' => const Color(0xffb8cbd8),
      'sage' => const Color(0xffb5c4a4),
      _ => const Color(0xffe8d1b3),
    };
    final highlight = switch (wall) {
      'blue' => const Color(0xffe2ebee),
      'sage' => const Color(0xffdee2cd),
      _ => const Color(0xffffedda),
    };
    const darkWood = Color(0xff65422f);
    const wood = Color(0xff976039);
    const edge = Color(0xff51372c);
    const gold = Color(0xffdb9e53);

    // Pixel wall, stepped wall corners and sparse dithered masonry.
    rect(0, 0, 64, 70, base);
    for (var row = 2; row < 68; row += 6) {
      for (var col = (row.isEven ? 3 : 8); col < 62; col += 11) {
        rect(col, row, 2, 1, row % 3 == 0 ? shadow : highlight);
      }
    }
    rect(0, 0, 64, 3, edge);
    rect(0, 3, 64, 2, darkWood);
    rect(0, 5, 64, 1, gold);
    rect(0, 6, 64, 1, shadow);
    rect(0, 0, 2, 70, wood);
    rect(2, 0, 1, 70, gold);
    rect(61, 0, 1, 70, gold);
    rect(62, 0, 2, 70, wood);

    // Hard-edged spotlights, drawn behind the framed artwork.
    for (final x in [10, 32, 54]) {
      rect(x - 2, 6, 4, 1, darkWood);
      rect(x - 1, 7, 2, 1, gold);
      for (var band = 0; band < 11; band++) {
        final halfWidth = 2 + band ~/ 2;
        final alpha = 19 - band;
        p.color = const Color(0xfffff5d6).withValues(alpha: alpha / 100);
        canvas.drawRect(
          Rect.fromLTWH(
            (x - halfWidth) * cell,
            (8 + band * 4) * yCell,
            halfWidth * 2 * cell,
            4 * yCell,
          ),
          p,
        );
      }
    }

    // Baseboard and timber floor are intentionally crisp rectangles.
    rect(0, 68, 64, 2, wood);
    rect(0, 70, 64, 1, edge);
    rect(0, 71, 64, 15, const Color(0xffbc865b));
    for (var i = 0; i < 5; i++) {
      rect(0, 71 + i * 3, 64, 1, const Color(0xffa57450));
    }
    for (var i = 0; i < 10; i++) {
      rect((i * 13) % 64, 72 + (i % 5) * 3, 1, 2, wood);
    }

    // Persian-inspired stepped pixel rug.
    rect(10, 77, 44, 8, edge);
    rect(12, 78, 40, 6, const Color(0xffa74d47));
    rect(14, 79, 36, 4, const Color(0xffd28a64));
    rect(16, 80, 32, 2, const Color(0xff673e64));
    for (var x = 18; x < 48; x += 6) {
      rect(x, 80, 2, 2, const Color(0xffeac795));
    }

    // Pixel wooden bench, below frames so it does not hide the artwork.
    rect(23, 71, 18, 2, edge);
    rect(22, 72, 20, 2, darkWood);
    rect(23, 70, 18, 2, const Color(0xffaf5263));
    rect(24, 69, 16, 1, const Color(0xffd78280));
    for (var x = 26; x <= 38; x += 4) {
      rect(x, 71, 1, 1, const Color(0xffe3a283));
    }
    rect(25, 74, 2, 5, edge);
    rect(37, 74, 2, 5, edge);
    rect(24, 78, 4, 1, darkWood);
    rect(36, 78, 4, 1, darkWood);

    // Simple potted pixel plants at the edges of the room.
    for (final x in [5, 58]) {
      rect(x - 3, 72, 6, 5, const Color(0xff477d92));
      rect(x - 2, 76, 4, 1, const Color(0xff2e5267));
      rect(x - 3, 72, 6, 1, const Color(0xffa8dee0));
      rect(x, 61, 1, 12, const Color(0xff406b4b));
      rect(x - 4, 63, 5, 2, const Color(0xff5d965d));
      rect(x + 1, 65, 4, 2, const Color(0xff3a7652));
      rect(x - 3, 59, 4, 3, const Color(0xff6daa69));
      rect(x + 1, 58, 3, 4, const Color(0xff477f52));
      rect(x - 1, 55, 3, 5, const Color(0xff538a50));
    }
  }

  @override
  bool shouldRepaint(MuseumRoomPainter old) => old.wall != wall;
}
