import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/painting/painting_controller.dart';
import 'package:pixelhub/features/painting/painting_preview_screen.dart';

import 'bootstrap_test.dart' show fixture;

class CatalogLevels implements LevelRepository {
  CatalogLevels(this.levels);
  final List<LevelDefinition> levels;
  @override
  Future<LevelDefinition> loadPreview() async => levels.first;
  @override
  Future<List<LevelDefinition>> loadLevels() async => levels;
}

class FixedLevels implements LevelRepository {
  FixedLevels(this.level);
  final LevelDefinition level;
  @override
  Future<LevelDefinition> loadPreview() async => level;
  @override
  Future<List<LevelDefinition>> loadLevels() async => [level];
}

Future<PaintingController> pumpPainting(
  WidgetTester tester, {
  LevelDefinition? level,
  MemoryPreferences? storage,
}) async {
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = const Size(390, 1200);
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  final preferences = storage ?? MemoryPreferences();
  await tester.pumpWidget(
    PixelhubApp(
      repository: FixedLevels(level ?? fixture()),
      progressRepository: preferences,
      preferences: preferences,
      initialRoute: '/painting/sunflower',
    ),
  );
  await tester.pumpAndSettle();
  return tester
      .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
      .controller;
}

void main() {
  testWidgets('a new deep-linked picture resets completion view state', (
    tester,
  ) async {
    final first = fixture();
    final second = LevelDefinition(
      id: 'heart',
      title: 'قلب',
      titleEn: 'Heart',
      schemaVersion: 2,
      contentVersion: 1,
      width: 2,
      height: 2,
      palette: first.palette,
      cells: first.cells,
    );
    final storage = MemoryPreferences();
    for (final level in [first, second]) {
      final session = PaintingSession(level);
      for (var index = 0; index < 4; index++) {
        session.selectColor(level.cells[index]);
        session.paintCell(index);
      }
      session.endStroke();
      await storage.write(session.snapshot);
    }
    await tester.pumpWidget(
      PixelhubApp(
        repository: CatalogLevels([first, second]),
        progressRepository: storage,
        preferences: storage,
        initialRoute: '/painting/sunflower',
      ),
    );
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('دیدن نتیجه'));
    await tester.tap(find.text('دیدن نتیجه'));
    await tester.pumpAndSettle();
    expect(find.byType(CompletionScreen), findsNothing);
    GoRouter.of(
      tester.element(find.byType(PaintingPreviewScreen)),
    ).go('/painting/heart');
    await tester.pumpAndSettle();
    expect(find.byType(CompletionScreen), findsOneWidget);
    expect(find.text('قلب'), findsOneWidget);
  });
  testWidgets(
    'Persian is default; English changes text/direction and survives reconstruction',
    (tester) async {
      final storage = MemoryPreferences();
      await pumpPainting(tester, storage: storage);
      expect(find.text('رنگ‌ها'), findsOneWidget);
      expect(
        Directionality.of(tester.element(find.byType(PaintingPreviewScreen))),
        TextDirection.rtl,
      );
      await tester.tap(find.text('English'));
      await tester.pumpAndSettle();
      expect(find.text('Colors'), findsOneWidget);
      expect(find.text('Sunflower'), findsOneWidget);
      expect(
        Directionality.of(tester.element(find.byType(PaintingPreviewScreen))),
        TextDirection.ltr,
      );
      expect(storage.language, 'en');
      await tester.pumpWidget(const SizedBox());
      await tester.pump();
      await tester.pumpWidget(
        PixelhubApp(
          repository: FixedLevels(fixture()),
          preferences: storage,
          progressRepository: storage,
          initialRoute: '/painting/sunflower',
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Colors'), findsOneWidget);
      await tester.tap(find.text('فارسی'));
      await tester.pumpAndSettle();
      expect(find.text('رنگ‌ها'), findsOneWidget);
      expect(storage.language, 'fa');
    },
  );

  testWidgets('valid taps paint; wrong color does not paint; Undo reverts', (
    tester,
  ) async {
    final controller = await pumpPainting(tester);
    final board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    await tester.tapAt(board.topLeft + board.size.center(Offset.zero) / 2);
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 1);
    await tester.tapAt(
      board.topLeft + Offset(board.width * .75, board.height * .25),
    );
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 1);
    await tester.tap(find.byTooltip('بازگردانی'));
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 0);
  });

  testWidgets('Reset needs confirmation and cancels without losing progress', (
    tester,
  ) async {
    final controller = await pumpPainting(tester);
    final board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    await tester.tapAt(
      board.topLeft + Offset(board.width * .25, board.height * .25),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('شروع دوباره'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('انصراف'));
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 1);
    await tester.tap(find.byTooltip('شروع دوباره'));
    await tester.pumpAndSettle();
    await tester.tap(
      find.descendant(
        of: find.byType(AlertDialog),
        matching: find.text('شروع دوباره'),
      ),
    );
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 0);
    expect(controller.session!.generation, 1);
  });

  testWidgets('completion follows correct painting of every color', (
    tester,
  ) async {
    final controller = await pumpPainting(tester);
    final board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    for (final cell in [(0, 0), (1, 1)]) {
      await tester.tapAt(
        board.topLeft +
            Offset(
              board.width * (cell.$1 + .5) / 2,
              board.height * (cell.$2 + .5) / 2,
            ),
      );
      await tester.pumpAndSettle();
    }
    await tester.tap(find.byKey(const ValueKey('color-1')));
    await tester.pump();
    for (final cell in [(1, 0), (0, 1)]) {
      await tester.tapAt(
        board.topLeft +
            Offset(
              board.width * (cell.$1 + .5) / 2,
              board.height * (cell.$2 + .5) / 2,
            ),
      );
      await tester.pumpAndSettle();
    }
    expect(find.byType(CompletionScreen), findsOneWidget);
    expect(find.text('آفرین، تصویرت کامل شد!'), findsOneWidget);
    expect(controller.session!.completedCount, 4);
    expect(controller.saveStatus, SaveStatus.saved);
  });

  testWidgets('pinch cannot paint and Move mode cannot paint', (tester) async {
    final controller = await pumpPainting(tester);
    final board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    final first = await tester.startGesture(
      board.center - const Offset(30, 0),
      pointer: 1,
    );
    final second = await tester.startGesture(
      board.center + const Offset(30, 0),
      pointer: 2,
    );
    await first.moveBy(const Offset(-25, 0));
    await second.moveBy(const Offset(25, 0));
    await tester.pump();
    await first.up();
    await second.up();
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 0);
    expect(
      tester
          .widget<InteractiveViewer>(find.byType(InteractiveViewer))
          .transformationController!
          .value
          .getMaxScaleOnAxis(),
      greaterThan(1),
    );
    await tester.tap(find.text('حرکت / زوم'));
    await tester.pumpAndSettle();
    await tester.dragFrom(board.center, const Offset(30, 0));
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 0);
  });

  testWidgets('fast stroke and inverse zoom mapping paint the intended cells', (
    tester,
  ) async {
    final level = LevelDefinition(
      id: 'sunflower',
      title: 'نمونه',
      titleEn: 'Sample',
      schemaVersion: 2,
      contentVersion: 1,
      width: 16,
      height: 16,
      palette: [0xff316349],
      cells: List.filled(256, 0),
    );
    final controller = await pumpPainting(tester, level: level);
    var board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    final gesture = await tester.startGesture(
      board.topLeft + Offset(board.width / 32, board.height / 32),
      kind: PointerDeviceKind.mouse,
    );
    await gesture.moveTo(
      board.topLeft + Offset(board.width * 31 / 32, board.height / 32),
    );
    await gesture.up();
    await tester.pumpAndSettle();
    expect(controller.session!.completedCount, 16);
    await tester.tap(find.byTooltip('بزرگ‌نمایی'));
    await tester.pumpAndSettle();
    board = tester.getRect(find.byKey(const ValueKey('painting-board')));
    final transform = tester
        .widget<InteractiveViewer>(find.byType(InteractiveViewer))
        .transformationController!;
    final position = MatrixUtils.transformPoint(
      transform.value,
      Offset(board.width * 5.5 / 16, board.height * 5.5 / 16),
    );
    await tester.tapAt(board.topLeft + position);
    await tester.pumpAndSettle();
    expect(controller.session!.isCompleted(5 * 16 + 5), isTrue);
    expect(controller.session!.isCompleted(4 * 16 + 4), isFalse);
  });
}
