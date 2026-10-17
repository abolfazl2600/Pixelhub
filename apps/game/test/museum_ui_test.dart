import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/museum/museum_room_painter.dart';
import 'package:pixelhub/features/museum/museum_theme_painter.dart';
import 'package:pixelhub/features/museum/pixel_sleeping_cat.dart';

import 'bootstrap_test.dart' show TestRepository, fixture;

Future<void> pumpMuseumApp(
  WidgetTester tester,
  MemoryPreferences store, {
  String? initialRoute,
}) async {
  final repository = TestRepository();
  await tester.pumpWidget(
    PixelhubApp(
      repository: repository,
      progressRepository: store,
      artworkRepository: store,
      preferences: store,
      initialRoute: initialRoute,
    ),
  );
  repository.requests.single.complete(fixture());
  await tester.pumpAndSettle();
}

Future<void> completeTestPicture(MemoryPreferences store) async {
  final level = fixture();
  final session = PaintingSession(level);
  for (var i = 0; i < level.cells.length; i++) {
    session.selectColor(level.cells[i]);
    session.paintCell(i);
  }
  await store.write(session.snapshot);
}

void main() {
  testWidgets('all four high-detail museum rooms paint at 180x240', (
    tester,
  ) async {
    for (final (theme, wall) in [
      ('classic', 'cream'),
      ('royal', 'emerald'),
      ('sky', 'blue'),
      ('botanical', 'sage'),
    ]) {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 360,
                height: 480,
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: CustomPaint(painter: MuseumRoomPainter(wall)),
                    ),
                    Positioned.fill(
                      child: CustomPaint(
                        painter: MuseumThemeDetailsPainter(theme),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
      expect(tester.takeException(), isNull, reason: theme);
    }
  });

  testWidgets('the museum starts empty, with six pixels slots and controls', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 844);
    addTearDown(tester.view.reset);

    final store = MemoryPreferences();
    await pumpMuseumApp(tester, store);
    await tester.tap(find.byKey(const ValueKey('open-museum')));
    await tester.pumpAndSettle();

    expect(find.text('موزه من'), findsOneWidget);
    expect(find.text('اتاق اول'), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-pixel-room')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-slot-0')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-slot-5')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-frames-button')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-walls-button')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-arrange-button')), findsOneWidget);
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint && widget.painter is MuseumRoomPainter,
      ),
      findsOneWidget,
    );
    expect(MuseumRoomPainter.pixelWidth, 180);
    expect(MuseumRoomPainter.pixelHeight, 240);
    expect(PixelSleepingCat.pixelWidth, 150);
    expect(PixelSleepingCat.pixelHeight, 80);
    // Approximately 40% more pixels across each axis, not an enlarged bitmap.
    expect(180 / 128, closeTo(1.4, .01));
    expect(240 / 172, closeTo(1.4, .01));
    expect(150 / 104, closeTo(1.4, .05));
    expect(80 / 56, closeTo(1.4, .05));
    expect(find.byKey(const ValueKey('museum-sleeping-cat')), findsOneWidget);
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint && widget.painter is PixelCatBodyPainter,
      ),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('four pixel room styles can be selected and restored', (
    tester,
  ) async {
    final store = MemoryPreferences();
    await completeTestPicture(store);
    await pumpMuseumApp(tester, store, initialRoute: '/museum');

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('museum-themes-button')),
      180,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.byKey(const ValueKey('museum-themes-button')));
    await tester.pumpAndSettle();

    expect(find.text('طرح موزه'), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-theme-classic')), findsOneWidget);
    expect(find.byKey(const ValueKey('museum-theme-royal')), findsOneWidget);
    // GridView builds lazily; the second row may be outside the viewport.
    final selector = tester.widget<GridView>(find.byType(GridView));
    expect(selector.childrenDelegate.estimatedChildCount, 4);
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint &&
            widget.painter is MuseumThemeThumbnailPainter,
      ),
      findsWidgets,
    );

    await tester.tap(find.byKey(const ValueKey('museum-theme-royal')));
    await tester.pumpAndSettle();
    final royal = await store.readMuseum();
    expect(royal.theme, 'royal');
    expect(royal.wall, 'emerald');
    expect(royal.frame, 'gold');
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint &&
            widget.painter is MuseumThemeDetailsPainter &&
            (widget.painter! as MuseumThemeDetailsPainter).theme == 'royal',
      ),
      findsOneWidget,
    );

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await pumpMuseumApp(tester, store, initialRoute: '/museum');
    expect((await store.readMuseum()).theme, 'royal');
    expect((await store.readMuseum()).slots, everyElement(isNull));
    expect(find.byKey(const ValueKey('museum-sleeping-cat')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('the sleeping cat flicks only its pixel tail slowly', (
    tester,
  ) async {
    final store = MemoryPreferences();
    await pumpMuseumApp(tester, store, initialRoute: '/museum');

    int tailFrame() {
      final paint = tester.widget<CustomPaint>(
        find.byWidgetPredicate(
          (widget) =>
              widget is CustomPaint && widget.painter is PixelCatTailPainter,
        ),
      );
      return (paint.painter! as PixelCatTailPainter).frame;
    }

    expect(tailFrame(), 0);
    await tester.pump(const Duration(milliseconds: 1100));
    expect(tailFrame(), 1);
    await tester.pump(const Duration(milliseconds: 1100));
    expect(tailFrame(), 2);
    await tester.pump(const Duration(milliseconds: 1100));
    expect(tailFrame(), 1);
    await tester.pump(const Duration(milliseconds: 1100));
    expect(tailFrame(), 0);

    // The static scenery and sleeping body never need an animation tick.
    expect(
      const MuseumRoomPainter(
        'sage',
      ).shouldRepaint(const MuseumRoomPainter('sage')),
      isFalse,
    );
    expect(
      const PixelCatBodyPainter().shouldRepaint(const PixelCatBodyPainter()),
      isFalse,
    );
    expect(
      const PixelCatTailPainter(1).shouldRepaint(const PixelCatTailPainter(0)),
      isTrue,
    );

    // Disposing the museum must cancel its periodic sprite updates.
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump(const Duration(seconds: 5));
    expect(tester.takeException(), isNull);
  });

  testWidgets('completed art can be hung and the room survives restart', (
    tester,
  ) async {
    final store = MemoryPreferences();
    await completeTestPicture(store);
    await pumpMuseumApp(tester, store, initialRoute: '/museum');
    expect(find.text('موزه من'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('museum-slot-0')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('museum-choice-sunflower')));
    await tester.pumpAndSettle();
    expect((await store.readMuseum()).slots.first, 'sunflower');

    // ListView lazily builds the controls below the tall pixel room.
    // Scroll to construct the toolbar before interacting with it.
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('museum-walls-button')),
      180,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.byKey(const ValueKey('museum-walls-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('museum-option-sage')));
    await tester.pumpAndSettle();
    expect((await store.readMuseum()).wall, 'sage');

    await tester.tap(find.byKey(const ValueKey('museum-frames-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('museum-option-gold')));
    await tester.pumpAndSettle();
    expect((await store.readMuseum()).frame, 'gold');

    await tester.tap(find.byKey(const ValueKey('museum-arrange-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('museum-option-staggered')));
    await tester.pumpAndSettle();
    expect((await store.readMuseum()).arrangement, 'staggered');

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await pumpMuseumApp(tester, store, initialRoute: '/museum');
    expect(find.text('۱ از ۶ تابلو'), findsOneWidget);
    expect((await store.readMuseum()).slots.first, 'sunflower');
    expect((await store.readMuseum()).frame, 'gold');
    expect((await store.readMuseum()).wall, 'sage');
    expect((await store.readMuseum()).arrangement, 'staggered');
    expect(tester.takeException(), isNull);
  });

  for (final language in ['fa', 'en']) {
    testWidgets('museum picker marks already hung artworks ($language)', (
      tester,
    ) async {
      final store = MemoryPreferences();
      await store.writeLanguage(language);
      await completeTestPicture(store);
      await pumpMuseumApp(tester, store, initialRoute: '/museum');

      await tester.tap(find.byKey(const ValueKey('museum-slot-0')));
      await tester.pumpAndSettle();
      final choice = find.byKey(const ValueKey('museum-choice-sunflower'));
      expect(
        find.text(
          language == 'fa' ? 'نقاشی‌های آماده نصب' : 'Available to hang',
        ),
        findsOneWidget,
      );
      await tester.tap(choice);
      await tester.pumpAndSettle();

      // A mounted artwork stays in the picker for other slots, but is
      // distinguished from an unmounted painting and identifies its frame.
      await tester.tap(find.byKey(const ValueKey('museum-slot-1')));
      await tester.pumpAndSettle();
      expect(
        find.text(
          language == 'fa'
              ? 'تابلوهای نصب‌شده در موزه'
              : 'Already on the museum wall',
        ),
        findsOneWidget,
      );
      expect(
        find.text(
          language == 'fa'
              ? 'روی دیوار · قاب ۱ — برای جابه‌جایی لمس کنید'
              : 'On the wall · Frame 1 — tap to move',
        ),
        findsOneWidget,
      );
      expect(
        (tester.widget<ListTile>(choice).trailing! as Icon).icon,
        Icons.collections_bookmark_rounded,
      );

      await tester.tap(choice);
      await tester.pumpAndSettle();
      final moved = await store.readMuseum();
      expect(moved.slots[0], isNull);
      expect(moved.slots[1], 'sunflower');
      expect(moved.slots.where((id) => id == 'sunflower'), hasLength(1));

      await tester.tap(find.byKey(const ValueKey('museum-slot-1')));
      await tester.pumpAndSettle();
      expect(
        find.text(
          language == 'fa' ? 'در همین قاب نصب شده' : 'Hanging in this frame',
        ),
        findsOneWidget,
      );
      expect(
        (tester.widget<ListTile>(choice).trailing! as Icon).icon,
        Icons.check_circle_rounded,
      );
    });
  }

  testWidgets('completed-art deep link lets player choose museum slot', (
    tester,
  ) async {
    final store = MemoryPreferences();
    await completeTestPicture(store);
    await pumpMuseumApp(
      tester,
      store,
      initialRoute: '/museum?artwork=sunflower',
    );
    expect(
      find.byKey(const ValueKey('museum-pending-artwork')),
      findsOneWidget,
    );
    await tester.tap(find.byKey(const ValueKey('museum-slot-2')));
    await tester.pumpAndSettle();
    expect((await store.readMuseum()).slots[2], 'sunflower');
    expect(find.byKey(const ValueKey('museum-pending-artwork')), findsNothing);
    expect(tester.takeException(), isNull);
  });
}
