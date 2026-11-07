import 'dart:math' as math;
import 'dart:typed_data';

import 'package:game_domain/game_domain.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';

/// Bounded offline export, independent of screen size and painting UI.
final class TimelapseGifLimits {
  const TimelapseGifLimits({
    this.maxFrames = 36,
    this.maxSide = 192,
    this.durationCentiseconds = 1000,
    this.maxBytes = 8 * 1024 * 1024,
  });

  final int maxFrames;
  final int maxSide;
  final int durationCentiseconds;
  final int maxBytes;
}

/// Selects only valid, current-generation, unexpired recorded cell states.
/// Multiple percentages from a single stroke may have identical snapshots.
List<ProgressSnapshot> prepareTimelapseFrames(
  LevelDefinition level,
  ProgressSnapshot completed,
  List<Map<String, Object?>> records, {
  DateTime? now,
  int maxFrames = 36,
}) {
  if (completed.completedCount != level.cells.length ||
      completed.levelId != level.id ||
      completed.levelChecksum != level.checksum ||
      completed.levelVersion != level.contentVersion) {
    throw const FormatException('Painting is not complete.');
  }
  if (maxFrames < 3 || maxFrames > 50) {
    throw const FormatException('Invalid frame limit.');
  }
  final clock = (now ?? DateTime.now().toUtc()).toUtc();
  final cutoff = clock.subtract(const Duration(hours: 120));
  final byMilestone = <int, ProgressSnapshot>{};
  for (final record in records) {
    try {
      if (record['schemaVersion'] != 1 ||
          record['levelId'] != level.id ||
          record['generation'] != completed.generation) {
        continue;
      }
      final milestone = record['milestonePercent'];
      final attained = record['attainedPercent'];
      if (milestone is! int ||
          attained is! int ||
          milestone < 1 ||
          milestone > 100 ||
          attained < milestone ||
          attained > 100) {
        continue;
      }
      final captured = DateTime.tryParse(record['capturedAt'] as String);
      if (captured == null ||
          !captured.toUtc().isAfter(cutoff) ||
          captured.toUtc().isAfter(clock)) {
        continue;
      }
      final snapshot = ProgressSnapshot.fromJson(
        Map<String, Object?>.from(record['progress'] as Map),
        level,
      );
      if (snapshot.generation != completed.generation ||
          (snapshot.completedCount - level.preFilledCount) *
                  100 ~/
                  level.paintableCellCount !=
              attained) {
        continue;
      }
      byMilestone.putIfAbsent(milestone, () => snapshot);
    } on Object {
      // Ignore corrupt optional replay data, never normal gameplay data.
    }
  }
  final last = byMilestone[100];
  if (last == null ||
      last.completedCount != level.cells.length ||
      !_sameBits(last.bits, completed.bits)) {
    throw const FormatException('No complete replay history available.');
  }
  final milestones = byMilestone.keys.toList()..sort();
  final unique = <ProgressSnapshot>[];
  ProgressSnapshot? previous;
  for (final milestone in milestones) {
    final state = byMilestone[milestone]!;
    if (previous != null && !_containsBits(state.bits, previous.bits)) {
      throw const FormatException('Replay checkpoints are out of order.');
    }
    if (previous == null || !_sameBits(previous.bits, state.bits)) {
      unique.add(state);
    }
    previous = state;
  }
  if (unique.length < 2) {
    throw const FormatException('Not enough recorded steps for a timelapse.');
  }
  if (unique.length <= maxFrames - 1) {
    return List<ProgressSnapshot>.unmodifiable(unique);
  }
  // Sample real recorded states uniformly: never synthesize cell states.
  final selected = <ProgressSnapshot>[];
  for (var i = 0; i < maxFrames - 1; i++) {
    final index = i * (unique.length - 1) ~/ (maxFrames - 2);
    selected.add(unique[index]);
  }
  return List<ProgressSnapshot>.unmodifiable(selected);
}

bool _sameBits(Uint8List a, Uint8List b) {
  if (a.length != b.length) return false;
  for (var i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
}

bool _containsBits(Uint8List newer, Uint8List older) {
  if (newer.length != older.length) return false;
  for (var i = 0; i < newer.length; i++) {
    if ((newer[i] & older[i]) != older[i]) return false;
  }
  return true;
}

/// Entry point for Flutter compute() (background isolate on Android).
/// This never uses screenshots, network, disk or gameplay state mutation.
Uint8List renderTimelapseGif(Map<String, Object?> payload) {
  final level = LevelDefinition.fromJson(
    Map<String, Object?>.from(payload['level'] as Map),
  );
  final complete = ProgressSnapshot.fromJson(
    Map<String, Object?>.from(payload['completed'] as Map),
    level,
  );
  final limits = TimelapseGifLimits(
    maxFrames: payload['maxFrames'] as int? ?? 36,
    maxSide: payload['maxSide'] as int? ?? 192,
    durationCentiseconds: payload['durationCentiseconds'] as int? ?? 1000,
    maxBytes: payload['maxBytes'] as int? ?? 8 * 1024 * 1024,
  );
  if (limits.maxSide < 64 ||
      limits.maxSide > 256 ||
      limits.durationCentiseconds < 100 ||
      limits.durationCentiseconds > 3000 ||
      limits.maxBytes < 1024 ||
      limits.maxBytes > 16 * 1024 * 1024 ||
      math.max(level.width, level.height) > limits.maxSide) {
    throw const FormatException('Artwork exceeds GIF export limits.');
  }
  final records = (payload['checkpoints'] as List)
      .map((item) => Map<String, Object?>.from(item as Map))
      .toList();
  final states = prepareTimelapseFrames(
    level,
    complete,
    records,
    maxFrames: limits.maxFrames,
  );
  final scale = math.max(
    1,
    math.min(8, limits.maxSide ~/ math.max(level.width, level.height)),
  );
  final encoder = img.GifEncoder(
    repeat: 0,
    quantizerType: img.QuantizerType.octree,
    dither: img.DitherKernel.none,
  );
  final frameCount = states.length + 1;
  final delay = math.max(2, limits.durationCentiseconds ~/ frameCount);
  // Frame zero shows the already-filled background, not a blank canvas.
  final empty = level.initialCompletedBits;
  for (var frame = 0; frame < frameCount; frame++) {
    final bits = frame == 0 ? empty : states[frame - 1].bits;
    final image = img.Image(
      width: level.width,
      height: level.height,
      numChannels: 3,
    );
    for (var p = 0; p < level.cells.length; p++) {
      final colored = (bits[p ~/ 8] & (1 << (p % 8))) != 0;
      final color = colored ? level.palette[level.cells[p]] : 0xfff5f5f5;
      image.setPixelRgb(
        p % level.width,
        p ~/ level.width,
        (color >> 16) & 255,
        (color >> 8) & 255,
        color & 255,
      );
    }
    encoder.addFrame(
      scale == 1
          ? image
          : img.copyResize(
              image,
              width: level.width * scale,
              height: level.height * scale,
              interpolation: img.Interpolation.nearest,
            ),
      duration: delay,
    );
  }
  final bytes = encoder.finish();
  if (bytes == null || bytes.isEmpty || bytes.length > limits.maxBytes) {
    throw const FormatException('GIF output exceeds the size limit.');
  }
  return bytes;
}
