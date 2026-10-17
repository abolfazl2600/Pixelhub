import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/features/museum/museum_controller.dart';

import 'bootstrap_test.dart' show fixture;

void main() {
  test('museum layout is versioned, validates IDs and never duplicates art', () {
    final initial = MuseumLayout();
    expect(initial.slots, hasLength(6));
    expect(initial.slots.every((id) => id == null), isTrue);
    expect(() => initial.slots[0] = 'sunflower', throwsUnsupportedError);

    final first = initial.place(0, 'sunflower');
    final moved = first.place(5, 'sunflower');
    expect(moved.slots.first, isNull);
    expect(moved.slots.last, 'sunflower');
    expect(moved.swap(0, 5).slots.first, 'sunflower');
    expect(moved.slots.last, 'sunflower');

    final custom = moved.copyWith(
      wall: 'sage',
      frame: 'gold',
      arrangement: 'staggered',
    );
    final saved = MuseumLayout.fromJson(custom.toJson());
    expect(saved.wall, 'sage');
    expect(saved.frame, 'gold');
    expect(saved.arrangement, 'staggered');
    expect(saved.slots.last, 'sunflower');

    expect(
      () => MuseumLayout(slots: ['sunflower']),
      throwsFormatException,
    );
    expect(
      () => MuseumLayout(slots: List<String?>.filled(6, 'sunflower')),
      throwsFormatException,
    );
    expect(() => initial.place(6, null), throwsRangeError);
    expect(() => MuseumLayout(wall: 'invalid'), throwsFormatException);
    expect(
      () => MuseumLayout.fromJson({...saved.toJson(), 'schemaVersion': 2}),
      throwsFormatException,
    );
  });

  test('museum persists decorations and only permits completed art', () async {
    final store = MemoryPreferences();
    final level = fixture();
    final library = LibraryController(store, store);
    addTearDown(library.dispose);
    library.setCatalog([level], {});
    await library.load();

    final museum = MuseumController(store, library);
    addTearDown(museum.dispose);
    await museum.load();
    expect(museum.ready, isTrue);
    expect(museum.visibleSlots.whereType<String>(), isEmpty);

    await expectLater(museum.place(0, level.id), throwsStateError);
    final session = PaintingSession(level);
    for (var i = 0; i < level.cells.length; i++) {
      session.selectColor(level.cells[i]);
      session.paintCell(i);
    }
    library.updateProgress(session.snapshot);
    await museum.place(0, level.id);
    await museum.setFrame('gold');
    await museum.setWall('blue');
    await museum.setArrangement('staggered');
    expect(museum.visibleSlots[0], level.id);
    expect(museum.layout.frame, 'gold');
    expect(museum.layout.wall, 'blue');
    expect(museum.layout.arrangement, 'staggered');

    final second = MuseumController(store, library);
    addTearDown(second.dispose);
    await second.load();
    expect(second.visibleSlots[0], level.id);
    expect(second.layout.frame, 'gold');
    expect(second.layout.wall, 'blue');
    expect(second.layout.arrangement, 'staggered');

    // An incomplete painting cannot be shown, even when an old layout
    // still contains its identifier.
    library.updateProgress(PaintingSession(level).snapshot);
    expect(second.visibleSlots[0], isNull);
    expect(second.layout.slots[0], level.id);

    await second.remove(0);
    expect((await store.readMuseum()).slots[0], isNull);
    await store.clearPixelhubData();
    expect((await store.readMuseum()).slots, everyElement(isNull));
  });

  test('museum storage errors do not alter the in-memory arrangement', () async {
    final store = MemoryPreferences();
    final failingRepository = _FailingMuseumStorage(store);
    final level = fixture();
    final library = LibraryController(store, store);
    addTearDown(library.dispose);
    library.setCatalog([level], {});
    await library.load();
    final museum = MuseumController(failingRepository, library);
    addTearDown(museum.dispose);
    await museum.load();
    expect(museum.layout.wall, 'cream');
    await expectLater(museum.setWall('sage'), throwsStateError);
    expect(museum.layout.wall, 'cream');
    expect(museum.busy, isFalse);
    failingRepository.fail = false;
    await museum.setWall('sage');
    expect(museum.layout.wall, 'sage');
  });
}

class _FailingMuseumStorage implements MuseumRepository {
  _FailingMuseumStorage(this.storage);

  final MemoryPreferences storage;
  bool fail = true;

  @override
  Future<MuseumLayout> readMuseum() => storage.readMuseum();

  @override
  Future<void> writeMuseum(MuseumLayout layout) {
    if (fail) return Future.error(StateError('Disk not writable'));
    return storage.writeMuseum(layout);
  }
}
