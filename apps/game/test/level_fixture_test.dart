import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/artwork_categories.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('bundled level loads through the production repository', () async {
    final level = await AssetLevelRepository().loadPreview();
    expect(level.id, 'sunflower');
    expect(level.schemaVersion, 2);
    expect(level.contentVersion, 2);
    expect(level.width, 16);
    expect(level.height, 16);
    expect(level.cells, hasLength(256));
    expect(level.palette, hasLength(6));
    expect(() => level.cells.add(0), throwsUnsupportedError);
  });

  test(
    'all forty-nine checksummed pictures load, including 32, 64 and 128 grids',
    () async {
      final levels = await AssetLevelRepository().loadLevels();
      expect(levels, hasLength(49));
      expect(
        levels.map((l) => l.width).toSet(),
        containsAll([16, 32, 64, 128]),
      );
      for (final level in levels) {
        expect(
          LevelDefinition.fromJson(level.toJson()).checksum,
          level.checksum,
        );
        expect(level.titleEn, isNotEmpty);
      }
    },
  );

  test(
    'every public gallery category has four bundled offline pictures',
    () async {
    const newIds = <String>{
      'offline-mona-lisa',
      'offline-starry-night',
      'offline-great-wave',
      'offline-girl-pearl',
      'offline-azadi-tower',
      'offline-persepolis',
      'offline-siosepol',
      'offline-nasir-molk',
      'offline-shamsa',
    };
    final repository = AssetLevelRepository();
    final levels = await repository.loadLevels();
    final metadata = await repository.loadMetadata();
    final counts = <String, int>{
      for (final category in publicArtworkCategories) category: 0,
    };

    expect(levels.map((art) => art.id).toSet(), hasLength(49));
    expect(
      levels.where((art) => newIds.contains(art.id)).length,
      newIds.length,
    );
    for (final level in levels) {
      final category = metadata[level.id]?.category;
      expect(
        counts.containsKey(category),
        isTrue,
        reason: 'Bundled level ${level.id} needs a public category.',
      );
      counts[category!] = counts[category]! + 1;
    }
    for (final category in publicArtworkCategories) {
      expect(
        counts[category],
        greaterThanOrEqualTo(4),
        reason: '$category must be usable with no network downloads.',
      );
    }
    expect(counts['masterpieces'], 4);
    expect(counts['persian_architecture'], 4);
    expect(counts['patterns'], 4);
    },
  );

  test('unsupported schema and malformed cells are rejected', () async {
    final source = await rootBundle.loadString(LevelAssets.sunflower);
    final json = jsonDecode(source) as Map<String, Object?>;
    expect(
      () => LevelDefinition.fromJson({...json, 'schemaVersion': 99}),
      throwsFormatException,
    );
    expect(
      () => LevelDefinition.fromJson({
        ...json,
        'cells': [99],
      }),
      throwsFormatException,
    );
    expect(() => LevelDefinition.fromJson({}), throwsFormatException);
    expect(
      () => LevelDefinition.fromJson({...json, 'checksum': 'bad'}),
      throwsFormatException,
    );
    expect(
      () => LevelDefinition.fromJson({
        ...json,
        'palette': ['bad-color'],
      }),
      throwsFormatException,
    );
  });
}
