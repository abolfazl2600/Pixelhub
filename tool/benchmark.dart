import 'dart:convert';
import 'dart:io';

import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';

void main() {
  final decoded =
      jsonDecode(File('apps/game/assets/levels/planet.json').readAsStringSync())
          as Map<String, Object?>;
  final parseTimes = <double>[];
  final paintTimes = <double>[];
  for (var run = 0; run < 25; run++) {
    final timer = Stopwatch()..start();
    final level = LevelDefinition.fromJson(decoded);
    parseTimes.add(timer.elapsedMicroseconds / 1000);
    final session = PaintingSession(level);
    timer.reset();
    for (var color = 0; color < level.palette.length; color++) {
      session.selectColor(color);
      session.beginStroke();
      for (var y = 0; y < level.height; y++) {
        session.paintLine(0, y, level.width - 1, y);
      }
      session.endStroke();
    }
    paintTimes.add(timer.elapsedMicroseconds / 1000);
    if (!session.isComplete || session.snapshot.completedCount != 16384)
      throw StateError('Incomplete benchmark');
  }
  double median(List<double> values) {
    final samples = values.skip(5).toList()..sort();
    return samples[samples.length ~/ 2];
  }

  print(
    jsonEncode({
      'platform': 'Dart VM on cloud Linux; not physical-device rendering',
      'grid': '128x128',
      'measuredRuns': 20,
      'warmupRuns': 5,
      'checksumAndParseMedianMs': median(parseTimes),
      'completePaintingMedianMs': median(paintTimes),
    }),
  );
}
