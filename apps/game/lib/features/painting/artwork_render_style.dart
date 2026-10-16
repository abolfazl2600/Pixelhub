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

/// Over-under spun yarn with rounded strands, contact shadows and fine
/// diagonal fiber ribs. Every pattern is anchored in artwork coordinates,
/// so zooming and panning never slide the texture across the painted cells.
///
/// Batched paths keep draw calls small, and the caller clips to painted cells.
/// No images, shaders or per-cell texture assets are required.
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
  final underFibers = Path();
  final overFibers = Path();
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

      // The short bow at each crossing lets the top strand visibly pass
      // *over* the lower strand, instead of resembling a flat checkerboard.
      final warp = Path()
        ..moveTo(cx, y)
        ..quadraticBezierTo(
          cx + pitch * (warpOver ? -.11 : .11),
          cy,
          cx,
          y + pitch,
        );
      final weft = Path()
        ..moveTo(x, cy)
        ..quadraticBezierTo(
          cx,
          cy + pitch * (warpOver ? .11 : -.11),
          x + pitch,
          cy,
        );
      under.addPath(warpOver ? weft : warp, Offset.zero);
      over.addPath(warpOver ? warp : weft, Offset.zero);

      // Three small angled slubs per strand suggest the twist and individual
      // fibers of spun cotton. Deterministic offsets break perfect repetition.
      // Lower fibers are painted before the raised strand occludes them.
      for (var turn = 0; turn < 3; turn++) {
        final jitter = (((xi * 13 + yi * 7 + turn * 5) & 7) - 3.5) * .005;
        final at = -.28 + turn * .28 + jitter;
        if (warpOver) {
          overFibers
            ..moveTo(cx - pitch * .17, cy + pitch * (at - .075))
            ..quadraticBezierTo(
              cx,
              cy + pitch * at,
              cx + pitch * .17,
              cy + pitch * (at + .075),
            );
          underFibers
            ..moveTo(cx + pitch * (at - .075), cy - pitch * .17)
            ..quadraticBezierTo(
              cx + pitch * at,
              cy,
              cx + pitch * (at + .075),
              cy + pitch * .17,
            );
        } else {
          overFibers
            ..moveTo(cx + pitch * (at - .075), cy - pitch * .17)
            ..quadraticBezierTo(
              cx + pitch * at,
              cy,
              cx + pitch * (at + .075),
              cy + pitch * .17,
            );
          underFibers
            ..moveTo(cx - pitch * .17, cy + pitch * (at - .075))
            ..quadraticBezierTo(
              cx,
              cy + pitch * at,
              cx + pitch * .17,
              cy + pitch * (at + .075),
            );
        }
      }
    }
  }

  void stroke(Path path, double fraction, Color color) {
    canvas.drawPath(
      path,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = fraction * pitch
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..isAntiAlias = true
        ..color = color,
    );
  }

  canvas.save();
  canvas.clipRect(bounds);
  // Pigment remains visible through the recesses and both yarn directions.
  canvas.drawRect(
    bounds,
    Paint()..color = Color.fromRGBO(24, 26, 32, .10 * strength),
  );

  // Each yarn casts a narrow displaced shadow underneath its curved body.
  canvas.save();
  canvas.translate(pitch * .04, pitch * .05);
  stroke(under, .68, Color.fromRGBO(18, 21, 29, .33 * strength));
  canvas.restore();
  stroke(under, .55, Color.fromRGBO(28, 30, 38, .19 * strength));
  stroke(under, .44, Color.fromRGBO(227, 222, 213, .14 * strength));
  stroke(under, .29, Color.fromRGBO(250, 248, 239, .16 * strength));
  stroke(under, .11, Color.fromRGBO(255, 253, 246, .23 * strength));
  stroke(underFibers, .08, Color.fromRGBO(31, 33, 39, .20 * strength));
  canvas.save();
  canvas.translate(-pitch * .018, -pitch * .018);
  stroke(underFibers, .035, Color.fromRGBO(255, 253, 245, .20 * strength));
  canvas.restore();

  // The upper strand has a stronger silhouette and a soft, matte highlight.
  canvas.save();
  canvas.translate(pitch * .045, pitch * .055);
  stroke(over, .72, Color.fromRGBO(15, 18, 27, .41 * strength));
  canvas.restore();
  stroke(over, .59, Color.fromRGBO(24, 27, 34, .25 * strength));
  stroke(over, .46, Color.fromRGBO(228, 226, 218, .17 * strength));
  stroke(over, .31, Color.fromRGBO(247, 247, 240, .26 * strength));
  stroke(over, .13, Color.fromRGBO(255, 255, 248, .49 * strength));
  stroke(overFibers, .095, Color.fromRGBO(31, 34, 38, .28 * strength));
  canvas.save();
  canvas.translate(-pitch * .018, -pitch * .018);
  stroke(overFibers, .04, Color.fromRGBO(255, 253, 245, .37 * strength));
  canvas.restore();
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
