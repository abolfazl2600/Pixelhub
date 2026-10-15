import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Draw one raised, faceted resin "diamond drill" on its separate dark socket.
///
/// Coordinates are stable in *artwork cell space*, never screen space. Each
/// completed color-by-number cell receives exactly one gem; no texture image,
/// random numbers, network download, or new progress representation is needed.
/// Low-detail geometry prevents dense 128x128 boards from doing thousands of
/// expensive tiny polygons until the player zooms in.
void paintDiamondGem(
  Canvas canvas,
  Rect rect,
  Color base, {
  required int column,
  required int row,
  double zoomScale = 1,
}) {
  if (rect.isEmpty) return;
  final w = rect.width;
  final h = rect.height;
  final side = math.min(w, h);
  final detailSide = side * zoomScale;

  // Rich, dark mounting well with an offset rim makes each drill a separate
  // piece instead of simply drawing light streaks across a flat cell.
  canvas.drawRect(rect, Paint()..color = const Color(0xff313842));
  final socket = Rect.fromCenter(
    center: rect.center + Offset(w * .018, h * .035),
    width: w * .96,
    height: h * .96,
  );
  canvas.drawRRect(
    RRect.fromRectAndRadius(socket, Radius.circular(side * .29)),
    Paint()
      ..color = const Color(0xff161e2a)
      ..isAntiAlias = true,
  );

  final light = Color.lerp(base, Colors.white, .52)!;
  final upper = Color.lerp(base, Colors.white, .33)!;
  final shine = Color.lerp(base, Colors.white, .74)!;
  final lower = Color.lerp(base, Colors.black, .25)!;
  final dark = Color.lerp(base, Colors.black, .44)!;
  final left = Color.lerp(base, Colors.white, .17)!;
  final right = Color.lerp(base, Colors.black, .14)!;

  Offset p(double x, double y) => Offset(rect.left + x * w, rect.top + y * h);
  void facet(List<Offset> points, Color color) {
    final path = Path()..addPolygon(points, true);
    canvas.drawPath(
      path,
      Paint()
        ..color = color
        ..isAntiAlias = detailSide >= 5,
    );
  }

  // At very small scales individual cuts cannot be resolved. The bead and
  // visible gap still read as rhinestones, at a fixed 1-bead-per-cell pitch.
  if (detailSide < 5) {
    canvas.drawOval(
      Rect.fromCenter(center: rect.center, width: w * .78, height: h * .78),
      Paint()..color = base,
    );
    canvas.drawOval(
      Rect.fromCenter(center: p(.38, .33), width: w * .27, height: h * .24),
      Paint()..color = light,
    );
    return;
  }

  // Eight-sided cut crystal. This silhouette avoids the square tile look and
  // produces a tiny but stable physical gap between neighboring diamonds.
  facet([
    p(.24, .06),
    p(.76, .06),
    p(.94, .24),
    p(.94, .76),
    p(.76, .94),
    p(.24, .94),
    p(.06, .76),
    p(.06, .24),
  ], dark);
  facet([
    p(.25, .10),
    p(.75, .10),
    p(.90, .25),
    p(.90, .74),
    p(.75, .90),
    p(.25, .90),
    p(.10, .74),
    p(.10, .25),
  ], base);

  // Four outer bevel directions use physically consistent top-left lighting.
  facet([p(.25, .10), p(.75, .10), p(.69, .32), p(.31, .32)], light);
  facet([
    p(.75, .10),
    p(.90, .25),
    p(.90, .74),
    p(.69, .68),
    p(.69, .32),
  ], right);
  facet([
    p(.90, .74),
    p(.75, .90),
    p(.25, .90),
    p(.31, .68),
    p(.69, .68),
  ], lower);
  facet([
    p(.25, .90),
    p(.10, .74),
    p(.10, .25),
    p(.25, .10),
    p(.31, .32),
    p(.31, .68),
  ], left);

  // Table (top polished facet) and its precise diamond-cut internal edges.
  facet([p(.31, .32), p(.69, .32), p(.69, .68), p(.31, .68)], upper);
  facet([p(.31, .32), p(.49, .25), p(.69, .32), p(.49, .49)], shine);
  facet([p(.69, .32), p(.75, .50), p(.69, .68), p(.49, .49)], base);
  facet([p(.69, .68), p(.49, .75), p(.31, .68), p(.49, .49)], right);
  facet([p(.31, .68), p(.25, .50), p(.31, .32), p(.49, .49)], light);

  // Deterministic micro-glint: slightly different cuts per bead, no random
  // flicker during scroll/zoom/animation, and no external texture files.
  if (detailSide >= 8) {
    final seed = (column * 37 + row * 61) & 3;
    final sparkle = seed == 0
        ? .36
        : seed == 1
        ? .43
        : .39;
    facet([
      p(sparkle, .21),
      p(sparkle + .09, .19),
      p(sparkle + .04, .31),
    ], const Color(0xccffffff));
    if (detailSide >= 14) {
      canvas.drawCircle(
        p(.29, .29),
        side * .025,
        Paint()..color = const Color(0xddffffff),
      );
    }
  }
}

/// Subtle unfilled cell holder; original color numbers still render on top.
void paintDiamondSocket(Canvas canvas, Rect rect) {
  if (rect.isEmpty || math.min(rect.width, rect.height) < 6) return;
  canvas.drawRRect(
    RRect.fromRectAndRadius(
      rect.deflate(math.min(rect.width, rect.height) * .12),
      Radius.circular(math.min(rect.width, rect.height) * .23),
    ),
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = math.min(rect.width, rect.height) * .055
      ..color = const Color(0x33546276),
  );
}
