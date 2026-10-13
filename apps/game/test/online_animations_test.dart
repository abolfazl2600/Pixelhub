import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';
import 'package:pixelhub/features/painting/completed_artwork_preview.dart';
import 'package:pixelhub/l10n/generated/app_localizations.dart';

import 'online_categories_test.dart' show onlineFixture;

void main() {
  for (final count in [1, 2, 14]) {
    test('download $count frames with painting, retain offline, delete', () async {
      final level = onlineFixture('online-animation-$count');
      final animationDocument = {
        'schemaVersion': 1,
        'levelId': level.id,
        'levelVersion': 1,
        'levelChecksum': level.checksum,
        'frameDurationMs': 120,
        'frames': [
          for (var i = 0; i < count; i++)
            {'changes': [[i % 4, i % 2]]},
        ],
      };
      final animationBody = jsonEncode(animationDocument);
      final levelBody = jsonEncode(level.toJson());
      final metadata = jsonEncode({
        'schemaVersion': 1,
        'pictures': [{
          'id': level.id, 'version': 1,
          'title': level.title, 'titleEn': level.titleEn,
          'category': 'nature', 'width': 2, 'height': 2,
          'bytes': utf8.encode(levelBody).length, 'checksum': level.checksum,
          'animation': {
            'bytes': utf8.encode(animationBody).length,
            'sha256': sha256.convert(utf8.encode(animationBody)).toString(),
            'frameCount': count,
          },
        }],
      });
      final paths = <String>[];
      final client = MockClient((request) async {
        paths.add(request.url.path);
        if (request.url.path.endsWith('catalog.json')) {
          return http.Response(metadata, 200);
        }
        if (request.url.path.endsWith('levels/${level.id}-v1.json')) {
          return http.Response(levelBody, 200);
        }
        if (request.url.path.endsWith('animations/${level.id}-v1.json')) {
          return http.Response(animationBody, 200);
        }
        return http.Response('Not found', 404);
      });
      addTearDown(client.close);
      final store = MemoryPreferences();
      final online = OnlineCatalogController(
        store,
        client: client,
        baseUrl: Uri.parse('https://example.test/online/'),
      );
      addTearDown(online.dispose);
      await online.checkForUpdates();
      await online.download(online.available.single);
      expect(online.downloaded.single.id, level.id);
      expect(online.animations[level.id]!.frameCount, count);
      expect(paths.any((path) => path.contains('/animations/')), isTrue);
      expect(online.animations[level.id]!.pixelsFor(level, 0)[0], 0);

      final offline = OnlineCatalogController(store);
      addTearDown(offline.dispose);
      await offline.loadDownloaded();
      expect(offline.downloaded.single.id, level.id);
      expect(offline.animations[level.id]!.frameCount, count);
      await offline.removeDownloaded(level.id);
      expect((await store.readDownloadedAnimations([level])), isEmpty);
      expect(await store.readDownloadedLevels(), isEmpty);
    });
  }

  test('tampered animation rejects entire online download', () async {
    final level = onlineFixture('online-animation-tampered');
    final levelBody = jsonEncode(level.toJson());
    final body = jsonEncode({
      'schemaVersion': 1, 'levelId': level.id,
      'levelVersion': 1, 'levelChecksum': level.checksum,
      'frameDurationMs': 140,
      'frames': [{'changes': <Object>[]}],
    });
    final info = jsonEncode({
      'schemaVersion': 1,
      'pictures': [{
        'id': level.id, 'version': 1,
        'title': level.title, 'titleEn': level.titleEn,
        'category': 'nature', 'width': 2, 'height': 2,
        'bytes': utf8.encode(levelBody).length, 'checksum': level.checksum,
        'animation': {
          'bytes': utf8.encode(body).length,
          'sha256': List.filled(64, 'a').join(), 'frameCount': 1,
        },
      }],
    });
    final client = MockClient((request) async {
      if (request.url.path.endsWith('/catalog.json')) {
        return http.Response(info, 200);
      }
      if (request.url.path.contains('/levels/')) {
        return http.Response(levelBody, 200);
      }
      return http.Response(body, 200);
    });
    addTearDown(client.close);
    final store = MemoryPreferences();
    final online = OnlineCatalogController(store, client: client);
    addTearDown(online.dispose);
    await online.checkForUpdates();
    await online.download(online.available.single);
    expect(online.downloaded, isEmpty);
    expect(online.failedDownloadId, level.id);
    expect(await store.readDownloadedLevels(), isEmpty);
    expect((await store.readDownloadedAnimations([level])), isEmpty);
  });

  test('animation changes do not modify the original painting', () {
    final level = onlineFixture('online-unchanged');
    final animation = PixelAnimation.fromJson({
      'schemaVersion': 1,
      'levelId': level.id,
      'levelVersion': 1,
      'levelChecksum': level.checksum,
      'frameDurationMs': 150,
      'frames': [
        {'changes': <Object>[]},
        {'changes': [[0, 1], [3, 1]]},
      ],
    }, level);
    final checksum = level.checksum;
    expect(animation.pixelsFor(level, 1), [1, 1, 1, 1]);
    expect(level.cells, [0, 1, 1, 0]);
    expect(level.checksum, checksum);
  });

  testWidgets('completed image exposes animation and still controls', (
    tester,
  ) async {
    final level = onlineFixture('online-widget-animation');
    final animation = PixelAnimation.fromJson({
      'schemaVersion': 1, 'levelId': level.id,
      'levelVersion': 1, 'levelChecksum': level.checksum,
      'frameDurationMs': 200,
      'frames': [
        {'changes': <Object>[]},
        {'changes': [[0, 1]]},
      ],
    }, level);
    await tester.pumpWidget(MaterialApp(
      locale: const Locale('fa'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      home: Scaffold(body: CompletedArtworkPreview(
        level: level, animation: animation,
      )),
    ));
    expect(find.byKey(const ValueKey('animation-frame')), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('still-artwork')));
    await tester.pump();
    expect(find.byKey(const ValueKey('animation-frame')), findsNothing);
    await tester.tap(find.byKey(const ValueKey('animated-artwork')));
    await tester.pump();
    expect(find.byKey(const ValueKey('animation-frame')), findsOneWidget);
  });
}
