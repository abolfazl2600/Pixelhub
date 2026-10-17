import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/core/pixel_art_preview.dart';
import 'package:pixelhub/features/painting/painting_preview_screen.dart';

import 'bootstrap_test.dart' show TestRepository, fixture;

LevelDefinition anotherLevel(String id) => LevelDefinition(
  id: id,
  title: 'نقاشی دوم',
  titleEn: 'Second picture',
  schemaVersion: 2,
  contentVersion: 1,
  width: 2,
  height: 2,
  palette: [0xfff8edb7, 0xff316349],
  cells: [0, 1, 1, 0],
);

class _MultipleLevels implements LevelRepository {
  _MultipleLevels(this.levels);

  final List<LevelDefinition> levels;

  @override
  Future<LevelDefinition> loadPreview() async => levels.first;

  @override
  Future<List<LevelDefinition>> loadLevels() async => levels;
}

ProgressSnapshot partiallyPainted(LevelDefinition level) {
  final session = PaintingSession(level);
  session.paintCell(0);
  return session.snapshot;
}

ProgressSnapshot fullyPainted(LevelDefinition level) {
  final session = PaintingSession(level);
  for (var i = 0; i < level.cells.length; i++) {
    session.selectColor(level.cells[i]);
    session.paintCell(i);
  }
  return session.snapshot;
}

Future<void> loadProgress() => Future<void>.delayed(Duration.zero);

void main() {
  test(
    'last opened incomplete picture survives recreation and falls back',
    () async {
      final store = MemoryPreferences();
      final first = fixture();
      final second = anotherLevel('second');
      await store.write(partiallyPainted(first));
      await store.write(partiallyPainted(second));

      final library = LibraryController(
        store,
        store,
        recentArtworkRepository: store,
      );
      addTearDown(library.dispose);
      library.setCatalog([first, second], {});
      await library.load();
      await library.loadRecentArtwork();
      await loadProgress();
      expect(library.continueLevel?.id, first.id);
      expect(library.recentlyOpenedLevel, isNull);

      await library.markOpened(second);
      expect(library.continueLevel?.id, second.id);
      expect(library.recentlyOpenedLevel?.id, second.id);

      final reopened = LibraryController(
        store,
        store,
        recentArtworkRepository: store,
      );
      addTearDown(reopened.dispose);
      reopened.setCatalog([first, second], {});
      await reopened.load();
      await reopened.loadRecentArtwork();
      await loadProgress();
      expect(reopened.continueLevel?.id, second.id);
      expect(reopened.continuePercent(second), 25);
      expect(reopened.recentlyOpenedLevel?.id, second.id);

      reopened.updateProgress(fullyPainted(second));
      // A completed most-recent artwork stays featured; it must not jump
      // back to a different older unfinished painting.
      expect(reopened.recentlyOpenedLevel?.id, second.id);
      expect(reopened.continueLevel?.id, first.id);
      reopened.updateProgress(PaintingSession(first).snapshot);
      expect(reopened.continueLevel, isNull);
    },
  );

  test('deleted, unavailable, and mismatched artwork cannot appear', () async {
    final store = MemoryPreferences();
    final first = fixture();
    final online = anotherLevel('online-test');
    final personal = anotherLevel('private-sketch');
    final library = LibraryController(
      store,
      store,
      recentArtworkRepository: store,
    );
    addTearDown(library.dispose);
    await store.write(partiallyPainted(first));
    await store.write(partiallyPainted(online));
    library.setCatalog([first], {});
    await library.load();
    await loadProgress();
    library.setDownloadedOnline([online]);
    await loadProgress();

    await library.markOpened(online);
    expect(library.continueLevel?.id, online.id);
    expect(library.recentlyOpenedLevel?.id, online.id);
    library.setDownloadedOnline([]);
    expect(library.recentlyOpenedLevel, isNull);
    expect(library.continueLevel?.id, first.id);

    await library.add(
      PrivateArtwork(
        level: personal,
        createdAt: DateTime.utc(2026, 1),
        difficulty: 'normal',
        colorLimit: 2,
        quarterTurns: 0,
        cropX: 0,
        cropY: 0,
      ),
    );
    library.updateProgress(partiallyPainted(personal));
    await library.markOpened(personal);
    expect(library.continueLevel?.id, personal.id);
    expect(library.recentlyOpenedLevel?.id, personal.id);
    await library.delete(personal);
    expect(library.recentlyOpenedLevel, isNull);
    expect(library.continueLevel?.id, first.id);

    // An older picture version cannot reuse another version's saved bits.
    library.setCatalog([anotherLevel('sunflower')], {});
    expect(library.continueLevel, isNull);
  });

  test('clearing app data clears the recent shortcut preference', () async {
    final store = MemoryPreferences();
    final library = LibraryController(
      store,
      store,
      recentArtworkRepository: store,
    );
    addTearDown(library.dispose);
    library.setCatalog([fixture()], {});
    await library.load();
    await library.markOpened(fixture());
    await library.clear();
    expect(await store.readRecentArtworkId(), isNull);
    expect(library.continueLevel, isNull);
    expect(library.recentlyOpenedLevel, isNull);
  });

  testWidgets('Continue navigates to saved progress, also after restart', (
    tester,
  ) async {
    final store = MemoryPreferences();
    final level = fixture();
    await store.write(partiallyPainted(level));
    await store.writeRecentArtworkId(level.id);
    await store.writeLanguage('en');

    Future<void> openApp() async {
      final repo = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          repository: repo,
          progressRepository: store,
          artworkRepository: store,
          preferences: store,
        ),
      );
      repo.requests.single.complete(level);
      await tester.pumpAndSettle();
    }

    await openApp();
    expect(find.text('Continue painting'), findsOneWidget);
    expect(find.text('Sunflower'), findsWidgets);
    expect(find.text('25%'), findsOneWidget);
    expect(
      find.byKey(const ValueKey('home-featured-artwork')),
      findsOneWidget,
    );
    expect(find.byType(PixelArtPreview), findsOneWidget);

    await tester.ensureVisible(find.byKey(const ValueKey('open-preview')));
    await tester.tap(find.byKey(const ValueKey('open-preview')));
    await tester.pumpAndSettle();
    expect(find.byType(PaintingPreviewScreen), findsOneWidget);
    expect(find.textContaining('Colored: 1 of 4'), findsOneWidget);
    expect((await store.read(level))?.completedCount, 1);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await openApp();
    expect(
      find.byKey(const ValueKey('home-featured-artwork')),
      findsOneWidget,
    );
    expect(find.byType(PixelArtPreview), findsOneWidget);
    expect(find.text('Continue painting'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  for (final viewport in [const Size(360, 780), const Size(1024, 768)]) {
    testWidgets('Continue card fits viewport $viewport in Persian', (
      tester,
    ) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = viewport;
      addTearDown(tester.view.reset);
      final level = fixture();
      final store = MemoryPreferences();
      await store.write(partiallyPainted(level));
      await store.writeRecentArtworkId(level.id);
      final repository = TestRepository();
      await tester.pumpWidget(
        PixelhubApp(
          repository: repository,
          progressRepository: store,
          artworkRepository: store,
          preferences: store,
        ),
      );
      repository.requests.single.complete(level);
      await tester.pumpAndSettle();
      expect(find.text('ادامه نقاشی'), findsOneWidget);
      expect(
        find.byKey(const ValueKey('home-featured-artwork')),
        findsOneWidget,
      );
      expect(find.byType(PixelArtPreview), findsOneWidget);
      await tester.ensureVisible(find.byKey(const ValueKey('open-preview')));
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('fresh and completed paintings have no Continue shortcut', (
    tester,
  ) async {
    final store = MemoryPreferences();
    final level = fixture();
    await store.writeRecentArtworkId(level.id);
    final repository = TestRepository();
    await tester.pumpWidget(
      PixelhubApp(
        repository: repository,
        progressRepository: store,
        artworkRepository: store,
        preferences: store,
      ),
    );
    repository.requests.single.complete(level);
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('home-featured-artwork')), findsOneWidget);
    expect(find.byType(PixelArtPreview), findsOneWidget);
    expect(find.text('ادامه نقاشی'), findsNothing);
  });

  testWidgets('only the last opened picture is featured, even if completed', (
    tester,
  ) async {
    final store = MemoryPreferences();
    final first = fixture();
    final second = anotherLevel('second');
    await store.write(partiallyPainted(first));
    await store.write(fullyPainted(second));
    await store.writeRecentArtworkId(second.id);
    await store.writeLanguage('en');
    final repository = _MultipleLevels([first, second]);

    await tester.pumpWidget(
      PixelhubApp(
        repository: repository,
        progressRepository: store,
        artworkRepository: store,
        preferences: store,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('home-featured-artwork')), findsOneWidget);
    expect(find.byType(PixelArtPreview), findsOneWidget);
    expect(find.text('Second picture'), findsOneWidget);
    expect(find.text('Sunflower'), findsNothing);
    expect(find.text('100%'), findsOneWidget);
    expect(find.text('View result'), findsOneWidget);

    await tester.ensureVisible(find.byKey(const ValueKey('open-preview')));
    await tester.tap(find.byKey(const ValueKey('open-preview')));
    await tester.pumpAndSettle();
    expect(find.byType(PaintingPreviewScreen), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await tester.pumpWidget(
      PixelhubApp(
        repository: _MultipleLevels([first, second]),
        progressRepository: store,
        artworkRepository: store,
        preferences: store,
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Second picture'), findsOneWidget);
    expect(find.byType(PixelArtPreview), findsOneWidget);
    expect(find.byKey(const ValueKey('home-featured-artwork')), findsOneWidget);
  });
}
