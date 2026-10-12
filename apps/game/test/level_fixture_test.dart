import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

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
    'all ten checksummed samples load, including 32, 64 and 128 grids',
    () async {
      final levels = await AssetLevelRepository().loadLevels();
      expect(levels, hasLength(10));
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
