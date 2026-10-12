part of 'game_domain.dart';

/// Immutable, account-scoped FIFO for idempotent offline progress operations.
/// Original photos, bearer tokens and private-artwork data are never stored.
final class ProgressSyncOutbox {
  ProgressSyncOutbox({
    required this.accountId,
    Iterable<PendingProgressSync> operations = const [],
  }) : operations = List<PendingProgressSync>.unmodifiable(operations) {
    if (!_accountPattern.hasMatch(accountId) ||
        this.operations.length > maxOperations ||
        this.operations.map((item) => item.operationId).toSet().length !=
            this.operations.length) {
      throw const FormatException('Invalid sync outbox.');
    }
  }

  factory ProgressSyncOutbox.fromJson(
    Map<String, Object?> json, {
    required String accountId,
  }) {
    try {
      if (json['schemaVersion'] != 1 || json['accountId'] != accountId) {
        throw const FormatException('Wrong account or outbox schema.');
      }
      final raw = json['operations']! as List<Object?>;
      if (raw.length > maxOperations) {
        throw const FormatException('Sync outbox capacity reached.');
      }
      return ProgressSyncOutbox(
        accountId: accountId,
        operations: raw.map(
          (value) => _decodeSyncOperation(value! as Map<String, Object?>),
        ),
      );
    } on TypeError {
      throw const FormatException('Malformed sync outbox.');
    }
  }

  static const int maxOperations = 128;
  static const int maxBytes = 512 * 1024;
  static final RegExp _accountPattern = RegExp(r'^[A-Za-z0-9._:@-]{1,160}$');

  final String accountId;
  final List<PendingProgressSync> operations;

  PendingProgressSync? get next => operations.isEmpty ? null : operations.first;
  bool get isEmpty => operations.isEmpty;

  /// Persist before sending. Retrying an identical ID is a no-op; never
  /// overwrite a possibly transmitted operation with different content.
  ProgressSyncOutbox enqueue(PendingProgressSync pending) {
    for (final existing in operations) {
      if (existing.operationId == pending.operationId) {
        if (jsonEncode(_encodeSyncOperation(existing)) ==
            jsonEncode(_encodeSyncOperation(pending))) {
          return this;
        }
        throw const FormatException('Operation ID reused with new content.');
      }
    }
    if (operations.length >= maxOperations) {
      throw const FormatException('Sync outbox capacity reached.');
    }
    return ProgressSyncOutbox(
      accountId: accountId,
      operations: [...operations, pending],
    );
  }

  /// Only after a durable, authenticated applied/unchanged server response.
  /// A timeout or stale-generation (409) must leave the operation queued.
  ProgressSyncOutbox acknowledge(String operationId) {
    if (next?.operationId != operationId) {
      throw StateError('Only an acknowledged queue head can be removed.');
    }
    return ProgressSyncOutbox(
      accountId: accountId,
      operations: operations.skip(1),
    );
  }

  Map<String, Object> toJson() => {
    'schemaVersion': 1,
    'accountId': accountId,
    'operations': operations.map(_encodeSyncOperation).toList(),
  };
}

Map<String, Object> _encodeSyncOperation(PendingProgressSync item) => {
  'operationId': item.operationId,
  'baseServerRevision': item.baseServerRevision,
  'baseGeneration': item.baseGeneration,
  'isReset': item.isReset,
  'progress': item.progress.toJson(),
};

/// Validate a persisted bitset before reconstructing an operation. The
/// backend must also verify the checksum against its trusted level catalog.
PendingProgressSync _decodeSyncOperation(Map<String, Object?> json) {
  try {
    final data = json['progress']! as Map<String, Object?>;
    if (data['schemaVersion'] != 1 ||
        data['levelId'] is! String ||
        !RegExp(r'^[a-z0-9-]{1,128}$').hasMatch(data['levelId']! as String) ||
        data['levelVersion'] is! int ||
        (data['levelVersion']! as int) < 1 ||
        data['levelChecksum'] is! String ||
        !RegExp(r'^[0-9a-f]{64}$').hasMatch(data['levelChecksum']! as String)) {
      throw const FormatException('Invalid queued level identity.');
    }
    final snapshot = ProgressSnapshot(
      levelId: data['levelId']! as String,
      levelVersion: data['levelVersion']! as int,
      levelChecksum: data['levelChecksum']! as String,
      cellCount: data['cellCount']! as int,
      generation: data['generation']! as int,
      revision: data['revision']! as int,
      bits: base64Decode(data['completedCells']! as String),
    );
    if (data['completedCount'] != snapshot.completedCount) {
      throw const FormatException('Queued progress count mismatch.');
    }
    return PendingProgressSync(
      operationId: json['operationId']! as String,
      progress: snapshot,
      baseServerRevision: json['baseServerRevision']! as int,
      baseGeneration: json['baseGeneration']! as int,
      isReset: json['isReset']! as bool,
    );
  } on TypeError {
    throw const FormatException('Malformed queued sync operation.');
  }
}

/// Durable storage port. No operation is uploaded until an authenticated
/// network coordinator is implemented and explicitly enabled in V4.
abstract interface class ProgressSyncOutboxRepository {
  Future<ProgressSyncOutbox> readSyncOutbox(String accountId);
  Future<ProgressSyncOutbox> enqueueSyncOperation(
    String accountId,
    PendingProgressSync operation,
  );
  Future<ProgressSyncOutbox> acknowledgeSyncOperation(
    String accountId,
    String operationId,
  );
}
