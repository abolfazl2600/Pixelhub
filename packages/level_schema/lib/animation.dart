import 'package:level_schema/level_schema.dart' show LevelDefinition;

/// Optional independent sidecar. Frames are sparse changes from the immutable
/// completed picture; they never change its checksum or painting progress.
final class PixelAnimation {
  PixelAnimation._({
    required this.levelId,
    required this.levelVersion,
    required this.levelChecksum,
    required this.frameDurationMs,
    required this.frames,
  });

  factory PixelAnimation.fromJson(
    Map<String, Object?> json,
    LevelDefinition level,
  ) {
    if (json['schemaVersion'] != 1 ||
        json['levelId'] != level.id ||
        json['levelVersion'] != level.contentVersion ||
        json['levelChecksum'] != level.checksum) {
      throw const FormatException('Animation does not match its picture.');
    }
    final duration = json['frameDurationMs'];
    final rawFrames = json['frames'];
    if (duration is! int ||
        duration < 60 ||
        duration > 2000 ||
        rawFrames is! List ||
        rawFrames.isEmpty) {
      throw const FormatException('Invalid animation timing or frame count.');
    }
    final frames = <List<PixelChange>>[];
    for (final raw in rawFrames) {
      if (raw is! Map || raw['changes'] is! List) {
        throw const FormatException('Malformed animation frame.');
      }
      final changes = <PixelChange>[];
      final seen = <int>{};
      for (final entry in raw['changes'] as List) {
        if (entry is! List ||
            entry.length != 2 ||
            entry[0] is! int ||
            entry[1] is! int) {
          throw const FormatException('Malformed animation pixel.');
        }
        final at = entry[0] as int;
        final color = entry[1] as int;
        if (at < 0 ||
            at >= level.cells.length ||
            color < 0 ||
            color >= level.palette.length ||
            !seen.add(at)) {
          throw const FormatException('Invalid animation pixel.');
        }
        changes.add(PixelChange(at, color));
      }
      frames.add(List.unmodifiable(changes));
    }
    return PixelAnimation._(
      levelId: level.id,
      levelVersion: level.contentVersion,
      levelChecksum: level.checksum,
      frameDurationMs: duration,
      frames: List.unmodifiable(frames),
    );
  }

  final String levelId;
  final int levelVersion;
  final String levelChecksum;
  final int frameDurationMs;
  final List<List<PixelChange>> frames;

  int get frameCount => frames.length;

  List<int> pixelsFor(LevelDefinition level, int frameIndex) {
    if (level.id != levelId ||
        level.contentVersion != levelVersion ||
        level.checksum != levelChecksum) {
      throw const FormatException('Animation belongs to another picture.');
    }
    final cells = List<int>.of(level.cells);
    for (final change in frames[frameIndex]) {
      cells[change.index] = change.color;
    }
    return cells;
  }

  Map<String, Object> toJson() => {
    'schemaVersion': 1,
    'levelId': levelId,
    'levelVersion': levelVersion,
    'levelChecksum': levelChecksum,
    'frameDurationMs': frameDurationMs,
    'frames': [
      for (final frame in frames)
        {
          'changes': [
            for (final change in frame) [change.index, change.color],
          ],
        },
    ],
  };
}

final class PixelChange {
  const PixelChange(this.index, this.color);
  final int index;
  final int color;
}
