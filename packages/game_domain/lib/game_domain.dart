import 'dart:convert';
import 'dart:typed_data';

import 'package:level_schema/level_schema.dart';

export 'artwork.dart';

part 'progress_sync.dart';
part 'progress_outbox.dart';

abstract interface class LevelRepository {
  Future<LevelDefinition> loadPreview();
  Future<List<LevelDefinition>> loadLevels();
}

/// Categories used by the existing online catalog and gallery filters.
const onlinePictureCategories = <String>{
  'nature',
  'animals',
  'objects',
  'patterns',
  'space',
};

/// Only explicitly downloaded online pictures are persisted locally.
/// Categories are stored separately from the immutable level JSON so existing
/// downloads and their progress remain compatible.
abstract interface class OnlineLevelStorage {
  Future<List<LevelDefinition>> readDownloadedLevels();
  Future<Map<String, String>> readDownloadedCategories();
  Future<void> saveDownloadedLevel(
    LevelDefinition level, {
    required String category,
  });
  Future<void> saveDownloadedCategory(String id, String category);
  Future<void> removeDownloadedLevel(String id);
}

abstract interface class ProgressRepository {
  Future<ProgressSnapshot?> read(LevelDefinition level);
  Future<void> write(ProgressSnapshot progress);
}

abstract interface class PreferencesRepository {
  Future<String?> readLanguage();
  Future<void> writeLanguage(String language);
}

/// Persist only the identifier of the most recently opened painting.
abstract interface class RecentArtworkRepository {
  Future<String?> readRecentArtworkId();
  Future<void> writeRecentArtworkId(String id);
  Future<void> clearRecentArtworkId();
}

/// Versioned compact bitset; stored independently of immutable level assets.
final class ProgressSnapshot {
  ProgressSnapshot({
    required this.levelId,
    required this.levelVersion,
    required this.levelChecksum,
    required this.cellCount,
    required this.generation,
    required this.revision,
    required Uint8List bits,
  }) : bits = Uint8List.fromList(bits).asUnmodifiableView() {
    if (cellCount < 1 ||
        cellCount > 65536 ||
        generation < 0 ||
        revision < 0 ||
        bits.length != (cellCount + 7) ~/ 8 ||
        (cellCount % 8 != 0 && bits.last >> (cellCount % 8) != 0)) {
      throw const FormatException('Invalid progress bitset.');
    }
  }

  factory ProgressSnapshot.fromJson(
    Map<String, Object?> json,
    LevelDefinition level,
  ) {
    try {
      if (json['schemaVersion'] != 1 ||
          json['levelId'] != level.id ||
          json['levelVersion'] != level.contentVersion ||
          json['levelChecksum'] != level.checksum ||
          json['cellCount'] != level.cells.length) {
        throw const FormatException('Progress belongs to a different level.');
      }
      final result = ProgressSnapshot(
        levelId: level.id,
        levelVersion: level.contentVersion,
        levelChecksum: level.checksum,
        cellCount: level.cells.length,
        generation: json['generation']! as int,
        revision: json['revision']! as int,
        bits: base64Decode(json['completedCells']! as String),
      );
      if (json['completedCount'] != result.completedCount) {
        throw const FormatException('Progress count mismatch.');
      }
      return result;
    } on TypeError {
      throw const FormatException('Malformed saved progress.');
    }
  }

  final String levelId;
  final int levelVersion;
  final String levelChecksum;
  final int cellCount;
  final int generation;
  final int revision;
  final Uint8List bits;

  bool isCompleted(int index) => bits[index ~/ 8] & (1 << (index % 8)) != 0;
  int get completedCount {
    var count = 0;
    for (final byte in bits) {
      var value = byte;
      while (value != 0) {
        value &= value - 1;
        count++;
      }
    }
    return count;
  }

  Map<String, Object> toJson() => {
    'schemaVersion': 1,
    'levelId': levelId,
    'levelVersion': levelVersion,
    'levelChecksum': levelChecksum,
    'cellCount': cellCount,
    'generation': generation,
    'revision': revision,
    'completedCells': base64Encode(bits),
    'completedCount': completedCount,
  };
}

abstract interface class AuthAdapter {
  Future<String?> currentUserId();
}

abstract interface class BillingAdapter {
  Future<bool> hasEntitlement(String productId);
}
