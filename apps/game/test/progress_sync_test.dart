import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

import 'bootstrap_test.dart' show fixture;

ProgressSnapshot progress(
  LevelDefinition level,
  List<int> completed, {
  int generation = 0,
  int revision = 0,
}) {
  final bits = Uint8List((level.cells.length + 7) ~/ 8);
  for (final index in completed) {
    bits[index ~/ 8] |= 1 << (index % 8);
  }
  return ProgressSnapshot(
    levelId: level.id,
    levelVersion: level.contentVersion,
    levelChecksum: level.checksum,
    cellCount: level.cells.length,
    generation: generation,
    revision: revision,
    bits: bits,
  );
}

PendingProgressSync change(
  ProgressSnapshot snapshot, {
  int baseGeneration = 0,
  int baseServerRevision = 0,
  bool reset = false,
  String operationId = 'device-operation-01',
}) => PendingProgressSync(
  operationId: operationId,
  progress: snapshot,
  baseServerRevision: baseServerRevision,
  baseGeneration: baseGeneration,
  isReset: reset,
);

void main() {
  test('disjoint offline painting merges even with a stale server revision', () {
    final level = fixture();
    final initial = ServerProgressState(
      progress: progress(level, [0], revision: 2),
      serverRevision: 5,
    );
    final result = mergeProgress(
      initial,
      change(progress(level, [3], revision: 1)),
    );

    expect(result.status, ProgressSyncStatus.applied);
    expect(result.state.serverRevision, 6);
    expect(result.state.progress.completedCount, 2);
    expect(result.state.progress.isCompleted(0), isTrue);
    expect(result.state.progress.isCompleted(3), isTrue);
    expect(result.state.progress.generation, 0);
    expect(initial.progress.completedCount, 1);
  });

  test('repeated ordinary paint is a no-op with stable server revision', () {
    final level = fixture();
    final server = ServerProgressState(
      progress: progress(level, [0, 3], revision: 8),
      serverRevision: 7,
    );
    final result = mergeProgress(
      server,
      change(progress(level, [0], revision: 1)),
    );

    expect(result.status, ProgressSyncStatus.unchanged);
    expect(identical(result.state, server), isTrue);
    expect(result.state.serverRevision, 7);
  });

  test('reset establishes a new epoch and clears old painted bits', () {
    final level = fixture();
    final server = ServerProgressState(
      progress: progress(level, [0, 1, 2], generation: 2, revision: 10),
      serverRevision: 6,
    );
    final reset = mergeProgress(
      server,
      change(
        progress(level, [3], generation: 3, revision: 11),
        baseGeneration: 2,
        baseServerRevision: 4,
        reset: true,
      ),
    );

    expect(reset.status, ProgressSyncStatus.applied);
    expect(reset.state.progress.generation, 3);
    expect(reset.state.progress.completedCount, 1);
    expect(reset.state.progress.isCompleted(3), isTrue);
    expect(reset.state.progress.isCompleted(0), isFalse);
    expect(reset.state.serverRevision, 7);
    expect(server.progress.completedCount, 3);
  });

  test('late offline painting cannot resurrect cells after reset', () {
    final level = fixture();
    final afterReset = ServerProgressState(
      progress: progress(level, [], generation: 1, revision: 3),
      serverRevision: 10,
    );
    final stale = mergeProgress(
      afterReset,
      change(progress(level, [0, 1], revision: 5)),
    );

    expect(stale.status, ProgressSyncStatus.staleGeneration);
    expect(identical(stale.state, afterReset), isTrue);
    expect(stale.state.progress.completedCount, 0);
    expect(stale.state.serverRevision, 10);
  });

  test('two concurrent resets cannot overwrite the winning reset', () {
    final level = fixture();
    final server = ServerProgressState(
      progress: progress(level, [1]),
      serverRevision: 0,
    );
    final first = mergeProgress(
      server,
      change(
        progress(level, [0], generation: 1),
        reset: true,
        operationId: 'first-reset-01',
      ),
    );
    final late = mergeProgress(
      first.state,
      change(
        progress(level, [3], generation: 1),
        reset: true,
        operationId: 'second-reset-02',
      ),
    );

    expect(late.status, ProgressSyncStatus.staleGeneration);
    expect(late.state.progress.isCompleted(0), isTrue);
    expect(late.state.progress.isCompleted(3), isFalse);
    expect(late.state.serverRevision, 1);
  });

  test('multiple local offline resets collapse to one server epoch', () {
    final level = fixture();
    final server = ServerProgressState(
      progress: progress(level, [0], generation: 4),
      serverRevision: 9,
    );
    final merged = mergeProgress(
      server,
      change(
        progress(level, [2], generation: 8, revision: 30),
        baseGeneration: 4,
        baseServerRevision: 9,
        reset: true,
      ),
    );

    expect(merged.status, ProgressSyncStatus.applied);
    expect(merged.state.progress.generation, 5);
    expect(merged.state.progress.isCompleted(2), isTrue);
    expect(merged.state.progress.isCompleted(0), isFalse);
  });

  test('rejects mismatched level data and future acknowledged revision', () {
    final level = fixture();
    final server = ServerProgressState(
      progress: progress(level, [0]),
      serverRevision: 2,
    );
    final invalidIdentity = ProgressSnapshot(
      levelId: level.id,
      levelVersion: level.contentVersion + 1,
      levelChecksum: level.checksum,
      cellCount: level.cells.length,
      generation: 0,
      revision: 1,
      bits: Uint8List(1),
    );

    expect(
      () => mergeProgress(server, change(invalidIdentity)),
      throwsFormatException,
    );
    expect(
      () => mergeProgress(
        server,
        change(
          progress(level, [1]),
          baseServerRevision: 3,
        ),
      ),
      throwsFormatException,
    );
    expect(
      () => change(progress(level, [0], generation: 1)),
      throwsFormatException,
    );
    expect(
      () => change(progress(level, [0]), operationId: 'bad id'),
      throwsFormatException,
    );
  });
}
