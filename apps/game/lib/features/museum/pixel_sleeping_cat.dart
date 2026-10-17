import 'dart:async';

import 'package:flutter/material.dart';

/// An independent 104 × 56 pixel sprite. The room and the sleeping body stay
/// static; only the tail layer changes on a slow, four-step loop.
class PixelSleepingCat extends StatefulWidget {
  const PixelSleepingCat({super.key});

  static const int pixelWidth = 104;
  static const int pixelHeight = 56;

  @override
  State<PixelSleepingCat> createState() => _PixelSleepingCatState();
}

class _PixelSleepingCatState extends State<PixelSleepingCat> {
  static const _tailSequence = [0, 1, 2, 1];

  Timer? _tailTimer;
  int _step = 0;

  @override
  void initState() {
    super.initState();
    // Timers (rather than a continuously ticking AnimationController) avoid
    // requesting new frames while the tail stays on the same pixel pose.
    _tailTimer = Timer.periodic(const Duration(milliseconds: 1100), (_) {
      if (!mounted ||
          !TickerMode.of(context) ||
          (MediaQuery.maybeOf(context)?.disableAnimations ?? false)) {
        return;
      }
      setState(() => _step = (_step + 1) % _tailSequence.length);
    });
  }

  @override
  void dispose() {
    _tailTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SizedBox.expand(
    child: Stack(
      children: [
        Positioned.fill(
          child: RepaintBoundary(
            child: CustomPaint(
              painter: PixelCatTailPainter(_tailSequence[_step]),
            ),
          ),
        ),
        const Positioned.fill(
          child: RepaintBoundary(
            child: CustomPaint(painter: PixelCatBodyPainter()),
          ),
        ),
      ],
    ),
  );
}

/// High-resolution tabby silhouette, ears, closed eyes and whiskers remain static.
class PixelCatBodyPainter extends CustomPainter {
  const PixelCatBodyPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final pixel = _CatPixels(canvas, size);
    const outline = Color(0xff593a2d);
    const furShadow = Color(0xffa76845);
    const fur = Color(0xffd69a63);
    const furGold = Color(0xffedb67b);
    const cream = Color(0xffffdbab);
    const light = Color(0xffffedca);
    const stripe = Color(0xff865037);
    const pink = Color(0xffbe7b7a);

    // The rounded back and tucked-in hindquarters are hand-pixeled at twice
    // the former sprite resolution, rather than scaling the old rectangles.
    pixel.draw(22, 32, 7, 11, outline);
    pixel.draw(27, 25, 5, 21, outline);
    pixel.draw(32, 22, 8, 26, outline);
    pixel.draw(40, 20, 24, 30, outline);
    pixel.draw(61, 23, 12, 24, outline);
    pixel.draw(23, 39, 49, 11, outline);
    pixel.draw(28, 32, 43, 15, fur);
    pixel.draw(33, 26, 36, 19, fur);
    pixel.draw(40, 23, 24, 20, furGold);
    pixel.draw(26, 39, 42, 8, cream);
    pixel.draw(32, 43, 35, 5, light);
    pixel.draw(37, 47, 23, 2, furShadow);
    pixel.draw(29, 35, 5, 10, furShadow);
    pixel.draw(34, 28, 2, 7, light);
    pixel.draw(39, 25, 16, 2, cream);
    pixel.draw(44, 28, 16, 2, furGold);
    pixel.draw(53, 45, 13, 2, furShadow);

    // Subtle individually stepped tabby markings (1–3 logical pixels).
    pixel.draw(39, 24, 2, 6, stripe);
    pixel.draw(41, 27, 2, 4, stripe);
    pixel.draw(46, 24, 2, 5, stripe);
    pixel.draw(48, 27, 2, 3, stripe);
    pixel.draw(55, 25, 2, 5, stripe);
    pixel.draw(57, 29, 2, 3, stripe);
    pixel.draw(30, 34, 2, 5, stripe);
    pixel.draw(32, 37, 2, 3, stripe);
    pixel.draw(40, 37, 3, 2, furShadow);
    pixel.draw(50, 37, 2, 3, furShadow);
    pixel.draw(59, 38, 2, 3, furShadow);
    pixel.draw(28, 44, 4, 1, cream);
    pixel.draw(33, 47, 4, 1, light);

    // Two clearly separated paws, folded beneath the chin.
    pixel.draw(61, 45, 29, 6, outline);
    pixel.draw(63, 44, 10, 6, cream);
    pixel.draw(77, 44, 10, 6, cream);
    pixel.draw(64, 45, 8, 2, light);
    pixel.draw(78, 45, 8, 2, light);
    pixel.draw(67, 48, 1, 2, furShadow);
    pixel.draw(71, 48, 1, 2, furShadow);
    pixel.draw(81, 48, 1, 2, furShadow);
    pixel.draw(85, 48, 1, 2, furShadow);

    // Two triangular, separately shaped cat ears with soft pink centres.
    pixel.draw(69, 21, 5, 13, outline);
    pixel.draw(72, 16, 5, 15, outline);
    pixel.draw(75, 13, 4, 16, outline);
    pixel.draw(78, 19, 4, 11, outline);
    pixel.draw(87, 19, 5, 11, outline);
    pixel.draw(90, 13, 4, 16, outline);
    pixel.draw(94, 16, 4, 15, outline);
    pixel.draw(98, 22, 3, 10, outline);
    pixel.draw(75, 19, 3, 10, furGold);
    pixel.draw(77, 22, 2, 6, pink);
    pixel.draw(90, 19, 4, 10, furGold);
    pixel.draw(92, 22, 2, 6, pink);

    // Round sleeping face, cheek, brighter muzzle and white chin.
    pixel.draw(67, 29, 30, 13, outline);
    pixel.draw(71, 25, 24, 20, outline);
    pixel.draw(75, 23, 17, 23, outline);
    pixel.draw(69, 33, 31, 9, outline);
    pixel.draw(72, 29, 25, 14, fur);
    pixel.draw(76, 25, 17, 18, furGold);
    pixel.draw(73, 34, 24, 7, cream);
    pixel.draw(79, 38, 20, 5, light);
    pixel.draw(82, 41, 15, 3, cream);
    pixel.draw(94, 36, 7, 6, cream);
    pixel.draw(96, 38, 4, 5, light);
    // Forehead stripes and symmetrical eyelid folds.
    pixel.draw(81, 25, 2, 5, stripe);
    pixel.draw(84, 27, 2, 4, stripe);
    pixel.draw(89, 26, 2, 5, stripe);
    pixel.draw(74, 35, 1, 3, furShadow);
    pixel.draw(79, 35, 5, 1, outline);
    pixel.draw(80, 36, 4, 1, outline);
    pixel.draw(88, 35, 5, 1, outline);
    pixel.draw(89, 36, 3, 1, outline);
    pixel.draw(78, 37, 5, 1, furShadow);
    pixel.draw(89, 37, 3, 1, furShadow);
    // Nose, mouth, cheek freckles and 1px whiskers are never antialiased.
    pixel.draw(97, 38, 3, 2, pink);
    pixel.draw(98, 40, 1, 2, outline);
    pixel.draw(96, 42, 2, 1, outline);
    pixel.draw(93, 42, 2, 1, outline);
    pixel.draw(94, 38, 1, 1, furShadow);
    pixel.draw(94, 40, 1, 1, furShadow);
    pixel.draw(98, 34, 5, 1, outline);
    pixel.draw(97, 36, 6, 1, outline);
    pixel.draw(99, 43, 4, 1, furShadow);
    pixel.draw(100, 45, 3, 1, outline);
    pixel.draw(76, 39, 3, 1, furShadow);
    pixel.draw(73, 42, 5, 1, furShadow);
  }

  @override
  bool shouldRepaint(PixelCatBodyPainter old) => false;
}

/// Three quantized tail poses, played 0 → 1 → 2 → 1 over 4.4 seconds.
/// The rest of the cat is in a separate RepaintBoundary.
class PixelCatTailPainter extends CustomPainter {
  const PixelCatTailPainter(this.frame);

  final int frame;

  @override
  void paint(Canvas canvas, Size size) {
    final pixel = _CatPixels(canvas, size);
    const outline = Color(0xff593a2d);
    const fur = Color(0xffd69a63);
    const furGold = Color(0xffedb67b);
    const stripe = Color(0xff865037);

    // Root tucks beneath the stationary hindquarters.
    pixel.draw(21, 37, 13, 10, outline);
    pixel.draw(21, 39, 13, 7, fur);
    pixel.draw(20, 41, 6, 3, stripe);
    if (frame == 0) {
      pixel.draw(12, 33, 14, 10, outline);
      pixel.draw(7, 27, 12, 11, outline);
      pixel.draw(5, 22, 9, 10, outline);
      pixel.draw(9, 31, 12, 6, fur);
      pixel.draw(8, 24, 6, 10, furGold);
      pixel.draw(7, 23, 2, 5, stripe);
      pixel.draw(11, 34, 3, 2, stripe);
    } else if (frame == 1) {
      pixel.draw(13, 30, 14, 13, outline);
      pixel.draw(8, 23, 13, 12, outline);
      pixel.draw(6, 17, 9, 11, outline);
      pixel.draw(10, 26, 12, 9, fur);
      pixel.draw(9, 19, 6, 10, furGold);
      pixel.draw(8, 18, 2, 5, stripe);
      pixel.draw(13, 30, 3, 2, stripe);
    } else {
      pixel.draw(14, 28, 13, 15, outline);
      pixel.draw(10, 18, 13, 15, outline);
      pixel.draw(7, 12, 10, 12, outline);
      pixel.draw(12, 22, 11, 10, fur);
      pixel.draw(10, 14, 7, 11, furGold);
      pixel.draw(9, 13, 2, 6, stripe);
      pixel.draw(16, 26, 3, 2, stripe);
    }
  }

  @override
  bool shouldRepaint(PixelCatTailPainter old) => old.frame != frame;
}

class _CatPixels {
  _CatPixels(this.canvas, this.size);

  final Canvas canvas;
  final Size size;
  final Paint _paint = Paint()..isAntiAlias = false;

  void draw(int x, int y, int width, int height, Color color) {
    _paint.color = color;
    canvas.drawRect(
      Rect.fromLTWH(
        x * size.width / PixelSleepingCat.pixelWidth,
        y * size.height / PixelSleepingCat.pixelHeight,
        width * size.width / PixelSleepingCat.pixelWidth,
        height * size.height / PixelSleepingCat.pixelHeight,
      ),
      _paint,
    );
  }
}
