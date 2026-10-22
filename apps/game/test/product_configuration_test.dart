import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
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

  test('unsupported product and disabled styles fail explicitly', () {
    expect(() => productById('animals'), throwsStateError);
    expect(productById('kids').allowsStyle('diamond'), isFalse);
    expect(productById('art').allowsStyle('canvas'), isTrue);
    expect(productById('kids').allowsPage('import'), isFalse);
  });
}
