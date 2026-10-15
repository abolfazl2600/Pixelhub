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
    // Raster equivalent of the artwork-space pigment and broken linen weave.
    // Retain 1024px output and pure-Dart computation for isolate-safe export.
    const pitch = 6;
    final cellWidth = output.width ~/ level.width;
    final cellHeight = output.height ~/ level.height;
    for (var y = 0; y < output.height; y++) {
      final yi = y ~/ pitch;
      final h = y % pitch;
      for (var x = 0; x < output.width; x++) {
        final xi = x ~/ pitch;
        final v = x % pitch;
        final original = output.getPixel(x, y);
        var red = original.r.toDouble();
        var green = original.g.toDouble();
        var blue = original.b.toDouble();

        // Uneven, transparent brush traces remain inside the paint cell.
        if (cellWidth >= 9 && cellHeight >= 9) {
          final column = x ~/ cellWidth;
          final row = y ~/ cellHeight;
          final variation = ((column * 37 + row * 59) & 15) / 15.0;
          final u = (x % cellWidth) / cellWidth;
          final t = (y % cellHeight) / cellHeight;
          if (u >= .07 &&
              u < .61 + variation * .22 &&
              t >= .15 + variation * .16 &&
              t < .25 + variation * .16) {
            red = red * .867 + 255 * .133;
            green = green * .867 + 255 * .133;
            blue = blue * .867 + 255 * .133;
          }
          if (u >= .12 + variation * .10 &&
              u < .63 + variation * .31 &&
              t >= .58 + variation * .13 &&
              t < .655 + variation * .13) {
            red = red * .914 + 12 * .086;
            green = green * .914 + 19 * .086;
            blue = blue * .914 + 19 * .086;
          }
        }

        // A gentle warm fabric ground still shows through opaque pigment.
        red = red * .904 + 242 * .096;
        green = green * .904 + 230 * .096;
        blue = blue * .904 + 208 * .096;

        final over = (xi + yi).isEven;
        // Interlaced strands break at different positions instead of forming
        // the harsh uninterrupted grid of the old Canvas renderer.
        final shadow =
            (v == 0 && (over ? h <= 4 : h <= 5) ? .32 : 0.0) +
            (h == 0 && (over ? v <= 5 : v <= 4) ? .18 : 0.0);
        if (shadow > 0) {
          final factor = shadow.clamp(0.0, .48);
          red = red * (1 - factor) + 64 * factor;
          green = green * (1 - factor) + 47 * factor;
          blue = blue * (1 - factor) + 39 * factor;
        }

        final highlight =
            (v == 1 && (over ? h >= 1 && h <= 3 : h >= 3) ? .37 : 0.0) +
            (h == 1 && (over ? v >= 2 && v <= 5 : v >= 1 && v <= 3)
                ? .22
                : 0.0);
        if (highlight > 0) {
          final factor = highlight.clamp(0.0, .49);
          red = red * (1 - factor) + 255 * factor;
          green = green * (1 - factor) + 251 * factor;
          blue = blue * (1 - factor) + 231 * factor;
        }
        if (h == 3 && v >= 2 && v <= 4) {
          red = red * .96 + 110 * .04;
          green = green * .96 + 85 * .04;
          blue = blue * .96 + 66 * .04;
        }
        if (((xi * 73 + yi * 137) & 15).isEven && v == 3 && h == 3) {
          red = red * .81 + 255 * .19;
          green = green * .81 + 249 * .19;
          blue = blue * .81 + 229 * .19;
        }

        output.setPixelRgb(
          x,
          y,
          red.round().clamp(0, 255),
          green.round().clamp(0, 255),
          blue.round().clamp(0, 255),
        );
      }
    }
  }
  return img.encodePng(output);
}
