import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
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
  test('last opened incomplete picture survives recreation and falls back', () async {
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

    await library.markOpened(second);
    expect(library.continueLevel?.id, second.id);

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

    reopened.updateProgress(fullyPainted(second));
    expect(reopened.continueLevel?.id, first.id);
    reopened.updateProgress(PaintingSession(first).snapshot);
    expect(reopened.continueLevel, isNull);
  });

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
    library.setDownloadedOnline([]);
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
    await library.delete(personal);
    expect(library.continueLevel?.id, first.id);

    // An older picture version cannot reuse another version's saved bits.
    library.setCatalog([
      anotherLevel('sunflower'),
    ], {});
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
    expect(find.byKey(const ValueKey('continue-painting-card')), findsOneWidget);

    await tester.ensureVisible(
      find.byKey(const ValueKey('continue-painting-button')),
    );
    await tester.tap(find.byKey(const ValueKey('continue-painting-button')));
    await tester.pumpAndSettle();
    expect(find.byType(PaintingPreviewScreen), findsOneWidget);
    expect(find.textContaining('Colored: 1 of 4'), findsOneWidget);
    expect((await store.read(level))?.completedCount, 1);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await openApp();
    expect(find.byKey(const ValueKey('continue-painting-card')), findsOneWidget);
    expect(find.text('Continue painting'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

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
    expect(find.byKey(const ValueKey('continue-painting-card')), findsNothing);
  });
}
