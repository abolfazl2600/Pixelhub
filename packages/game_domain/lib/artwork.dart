import 'package:level_schema/level_schema.dart';

/// Private artwork keeps only the converted grid, never the original photo.
final class PrivateArtwork {
  PrivateArtwork({
    required this.level,
    required this.createdAt,
    required this.difficulty,
    required this.colorLimit,
    required this.quarterTurns,
    required this.cropX,
    required this.cropY,
  }) {
    if (!level.id.startsWith('private-') ||
        !{'easy', 'normal', 'hard'}.contains(difficulty) ||
        colorLimit < 2 ||
        colorLimit > 24 ||
        quarterTurns < 0 ||
        quarterTurns > 3 ||
        !cropX.isFinite ||
        !cropY.isFinite ||
        cropX < 0 ||
        cropX > 1 ||
        cropY < 0 ||
        cropY > 1) {
      throw const FormatException('Invalid private artwork.');
    }
  }

  factory PrivateArtwork.fromJson(Map<String, Object?> json) {
    if (json['schemaVersion'] != 1) {
      throw const FormatException('Unsupported artwork version.');
    }
    return PrivateArtwork(
      level: LevelDefinition.fromJson(json['level']! as Map<String, Object?>),
      createdAt: DateTime.parse(json['createdAt']! as String),
      difficulty: json['difficulty']! as String,
      colorLimit: json['colorLimit']! as int,
      quarterTurns: json['quarterTurns']! as int,
      cropX: (json['cropX']! as num).toDouble(),
      cropY: (json['cropY']! as num).toDouble(),
    );
  }

  final LevelDefinition level;
  final DateTime createdAt;
  final String difficulty;
  final int colorLimit;
  final int quarterTurns;
  final double cropX;
  final double cropY;

  Map<String, Object> toJson() => {
    'schemaVersion': 1,
    'level': level.toJson(),
    'createdAt': createdAt.toUtc().toIso8601String(),
    'difficulty': difficulty,
    'colorLimit': colorLimit,
    'quarterTurns': quarterTurns,
    'cropX': cropX,
    'cropY': cropY,
  };
}

final class ArtworkLibrary {
  ArtworkLibrary({
    Iterable<PrivateArtwork> artworks = const [],
    Iterable<String> favorites = const [],
    this.coins = 120,
    this.totalPoints = 0,
    Iterable<String> unlocked = const [],
    Iterable<String> rewarded = const [],
  }) : artworks = List.unmodifiable(artworks),
       favorites = Set.unmodifiable(favorites),
       unlocked = Set.unmodifiable(unlocked),
       rewarded = Set.unmodifiable(rewarded) {
    if (this.artworks.length > 20 ||
        this.favorites.length > 500 ||
        this.artworks.map((art) => art.level.id).toSet().length !=
            this.artworks.length ||
        coins < 0 ||
        coins > 1000000000 ||
        totalPoints < 0 ||
        totalPoints > 1000000000 ||
        this.unlocked.length > 5000 ||
        this.rewarded.length > 5000 ||
        [...this.favorites, ...this.unlocked, ...this.rewarded].any(
          (id) => !RegExp(r'^[a-z0-9-]+$').hasMatch(id),
        )) {
      throw const FormatException('Invalid artwork library.');
    }
  }
  factory ArtworkLibrary.fromJson(Map<String, Object?> json) {
    if (json['schemaVersion'] != 1) {
      throw const FormatException('Unsupported library version.');
    }
    return ArtworkLibrary(
      artworks: (json['artworks']! as List<Object?>).map(
        (value) => PrivateArtwork.fromJson(value! as Map<String, Object?>),
      ),
      favorites: (json['favorites']! as List<Object?>).cast<String>(),
      // Version-one libraries predate coins; give existing players the same
      // starter wallet as new players without erasing their saved gallery.
      coins: json['coins'] == null ? 120 : json['coins']! as int,
      totalPoints: json['totalPoints'] == null
          ? 0
          : json['totalPoints']! as int,
      unlocked: (json['unlocked'] as List<Object?>? ?? const []).cast<String>(),
      rewarded: (json['rewarded'] as List<Object?>? ?? const []).cast<String>(),
    );
  }
  final List<PrivateArtwork> artworks;
  final Set<String> favorites;
  final int coins;
  final int totalPoints;
  final Set<String> unlocked;
  final Set<String> rewarded;

  ArtworkLibrary copyWith({
    Iterable<PrivateArtwork>? artworks,
    Iterable<String>? favorites,
    int? coins,
    int? totalPoints,
    Iterable<String>? unlocked,
    Iterable<String>? rewarded,
  }) => ArtworkLibrary(
    artworks: artworks ?? this.artworks,
    favorites: favorites ?? this.favorites,
    coins: coins ?? this.coins,
    totalPoints: totalPoints ?? this.totalPoints,
    unlocked: unlocked ?? this.unlocked,
    rewarded: rewarded ?? this.rewarded,
  );

  Map<String, Object> toJson() => {
    'schemaVersion': 1,
    'artworks': artworks.map((art) => art.toJson()).toList(),
    'favorites': favorites.toList()..sort(),
    'coins': coins,
    'totalPoints': totalPoints,
    'unlocked': unlocked.toList()..sort(),
    'rewarded': rewarded.toList()..sort(),
  };
}

abstract interface class ArtworkRepository {
  Future<ArtworkLibrary> readLibrary();
  Future<void> writeLibrary(ArtworkLibrary library);
  Future<void> removeProgress(LevelDefinition level);
  Future<void> clearPixelhubData();
}

final class CatalogMetadata {
  const CatalogMetadata({required this.category, required this.tags});
  final String category;
  final List<String> tags;
}

abstract interface class CatalogMetadataRepository {
  Future<Map<String, CatalogMetadata>> loadMetadata();
}
