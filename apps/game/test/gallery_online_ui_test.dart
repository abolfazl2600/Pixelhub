import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/gallery_screen.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';
import 'package:pixelhub/l10n/generated/app_localizations.dart';

import 'bootstrap_test.dart' show fixture;

MockClient catalogClient() {
  final entries = [
    for (var i = 0; i < 15; i++)
      {
        'id': 'online-gallery-test-$i',
        'version': 1,
        'title': 'طرح آنلاین $i',
        'titleEn': 'Online art $i',
        'category': i < 9 ? 'animals' : 'objects',
        'width': 16,
        'height': 16,
        'bytes': 100,
        'checksum': List.filled(64, 'b').join(),
      },
  ];
  return MockClient((request) async {
    if (request.url.path.endsWith('catalog.json')) {
      return http.Response.bytes(
        utf8.encode(jsonEncode({'schemaVersion': 1, 'pictures': entries})),
        200,
      );
    }
    return http.Response('Not found', 404);
  });
}

void main() {
  testWidgets('online artwork follows the local category and is paginated', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 900);
    addTearDown(tester.view.reset);
    final store = MemoryPreferences();
    final library = LibraryController(store, store);
    addTearDown(library.dispose);
    final flower = fixture();
    library.setCatalog([flower], {});
    library.setOnlineCategories({flower.id: 'animals'});
    await library.load();
    final client = catalogClient();
    addTearDown(client.close);
    final online = OnlineCatalogController(
      store,
      client: client,
      baseUrl: Uri.parse('https://example.test/online/'),
    );
    addTearDown(online.dispose);

    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('fa'),
        supportedLocales: AppLocalizations.supportedLocales,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        home: GalleryScreen(library: library, online: online),
      ),
    );
    await tester.pumpAndSettle();
    expect(online.status, OnlineCatalogStatus.ready);
    expect(online.available, hasLength(15));
    expect(find.text('روی دستگاه'), findsOneWidget);
    expect(find.byKey(ValueKey('local-picture-${flower.id}')), findsOneWidget);

    // Selecting Animals keeps the local picture and filters online metadata.
    await tester.tap(find.widgetWithText(ChoiceChip, 'جانوران'));
    await tester.pumpAndSettle();
    expect(find.byKey(ValueKey('local-picture-${flower.id}')), findsOneWidget);
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('online-gallery-section')),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('جانوران آنلاین'), findsOneWidget);
    expect(
      online.available.where((art) => art.category == 'animals'),
      hasLength(9),
    );

    // Changing the chip resets pagination and the local empty state.
    await tester.drag(find.byType(CustomScrollView), const Offset(0, 2000));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(ChoiceChip, 'اشیا'));
    await tester.pumpAndSettle();
    expect(
      find.text('هنوز نقاشی‌ای از این دسته روی دستگاه نیست.'),
      findsOneWidget,
    );
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('online-gallery-section')),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('اشیا آنلاین'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('personal gallery remains entirely local', (tester) async {
    final store = MemoryPreferences();
    final library = LibraryController(store, store);
    addTearDown(library.dispose);
    await library.load();
    final client = catalogClient();
    addTearDown(client.close);
    final online = OnlineCatalogController(
      store,
      client: client,
      baseUrl: Uri.parse('https://example.test/online/'),
    );
    addTearDown(online.dispose);
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('fa'),
        supportedLocales: AppLocalizations.supportedLocales,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        home: GalleryScreen(library: library, online: online, personal: true),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('online-gallery-section')), findsNothing);
    expect(online.status, OnlineCatalogStatus.idle);
    expect(tester.takeException(), isNull);
  });
}
