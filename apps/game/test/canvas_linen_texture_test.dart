import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';

void main() {
  test('Canvas weave is visible over both pale and deep paint', () async {
    const width = 120;
    const height = 120;
    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);
    canvas.drawRect(
      const Rect.fromLTWH(0, 0, 60, 120),
      Paint()..color = const Color(0xffebded0),
    );
    canvas.drawRect(
      const Rect.fromLTWH(60, 0, 60, 120),
      Paint()..color = const Color(0xff34435d),
    );

    paintCanvasTexture(
      canvas,
      const Rect.fromLTWH(0, 0, width, height),
      cellWidth: 6,
      cellHeight: 6,
    );
    final picture = recorder.endRecording();
    final image = await picture.toImage(width, height);
    final pixels = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    expect(pixels, isNotNull);

    int red(int x, int y) => pixels!.getUint8((y * width + x) * 4);
    // Adjacent shadowed yarns and raised highlights must be visible.
    expect(red(31, 61) - red(30, 60), greaterThan(30));
    expect(red(91, 61) - red(90, 60), greaterThan(30));
    // In each color region the cloth should be more than faint 4%-opacity
    // strokes; the difference is obvious at standard mobile preview scale.
    expect(red(30, 60), isNot(red(31, 61)));
    expect(red(90, 60), isNot(red(91, 61)));

    image.dispose();
    picture.dispose();
  });
}
