import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';
import 'package:pixelhub/features/painting/woven_thread_pattern.dart';

Future<ByteData> renderFabric() async {
  const width = 126;
  const height = 126;
  final recorder = ui.PictureRecorder();
  final canvas = Canvas(recorder);
  canvas.drawRect(
    const Rect.fromLTWH(0, 0, 63, 126),
    Paint()..color = const Color(0xffebded0),
  );
  canvas.drawRect(
    const Rect.fromLTWH(63, 0, 63, 126),
    Paint()..color = const Color(0xff34435d),
  );
  paintCanvasTexture(
    canvas,
    const Rect.fromLTWH(0, 0, 126, 122),
    cellWidth: 20,
    cellHeight: 20,
  );
  final picture = recorder.endRecording();
  final image = await picture.toImage(width, height);
  final data = (await image.toByteData(format: ui.ImageByteFormat.rawRgba))!;
  image.dispose();
  picture.dispose();
  return data;
}

void main() {
  test('yarn alternates top thread at every crossing and has shaded edges', () {
    const pitch = 12.0;
    final top = wovenThreadLighting(6, 6, pitch);
    final gap = wovenThreadLighting(1, 1, pitch);
    expect(top.lift, greaterThan(gap.lift));
    expect(shadeWovenChannel(70, top), greaterThan(shadeWovenChannel(70, gap)));
    expect(
      shadeWovenChannel(230, top),
      greaterThan(shadeWovenChannel(230, gap)),
    );
    // At alternate tile intersections the direction of the raised strand
    // flips: a point near the warp remains bright only on even crossings.
    final evenWarp = wovenThreadLighting(6, 3, pitch);
    final oddWarp = wovenThreadLighting(18, 3, pitch);
    expect(evenWarp, isNot(oddWarp));
    expect(wovenThreadPitch(2, 2), 6);
    expect(wovenThreadPitch(50, 50), 12);
    expect(shadeWovenChannel(255, top), lessThanOrEqualTo(255));
  });

  test(
    'raised yarn is visible on pale and dark pigment, with no overflow',
    () async {
      final pixels = await renderFabric();
      int red(int x, int y) => pixels.getUint8((y * 126 + x) * 4);
      // Measure several warp/weft crossings instead of assuming a strand
      // center always lands on one device pixel after anti-aliasing.
      int contrast(int x0, int x1) {
        var darkest = 255;
        var lightest = 0;
        for (var y = 2; y < 40; y += 2) {
          for (var x = x0; x < x1; x += 2) {
            final value = red(x, y);
            if (value < darkest) darkest = value;
            if (value > lightest) lightest = value;
          }
        }
        return lightest - darkest;
      }

      expect(contrast(2, 60), greaterThan(25));
      expect(contrast(68, 123), greaterThan(18));
      // Drawing is confined to its rectangle. The bottom rows are untouched.
      expect(red(22, 124), 0xeb);
      expect(red(100, 124), 0x34);
      final again = await renderFabric();
      expect(
        again.buffer.asUint8List(),
        orderedEquals(pixels.buffer.asUint8List()),
      );
    },
  );
}
