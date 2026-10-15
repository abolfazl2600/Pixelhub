import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pixelhub/features/painting/diamond_gem_painter.dart';

void main() {
  test(
    'Diamonds have individual sockets, bright cut facets and palette colors',
    () async {
      final recorder = ui.PictureRecorder();
      final canvas = Canvas(recorder);
      canvas.drawColor(const Color(0xffe9edf4), BlendMode.src);
      paintDiamondGem(
        canvas,
        const Rect.fromLTWH(0, 0, 32, 32),
        const Color(0xffcb3232),
        column: 0,
        row: 0,
      );
      paintDiamondGem(
        canvas,
        const Rect.fromLTWH(32, 0, 32, 32),
        const Color(0xff32944c),
        column: 1,
        row: 0,
      );
      final picture = recorder.endRecording();
      final image = await picture.toImage(64, 32);
      final data = (await image.toByteData(
        format: ui.ImageByteFormat.rawRgba,
      ))!;
      int channel(int x, int y, int component) =>
          data.getUint8((y * 64 + x) * 4 + component);

      // Non-flat: the bead's center and raised upper facet differ from sockets.
      expect(channel(16, 16, 0), greaterThan(channel(2, 2, 0) + 60));
      expect(channel(14, 9, 0), greaterThan(channel(14, 26, 0)));
      expect(channel(48, 16, 1), greaterThan(channel(16, 16, 1)));
      // The mounts are separate, so no flat stripe joins two same-color cells.
      expect(channel(31, 16, 0), lessThan(channel(16, 16, 0)));
      expect(channel(32, 16, 1), lessThan(channel(48, 16, 1)));
      image.dispose();
      picture.dispose();
    },
  );

  test(
    'Diamond cut is deterministic and adds zoom detail to tiny cells',
    () async {
      Future<List<int>> pixels(double zoom) async {
        final recorder = ui.PictureRecorder();
        final canvas = Canvas(recorder);
        paintDiamondGem(
          canvas,
          const Rect.fromLTWH(0, 0, 4, 4),
          const Color(0xff8d63ae),
          column: 9,
          row: 7,
          zoomScale: zoom,
        );
        final picture = recorder.endRecording();
        final image = await picture.toImage(4, 4);
        final data = (await image.toByteData(
          format: ui.ImageByteFormat.rawRgba,
        ))!;
        final bytes = data.buffer.asUint8List().toList(growable: false);
        image.dispose();
        picture.dispose();
        return bytes;
      }

      final low = await pixels(1);
      final detailed = await pixels(6);
      expect(low, isNot(orderedEquals(detailed)));
      expect(await pixels(6), orderedEquals(detailed));
    },
  );

  test('Unfinished diamond socket does not color or fill the target', () async {
    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);
    canvas.drawColor(const Color(0xffe9edf4), BlendMode.src);
    paintDiamondSocket(canvas, const Rect.fromLTWH(0, 0, 30, 30));
    final picture = recorder.endRecording();
    final image = await picture.toImage(30, 30);
    final data = (await image.toByteData(format: ui.ImageByteFormat.rawRgba))!;
    final center = (15 * 30 + 15) * 4;
    expect(data.getUint8(center), 0xe9); // Number remains readable above it.
    image.dispose();
    picture.dispose();
  });
}
