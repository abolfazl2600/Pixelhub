import 'package:flutter/foundation.dart'
    show TargetPlatform, debugDefaultTargetPlatformOverride;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/core/pixel_art_preview.dart';

import 'bootstrap_test.dart' show TestRepository, fixture;

// Asset I/O must run in real async time, outside the widget fake clock.
Future<void> pumpAssetApp(WidgetTester tester, {String? initialRoute}) async {
  final level = await tester.runAsync(AssetLevelRepository().loadPreview);
  final repository = TestRepository();
  await tester.pumpWidget(
    PixelhubApp(
      repository: repository,
      initialRoute: initialRoute,
      progressRepository: MemoryPreferences(),
      preferences: MemoryPreferences(),
    ),
  );
  repository.requests.single.complete(level!);
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('splash loads asset and navigates to preview and back', (
    tester,
  ) async {
    final repository = TestRepository();
    await tester.pumpWidget(
      PixelhubApp(
        repository: repository,
        progressRepository: MemoryPreferences(),
        preferences: MemoryPreferences(),
      ),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    repository.requests.single.complete(fixture());
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
    expect(
      Directionality.of(tester.element(find.byType(PixelArtPreview))),
      TextDirection.rtl,
    );
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('open-preview')),
      250,
    );
    await tester.tap(find.byKey(const ValueKey('open-preview')));
    await tester.pumpAndSettle();
    expect(find.text('رنگ‌ها'), findsOneWidget);
    await tester.tap(find.byTooltip('بازگشت به خانه'));
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  for (final language in ['fa', 'en']) {
    testWidgets('coins only are displayed in Home and Profile ($language)', (
      tester,
    ) async {
      final store = MemoryPreferences();
      await store.writeLibrary(ArtworkLibrary(coins: 87, totalPoints: 1234));
      await store.writeLanguage(language);
      final repository = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          repository: repository,
          progressRepository: store,
          artworkRepository: store,
          preferences: store,
        ),
      );
      repository.requests.single.complete(fixture());
      await tester.pumpAndSettle();

      final coinLabel = language == 'fa' ? 'سکه‌های من' : 'My coins';
      final pointLabel = language == 'fa' ? 'امتیاز کل' : 'Total points';
      final coinDigits = language == 'fa' ? '۸۷' : '87';
      expect(find.textContaining(coinLabel), findsOneWidget);
      expect(find.textContaining(coinDigits), findsWidgets);
      expect(find.textContaining(pointLabel), findsNothing);

      GoRouter.of(
        tester.element(find.byKey(const ValueKey('home-scroll'))),
      ).go('/profile');
      await tester.pumpAndSettle();
      // The profile metrics appear below the header in a lazily built list.
      await tester.scrollUntilVisible(
        find.text(coinLabel),
        180,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.text(coinLabel), findsOneWidget);
      expect(find.text(coinDigits), findsOneWidget);
      expect(find.textContaining(pointLabel), findsNothing);
      expect((await store.readLibrary()).totalPoints, 1234);
      expect((await store.readLibrary()).coins, 87);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('failed bootstrap presents a working retry', (tester) async {
    final repository = TestRepository();
    await tester.pumpWidget(
      PixelhubApp(
        repository: repository,
        progressRepository: MemoryPreferences(),
        preferences: MemoryPreferences(),
      ),
    );
    repository.requests.single.completeError(StateError('missing asset'));
    await tester.pumpAndSettle();
    expect(find.text('بارگذاری تصویرها انجام نشد.'), findsOneWidget);
    await tester.tap(find.text('تلاش دوباره'));
    await tester.pump();
    repository.requests.last.complete(fixture());
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
  });

  for (final viewport in [
    const Size(360, 800),
    const Size(390, 844),
    const Size(430, 932),
    const Size(800, 360),
    const Size(1440, 900),
  ]) {
    testWidgets('full viewport frame at $viewport, safe scroll and back', (
      tester,
    ) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = viewport;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await pumpAssetApp(tester);
      final frame = find.byKey(const ValueKey('mobile-frame'));
      final width = viewport.width;
      expect(tester.getSize(frame).width, width);
      expect(tester.getTopLeft(frame).dx, (viewport.width - width) / 2);
      await tester.scrollUntilVisible(
        find.byKey(const ValueKey('open-preview')),
        200,
      );
      await tester.tap(find.byKey(const ValueKey('open-preview')));
      await tester.pumpAndSettle();
      // Palette stays pinned regardless of the page's vertical scroll.
      final palette = find.byKey(const ValueKey('color-palette-scroll'));
      expect(palette, findsOneWidget);
      expect(
        tester.getRect(palette).bottom,
        lessThanOrEqualTo(viewport.height),
      );
      expect(tester.takeException(), isNull);
      expect(tester.getSize(frame).width, width);
    });
  }

  testWidgets('desktop is capped, but tablets still use the whole viewport', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    debugDefaultTargetPlatformOverride = TargetPlatform.linux;
    addTearDown(tester.view.reset);

    tester.view.physicalSize = const Size(1440, 900);
    await pumpAssetApp(tester);

    final frame = find.byKey(const ValueKey('mobile-frame'));
    expect(tester.getSize(frame).width, 880);
    expect(tester.getTopLeft(frame).dx, 280);
    expect(
      MediaQuery.sizeOf(
        tester.element(find.byKey(const ValueKey('home-scroll'))),
      ).width,
      880,
    );
    expect(tester.takeException(), isNull);

    // Even on a desktop, a tablet-sized window is never letterboxed.
    tester.view.physicalSize = const Size(1024, 768);
    await tester.pumpAndSettle();
    expect(tester.getSize(frame).width, 1024);
    expect(tester.getTopLeft(frame).dx, 0);

    // Flutter checks foundation debug overrides before tearDown callbacks run.
    debugDefaultTargetPlatformOverride = null;
    expect(tester.takeException(), isNull);
  });

  testWidgets('large Android tablet stays full-width in landscape', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(1366, 1024);
    addTearDown(tester.view.reset);

    await pumpAssetApp(tester);
    final frame = find.byKey(const ValueKey('mobile-frame'));
    expect(tester.getSize(frame).width, 1366);
    expect(tester.getTopLeft(frame).dx, 0);
    expect(tester.takeException(), isNull);
  });

  testWidgets('direct painting route restores the local asset', (tester) async {
    await pumpAssetApp(tester, initialRoute: '/painting');
    expect(find.text('رنگ‌ها'), findsOneWidget);
    await tester.tap(find.byTooltip('بازگشت به خانه'));
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
  });

  testWidgets('system Back returns from the nested preview route', (
    tester,
  ) async {
    await pumpAssetApp(tester, initialRoute: '/painting');
    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
    expect(find.byTooltip('بازگشت به خانه'), findsNothing);
  });

  testWidgets('unknown route has a working Home recovery', (tester) async {
    await pumpAssetApp(tester, initialRoute: '/missing');
    expect(find.text('این صفحه پیدا نشد.'), findsOneWidget);
    await tester.tap(find.text('بازگشت به خانه'));
    await tester.pumpAndSettle();
    expect(find.text('کمی مکث،\nکمی رنگ.'), findsOneWidget);
  });

  testWidgets('safe insets and larger text remain scrollable', (tester) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(360, 640);
    tester.view.padding = const FakeViewPadding(top: 32, bottom: 24);
    tester.platformDispatcher.textScaleFactorTestValue = 1.5;
    addTearDown(tester.view.reset);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await pumpAssetApp(tester);
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('open-preview')),
      200,
    );
    await tester.tap(find.byKey(const ValueKey('open-preview')));
    await tester.pumpAndSettle();
    final palette = find.byKey(const ValueKey('color-palette-scroll'));
    expect(palette, findsOneWidget);
    expect(tester.getRect(palette).bottom, lessThanOrEqualTo(640));
    expect(tester.takeException(), isNull);
  });
}
