import 'dart:convert';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:game_domain/game_domain.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';

/// Pure Dart payload for compute(). Frames are reconstructed from cell bitsets,
/// never from UI screenshots. GIF frames are deliberately size/count bounded.
Uint8List encodePaintingTimelapse(Map<String, Object?> input) {
  final level = LevelDefinition.fromJson(
    Map<String, Object>.from(input['level']! as Map),
  );
  final generation = input['generation']! as int;
  final raw = input['checkpoints']! as List;
  final snapshots = <(int, ProgressSnapshot)>[];
  for (final item in raw) {
    final record = Map<String, Object?>.from(item as Map);
    if (record['generation'] != generation) continue;
    final milestone = record['milestonePercent'];
    if (milestone is! int || milestone < 1 || milestone > 100) continue;
    try {
      final snapshot = ProgressSnapshot.fromJson(
        Map<String, Object?>.from(record['progress']! as Map),
        level,
      );
      if (snapshot.generation != generation) continue;
      snapshots.add((milestone, snapshot));
    } on Object {
      // Ignore corrupted or incompatible replay records.
    }
  }
  snapshots.sort((a, b) => a.$1.compareTo(b.$1));
  if (snapshots.isEmpty || snapshots.last.$1 != 100 ||
      !snapshots.last.$2.isCompleted(0) && level.cells.length == 1 ||
      snapshots.last.$2.completedCount != level.cells.length) {
    throw const FormatException('Complete replay checkpoints unavailable.');
  }
  final unique = <ProgressSnapshot>[];
  Uint8List? previous;
  var previousCount = -1;
  for (final item in snapshots) {
    final current = item.$2;
    if (current.completedCount < previousCount) {
      throw const FormatException('Replay progress is not monotonic.');
    }
    if (previous != null) {
      for (var i = 0; i < previous.length; i++) {
        if ((previous[i] & current.bits[i]) != previous[i]) {
          throw const FormatException('Replay cells changed unexpectedly.');
        }
      }
    }
    previous = current.bits;
    previousCount = current.completedCount;
    if (unique.isEmpty || unique.last.completedCount != current.completedCount) {
      unique.add(current);
    }
  }
  if (unique.length < 2) {
    throw const FormatException('Insufficient distinct replay frames.');
  }

  const maxFrames = 48;
  const maxSide = 320;
  const durationCentiseconds = 1000; // 10 seconds.
  final maxDimension = math.max(level.width, level.height);
  final scale = math.max(1, maxSide ~/ maxDimension);
  final width = level.width * scale;
  final height = level.height * scale;
  final frames = <ProgressSnapshot?>[null];
  for (var i = 0; i < unique.length; i++) {
    if (frames.length >= maxFrames - 1) break;
    final index = ((i + 1) * (unique.length - 1) / math.min(
      unique.length, maxFrames - 2,
    )).round().clamp(0, unique.length - 1);
    final frame = unique[index];
    if (frames.last != frame) frames.add(frame);
  }
  if (frames.last != unique.last) frames.add(unique.last);

  final encoder = img.GifEncoder();
  final frameDuration = math.max(2, durationCentiseconds ~/ frames.length);
  for (final snapshot in frames) {
    final image = img.Image(width: width, height: height, numChannels: 3);
    for (var y = 0; y < height; y++) {
      final sourceY = y ~/ scale;
      for (var x = 0; x < width; x++) {
        final cell = sourceY * level.width + x ~/ scale;
        final colored = snapshot != null && snapshot.isCompleted(cell);
        final color = colored ? level.palette[level.cells[cell]] : 0xffeeeeee;
        image.setPixelRgb(
          x, y, (color >> 16) & 255, (color >> 8) & 255, color & 255,
        );
      }
    }
    encoder.addFrame(image, duration: frameDuration);
  }
  final bytes = encoder.finish();
  if (bytes == null || bytes.isEmpty) {
    throw const FormatException('GIF encoding failed.');
  }
  return bytes;
}
