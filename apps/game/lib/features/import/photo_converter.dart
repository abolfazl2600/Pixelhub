import 'dart:math' as math;
import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';

const maxPhotoBytes = 12 * 1024 * 1024;

final class NormalizedPhoto {
  const NormalizedPhoto(this.bytes, this.width, this.height);
  final Uint8List bytes;
  final int width;
  final int height;
}

/// Check encoded dimensions before allocating a full frame. Only still images
/// in supported formats are accepted; all metadata is stripped on re-encoding.
NormalizedPhoto normalizePhoto(Uint8List bytes) {
  if (bytes.isEmpty || bytes.length > maxPhotoBytes) {
    throw const FormatException('photoTooLarge');
  }
  try {
    final img.Decoder decoder = switch (img.findDecoderForData(bytes)) {
      img.JpegDecoder decoder => decoder,
      img.PngDecoder decoder => decoder,
      img.WebPDecoder decoder => decoder,
      _ => throw const FormatException('photoUnsupported'),
    };
    final info = decoder.startDecode(bytes);
    if (info == null || info.width < 1 || info.height < 1) {
      throw const FormatException('photoUnsupported');
    }
    if (info.width > 6000 ||
        info.height > 6000 ||
        info.width * info.height > 12000000) {
      throw const FormatException('photoTooLarge');
    }
    if (info.numFrames > 1 || (info is img.WebPInfo && info.hasAnimation)) {
      throw const FormatException('photoAnimated');
    }
    final decoded = decoder.decodeFrame(0);
    if (decoded == null) {
      throw const FormatException('photoUnsupported');
    }
    var source = img.bakeOrientation(decoded);
    source = source.convert(format: img.Format.uint8, numChannels: 4);
    if (math.max(source.width, source.height) > 1024) {
      final scale = 1024 / math.max(source.width, source.height);
      source = img.copyResize(
        source,
        width: math.max(1, (source.width * scale).round()),
        height: math.max(1, (source.height * scale).round()),
        interpolation: img.Interpolation.average,
      );
    }
    // Fresh RGB canvas drops EXIF/GPS/ICC and composites transparent pixels.
    final clean = img.Image(
      width: source.width,
      height: source.height,
      numChannels: 3,
    );
    for (final pixel in source) {
      final alpha = pixel.a.toDouble() / pixel.maxChannelValue;
      clean.setPixelRgb(
        pixel.x,
        pixel.y,
        (pixel.r * alpha + 255 * (1 - alpha)).round(),
        (pixel.g * alpha + 255 * (1 - alpha)).round(),
        (pixel.b * alpha + 255 * (1 - alpha)).round(),
      );
    }
    return NormalizedPhoto(img.encodePng(clean), clean.width, clean.height);
  } on FormatException {
    rethrow;
  } on Object {
    throw const FormatException('photoUnsupported');
  }
}

/// Shared deterministic median-cut converter. Native compute runs in an
/// isolate; Web compute runs locally after the UI has displayed its busy state.
Map<String, Object> convertPhoto(Map<String, Object> request) {
  final bytes = request['bytes']! as Uint8List;
  var source = img.decodePng(bytes);
  if (source == null) {
    throw const FormatException('photoUnsupported');
  }
  final turns = request['quarterTurns']! as int;
  if (turns != 0) source = img.copyRotate(source, angle: turns * 90);
  final side = math.min(source.width, source.height);
  final crop = img.copyCrop(
    source,
    x: ((source.width - side) * (request['cropX']! as double)).round(),
    y: ((source.height - side) * (request['cropY']! as double)).round(),
    width: side,
    height: side,
  );
  final size = request['size']! as int;
  final count = request['colorLimit']! as int;
  if (![32, 64, 128].contains(size) || count < 2 || count > 24) {
    throw const FormatException('Invalid conversion settings.');
  }
  final pixels = img.copyResize(
    crop,
    width: size,
    height: size,
    interpolation: img.Interpolation.average,
  );
  // Histogram limits work to 32K RGB buckets, without dithering numbered cells.
  final histogram = <int, _Bucket>{};
  for (final pixel in pixels) {
    final r = pixel.r.toInt(), g = pixel.g.toInt(), b = pixel.b.toInt();
    final key = ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3);
    (histogram[key] ??= _Bucket()).add(r, g, b);
  }
  final boxes = <List<_Bucket>>[histogram.values.toList()];
  while (boxes.length < count) {
    var chosen = -1, score = -1;
    for (var i = 0; i < boxes.length; i++) {
      if (boxes[i].length < 2) continue;
      final candidate =
          _spread(boxes[i]).$2 *
          boxes[i].fold<int>(0, (n, bucket) => n + bucket.count);
      if (candidate > score) {
        chosen = i;
        score = candidate;
      }
    }
    if (chosen < 0) break;
    final box = boxes.removeAt(chosen);
    final channel = _spread(box).$1;
    box.sort((a, b) => a.channel(channel).compareTo(b.channel(channel)));
    final half = box.fold(0, (n, bucket) => n + bucket.count) / 2;
    var accumulated = 0, split = 1;
    for (var i = 0; i < box.length - 1; i++) {
      accumulated += box[i].count;
      split = i + 1;
      if (accumulated >= half) break;
    }
    boxes.add(box.sublist(0, split));
    boxes.add(box.sublist(split));
  }
  final palette =
      boxes
          .map((box) {
            final total = box.fold(0, (n, b) => n + b.count);
            final r = (box.fold(0, (n, b) => n + b.r) / total).round();
            final g = (box.fold(0, (n, b) => n + b.g) / total).round();
            final b = (box.fold(0, (n, b) => n + b.b) / total).round();
            return 0xff000000 | (r << 16) | (g << 8) | b;
          })
          .toSet()
          .toList()
        ..sort();
  final cells = <int>[];
  for (final pixel in pixels) {
    var closest = 0, distance = double.infinity;
    for (var i = 0; i < palette.length; i++) {
      final r = pixel.r.toDouble() - ((palette[i] >> 16) & 255);
      final g = pixel.g.toDouble() - ((palette[i] >> 8) & 255);
      final b = pixel.b.toDouble() - (palette[i] & 255);
      final delta = r * r + g * g + b * b;
      if (delta < distance) {
        distance = delta;
        closest = i;
      }
    }
    cells.add(closest);
  }
  // Remove unused palette entries after nearest-color assignment.
  final used = cells.toSet().toList()..sort();
  return LevelDefinition(
    id: request['id']! as String,
    title: request['title']! as String,
    titleEn: request['titleEn']! as String,
    schemaVersion: LevelAssets.currentSchemaVersion,
    contentVersion: 1,
    width: size,
    height: size,
    palette: used.map((i) => palette[i]).toList(),
    cells: cells.map((i) => used.indexOf(i)).toList(),
  ).toJson();
}

final class _Bucket {
  int count = 0, r = 0, g = 0, b = 0;
  void add(int red, int green, int blue) {
    count++;
    r += red;
    g += green;
    b += blue;
  }

  int channel(int index) => ([r, g, b][index] / count).round();
}

(int, int) _spread(List<_Bucket> box) {
  var channel = 0, widest = -1;
  for (var i = 0; i < 3; i++) {
    var low = 255, high = 0;
    for (final bucket in box) {
      low = math.min(low, bucket.channel(i));
      high = math.max(high, bucket.channel(i));
    }
    if (high - low > widest) {
      widest = high - low;
      channel = i;
    }
  }
  return (channel, widest);
}

Uint8List renderLevelPng(Map<String, Object> source) {
  final style = source['renderStyle'] == 'canvas' ? 'canvas' : 'pixel';
  final levelJson = Map<String, Object>.from(source)..remove('renderStyle');
  final level = LevelDefinition.fromJson(levelJson);
  final image = img.Image(
    width: level.width,
    height: level.height,
    numChannels: 3,
  );
  for (var y = 0; y < level.height; y++) {
    for (var x = 0; x < level.width; x++) {
      final color = level.palette[level.cells[y * level.width + x]];
      image.setPixelRgb(
        x,
        y,
        (color >> 16) & 255,
        (color >> 8) & 255,
        color & 255,
      );
    }
  }
  final scale = 1024 ~/ math.max(level.width, level.height);
  final output = img.copyResize(
    image,
    width: level.width * scale,
    height: level.height * scale,
    interpolation: img.Interpolation.nearest,
  );
  if (style == 'canvas') {
    // A deterministic low-opacity weave, scaled to the final PNG and anchored
    // to the image origin. Pixel mode remains byte-for-byte legacy rendering.
    final step = math.max(5, scale ~/ 2);
    for (var y = 0; y < output.height; y++) {
      for (var x = 0; x < output.width; x++) {
        final vertical = x % step == 0;
        final horizontal = y % step == 0;
        if (!vertical && !horizontal) continue;
        final pixel = output.getPixel(x, y);
        final alpha = vertical && horizontal ? .10 : .055;
        output.setPixelRgb(
          x,
          y,
          (pixel.r.toDouble() * (1 - alpha) + 91 * alpha).round(),
          (pixel.g.toDouble() * (1 - alpha) + 69 * alpha).round(),
          (pixel.b.toDouble() * (1 - alpha) + 44 * alpha).round(),
        );
      }
    }
  }
  return img.encodePng(output);
}
