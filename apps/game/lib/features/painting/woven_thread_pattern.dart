import 'dart:math' as math;

/// Pure-Dart geometry shared by Flutter's woven-thread painter and PNG export.
///
/// The textile is anchored at artwork coordinate (0, 0), never screen pixels.
/// Crossing parity flips at each intersection to mimic a plain-weave fabric.
double wovenThreadPitch(double cellWidth, double cellHeight) {
  final smaller = math.min(cellWidth, cellHeight);
  if (!smaller.isFinite || smaller <= 0) return 8;
  return (smaller * .42).clamp(6.0, 12.0).toDouble();
}

/// Premultiplied color adjustment that preserves the source palette hue.
typedef YarnLighting = ({double multiply, double lift});

YarnLighting wovenThreadLighting(double x, double y, double pitch) {
  final column = (x / pitch).floor();
  final row = (y / pitch).floor();
  final u = x / pitch - column;
  final v = y / pitch - row;
  final verticalOnTop = (column + row).isEven;

  // A little bow toward the crossover gives strands a rounded silhouette.
  final verticalMid = 2 * v - 1;
  final horizontalMid = 2 * u - 1;
  final verticalBow =
      (verticalOnTop ? -.055 : .055) * (1 - verticalMid * verticalMid);
  final horizontalBow =
      (verticalOnTop ? .055 : -.055) * (1 - horizontalMid * horizontalMid);
  final warp = (u - .5 - verticalBow).abs();
  final weft = (v - .5 - horizontalBow).abs();
  final nearWarp = warp < .28;
  final nearWeft = weft < .28;

  if (!nearWarp && !nearWeft) {
    // The recessed fabric between adjacent rounded yarns.
    return (multiply: .91, lift: 0);
  }

  final topDistance = verticalOnTop ? warp : weft;
  final underDistance = verticalOnTop ? weft : warp;
  final topPresent = topDistance < .24;
  final underPresent = underDistance < .24;

  if (topPresent) {
    // The yarn is cylindrical: its bright central core has shaded shoulders.
    final side = topDistance / .24;
    if (side < .27) return (multiply: 1.05, lift: 31);
    if (side < .60) return (multiply: 1.00, lift: 15);
    return (multiply: .79, lift: 2);
  }
  if (underPresent) {
    final side = underDistance / .24;
    if (side < .36) return (multiply: .99, lift: 13);
    return (multiply: .78, lift: 2);
  }
  // A cast shadow follows the edges of both threads.
  return (multiply: .75, lift: 1);
}

int shadeWovenChannel(int channel, YarnLighting lighting) =>
    (channel * lighting.multiply + lighting.lift).round().clamp(0, 255).toInt();
