import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/painting/painting_controller.dart';

import 'bootstrap_test.dart' show fixture;

class ControlledStore implements ProgressRepository {
  final records = <ProgressSnapshot>[];
  final pending = <Completer<void>>[];
  bool readFails = false;
  @override
  Future<ProgressSnapshot?> read(LevelDefinition level) async {
    if (readFails) throw const FormatException('corrupt');
    return null;
  }

  @override
  Future<void> write(ProgressSnapshot progress) {
    records.add(progress);
    final done = Completer<void>();
    pending.add(done);
    return done.future;
  }
}

void main() {
  test('coalesced autosaves cannot restore colors after reset', () async {
    final store = ControlledStore();
    final controller = PaintingController(fixture(), store);
    addTearDown(controller.dispose);
    await controller.load();
    controller.beginStroke();
    controller.paintLine(0, 0, 0, 0);
    controller.endStroke();
    expect(store.records.single.completedCount, 1);
    controller.reset();
    store.pending[0].complete();
    await Future<void>.delayed(Duration.zero);
    expect(store.records.last.completedCount, 0);
    expect(store.records.last.generation, 1);
    store.pending[1].complete();
    await controller.flush();
    expect(controller.saveStatus, SaveStatus.saved);
  });

  test(
    'failed write retains progress and retries the latest snapshot',
    () async {
      final store = ControlledStore();
      final controller = PaintingController(fixture(), store);
      addTearDown(controller.dispose);
      await controller.load();
      controller.beginStroke();
      controller.paintLine(0, 0, 0, 0);
      controller.endStroke();
      store.pending[0].completeError(StateError('full storage'));
      await controller.flush();
      expect(controller.saveStatus, SaveStatus.error);
      expect(controller.session!.completedCount, 1);
      final retry = controller.flush();
      expect(store.records.last.completedCount, 1);
      store.pending[1].complete();
      await retry;
      expect(controller.saveStatus, SaveStatus.saved);
    },
  );

  test('damaged stored data is not overwritten during loading', () async {
    final store = ControlledStore()..readFails = true;
    final controller = PaintingController(fixture(), store);
    addTearDown(controller.dispose);
    await controller.load();
    expect(controller.status, PaintingStatus.error);
    expect(store.records, isEmpty);
    controller.reset();
    expect(store.records.single.completedCount, 0);
    store.pending.single.complete();
    await controller.flush();
  });

  test('a recreated controller resumes progress and completion', () async {
    final store = MemoryPreferences();
    final controller = PaintingController(fixture(), store);
    await controller.load();
    for (var color = 0; color < 2; color++) {
      controller.selectColor(color);
      controller.beginStroke();
      controller.paintLine(0, 0, 1, 1);
      controller.paintLine(1, 0, 0, 1);
      controller.endStroke();
    }
    await controller.flush();
    controller.dispose();
    final reopened = PaintingController(fixture(), store);
    addTearDown(reopened.dispose);
    await reopened.load();
    expect(reopened.session!.isComplete, isTrue);
    expect(reopened.session!.completedCount, 4);
  });
  test(
    'hint does not change progress; bomb paints and reset clears hint',
    () async {
      final store = MemoryPreferences();
      final controller = PaintingController(fixture(), store);
      addTearDown(controller.dispose);
      await controller.load();
      final before = controller.session!.snapshot.revision;
      expect(controller.showHint(), 0);
      expect(controller.hintIndex, 0);
      expect(controller.session!.snapshot.revision, before);
      expect(controller.useBomb(), 2);
      expect(controller.hintIndex, isNull);
      await controller.flush();
      expect(controller.session!.completedCount, 2);
      expect(controller.session!.canUndo, isTrue);
      controller.undo();
      await controller.flush();
      expect(controller.session!.completedCount, 0);
      controller.showHint();
      controller.reset();
      await controller.flush();
      expect(controller.hintIndex, isNull);
      expect(controller.session!.generation, 1);
    },
  );
}
