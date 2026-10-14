import 'package:level_schema/level_schema.dart';

import 'artwork_difficulty.dart';

/// Local earned coins only: no billing, ads or network dependency.
/// Different paintings of the same difficulty can still have different prices.
int artworkPrice(String id, ArtworkDifficulty difficulty) {
  final hash = id.codeUnits.fold<int>(0, (sum, unit) => (sum * 31 + unit) % 997);
  return switch (difficulty) {
    ArtworkDifficulty.easy => 20 + (hash % 4) * 5,
    ArtworkDifficulty.medium => 45 + (hash % 5) * 5,
    ArtworkDifficulty.hard => 80 + (hash % 5) * 10,
  };
}

int artworkReward(ArtworkDifficulty difficulty) => switch (difficulty) {
  ArtworkDifficulty.easy => 40,
  ArtworkDifficulty.medium => 75,
  ArtworkDifficulty.hard => 125,
};

int priceForLevel(LevelDefinition level) =>
    artworkPrice(level.id, difficultyForLevel(level));

int rewardForLevel(LevelDefinition level) =>
    artworkReward(difficultyForLevel(level));

/// New imported art is free. The starter sunflower remains permanently free.
/// Existing artwork with saved progress is grandfathered into ownership.
bool alwaysFreeArtwork(String id) =>
    id == 'sunflower' || id.startsWith('private-');
