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
    child: AspectRatio(
      aspectRatio: level.width / level.height,
      child: CustomPaint(painter: _FixturePainter(level, renderStyle)),
    ),
  );
}

class _FixturePainter extends CustomPainter {
  _FixturePainter(this.level, this.renderStyle);

  final LevelDefinition level;
  final ArtworkRenderStyle renderStyle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..isAntiAlias = false;
    if (renderStyle == ArtworkRenderStyle.diamond) {
      canvas.drawRect(Offset.zero & size, Paint()..color = const Color(0xffe9edf4));
    }
    for (var y = 0; y < level.height; y++) {
      for (var x = 0; x < level.width; x++) {
        paint.color = Color(level.palette[level.cells[y * level.width + x]]);
        final rect = Rect.fromLTRB(
          x * size.width / level.width,
          y * size.height / level.height,
          (x + 1) * size.width / level.width,
          (y + 1) * size.height / level.height,
        );
        if (renderStyle == ArtworkRenderStyle.diamond) {
          paintDiamondGem(canvas, rect, paint.color, column: x, row: y);
        } else {
          canvas.drawRect(rect, paint);
        }
        if (renderStyle == ArtworkRenderStyle.canvas) {
          paintCanvasPigment(canvas, rect, column: x, row: y);
        }
      }
    }
    artworkStylePainters[renderStyle]?.call(
      canvas,
      Offset.zero & size,
      cellWidth: size.width / level.width,
      cellHeight: size.height / level.height,
    );
  }

  @override
  bool shouldRepaint(_FixturePainter oldDelegate) =>
      oldDelegate.level != level || oldDelegate.renderStyle != renderStyle;
}
