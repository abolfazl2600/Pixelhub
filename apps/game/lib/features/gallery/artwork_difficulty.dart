import 'dart:math' as math;

import 'package:level_schema/level_schema.dart';

/// A display-only estimate; it is never written to artwork or progress data.
enum ArtworkDifficulty {
  easy,
  medium,
  hard,
}

/// Scores the actual grid and the number of distinct colors used by its cells.
///
/// The current bundled catalog contains mostly 16x16 and 32x32 levels. The
/// score uses the square-root of cell count (grid side), plus a color-count
/// weight, so 16x16 works with up to four colors trend Easy, common 32x32
/// works with three or four colors trend Medium, and denser/more colorful
/// works trend Hard. These thresholds deliberately produce all three groups
/// without treating every 32x32 grid as automatically Hard.
ArtworkDifficulty artworkDifficultyFor({
  required int width,
  required int height,
  required int colorCount,
}) {
  if (width < 1 || height < 1 || colorCount < 1) {
    throw ArgumentError('Grid dimensions and color count must be positive.');
  }
  final gridSide = math.sqrt(width * height);
  final score = gridSide * 4 + colorCount * 24;
  if (score <= 175) return ArtworkDifficulty.easy;
  if (score <= 230) return ArtworkDifficulty.medium;
  return ArtworkDifficulty.hard;
}

/// Uses colors actually present in the cell matrix, not unused palette slots.
ArtworkDifficulty difficultyForLevel(LevelDefinition level) =>
    artworkDifficultyFor(
      width: level.width,
      height: level.height,
      colorCount: level.cells.toSet().length,
    );

/// Legacy online catalog entries do not include color metadata. New catalogs
/// provide the actual used-color count; older entries use a documented
/// four-color estimate until downloaded level data becomes available.
ArtworkDifficulty difficultyForOnlineGrid({
  required int width,
  required int height,
  int? colorCount,
}) => artworkDifficultyFor(
  width: width,
  height: height,
  colorCount: colorCount ?? 4,
);
