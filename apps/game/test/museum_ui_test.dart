import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/museum/museum_room_painter.dart';

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
