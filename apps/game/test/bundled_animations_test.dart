import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('bundled animation catalog matches immutable paintings', () async {
    final levels = await AssetLevelRepository().loadLevels();
    final byId = {for (final level in levels) level.id: level};
    final source = await rootBundle.loadString('assets/animations/catalog.json');
    final catalog = jsonDecode(source) as Map<String, dynamic>;
    expect(catalog, isNotEmpty);
    for (final entry in catalog.entries) {
      final level = byId[entry.key]!;
      final original = List<int>.of(level.cells);
      final raw = await rootBundle.loadString('assets/animations/${entry.value}');
      final animation = PixelAnimation.fromJson(
        jsonDecode(raw) as Map<String, Object?>,
        level,
      );
      expect(animation.frameCount, greaterThan(1));
      final poses = <String>{};
      for (var frame = 0; frame < animation.frameCount; frame++) {
        final pixels = animation.pixelsFor(level, frame);
        expect(pixels, hasLength(original.length));
        expect(pixels.every((p) => p >= 0 && p < level.palette.length), isTrue);
        poses.add(pixels.join(','));
      }
      expect(poses.length, greaterThan(1), reason: level.id);
      expect(level.cells, original);
      expect(animation.pixelsFor(level, 0), original);
      expect(animation.pixelsFor(level, animation.frameCount - 1), original);
    }
  });
}
