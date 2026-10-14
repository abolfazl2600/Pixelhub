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

/// Deterministic, multi-layer linen weave for the optional Canvas look.
///
/// Every position is in *artwork coordinates*, including when the board pans
/// and zooms. Alternating raised threads, recess shadows and tiny irregular
/// fibers create a visible cloth surface on both light and dark pigments.
/// This only changes rendering: numbered cells, palette and saved progress
/// remain unchanged. A fixed thread pitch avoids expensive cell-wise textures
/// for large (up to 128×128) paintings and long online animations.
void paintCanvasTexture(
  Canvas canvas,
  Rect bounds, {
  required double cellWidth,
  required double cellHeight,
  double opacity = .24,
}) {
  if (bounds.isEmpty) return;
  // Thread density follows the display, not the level's pixel dimensions.
  // Keep the textile identifiable even on 64/128-grid finished paintings.
  const spacing = 6.0;
  final strength = opacity.clamp(0.0, 0.4).toDouble();

  final glaze = Paint()
    ..color = Color.fromRGBO(239, 224, 198, strength * .30);
  final threadShadow = Paint()
    ..isAntiAlias = false
    ..strokeWidth = .95
    ..color = Color.fromRGBO(78, 57, 38, strength * 1.22);
  final threadLight = Paint()
    ..isAntiAlias = false
    ..strokeWidth = .85
    ..color = Color.fromRGBO(255, 251, 230, strength * 1.48);
  final threadEdge = Paint()
    ..isAntiAlias = false
    ..strokeWidth = .42
    ..color = Color.fromRGBO(112, 82, 55, strength * .58);
  final raisedKnot = Paint()
    ..isAntiAlias = false
    ..color = Color.fromRGBO(255, 253, 239, strength * 1.30);
  final recessedKnot = Paint()
    ..isAntiAlias = false
    ..color = Color.fromRGBO(88, 68, 46, strength * .90);

  canvas.save();
  canvas.clipRect(bounds);
  canvas.drawRect(bounds, glaze);

  // A close pair of shade and light strokes makes every yarn visibly raised.
  // Opposing horizontal and vertical pairs interlock like woven cotton.
  final xStart = (bounds.left / spacing).floor();
  final xEnd = (bounds.right / spacing).ceil();
  final yStart = (bounds.top / spacing).floor();
  final yEnd = (bounds.bottom / spacing).ceil();

  for (var xi = xStart; xi <= xEnd; xi++) {
    final x = xi * spacing;
    canvas.drawLine(
      Offset(x + .45, bounds.top),
      Offset(x + .45, bounds.bottom),
      threadShadow,
    );
    canvas.drawLine(
      Offset(x + 1.6, bounds.top),
      Offset(x + 1.6, bounds.bottom),
      threadLight,
    );
    canvas.drawLine(
      Offset(x + 2.4, bounds.top),
      Offset(x + 2.4, bounds.bottom),
      threadEdge,
    );
  }
  for (var yi = yStart; yi <= yEnd; yi++) {
    final y = yi * spacing;
    canvas.drawLine(
      Offset(bounds.left, y + .45),
      Offset(bounds.right, y + .45),
      threadShadow,
    );
    canvas.drawLine(
      Offset(bounds.left, y + 1.6),
      Offset(bounds.right, y + 1.6),
      threadLight,
    );
    canvas.drawLine(
      Offset(bounds.left, y + 2.4),
      Offset(bounds.right, y + 2.4),
      threadEdge,
    );
  }

  // Intersections alternately catch light and recess into the fabric. Sparse,
  // asymmetric dashes prevent the texture looking like a plain square grid.
  for (var yi = yStart; yi <= yEnd; yi++) {
    final y = yi * spacing;
    for (var xi = xStart; xi <= xEnd; xi++) {
      final x = xi * spacing;
      if ((xi + yi).isEven) {
        canvas.drawRect(
          Rect.fromLTWH(x + .2, y + 1.1, 2.5, .95),
          raisedKnot,
        );
      } else {
        canvas.drawRect(
          Rect.fromLTWH(x + 1.15, y + .2, .95, 2.5),
          recessedKnot,
        );
      }
    }
  }
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
