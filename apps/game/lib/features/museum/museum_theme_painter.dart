import 'package:flutter/material.dart';

/// Extra décor drawn over the static room, but underneath the user's framed
/// paintings and animated sleeping cat. All geometry is quantized to the
/// 128×172 logical pixel grid. These are four usable room designs, not baked-in
/// screenshots containing someone else's artwork.
class MuseumThemeDetailsPainter extends CustomPainter {
  const MuseumThemeDetailsPainter(this.theme);

  final String theme;

  @override
  void paint(Canvas canvas, Size size) {
    final dx = size.width / 128;
    final dy = size.height / 172;
    final paint = Paint()..isAntiAlias = false;
    void block(int x, int y, int w, int h, Color color) {
      paint.color = color;
      canvas.drawRect(Rect.fromLTWH(x * dx, y * dy, w * dx, h * dy), paint);
    }

    const gold = Color(0xffd5a044);
    const brightGold = Color(0xffffe19a);
    const darkGold = Color(0xff8d642e);
    const green = Color(0xff37734e);
    const lightLeaf = Color(0xff8cbb75);
    const shadowLeaf = Color(0xff24593b);

    switch (theme) {
      case 'classic':
        // Gold carved cornice, symmetrical classical reliefs and rug border.
        block(7, 11, 114, 2, darkGold);
        block(9, 14, 110, 1, brightGold);
        for (final x in [19, 63, 107]) {
          block(x - 7, 5, 14, 1, gold);
          block(x - 1, 3, 2, 5, brightGold);
          block(x - 4, 8, 8, 2, darkGold);
          block(x - 2, 7, 4, 3, gold);
        }
        for (final x in [5, 121]) {
          for (var y = 27; y < 130; y += 18) {
            block(x, y, 2, 4, gold);
            block(x, y + 5, 1, 2, brightGold);
          }
        }
        for (var x = 28; x < 100; x += 12) {
          block(x, 158, 3, 2, brightGold);
          block(x + 2, 168, 2, 1, brightGold);
        }
      case 'royal':
        // Rich emerald wall has a gold-art-deco crown, corner flutes,
        // jewel-toned carpet, and a dark, regal upholstered bench.
        block(6, 9, 116, 3, darkGold);
        block(6, 12, 116, 1, brightGold);
        block(6, 15, 116, 1, gold);
        for (var x = 8; x < 120; x += 12) {
          block(x, 9, 3, 1, brightGold);
          block(x + 3, 14, 2, 1, darkGold);
        }
        for (final x in [8, 117]) {
          block(x, 20, 3, 115, darkGold);
          block(x + 1, 21, 1, 110, brightGold);
          for (var y = 24; y < 133; y += 16) {
            block(x - 2, y, 7, 1, gold);
            block(x, y + 2, 3, 1, gold);
          }
        }
        for (final x in [20, 64, 108]) {
          block(x - 5, 17, 10, 2, darkGold);
          block(x - 2, 20, 4, 2, brightGold);
          block(x - 1, 22, 2, 3, brightGold);
        }
        block(18, 158, 92, 13, const Color(0xff1e453f));
        block(21, 159, 86, 11, gold);
        block(24, 160, 80, 9, const Color(0xff143d3b));
        block(27, 161, 74, 7, const Color(0xff9d6235));
        block(30, 162, 68, 5, const Color(0xff174a49));
        for (var x = 35; x < 100; x += 12) {
          block(x, 163, 3, 3, brightGold);
          block(x + 4, 166, 2, 1, darkGold);
        }
        block(45, 137, 42, 4, const Color(0xff71374e));
        block(47, 136, 38, 1, gold);
        for (var x = 51; x < 80; x += 7) {
          block(x, 140, 2, 1, gold);
        }
      case 'sky':
        // Skylight with blue sky and pixel clouds, minimalist trim, plus
        // a light geometric rug in place of the heavy Persian carpet.
        const sky = Color(0xff87bcd8);
        const skyLight = Color(0xffcdebf5);
        const frame = Color(0xff94aeb9);
        const cloud = Color(0xfff7f8ed);
        block(9, 1, 110, 11, frame);
        block(11, 1, 106, 9, sky);
        block(11, 1, 106, 2, skyLight);
        for (final x in [27, 63, 99]) {
          block(x, 1, 2, 10, const Color(0xffe3f0ef));
          block(x + 8, 4, 8, 2, cloud);
          block(x + 10, 3, 4, 1, cloud);
        }
        block(9, 11, 110, 2, const Color(0xffe4ebe9));
        block(9, 14, 110, 1, frame);
        block(5, 22, 3, 111, const Color(0xffc3d9df));
        block(120, 22, 3, 111, const Color(0xffc3d9df));
        for (final x in [6, 121]) {
          for (var y = 28; y < 130; y += 19) {
            block(x, y, 1, 4, skyLight);
          }
        }
        block(18, 157, 92, 13, const Color(0xff87aabb));
        block(20, 158, 88, 11, const Color(0xffecedde));
        block(23, 159, 82, 9, skyLight);
        block(26, 160, 76, 7, const Color(0xfff8f3e7));
        for (var x = 30; x < 98; x += 14) {
          block(x, 161, 4, 5, sky);
          block(x - 2, 163, 8, 1, sky);
        }
        block(45, 137, 42, 4, const Color(0xff80aebf));
        block(47, 136, 38, 1, const Color(0xffe9f4ed));
      case 'botanical':
        // Living vines, flowering branches, natural timber and an olive rug.
        block(7, 9, 114, 2, const Color(0xff785638));
        block(7, 13, 114, 2, const Color(0xffb99b6a));
        for (var x = 11; x <= 119; x += 9) {
          block(x, 14, 3, 3, green);
          block(x + 1, 17, 2, 3, lightLeaf);
          if (x % 3 == 2) {
            block(x + 1, 20, 1, 5, shadowLeaf);
            block(x - 1, 23, 3, 2, green);
            block(x + 2, 26, 3, 2, lightLeaf);
          }
        }
        for (final cx in [10, 118]) {
          block(cx, 18, 2, 96, shadowLeaf);
          for (var y = 20; y < 115; y += 10) {
            final direction = (y ~/ 10).isEven ? -1 : 1;
            block(cx + direction * 2, y, 7, 2, green);
            block(cx + direction * 3, y + 2, 4, 2, lightLeaf);
            block(cx, y + 4, 3, 1, shadowLeaf);
            if (y % 3 == 2) {
              block(cx + direction * 3, y + 2, 2, 2, const Color(0xffeac7a0));
              block(cx + direction * 4, y + 3, 1, 1, const Color(0xffc76e73));
            }
          }
        }
        block(17, 158, 94, 13, const Color(0xff455c39));
        block(20, 159, 88, 11, const Color(0xff9bba79));
        block(23, 160, 82, 9, const Color(0xff466348));
        block(26, 161, 76, 7, const Color(0xffb7c58e));
        block(29, 162, 70, 5, const Color(0xff667c50));
        for (var x = 34; x < 96; x += 9) {
          block(x, 163, 3, 3, const Color(0xffe5d99e));
          block(x + 2, 164, 2, 1, shadowLeaf);
        }
        block(45, 137, 42, 4, const Color(0xff77966e));
        block(47, 136, 38, 1, const Color(0xffd3dab0));
    }
  }

  @override
  bool shouldRepaint(MuseumThemeDetailsPainter old) => old.theme != theme;
}

/// Compact scene thumbnail, used for selecting among the four full museum
/// concepts. Deliberately draws representative live frames, not the fixed
/// painting thumbnails from a promotional mockup.
class MuseumThemeThumbnailPainter extends CustomPainter {
  const MuseumThemeThumbnailPainter(this.theme);

  final String theme;

  @override
  void paint(Canvas canvas, Size size) {
    final dx = size.width / 64;
    final dy = size.height / 72;
    final paint = Paint()..isAntiAlias = false;
    void block(int x, int y, int w, int h, Color color) {
      paint.color = color;
      canvas.drawRect(Rect.fromLTWH(x * dx, y * dy, w * dx, h * dy), paint);
    }

    final wall = switch (theme) {
      'royal' => const Color(0xff153d35),
      'sky' => const Color(0xffd7e9ed),
      'botanical' => const Color(0xffb6c7a2),
      _ => const Color(0xfff5dec0),
    };
    final floor = switch (theme) {
      'royal' => const Color(0xff63412e),
      'sky' => const Color(0xffd6bd9d),
      'botanical' => const Color(0xff977044),
      _ => const Color(0xffa2734f),
    };
    final trim = switch (theme) {
      'royal' => const Color(0xffe4b951),
      'sky' => const Color(0xffa3b6ba),
      'botanical' => const Color(0xff4f7951),
      _ => const Color(0xff7b4d35),
    };
    block(0, 0, 64, 55, wall);
    block(0, 0, 64, 3, trim);
    block(0, 3, 3, 52, trim);
    block(61, 3, 3, 52, trim);
    for (var x = 10; x < 61; x += 21) {
      block(x, 5, 4, 2, trim);
      block(x + 1, 7, 2, 2, const Color(0xffffde9a));
    }
    for (var i = 0; i < 6; i++) {
      final x = 6 + (i % 3) * 18;
      final y = 15 + (i ~/ 3) * 20;
      block(x + 1, y + 1, 15, 15, const Color(0xff3c302a));
      block(x, y, 15, 15, trim);
      block(x + 2, y + 2, 11, 11, const Color(0xffffedd1));
      block(
        x + 4,
        y + 5,
        7,
        5,
        [
          const Color(0xffdc7754),
          const Color(0xff8aa9c9),
          const Color(0xffc38eac),
          const Color(0xffedbb4a),
          const Color(0xff79a977),
          const Color(0xffd87c6c),
        ][i],
      );
    }
    block(0, 55, 64, 17, floor);
    block(9, 63, 46, 8, trim);
    block(11, 64, 42, 6, const Color(0xff914e5e));
    block(13, 65, 38, 4, const Color(0xffe3b777));
    block(23, 56, 19, 3, const Color(0xff845537));
    block(25, 59, 2, 7, const Color(0xff6a422e));
    block(38, 59, 2, 7, const Color(0xff6a422e));
    if (theme == 'botanical') {
      for (final x in [4, 56]) {
        block(x, 31, 2, 27, const Color(0xff4a774b));
        for (var y = 34; y < 57; y += 7) {
          block(x - 2, y, 5, 3, const Color(0xff7cbd73));
        }
      }
    } else if (theme == 'sky') {
      block(8, 2, 48, 4, const Color(0xff99ccdf));
      block(14, 3, 9, 2, const Color(0xfff5f7f3));
      block(39, 4, 7, 2, const Color(0xfff5f7f3));
    } else if (theme == 'royal') {
      for (var y = 12; y < 54; y += 10) {
        block(3, y, 1, 3, const Color(0xffffda77));
        block(60, y, 1, 3, const Color(0xffffda77));
      }
    }
  }

  @override
  bool shouldRepaint(MuseumThemeThumbnailPainter old) => old.theme != theme;
}
