import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/core/pixel_art_preview.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/products/product_configuration.dart';
import 'package:pixelhub/products/product_home.dart';

import 'bootstrap_test.dart' show TestRepository, fixture;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
    'real product manifests load shared levels with audience filtering',
    () async {
      for (final id in ['pixelhub', 'kids', 'art']) {
        final product = productById(id);
        final repository = AssetLevelRepository(
          catalogPath: product.offlineManifest,
        );
        final levels = await repository.loadLevels();
        final metadata = await repository.loadMetadata();
        expect(levels, isNotEmpty);
        for (final level in levels) {
          expect(product.categories, contains(metadata[level.id]!.category));
          expect(level.width, lessThanOrEqualTo(product.maxDimension));
          expect(level.height, lessThanOrEqualTo(product.maxDimension));
        }
      }
    },
  );
  test(
    'disabled coins grant access without changing wallet or ledger',
    () async {
      final store = MemoryPreferences();
      final library = LibraryController(store, store, coinsEnabled: false);
      await library.load();
      final level = fixture();
      final before = library.library.toJson();
      expect(library.canPaint(level), isTrue);
      await library.unlock(level);
      await library.spendToolCoins(500);
      await library.rewardCompletion(level);
      expect(library.library.toJson(), before);
      library.dispose();
    },
  );

  for (final id in ['kids', 'art']) {
    testWidgets('$id composes its own home and blocks disabled deep links', (
      tester,
    ) async {
      final product = productById(id);
      final store = MemoryPreferences();
      final repository = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          product: product,
          repository: repository,
          progressRepository: store,
          preferences: store,
        ),
      );
      repository.requests.single.complete(fixture());
      await tester.pumpAndSettle();
      expect(find.byType(ProductHome), findsOneWidget);
      expect(find.text(product.displayNameFa), findsOneWidget);
      expect(find.textContaining('سکه‌های من'), findsNothing);
      if (id == 'kids') {
        expect(find.byTooltip('پروفایل'), findsNothing);
        expect(find.text('۱. یک رنگ انتخاب کن'), findsOneWidget);
        // A square drawing in Kids must never fill a rectangular card.
        final previewFinder = find.byType(PixelArtPreview);
        await tester.ensureVisible(previewFinder);
        await tester.pumpAndSettle();
        final artworkFinder = find.descendant(
          of: previewFinder,
          matching: find.byType(CustomPaint),
        );
        final artwork = tester.getSize(artworkFinder.first);
        expect(artwork.width, lessThanOrEqualTo(176));
        expect(artwork.height, lessThanOrEqualTo(176));
        expect(artwork.width / artwork.height, closeTo(1, 0.001));
        final themedContext = tester.element(find.byType(ProductHome));
        final theme = Theme.of(themedContext);
        expect(theme.colorScheme.primary, const Color(0xff146B60));
        expect(theme.colorScheme.secondary, const Color(0xffFFC857));
        expect(theme.scaffoldBackgroundColor, const Color(0xffFFF9F1));
        expect(
          theme.filledButtonTheme.style?.minimumSize?.resolve({}),
          const Size(64, 68),
        );
      }
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
      final blockedRepository = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          product: product,
          repository: blockedRepository,
          progressRepository: store,
          preferences: store,
          initialRoute: '/import',
        ),
      );
      blockedRepository.requests.single.complete(fixture());
      await tester.pumpAndSettle();
      expect(find.byType(ProductHome), findsNothing);
      expect(find.text('این صفحه پیدا نشد.'), findsOneWidget);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    });
  }

  testWidgets('Kids home stays usable on narrow phones and tablets', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    for (final size in <Size>[
      const Size(320, 760),
      const Size(390, 844),
      const Size(820, 1024),
      const Size(1180, 920),
    ]) {
      tester.view.physicalSize = size;
      final store = MemoryPreferences();
      final repository = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          product: productById('kids'),
          repository: repository,
          progressRepository: store,
          preferences: store,
        ),
      );
      repository.requests.single.complete(fixture());
      await tester.pumpAndSettle();

      expect(find.byType(ProductHome), findsOneWidget);
      expect(find.text('۱. یک رنگ انتخاب کن'), findsOneWidget);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    }
  });

  test('unsupported product and disabled styles fail explicitly', () {
    expect(() => productById('animals'), throwsStateError);
    expect(productById('kids').allowsStyle('diamond'), isFalse);
    expect(productById('art').allowsStyle('canvas'), isTrue);
    expect(productById('kids').allowsPage('import'), isFalse);
  });
}
