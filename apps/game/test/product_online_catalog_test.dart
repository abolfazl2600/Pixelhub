import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';

import 'online_categories_test.dart' show onlineFixture;

Map<String, Object?> picture(String id, String category, {int size = 2}) {
  final level = onlineFixture(id);
  return {
    'id': id,
    'version': 1,
    'title': level.title,
    'titleEn': level.titleEn,
    'category': category,
    'width': size,
    'height': size,
    'bytes': 100,
    'checksum': level.checksum,
  };
}

void main() {
  test(
    'product manifest identity and shared asset paths remain separate',
    () async {
      final requested = <Uri>[];
      final client = MockClient((request) async {
        requested.add(request.url);
        return http.Response(
          jsonEncode({
            'schemaVersion': 1,
            'productId': 'kids',
            'pictures': [
              picture('online-child', 'animals'),
              picture('online-art', 'masterpieces'),
              picture('online-large', 'animals', size: 64),
            ],
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });
      final controller = OnlineCatalogController(
        MemoryPreferences(),
        client: client,
        baseUrl: Uri.parse('https://example.test/online/'),
        productId: 'kids',
        catalogPath: 'products/kids/catalog.json',
        allowedCategories: ['animals'],
        maxDimension: 32,
      );
      addTearDown(controller.dispose);
      await controller.checkForUpdates();
      expect(controller.status, OnlineCatalogStatus.ready);
      expect(controller.pictures.map((p) => p.id), ['online-child']);
      expect(requested.single.path, '/online/products/kids/catalog.json');
      expect(
        controller.previewUrl(controller.pictures.single).path,
        '/online/previews/online-child-v1.png',
      );
    },
  );

  test('another product manifest cannot populate the gallery', () async {
    final controller = OnlineCatalogController(
      MemoryPreferences(),
      productId: 'art',
      client: MockClient(
        (request) async => http.Response(
          jsonEncode({
            'schemaVersion': 1,
            'productId': 'kids',
            'pictures': [picture('online-child', 'animals')],
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        ),
      ),
    );
    addTearDown(controller.dispose);
    await controller.checkForUpdates();
    expect(controller.status, OnlineCatalogStatus.error);
    expect(controller.pictures, isEmpty);
  });

  test('disabled online service never makes network requests', () async {
    var requests = 0;
    final controller = OnlineCatalogController(
      MemoryPreferences(),
      enabled: false,
      client: MockClient((request) async {
        requests++;
        return http.Response('{}', 500);
      }),
    );
    addTearDown(controller.dispose);
    await controller.loadDownloaded();
    await controller.checkForUpdates();
    expect(controller.isLoaded, isTrue);
    expect(requests, 0);
    expect(controller.pictures, isEmpty);
  });

  test(
    'cached downloads are re-filtered without deleting durable artwork',
    () async {
      final store = MemoryPreferences();
      await store.saveDownloadedLevel(
        onlineFixture('online-animal'),
        category: 'animals',
      );
      await store.saveDownloadedLevel(
        onlineFixture('online-art'),
        category: 'masterpieces',
      );
      final controller = OnlineCatalogController(
        store,
        productId: 'art',
        allowedCategories: ['masterpieces'],
      );
      addTearDown(controller.dispose);
      await controller.loadDownloaded();
      expect(controller.downloaded.map((p) => p.id), ['online-art']);
      expect(await store.readDownloadedLevels(), hasLength(2));
    },
  );
}
