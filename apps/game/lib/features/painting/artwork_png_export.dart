import 'dart:math' as math;
import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';

import '../import/diamond_photo_renderer.dart';
import 'woven_thread_pattern.dart';

/// Pure-Dart PNG renderers, safe to run with compute() on Android and Web.
///
/// Register one renderer for each ArtworkRenderStyle.storageId. The test suite
/// enforces full coverage whenever new UI styles are introduced. Keeping
/// renderers here avoids modifying the export pipeline for each new texture.
typedef ArtworkPngRenderer = img.Image Function(LevelDefinition level);

final Map<String, ArtworkPngRenderer> artworkPngRenderers =
    Map<String, ArtworkPngRenderer>.unmodifiable({
      'pixel': _renderPixelImage,
      'canvas': _renderWovenImage,
      'diamond': renderDiamondImage,
    });

/// Renders the exact requested style; unknown styles must never silently
/// produce a flat Pixel image in place of the user's selected texture.
Uint8List renderLevelPng(Map<String, Object> source) {
  final styleId = source['renderStyle'] ?? 'pixel';
  if (styleId is! String) {
    throw const FormatException('Invalid artwork export style.');
  }
  final renderer = artworkPngRenderers[styleId];
  if (renderer == null) {
    throw FormatException('Missing artwork PNG renderer for $styleId.');
  }
  final levelJson = Map<String, Object>.from(source)..remove('renderStyle');
  final level = LevelDefinition.fromJson(levelJson);
  return img.encodePng(renderer(level));
}

img.Image _renderPixelImage(LevelDefinition level) {
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
  return img.copyResize(
    image,
    width: level.width * scale,
    height: level.height * scale,
    interpolation: img.Interpolation.nearest,
  );
}

img.Image _renderWovenImage(LevelDefinition level) {
  final output = _renderPixelImage(level);
  // Share over-under yarn geometry with the Flutter preview. This renderer
  // runs in an isolate, so it deliberately does not depend on dart:ui.
  final pitch = wovenThreadPitch(
    output.width / level.width,
    output.height / level.height,
  );
  for (var y = 0; y < output.height; y++) {
    for (var x = 0; x < output.width; x++) {
      final original = output.getPixel(x, y);
      final light = wovenThreadLighting(x + .5, y + .5, pitch);
      output.setPixelRgb(
        x,
        y,
        shadeWovenChannel(original.r.toInt(), light),
        shadeWovenChannel(original.g.toInt(), light),
        shadeWovenChannel(original.b.toInt(), light),
      );
    }
  }
  return output;
}
