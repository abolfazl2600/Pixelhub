import 'package:flutter/material.dart';

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

/// An artwork-space woven linen surface, intentionally different from the
/// perfectly flat Pixel style. Broken strands and alternating crossings give
/// the colored pigment the appearance of sitting on absorbent fabric.
///
/// Drawing cost depends on visible surface area, NOT on the number of artwork
/// cells (which may be 128x128). All marks have deterministic coordinates so
/// zooming, panning and moving between still/animated views do not flicker.
/// No image assets, randomness or saved artwork changes are required.
void paintCanvasTexture(
  Canvas canvas,
  Rect bounds, {
  required double cellWidth,
  required double cellHeight,
  double opacity = .30,
}) {
  if (bounds.isEmpty || opacity <= 0) return;
  const pitch = 6.0;
  final strength = opacity.clamp(0.0, .4).toDouble();
  final shadowFibers = Path();
  final raisedFibers = Path();
  final fineFibers = Path();
  final grain = Path();
  final xStart = (bounds.left / pitch).floor() - 1;
  final xEnd = (bounds.right / pitch).ceil();
  final yStart = (bounds.top / pitch).floor() - 1;
  final yEnd = (bounds.bottom / pitch).ceil();

  // Draw discontinuous strands instead of uninterrupted vertical/horizontal
  // grid lines. Short woven segments alternate which thread goes over.
  for (var yi = yStart; yi <= yEnd; yi++) {
    final y = yi * pitch;
    for (var xi = xStart; xi <= xEnd; xi++) {
      final x = xi * pitch;
      final seed = (xi * 73 + yi * 137) & 15;
      final shift = (seed - 7) * .065;
      final over = (xi + yi).isEven;

      shadowFibers
        ..moveTo(x + .46 + shift, y + .3)
        ..lineTo(x + .46 + shift, y + (over ? 4.8 : 5.55))
        ..moveTo(x + .25, y + .46 - shift)
        ..lineTo(x + (over ? 5.55 : 4.75), y + .46 - shift);
      raisedFibers
        ..moveTo(x + 1.48 + shift, y + (over ? .7 : 2.55))
        ..lineTo(x + 1.48 + shift, y + (over ? 3.85 : 5.25))
        ..moveTo(x + (over ? 2.35 : .75), y + 1.45 - shift)
        ..lineTo(x + (over ? 5.2 : 3.8), y + 1.45 - shift);
      fineFibers
        ..moveTo(x + 2.35, y + 3.15 + shift)
        ..lineTo(x + 4.5, y + 3.15 + shift);
      // Small slubs resemble paint catching the high points of real linen.
      if (seed.isEven) {
        grain.addOval(Rect.fromLTWH(x + 2.65 + shift, y + 2.85, 1.1, .7));
      }
    }
  }

  canvas.save();
  canvas.clipRect(bounds);
  canvas.drawRect(
    bounds,
    Paint()..color = Color.fromRGBO(242, 230, 208, strength * .32),
  );
  canvas.drawPath(
    shadowFibers,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = .9
      ..isAntiAlias = false
      ..color = Color.fromRGBO(64, 47, 39, strength * 1.08),
  );
  canvas.drawPath(
    raisedFibers,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = .95
      ..isAntiAlias = false
      ..color = Color.fromRGBO(255, 251, 231, strength * 1.22),
  );
  canvas.drawPath(
    fineFibers,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = .55
      ..isAntiAlias = false
      ..color = Color.fromRGBO(110, 85, 66, strength * .44),
  );
  canvas.drawPath(
    grain,
    Paint()..color = Color.fromRGBO(255, 249, 229, strength * .63),
  );
  canvas.restore();
}

/// Translucent, slightly uneven pigment strokes on *completed* cells.
/// The underlying palette color remains accurate and the strokes stay within
/// that cell. Omit these details on dense grids where they would become
/// expensive and visually noisy; the weave remains visible on those grids.
void paintCanvasPigment(
  Canvas canvas,
  Rect rect, {
  required int column,
  required int row,
}) {
  final w = rect.width, h = rect.height;
  if (w < 9 || h < 9) return;
  final variation = ((column * 37 + row * 59) & 15) / 15.0;
  final top = rect.top + h * (.15 + variation * .16);
  final bottom = rect.top + h * (.58 + variation * .13);

  canvas.save();
  canvas.clipRect(rect);
  canvas.drawRRect(
    RRect.fromRectAndRadius(
      Rect.fromLTWH(
        rect.left + w * .07,
        top,
        w * (.54 + variation * .22),
        h * .10,
      ),
      Radius.circular(h * .045),
    ),
    Paint()..color = const Color(0x22ffffff),
  );
  canvas.drawRRect(
    RRect.fromRectAndRadius(
      Rect.fromLTWH(
        rect.left + w * (.12 + variation * .10),
        bottom,
        w * (.51 + variation * .21),
        h * .075,
      ),
      Radius.circular(h * .037),
    ),
    Paint()..color = const Color(0x160c1313),
  );
  // Irregular dry-brush granulation on the high points of the weave.
  canvas.drawOval(
    Rect.fromLTWH(
      rect.left + w * (.54 + variation * .12),
      rect.top + h * .42,
      w * .09,
      h * .055,
    ),
    Paint()..color = const Color(0x27ffffff),
  );
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
