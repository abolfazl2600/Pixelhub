import 'package:flutter/material.dart';
import 'package:level_schema/level_schema.dart';

import '../l10n/strings.dart';
import '../features/painting/artwork_render_style.dart';

/// Read-only fixture rendering. No input, painting engine or progress in V1.
class PixelArtPreview extends StatelessWidget {
  const PixelArtPreview({required this.level, super.key});

  final LevelDefinition level;

  @override
  Widget build(BuildContext context) => Semantics(
    label: context.strings.previewLabel(
      level.titleFor(context.isPersian ? 'fa' : 'en'),
      context.digits(level.width),
      context.digits(level.height),
    ),
    image: true,
    child: AspectRatio(
      aspectRatio: level.width / level.height,
      child: CustomPaint(painter: _FixturePainter(level)),
    ),
  );
}

class _FixturePainter extends CustomPainter {
  _FixturePainter(this.level);

  final LevelDefinition level;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..isAntiAlias = false;
    for (var y = 0; y < level.height; y++) {
      for (var x = 0; x < level.width; x++) {
        paint.color = Color(level.palette[level.cells[y * level.width + x]]);
        canvas.drawRect(
          Rect.fromLTRB(
            x * size.width / level.width,
            y * size.height / level.height,
            (x + 1) * size.width / level.width,
            (y + 1) * size.height / level.height,
          ),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(_FixturePainter oldDelegate) => oldDelegate.level != level;
}
