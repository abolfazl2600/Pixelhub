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
    expect(level.schemaVersion, 1);
    expect(level.contentVersion, 1);
    expect(level.width, 16);
    expect(level.height, 16);
    expect(level.cells, hasLength(256));
    expect(level.palette, hasLength(6));
    expect(() => level.cells.add(0), throwsUnsupportedError);
  });

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
      () => LevelDefinition.fromJson({
        ...json,
        'palette': ['bad-color'],
      }),
      throwsFormatException,
    );
  });
}
