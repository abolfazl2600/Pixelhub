import 'package:flutter/material.dart';

import 'woven_thread_pattern.dart';

/// Presentation-only styles. Never serialize this value into artwork JSON.
enum ArtworkRenderStyle {
  pixel('pixel'),
  canvas('canvas'),
  diamond('diamond');

  const ArtworkRenderStyle(this.storageId);
  final String storageId;

  static ArtworkRenderStyle fromStorage(Object? value) => switch (value) {
    'canvas' => ArtworkRenderStyle.canvas,
    'diamond' => ArtworkRenderStyle.diamond,
    _ => ArtworkRenderStyle.pixel,
  };
}

/// A true over-under fabric: horizontal and vertical rounded yarns alternate
/// at every crossing, including raised cores, cast shadows and edge highlights.
///
/// The grid is anchored in artwork space, so translations do not change its
/// pattern. Path batches keep rendering cost independent of artwork cell count.
/// Clip the live painter to *completed* cells before calling this function.
void paintCanvasTexture(
  Canvas canvas,
  Rect bounds, {
  required double cellWidth,
  required double cellHeight,
  double opacity = .9,
}) {
  if (bounds.isEmpty || opacity <= 0) return;
  final pitch = wovenThreadPitch(cellWidth, cellHeight);
  final strength = opacity.clamp(0.0, 1.0).toDouble();
  final under = Path();
  final over = Path();
  final ends = Path();
  final minX = (bounds.left / pitch).floor() - 1;
  final maxX = (bounds.right / pitch).ceil() + 1;
  final minY = (bounds.top / pitch).floor() - 1;
  final maxY = (bounds.bottom / pitch).ceil() + 1;

  for (var yi = minY; yi <= maxY; yi++) {
    final y = yi * pitch;
    final cy = y + pitch * .5;
    for (var xi = minX; xi <= maxX; xi++) {
      final x = xi * pitch;
      final cx = x + pitch * .5;
      final warpOver = (xi + yi).isEven;
      final vertical = Path()
        ..moveTo(cx, y)
        ..quadraticBezierTo(
          cx + pitch * (warpOver ? -.11 : .11),
          cy,
          cx,
          y + pitch,
        );
      final horizontal = Path()
        ..moveTo(x, cy)
        ..quadraticBezierTo(
          cx,
          cy + pitch * (warpOver ? .11 : -.11),
          x + pitch,
          cy,
        );
      under.addPath(warpOver ? horizontal : vertical, Offset.zero);
      over.addPath(warpOver ? vertical : horizontal, Offset.zero);

      // Subtle twist fibers interrupt the otherwise perfectly smooth yarn.
      if (((xi * 31 + yi * 17) & 3) == 0) {
        ends
          ..moveTo(cx - pitch * .11, cy - pitch * .06)
          ..lineTo(cx + pitch * .08, cy + pitch * .065);
      }
    }
  }

  void stroke(Path path, double width, Color color) {
    canvas.drawPath(
      path,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = width * pitch
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..isAntiAlias = true
        ..color = color,
    );
  }

  canvas.save();
  canvas.clipRect(bounds);
  // Dark gaps are visible between yarns but do not replace the palette color.
  canvas.drawRect(
    bounds,
    Paint()..color = Color.fromRGBO(20, 25, 30, .08 * strength),
  );
  stroke(under, .53, Color.fromRGBO(21, 23, 31, .31 * strength));
  stroke(under, .38, Color.fromRGBO(225, 227, 225, .13 * strength));
  stroke(under, .12, Color.fromRGBO(255, 255, 252, .25 * strength));
  // Overlying yarn receives a stronger cast shadow and cylindrical highlight.
  stroke(over, .58, Color.fromRGBO(17, 21, 28, .40 * strength));
  stroke(over, .43, Color.fromRGBO(224, 228, 230, .17 * strength));
  stroke(over, .16, Color.fromRGBO(255, 255, 250, .52 * strength));
  stroke(ends, .045, Color.fromRGBO(255, 252, 245, .28 * strength));
  canvas.restore();
}

/// Registry makes adding future rendering looks independent of level data.
typedef ArtworkStylePainter =
    void Function(
      Canvas canvas,
      Rect bounds, {
      required double cellWidth,
      required double cellHeight,
    });

final Map<ArtworkRenderStyle, ArtworkStylePainter> artworkStylePainters = {
  ArtworkRenderStyle.canvas: paintCanvasTexture,
};
