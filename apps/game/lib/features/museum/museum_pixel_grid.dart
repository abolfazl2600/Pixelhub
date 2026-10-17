import 'package:flutter/material.dart';

/// Shared high-density pixel grid for all four museum rooms.
///
/// Artwork slots still use the historical 64×86 placement grid, and the
/// existing room illustration was authored at 128×172. Mapping every edge
/// separately to the new 180×240 grid preserves those compositions without
/// blurry, fractional rectangles. New fine details use [fine] directly.
final class MuseumPixelGrid {
  MuseumPixelGrid(this.canvas, this.size);

  static const int width = 180;
  static const int height = 240;
  static const int originalWidth = 128;
  static const int originalHeight = 172;

  final Canvas canvas;
  final Size size;
  final Paint _paint = Paint()..isAntiAlias = false;

  void legacy(int x, int y, int w, int h, Color color) {
    final left = (x * width / originalWidth).round();
    final top = (y * height / originalHeight).round();
    final right = ((x + w) * width / originalWidth).round();
    final bottom = ((y + h) * height / originalHeight).round();
    fine(left, top, right - left, bottom - top, color);
  }

  void fine(int x, int y, int w, int h, Color color) {
    if (w <= 0 || h <= 0) return;
    _paint.color = color;
    canvas.drawRect(
      Rect.fromLTWH(
        x * size.width / width,
        y * size.height / height,
        w * size.width / width,
        h * size.height / height,
      ),
      _paint,
    );
  }
}
