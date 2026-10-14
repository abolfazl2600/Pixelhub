import 'package:flutter_test/flutter_test.dart';
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/features/gallery/artwork_difficulty.dart';

LevelDefinition level({
  int width = 16,
  int height = 16,
  List<int> palette = const [0xff000000, 0xffffffff],
  List<int>? cells,
}) => LevelDefinition(
  id: 'difficulty-test',
  title: 'آزمون',
  titleEn: 'Test',
  schemaVersion: 2,
  contentVersion: 1,
  width: width,
  height: height,
  palette: palette,
  cells: cells ?? List.generate(width * height, (index) => index % palette.length),
);

void main() {
  test('calibrated thresholds produce Easy, Medium and Hard groups', () {
    expect(
      artworkDifficultyFor(width: 16, height: 16, colorCount: 4),
      ArtworkDifficulty.easy,
    );
    expect(
      artworkDifficultyFor(width: 16, height: 16, colorCount: 5),
      ArtworkDifficulty.medium,
    );
    expect(
      artworkDifficultyFor(width: 32, height: 32, colorCount: 4),
      ArtworkDifficulty.medium,
    );
    expect(
      artworkDifficultyFor(width: 32, height: 32, colorCount: 5),
      ArtworkDifficulty.hard,
    );
    expect(
      artworkDifficultyFor(width: 24, height: 24, colorCount: 8),
      ArtworkDifficulty.hard,
    );
  });

  test('uses distinct colors actually used by cells, not unused palette slots', () {
    final artwork = level(
      palette: const [
        0xff000000,
        0xffffffff,
        0xffff0000,
        0xff00ff00,
        0xff0000ff,
      ],
      cells: List.generate(256, (index) => index.isEven ? 0 : 1),
    );
    expect(difficultyForLevel(artwork), ArtworkDifficulty.easy);
  });

  test('online catalog colors are used when present and legacy fallback is stable', () {
    expect(
      difficultyForOnlineGrid(width: 16, height: 16, colorCount: 4),
      ArtworkDifficulty.easy,
    );
    expect(
      difficultyForOnlineGrid(width: 16, height: 16),
      ArtworkDifficulty.easy,
    );
    expect(
      difficultyForOnlineGrid(width: 32, height: 32),
      ArtworkDifficulty.medium,
    );
  });

  test('rejects invalid grid metadata', () {
    expect(
      () => artworkDifficultyFor(width: 0, height: 16, colorCount: 4),
      throwsArgumentError,
    );
    expect(
      () => artworkDifficultyFor(width: 16, height: 16, colorCount: 0),
      throwsArgumentError,
    );
  });
}
