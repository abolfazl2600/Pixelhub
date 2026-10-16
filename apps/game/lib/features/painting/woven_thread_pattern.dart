import 'dart:math' as math;

/// Pure-Dart geometry shared by Flutter's woven-thread painter and PNG export.
///
/// The weave is fixed to artwork coordinates, not to the viewport or zoom.
/// Each intersection alternates which strand is raised.
double wovenThreadPitch(double cellWidth, double cellHeight) {
  final smaller = math.min(cellWidth, cellHeight);
  if (!smaller.isFinite || smaller <= 0) return 8;
  return (smaller * .42).clamp(6.0, 12.0).toDouble();
}

/// Palette-preserving light and shadow for one point in the woven yarn.
typedef YarnLighting = ({double multiply, double lift});

/// A gently twisted fiber ridge. The diagonal phase follows the yarn and
/// varies between intersections, avoiding a flat, mechanically striped look.
double _fiberRidge(
  double along,
  double across,
  int column,
  int row,
) {
  final phase = along * 3.5 + across * 2.1 + (column * 7 + row * 11) * .07;
  final fraction = phase - phase.floor();
  return 1 - 4 * (fraction - .5).abs();
}

YarnLighting wovenThreadLighting(double x, double y, double pitch) {
  if (!pitch.isFinite || pitch <= 0) {
    return (multiply: 1, lift: 0);
  }
  final column = (x / pitch).floor();
  final row = (y / pitch).floor();
  final u = x / pitch - column;
  final v = y / pitch - row;
  final verticalOnTop = (column + row).isEven;

  // Threads bend very slightly around one another at the crossings.
  final verticalMid = 2 * v - 1;
  final horizontalMid = 2 * u - 1;
  final verticalBow =
      (verticalOnTop ? -.055 : .055) * (1 - verticalMid * verticalMid);
  final horizontalBow =
      (verticalOnTop ? .055 : -.055) * (1 - horizontalMid * horizontalMid);
  final warpOffset = u - .5 - verticalBow;
  final weftOffset = v - .5 - horizontalBow;
  final warp = warpOffset.abs();
  final weft = weftOffset.abs();

  if (warp >= .33 && weft >= .33) {
    // The recessed cloth stays colored, rather than becoming a black grid.
    return (multiply: .88, lift: 0);
  }

  final topDistance = verticalOnTop ? warp : weft;
  final underDistance = verticalOnTop ? weft : warp;
  final along = verticalOnTop ? v : u;
  final across = verticalOnTop ? warpOffset : weftOffset;
  final fiber = _fiberRidge(along, across, column, row);
  // Fine, deterministic flecks suggest loose cotton fibers without assets or
  // randomness: identical artwork exports always contain identical stitches.
  final hash = (x.floor() * 73856093) ^ (y.floor() * 19349663);
  final grain = ((hash & 7) - 3.5) * .45;

  if (topDistance < .27) {
    // Convex yarn: its center catches diffuse light while its shoulders fall
    // into the shadow of the next thread. Fine diagonal twist rides on top.
    final side = topDistance / .27;
    final roundness = 1 - side * side;
    return (
      multiply: .79 + .245 * roundness + .045 * fiber,
      lift: 2 + 25 * roundness + 6 * fiber + grain,
    );
  }
  if (underDistance < .27) {
    final side = underDistance / .27;
    final roundness = 1 - side * side;
    return (
      multiply: .74 + .18 * roundness + .03 * fiber,
      lift: 1 + 14 * roundness + 4 * fiber + grain,
    );
  }

  // Tight contact shadows make overlapping loops legible at small sizes.
  return (multiply: .70, lift: .5);
}

int shadeWovenChannel(int channel, YarnLighting lighting) =>
    (channel * lighting.multiply + lighting.lift).round().clamp(0, 255).toInt();
