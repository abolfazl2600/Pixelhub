import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

import 'bootstrap_test.dart' show fixture;

PendingProgressSync pending(
  LevelDefinition level, {
  String id = 'operation-one-01',
  int cell = 0,
  int generation = 0,
  bool reset = false,
}) {
  final bits = Uint8List((level.cells.length + 7) ~/ 8);
  bits[cell ~/ 8] |= 1 << (cell % 8);
  return PendingProgressSync(
    operationId: id,
    progress: ProgressSnapshot(
      levelId: level.id,
      levelVersion: level.contentVersion,
      levelChecksum: level.checksum,
      cellCount: level.cells.length,
      generation: generation,
      revision: 1,
      bits: bits,
    ),
    baseServerRevision: 5,
    baseGeneration: 0,
    isReset: reset,
  );
}

void main() {
  test('outbox JSON preserves painting, reset and stable operation IDs', () {
    final level = fixture();
    final source = ProgressSyncOutbox(
      accountId: 'account-a',
      operations: [
        pending(level),
        pending(
          level,
          id: 'reset-operation-02',
          cell: 3,
          generation: 1,
          reset: true,
        ),
      ],
    );
    final decoded = ProgressSyncOutbox.fromJson(
      jsonDecode(jsonEncode(source.toJson())) as Map<String, Object?>,
      accountId: 'account-a',
    );
    expect(decoded.operations.length, 2);
    expect(decoded.next!.operationId, 'operation-one-01');
    expect(decoded.operations[1].isReset, isTrue);
    expect(decoded.operations[1].progress.isCompleted(3), isTrue);
    expect(decoded.operations[1].baseServerRevision, 5);
  });

  test('retry with same ID and content is safe; changed content is rejected', () {
    final level = fixture();
    final first = pending(level);
    final queue = ProgressSyncOutbox(accountId: 'account-a').enqueue(first);
    expect(identical(queue.enqueue(first), queue), isTrue);
    expect(
      () => queue.enqueue(pending(level, cell: 1)),
      throwsFormatException,
    );
  });

  test('acknowledgment removes only the FIFO head', () {
    final level = fixture();
    final queue = ProgressSyncOutbox(accountId: 'account-a')
        .enqueue(pending(level))
        .enqueue(pending(level, id: 'operation-two-02', cell: 2));
    expect(
      () => queue.acknowledge('operation-two-02'),
      throwsStateError,
    );
    final after = queue.acknowledge('operation-one-01');
    expect(after.operations.length, 1);
    expect(after.next!.operationId, 'operation-two-02');
    expect(queue.operations.length, 2);
  });

  test('cross-account access and corrupt completed counts are rejected', () {
    final source = ProgressSyncOutbox(
      accountId: 'account-a',
      operations: [pending(fixture())],
    );
    expect(
      () => ProgressSyncOutbox.fromJson(
        source.toJson(),
        accountId: 'account-b',
      ),
      throwsFormatException,
    );
    final json =
        jsonDecode(jsonEncode(source.toJson())) as Map<String, Object?>;
    final operations = json['operations']! as List<Object?>;
    final item = operations.first! as Map<String, Object?>;
    final progress = item['progress']! as Map<String, Object?>;
    progress['completedCount'] = 999;
    expect(
      () => ProgressSyncOutbox.fromJson(json, accountId: 'account-a'),
      throwsFormatException,
    );
  });

  test('memory adapter isolates accounts and retains resets', () async {
    final repository = MemoryPreferences();
    final level = fixture();
    await repository.enqueueSyncOperation(
      'account-a',
      pending(level, id: 'reset-operation-01', generation: 1, reset: true),
    );
    expect((await repository.readSyncOutbox('account-b')).isEmpty, isTrue);
    expect(
      (await repository.readSyncOutbox('account-a')).next!.isReset,
      isTrue,
    );
    final after = await repository.acknowledgeSyncOperation(
      'account-a',
      'reset-operation-01',
    );
    expect(after.isEmpty, isTrue);
    await repository.enqueueSyncOperation('account-b', pending(level));
    await repository.clearPixelhubData();
    expect((await repository.readSyncOutbox('account-b')).isEmpty, isTrue);
  });

  test('bounded capacity and invalid scope fail closed', () {
    final level = fixture();
    var queue = ProgressSyncOutbox(accountId: 'account-a');
    for (var i = 0; i < ProgressSyncOutbox.maxOperations; i++) {
      final operationId = 'operation-' + i.toString().padLeft(5, '0');
      queue = queue.enqueue(pending(level, id: operationId));
    }
    expect(queue.operations.length, ProgressSyncOutbox.maxOperations);
    expect(
      () => queue.enqueue(pending(level, id: 'operation-overflow')),
      throwsFormatException,
    );
    expect(
      () => ProgressSyncOutbox(accountId: '../account'),
      throwsFormatException,
    );
  });
}
