import 'dart:math' as math;

import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';

/// Pure-Dart, isolate-safe counterpart of the on-screen faceted gem painter.
///
/// Creates a proper resin bead for every numbered pixel, keeping the one-cell
/// gap, mounting shadow, polygon facets, physical light direction, and stable
/// micro-glint in exported PNGs. This does not require Flutter's dart:ui API
/// and therefore also works in web conversion/compute contexts.
img.Image renderDiamondImage(LevelDefinition level) {
  final scale = 1024 ~/ math.max(level.width, level.height);
  final cw = scale, ch = scale;
  final output = img.Image(
    width: level.width * cw,
    height: level.height * ch,
    numChannels: 3,
  );

  // Normalized polygons mirror diamond_gem_painter.dart. Lists are allocated
  // once, rather than once per output pixel.
  const upperBevel = [.25,.10, .75,.10, .69,.32, .31,.32];
  const rightBevel = [.75,.10, .90,.25, .90,.74, .69,.68, .69,.32];
  const bottomBevel = [.90,.74, .75,.90, .25,.90, .31,.68, .69,.68];
  const leftBevel = [.25,.90, .10,.74, .10,.25, .25,.10, .31,.32, .31,.68];
  const table = [.31,.32, .69,.32, .69,.68, .31,.68];
  const cutTop = [.31,.32, .49,.25, .69,.32, .49,.49];
  const cutRight = [.69,.32, .75,.50, .69,.68, .49,.49];
  const cutBottom = [.69,.68, .49,.75, .31,.68, .49,.49];
  const cutLeft = [.31,.68, .25,.50, .31,.32, .49,.49];

  for (var row = 0; row < level.height; row++) {
    for (var column = 0; column < level.width; column++) {
      final base = level.palette[level.cells[row * level.width + column]];
      final r = (base >> 16) & 255;
      final g = (base >> 8) & 255;
      final b = base & 255;
      final glint = (column * 37 + row * 61) & 3;
      final sparkle = glint == 0 ? .36 : glint == 1 ? .43 : .39;
      final glintFacet = [sparkle, .21, sparkle + .09, .19, sparkle + .04, .31];

      for (var iy = 0; iy < ch; iy++) {
        final v = (iy + .5) / ch;
        for (var ix = 0; ix < cw; ix++) {
          final u = (ix + .5) / cw;
          final minU = math.min(u, 1 - u);
          final minV = math.min(v, 1 - v);
          double mix = 0;
          var target = 255; // White for light faces; black for dark faces.
          var fixed = -1; // RRGGBB background, when the bead is absent.

          if (minU < .01 || minV < .01) {
            fixed = 0xe9edf4;
          } else if (minU < .06 || minV < .06 ||
              minU + minV < .30) {
            fixed = 0x161e2a; // Recessed mounting well.
          } else if (minU < .10 || minV < .10 ||
              minU + minV < .35) {
            mix = .44;
            target = 0;
          } else {
            // Last-applied facets take precedence, just as in CustomPainter.
            if (_insidePolygon(u, v, cutLeft)) {
              mix = .52;
            } else if (_insidePolygon(u, v, cutBottom)) {
              mix = .14;
              target = 0;
            } else if (_insidePolygon(u, v, cutRight)) {
              mix = 0;
            } else if (_insidePolygon(u, v, cutTop)) {
              mix = .74;
            } else if (_insidePolygon(u, v, table)) {
              mix = .33;
            } else if (_insidePolygon(u, v, leftBevel)) {
              mix = .17;
            } else if (_insidePolygon(u, v, bottomBevel)) {
              mix = .25;
              target = 0;
            } else if (_insidePolygon(u, v, rightBevel)) {
              mix = .14;
              target = 0;
            } else if (_insidePolygon(u, v, upperBevel)) {
              mix = .52;
            }
            if (cw >= 8 && _insidePolygon(u, v, glintFacet)) {
              mix = .82; // White glint with 80%-opacity coverage.
            }
          }

          final rr = fixed >= 0 ? (fixed >> 16) & 255 :
              (r * (1 - mix) + target * mix).round().clamp(0, 255);
          final gg = fixed >= 0 ? (fixed >> 8) & 255 :
              (g * (1 - mix) + target * mix).round().clamp(0, 255);
          final bb = fixed >= 0 ? fixed & 255 :
              (b * (1 - mix) + target * mix).round().clamp(0, 255);
          output.setPixelRgb(column * cw + ix, row * ch + iy, rr, gg, bb);
        }
      }
    }
  }
  return output;
}

bool _insidePolygon(double x, double y, List<double> vertices) {
  var inside = false;
  for (var i = 0, j = vertices.length - 2;
      i < vertices.length;
      j = i, i += 2) {
    final xi = vertices[i], yi = vertices[i + 1];
    final xj = vertices[j], yj = vertices[j + 1];
    if ((yi > y) != (yj > y) &&
        x < (xj - xi) * (y - yi) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}
