import 'dart:async';

import 'package:flutter/material.dart';

/// An independent 52 × 28 pixel sprite. The room and the sleeping body stay
/// static; only the tail layer changes on a slow, four-step loop.
class PixelSleepingCat extends StatefulWidget {
  const PixelSleepingCat({super.key});

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

/// The fur, sleeping expression, ears and paws never repaint with the tail.
class PixelCatBodyPainter extends CustomPainter {
  const PixelCatBodyPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final pixel = _CatPixels(canvas, size);
    const ink = Color(0xff654434);
    const shadow = Color(0xffa66a48);
    const body = Color(0xffd9a474);
    const cream = Color(0xfff5d4a0);
    const light = Color(0xffffe7bc);
    const pink = Color(0xffc47e7d);

    // Curled back, chest and belly: a small but readable sleeping silhouette.
    pixel.draw(13, 12, 24, 11, ink);
    pixel.draw(17, 9, 17, 6, ink);
    pixel.draw(11, 15, 30, 8, ink);
    pixel.draw(13, 13, 25, 9, body);
    pixel.draw(18, 10, 15, 7, body);
    pixel.draw(13, 17, 25, 5, cream);
    pixel.draw(16, 12, 15, 2, light);
    pixel.draw(18, 15, 5, 2, shadow);
    pixel.draw(25, 11, 2, 3, shadow);
    pixel.draw(31, 13, 2, 4, shadow);
    pixel.draw(17, 19, 8, 2, light);
    pixel.draw(20, 21, 12, 2, shadow);

    // Two small folded paws beneath the muzzle, with separated toes.
    pixel.draw(29, 21, 13, 4, ink);
    pixel.draw(30, 21, 5, 3, cream);
    pixel.draw(36, 21, 5, 3, cream);
    pixel.draw(34, 22, 1, 2, shadow);
    pixel.draw(39, 22, 1, 2, shadow);

    // Both ears and a distinct round head; nose faces to the right.
    pixel.draw(33, 9, 16, 14, ink);
    pixel.draw(34, 7, 5, 6, ink);
    pixel.draw(43, 6, 5, 7, ink);
    pixel.draw(35, 8, 3, 5, cream);
    pixel.draw(44, 7, 3, 6, cream);
    pixel.draw(36, 10, 2, 3, pink);
    pixel.draw(45, 9, 1, 3, pink);
    pixel.draw(34, 11, 13, 10, body);
    pixel.draw(36, 12, 10, 7, cream);
    pixel.draw(39, 18, 8, 3, light);
    pixel.draw(44, 17, 4, 3, light);

    // Closed eyes, small nose, tiny mouth and fine, stepped whiskers.
    pixel.draw(36, 15, 5, 1, ink);
    pixel.draw(42, 15, 3, 1, ink);
    pixel.draw(37, 16, 3, 1, shadow);
    pixel.draw(43, 16, 1, 1, shadow);
    pixel.draw(46, 18, 2, 2, pink);
    pixel.draw(45, 20, 1, 1, ink);
    pixel.draw(43, 21, 2, 1, ink);
    pixel.draw(48, 19, 3, 1, ink);
    pixel.draw(48, 21, 3, 1, ink);
    pixel.draw(46, 22, 3, 1, shadow);
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
    const ink = Color(0xff654434);
    const fur = Color(0xffd9a474);
    const light = Color(0xfff5d4a0);

    // The root is tucked under the resting body; the tip sways a few pixels.
    pixel.draw(10, 17, 8, 6, ink);
    pixel.draw(10, 18, 8, 4, fur);
    if (frame == 0) {
      pixel.draw(6, 17, 7, 5, ink);
      pixel.draw(3, 14, 6, 6, ink);
      pixel.draw(2, 11, 5, 5, ink);
      pixel.draw(4, 15, 4, 4, fur);
      pixel.draw(3, 12, 3, 4, light);
    } else if (frame == 1) {
      pixel.draw(6, 15, 7, 7, ink);
      pixel.draw(3, 12, 6, 6, ink);
      pixel.draw(2, 9, 5, 5, ink);
      pixel.draw(5, 16, 4, 4, fur);
      pixel.draw(3, 10, 3, 4, light);
    } else {
      pixel.draw(7, 14, 6, 7, ink);
      pixel.draw(4, 9, 6, 7, ink);
      pixel.draw(3, 6, 5, 5, ink);
      pixel.draw(5, 12, 4, 5, fur);
      pixel.draw(4, 7, 3, 4, light);
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
        x * size.width / 52,
        y * size.height / 28,
        width * size.width / 52,
        height * size.height / 28,
      ),
      _paint,
    );
  }
}
