import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';

import 'artwork_difficulty.dart';

/// Local earned coins only: no billing, ads or network dependency.
/// Different paintings of the same difficulty can still have different prices.
int artworkPrice(String id, ArtworkDifficulty difficulty) {
  // Redesigns keep the previous artwork's price to avoid an economy change.
  final pricingId = switch (id) {
    'online-elephant-detailed' => 'online-elephant',
    'online-penguin-detailed' => 'online-penguin',
    'online-parrot-detailed' => 'online-parrot',
    'online-classic-animated70-primavera' =>
      'online-classic-animated64-primavera',
    'online-classic-animated70-tower-babel' =>
      'online-classic-animated64-tower-babel',
    'online-classic-animated70-hunters-snow' =>
      'online-classic-animated64-hunters-snow',
    'online-classic-animated70-ophelia' =>
      'online-classic-animated64-ophelia',
    'online-classic-animated70-lady-shalott' =>
      'online-classic-animated64-lady-shalott',
    'online-classic-animated70-olympia' =>
      'online-classic-animated64-olympia',
    'online-classic-animated70-luncheon-grass' =>
      'online-classic-animated64-luncheon-grass',
    _ => id,
  };
  final hash = pricingId.codeUnits.fold<int>(
    0,
    (sum, unit) => (sum * 31 + unit) % 997,
  );
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

/// Coins are earned by finishing paintings, then optionally spent on tools.
/// No subscriptions, advertising or remote inventory are required.
int precisionToolPrice(PrecisionPaintTool tool) => switch (tool) {
  PrecisionPaintTool.magicWand => 12,
  PrecisionPaintTool.colorSplash => 6,
};
