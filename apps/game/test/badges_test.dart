import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/badges/badge_controller.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';

LevelDefinition animal(int index) => LevelDefinition(
  id: 'animal-$index',
  title: 'حیوان',
  titleEn: 'Animal',
  schemaVersion: 2,
  contentVersion: 1,
  width: 2,
  height: 2,
  palette: [0xff000000, 0xffffffff],
  cells: [0, 1, 0, 1],
);

ProgressSnapshot finished(LevelDefinition level) => ProgressSnapshot(
  levelId: level.id,
  levelVersion: level.contentVersion,
  levelChecksum: level.checksum,
  cellCount: level.cells.length,
  generation: 0,
  revision: 1,
  bits: Uint8List.fromList([15]),
);

const catalog = '''
{
  "version": 1,
  "badges": [
    {
      "id": "animal_first",
      "titleFa": "اولین دوست حیوانات",
      "titleEn": "First Animal Friend",
      "descriptionFa": "اولین حیوان",
      "descriptionEn": "One animal",
      "category": "animals",
      "required": 1,
      "image": "images/animal_first.png",
      "bytes": 100,
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    {
      "id": "animal_five",
      "titleFa": "دوستدار حیوانات",
      "titleEn": "Animal Lover",
      "descriptionFa": "پنج حیوان",
      "descriptionEn": "Five animals",
      "category": "animals",
      "required": 5,
      "image": "images/animal_five.png",
      "bytes": 100,
      "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  ]
}
''';

void main() {
  test(
    'online badges unlock after one and five distinct completed animals',
    () async {
      final store = MemoryPreferences();
      final library = LibraryController(store, store);
      final levels = List.generate(5, animal);
      library.setCatalog(levels, {});
      library.setOnlineCategories({
        for (final item in levels) item.id: 'animals',
      });

      final client = MockClient((request) async {
        if (request.url.path.endsWith('/catalog.json')) {
          return http.Response(catalog, 200);
        }
        return http.Response('missing icon', 404);
      });
      final badges = BadgeController(
        library,
        store,
        baseUrl: Uri.parse('https://example.test/badges/'),
        client: client,
      );
      addTearDown(() {
        badges.dispose();
        library.dispose();
        client.close();
      });
      await badges.initialize();
      await badges.refresh();
      // Remote refresh starts during initialize, so wait for its completion.
      while (badges.refreshing) {
        await Future<void>.delayed(const Duration(milliseconds: 1));
      }
      expect(badges.badges.length, 2);
      expect(badges.earnedCount, 0);

      library.updateProgress(finished(levels.first));
      await badges.settle();
      expect(badges.isEarned(badges.badges.first), isTrue);
      expect(badges.isEarned(badges.badges.last), isFalse);
      expect(await store.readEarnedBadges(), contains('animal_first'));

      for (final item in levels.skip(1)) {
        library.updateProgress(finished(item));
      }
      await badges.settle();
      expect(badges.earnedCount, 2);
      expect(
        await store.readEarnedBadges(),
        containsAll(<String>['animal_first', 'animal_five']),
      );

      // Resetting visible progress cannot take away an already earned badge.
      library.updateProgress(
        ProgressSnapshot(
          levelId: levels.first.id,
          levelVersion: levels.first.contentVersion,
          levelChecksum: levels.first.checksum,
          cellCount: 4,
          generation: 1,
          revision: 2,
          bits: Uint8List.fromList([0]),
        ),
      );
      await badges.settle();
      expect(badges.earnedCount, 2);

      // Award data is restored after constructing a new controller.
      final restored = BadgeController(
        library,
        store,
        baseUrl: Uri.parse('https://example.test/badges/'),
        client: client,
      );
      addTearDown(restored.dispose);
      await restored.initialize();
      expect(restored.earnedCount, 2);
    },
  );

  test('reject duplicate or unsafe remote icon definitions', () {
    expect(parseBadgeCatalog(catalog).first.requiredCount, 1);
    final unsafe = catalog.replaceFirst(
      'images/animal_first.png',
      '../evil.png',
    );
    expect(() => parseBadgeCatalog(unsafe), throwsFormatException);
    final duplicate = jsonDecode(catalog) as Map<String, dynamic>;
    (duplicate['badges'] as List).add((duplicate['badges'] as List).first);
    expect(
      () => parseBadgeCatalog(jsonEncode(duplicate)),
      throwsFormatException,
    );
  });
}
