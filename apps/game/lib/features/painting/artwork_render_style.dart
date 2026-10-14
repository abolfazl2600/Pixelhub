import 'dart:ui' as ui;

import 'package:flutter/material.dart';

/// Presentation-only styles. Never serialize this value into artwork JSON.
enum ArtworkRenderStyle {
  pixel('pixel'),
  canvas('canvas');

  const ArtworkRenderStyle(this.storageId);
  final String storageId;

  static ArtworkRenderStyle fromStorage(Object? value) =>
      value == 'canvas' ? ArtworkRenderStyle.canvas : ArtworkRenderStyle.pixel;
}

/// Shared, procedural canvas texture. Coordinates are artwork-space coordinates,
/// so the weave stays anchored when the board is panned or zoomed.
void paintCanvasTexture(
  Canvas canvas,
  Rect bounds, {
  required double cellWidth,
  required double cellHeight,
  double opacity = .04,
}) {
  if (bounds.isEmpty) return;
  final cellScale = ((cellWidth + cellHeight) / 56)
      .clamp(0.0, 1.0)
      .toDouble();
  final spacing = ui.lerpDouble(3.5, 7.0, cellScale)!
      .clamp(2.5, 7.0)
      .toDouble();
  final minor = Paint()
    ..isAntiAlias = false
    ..strokeWidth = .45
    ..color = Color.fromRGBO(83, 62, 39, opacity);
  final highlight = Paint()
    ..isAntiAlias = false
    ..strokeWidth = .35
    ..color = Color.fromRGBO(255, 255, 255, opacity * .75);
  canvas.save();
  canvas.clipRect(bounds);
  final firstX = (bounds.left / spacing).floor() * spacing;
  final firstY = (bounds.top / spacing).floor() * spacing;
  for (var x = firstX; x <= bounds.right; x += spacing) {
    canvas.drawLine(
      Offset(x, bounds.top),
      Offset(x, bounds.bottom),
      minor,
    );
    canvas.drawLine(
      Offset(x + spacing * .28, bounds.top),
      Offset(x + spacing * .28, bounds.bottom),
      highlight,
    );
  }
  for (var y = firstY; y <= bounds.bottom; y += spacing) {
    canvas.drawLine(
      Offset(bounds.left, y),
      Offset(bounds.right, y),
      minor,
    );
    canvas.drawLine(
      Offset(bounds.left, y + spacing * .28),
      Offset(bounds.right, y + spacing * .28),
      highlight,
    );
  }
  canvas.restore();
}

/// Registry makes adding future rendering looks independent of level data.
typedef ArtworkStylePainter = void Function(
  Canvas canvas,
  Rect bounds, {
  required double cellWidth,
  required double cellHeight,
});

final Map<ArtworkRenderStyle, ArtworkStylePainter> artworkStylePainters = {
  ArtworkRenderStyle.canvas: paintCanvasTexture,
};
