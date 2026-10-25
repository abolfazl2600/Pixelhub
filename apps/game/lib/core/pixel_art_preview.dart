import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:level_schema/level_schema.dart';

import '../l10n/strings.dart';
import '../features/painting/artwork_render_style.dart';
import '../features/painting/diamond_gem_painter.dart';

/// Read-only fixture rendering. No input, painting engine or progress in V1.
class PixelArtPreview extends StatelessWidget {
  const PixelArtPreview({
    required this.level,
    this.renderStyle = ArtworkRenderStyle.pixel,
    super.key,
  });

  final LevelDefinition level;
  final ArtworkRenderStyle renderStyle;

  @override
  Widget build(BuildContext context) => Semantics(
    label: context.strings.previewLabel(
      level.titleFor(context.isPersian ? 'fa' : 'en'),
      context.digits(level.width),
      context.digits(level.height),
    ),
    image: true,
    // Relax tight card constraints so the painted cells keep their shape.
    child: Center(
      child: AspectRatio(
        aspectRatio: level.width / level.height,
        child: CustomPaint(painter: _FixturePainter(level, renderStyle)),
      ),
    ),
  );
}

class _FixturePainter extends CustomPainter {
  _FixturePainter(this.level, this.renderStyle);

  final LevelDefinition level;
  final ArtworkRenderStyle renderStyle;

  @override
  void paint(Canvas canvas, Size size) {
    // Fit uniformly even if a parent gives us a wide or tall canvas.
    // Both edges of each pixel must always have the same length.
    final cellSize = math.min(
      size.width / level.width,
      size.height / level.height,
    );
    if (!cellSize.isFinite || cellSize <= 0) return;

    final artworkSize = Size(cellSize * level.width, cellSize * level.height);
    canvas.save();
    canvas.translate(
      (size.width - artworkSize.width) / 2,
      (size.height - artworkSize.height) / 2,
    );

    final paint = Paint()..isAntiAlias = false;
    if (renderStyle == ArtworkRenderStyle.diamond) {
      canvas.drawRect(
        Offset.zero & artworkSize,
        Paint()..color = const Color(0xffe9edf4),
      );
    }
    for (var y = 0; y < level.height; y++) {
      for (var x = 0; x < level.width; x++) {
        paint.color = Color(level.palette[level.cells[y * level.width + x]]);
        final rect = Rect.fromLTWH(
          x * cellSize,
          y * cellSize,
          cellSize,
          cellSize,
        );
        if (renderStyle == ArtworkRenderStyle.diamond) {
          paintDiamondGem(canvas, rect, paint.color, column: x, row: y);
        } else {
          canvas.drawRect(rect, paint);
        }
      }
    }
    artworkStylePainters[renderStyle]?.call(
      canvas,
      Offset.zero & artworkSize,
      cellWidth: cellSize,
      cellHeight: cellSize,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(_FixturePainter oldDelegate) =>
      oldDelegate.level != level || oldDelegate.renderStyle != renderStyle;
}
