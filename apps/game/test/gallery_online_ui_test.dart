import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/gallery_screen.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';
import 'package:pixelhub/l10n/generated/app_localizations.dart';

import 'bootstrap_test.dart' show fixture;
import 'online_categories_test.dart' show onlineFixture, serverFor;

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
      scrollable: find
          .descendant(
            of: find.byType(CustomScrollView),
            matching: find.byType(Scrollable),
          )
          .first,
    );
    expect(find.text('جانوران آنلاین'), findsOneWidget);
    expect(
      online.available.where((art) => art.category == 'animals'),
      hasLength(9),
    );

    final firstOnlineCard = find.byKey(
      const ValueKey('online-picture-online-gallery-test-0'),
    );
    final firstDownloadButton = find.byKey(
      const ValueKey('online-download-online-gallery-test-0'),
    );
    await tester.scrollUntilVisible(
      firstDownloadButton,
      250,
      scrollable: find
          .descendant(
            of: find.byType(CustomScrollView),
            matching: find.byType(Scrollable),
          )
          .first,
    );
    expect(firstOnlineCard, findsOneWidget);
    expect(firstDownloadButton, findsOneWidget);
    final image = find.descendant(
      of: firstOnlineCard,
      matching: find.byType(Image),
    );
    expect(image, findsOneWidget);
    expect(
      tester.getTopLeft(firstDownloadButton).dy,
      greaterThanOrEqualTo(tester.getBottomLeft(image).dy),
    );
    expect(
      find.descendant(
        of: firstOnlineCard,
        matching: find.text('تصاویر آنلاین'),
      ),
      findsNothing,
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
      scrollable: find
          .descendant(
            of: find.byType(CustomScrollView),
            matching: find.byType(Scrollable),
          )
          .first,
    );
    expect(find.text('اشیا آنلاین'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('downloaded online picture opens painting immediately', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 900);
    addTearDown(tester.view.reset);
    final level = onlineFixture('online-gallery-direct-open');
    final client = serverFor(level);
    addTearDown(client.close);
    final store = MemoryPreferences();
    final library = LibraryController(store, store);
    addTearDown(library.dispose);
    library.setCatalog([fixture()], {});
    await library.load();
    final online = OnlineCatalogController(
      store,
      client: client,
      baseUrl: Uri.parse('https://example.test/online/'),
    );
    addTearDown(online.dispose);
    online.addListener(() {
      if (online.isLoaded) library.setDownloadedOnline(online.downloaded);
      library.setOnlineCategories(online.categories);
    });
    await online.loadDownloaded();

    final router = GoRouter(
      initialLocation: '/gallery',
      routes: [
        GoRoute(
          path: '/gallery',
          builder: (context, state) => ListenableBuilder(
            listenable: library,
            builder: (context, _) =>
                GalleryScreen(library: library, online: online),
          ),
        ),
        GoRoute(
          path: '/painting/:id',
          builder: (context, state) =>
              Scaffold(body: Text('Painting ${state.pathParameters['id']}')),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      MaterialApp.router(
        routerConfig: router,
        locale: const Locale('fa'),
        supportedLocales: AppLocalizations.supportedLocales,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
      ),
    );
    await tester.pumpAndSettle();
    final downloadKey = ValueKey('online-download-${level.id}');
    await tester.scrollUntilVisible(
      find.byKey(downloadKey),
      280,
      scrollable: find
          .descendant(
            of: find.byType(CustomScrollView),
            matching: find.byType(Scrollable),
          )
          .first,
    );
    await tester.tap(find.byKey(downloadKey));
    await tester.pumpAndSettle();
    expect(online.downloaded.map((value) => value.id), contains(level.id));
    expect(find.text('Painting ${level.id}'), findsOneWidget);
    expect(
      router.routeInformationProvider.value.uri.path,
      '/painting/${level.id}',
    );
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
