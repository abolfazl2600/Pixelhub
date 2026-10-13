import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';

LevelDefinition onlineFixture(String id) => LevelDefinition(
  id: id,
  title: 'نمونه',
  titleEn: 'Sample',
  schemaVersion: 2,
  contentVersion: 1,
  width: 2,
  height: 2,
  palette: [0xff000000, 0xffffffff],
  cells: [0, 1, 1, 0],
);

MockClient serverFor(LevelDefinition level, {String category = 'animals'}) {
  final body = jsonEncode(level.toJson());
  final metadata = jsonEncode({
    'schemaVersion': 1,
    'pictures': [
      {
        'id': level.id,
        'version': level.contentVersion,
        'title': level.title,
        'titleEn': level.titleEn,
        'category': category,
        'width': level.width,
        'height': level.height,
        'bytes': utf8.encode(body).length,
        'checksum': level.checksum,
      },
    ],
  });
  return MockClient((request) async {
    if (request.url.path.endsWith('/catalog.json')) {
      return http.Response(metadata, 200);
    }
    if (request.url.path.endsWith('/${level.id}-v1.json')) {
      return http.Response(body, 200);
    }
    return http.Response('Not found', 404);
  });
}

/// An existing installation created before category metadata was persisted.
class LegacyDownloads implements OnlineLevelStorage {
  LegacyDownloads(this.level);
  final LevelDefinition level;
  final Map<String, String> savedCategories = {};
  bool deleted = false;

  @override
  Future<List<LevelDefinition>> readDownloadedLevels() async =>
      deleted ? [] : [level];

  @override
  Future<Map<String, String>> readDownloadedCategories() async =>
      Map.unmodifiable(savedCategories);

  @override
  Future<void> saveDownloadedLevel(
    LevelDefinition value, {
    required String category,
  }) async {
    throw StateError('Should not redownload an already stored level.');
  }

  @override
  Future<void> saveDownloadedCategory(String id, String category) async {
    if (!deleted && id == level.id) savedCategories[id] = category;
  }

  @override
  Future<void> removeDownloadedLevel(String id) async {
    if (id == level.id) {
      deleted = true;
      savedCategories.remove(id);
    }
  }
}

void main() {
  test(
    'fresh download stores category and a full offline restart restores it',
    () async {
      final level = onlineFixture('online-test-lion');
      final store = MemoryPreferences();
      final client = serverFor(level);
      addTearDown(client.close);

      final online = OnlineCatalogController(
        store,
        client: client,
        baseUrl: Uri.parse('https://example.test/online/'),
      );
      addTearDown(online.dispose);
      await online.checkForUpdates();
      expect(online.status, OnlineCatalogStatus.ready);
      expect(online.available, hasLength(1));
      await online.download(online.available.single);

      expect(await store.readDownloadedCategories(), {level.id: 'animals'});
      expect(online.available, isEmpty);
      expect(online.downloaded.single.checksum, level.checksum);

      // Reconstruct all controllers without requesting or injecting a catalog.
      final offline = OnlineCatalogController(
        store,
        baseUrl: Uri.parse('https://unreachable.test/online/'),
      );
      addTearDown(offline.dispose);
      await offline.loadDownloaded();
      expect(offline.pictures, isEmpty);
      expect(offline.categories[level.id], 'animals');

      final library = LibraryController(store, store);
      addTearDown(library.dispose);
      library.setDownloadedOnline(offline.downloaded);
      library.setOnlineCategories(offline.categories);
      expect(library.levels, hasLength(1));
      expect(library.category(library.levels.single), 'animals');
      expect(library.levels.single.checksum, level.checksum);
    },
  );

  test(
    'legacy downloads survive offline and are backfilled after reconnection',
    () async {
      final level = onlineFixture('online-legacy-lion');
      final store = LegacyDownloads(level);
      final offline = OnlineCatalogController(store);
      await offline.loadDownloaded();
      expect(offline.downloaded.single.id, level.id);
      final library = LibraryController(
        MemoryPreferences(),
        MemoryPreferences(),
      );
      addTearDown(library.dispose);
      library.setDownloadedOnline(offline.downloaded);
      library.setOnlineCategories(offline.categories);
      expect(library.category(level), 'patterns');
      offline.dispose();

      final client = serverFor(level);
      addTearDown(client.close);
      final connected = OnlineCatalogController(
        store,
        client: client,
        baseUrl: Uri.parse('https://example.test/online/'),
      );
      await connected.loadDownloaded();
      await connected.checkForUpdates();
      expect(connected.status, OnlineCatalogStatus.ready);
      expect(store.savedCategories[level.id], 'animals');
      expect(connected.available, isEmpty);
      connected.dispose();

      final restored = OnlineCatalogController(store);
      addTearDown(restored.dispose);
      await restored.loadDownloaded();
      library.setDownloadedOnline(restored.downloaded);
      library.setOnlineCategories(restored.categories);
      expect(library.category(level), 'animals');
      expect(restored.downloaded.single.checksum, level.checksum);
    },
  );

  test(
    'removing a download clears its category and permits redownload',
    () async {
      final level = onlineFixture('online-test-owl');
      final store = MemoryPreferences();
      await store.saveDownloadedLevel(level, category: 'animals');
      final controller = OnlineCatalogController(store);
      addTearDown(controller.dispose);
      await controller.loadDownloaded();
      expect(controller.categories[level.id], 'animals');
      await controller.removeDownloaded(level.id);
      expect(controller.downloaded, isEmpty);
      expect(controller.categories, isEmpty);
      expect(await store.readDownloadedLevels(), isEmpty);
      expect(await store.readDownloadedCategories(), isEmpty);
    },
  );

  test(
    'clearing all local data removes downloads and category metadata',
    () async {
      final level = onlineFixture('online-test-fox');
      final store = MemoryPreferences();
      await store.saveDownloadedLevel(level, category: 'animals');
      await store.clearPixelhubData();
      expect(await store.readDownloadedLevels(), isEmpty);
      expect(await store.readDownloadedCategories(), isEmpty);
    },
  );

  test('legacy data is not destroyed when catalog cannot be fetched', () async {
    final level = onlineFixture('online-test-existing');
    final store = LegacyDownloads(level);
    final client = MockClient((_) async => http.Response('offline', 503));
    addTearDown(client.close);
    final controller = OnlineCatalogController(
      store,
      client: client,
      baseUrl: Uri.parse('https://example.test/online/'),
    );
    addTearDown(controller.dispose);
    await controller.loadDownloaded();
    await controller.checkForUpdates();
    expect(controller.status, OnlineCatalogStatus.error);
    expect(controller.downloaded.single.id, level.id);
    expect(controller.categories, isEmpty);
    expect(store.savedCategories, isEmpty);
  });
}
