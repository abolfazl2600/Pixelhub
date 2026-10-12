part of 'game_domain.dart';

/// The server-authoritative progress for a single immutable level version.
///
/// [serverRevision] is independent of [ProgressSnapshot.revision], which is
/// a local counter. The backend must persist both fields transactionally.
final class ServerProgressState {
  ServerProgressState({required this.progress, required this.serverRevision}) {
    if (serverRevision < 0) {
      throw const FormatException('Invalid server revision.');
    }
  }

  final ProgressSnapshot progress;
  final int serverRevision;
}

/// One queued client operation. No original photo or personal artwork data
/// is included. [baseGeneration] is the last acknowledged *server* epoch.
///
/// The caller assigns a stable operation ID and retains it across retries.
/// The backend must deduplicate IDs before calling [mergeProgress], especially
/// for resets. This pure function does not provide persistent deduplication.
final class PendingProgressSync {
  PendingProgressSync({
    required this.operationId,
    required this.progress,
    required this.baseServerRevision,
    required this.baseGeneration,
    this.isReset = false,
  }) {
    if (!_operationIdPattern.hasMatch(operationId) ||
        baseServerRevision < 0 ||
        baseGeneration < 0 ||
        (isReset
            ? progress.generation <= baseGeneration
            : progress.generation != baseGeneration)) {
      throw const FormatException('Invalid pending progress operation.');
    }
  }

  static final RegExp _operationIdPattern = RegExp(r'^[A-Za-z0-9_-]{8,128}

  final String operationId;
  final ProgressSnapshot progress;
  final int baseServerRevision;
  final int baseGeneration;
  final bool isReset;
}

enum ProgressSyncStatus { applied, unchanged, staleGeneration }

final class ProgressSyncResult {
  const ProgressSyncResult._(this.state, this.status);

  final ServerProgressState state;
  final ProgressSyncStatus status;
}

/// Pure V4 server-side conflict policy for *already authorized* requests.
///
/// In one generation, painting is a monotonic bitwise union, even when the
/// client last observed an older server revision. Reset starts a new server
/// generation and replaces the bits with the caller's post-reset painting.
/// An operation from any older generation is rejected without mutation.
///
/// The backend must check the authenticated user, immutable level identity,
/// and (user ID, operation ID) idempotency in the same DB transaction. It must
/// not feed duplicate resets back into this function.
ProgressSyncResult mergeProgress(
  ServerProgressState server,
  PendingProgressSync pending,
) {
  final current = server.progress;
  final incoming = pending.progress;
  if (current.levelId != incoming.levelId ||
      current.levelVersion != incoming.levelVersion ||
      current.levelChecksum != incoming.levelChecksum ||
      current.cellCount != incoming.cellCount) {
    throw const FormatException('Cannot merge different level versions.');
  }
  if (pending.baseServerRevision > server.serverRevision) {
    throw const FormatException('Client references a future server revision.');
  }
  if (pending.baseGeneration != current.generation) {
    return ProgressSyncResult._(server, ProgressSyncStatus.staleGeneration);
  }

  final nextBits = Uint8List.fromList(
    pending.isReset ? incoming.bits : current.bits,
  );
  var changed = pending.isReset;
  if (!pending.isReset) {
    for (var i = 0; i < nextBits.length; i++) {
      final union = nextBits[i] | incoming.bits[i];
      if (union != nextBits[i]) changed = true;
      nextBits[i] = union;
    }
  }
  if (!changed) {
    return ProgressSyncResult._(server, ProgressSyncStatus.unchanged);
  }

  final latestLocalRevision = current.revision > incoming.revision
      ? current.revision
      : incoming.revision;
  final result = ProgressSnapshot(
    levelId: current.levelId,
    levelVersion: current.levelVersion,
    levelChecksum: current.levelChecksum,
    cellCount: current.cellCount,
    generation: current.generation + (pending.isReset ? 1 : 0),
    revision: latestLocalRevision + 1,
    bits: nextBits,
  );
  return ProgressSyncResult._(
    ServerProgressState(
      progress: result,
      serverRevision: server.serverRevision + 1,
    ),
    ProgressSyncStatus.applied,
  );
}
);

  final String operationId;
  final ProgressSnapshot progress;
  final int baseServerRevision;
  final int baseGeneration;
  final bool isReset;
}

enum ProgressSyncStatus { applied, unchanged, staleGeneration }

final class ProgressSyncResult {
  const ProgressSyncResult._(this.state, this.status);

  final ServerProgressState state;
  final ProgressSyncStatus status;
}

/// Pure V4 server-side conflict policy for *already authorized* requests.
///
/// In one generation, painting is a monotonic bitwise union, even when the
/// client last observed an older server revision. Reset starts a new server
/// generation and replaces the bits with the caller's post-reset painting.
/// An operation from any older generation is rejected without mutation.
///
/// The backend must check the authenticated user, immutable level identity,
/// and (user ID, operation ID) idempotency in the same DB transaction. It must
/// not feed duplicate resets back into this function.
ProgressSyncResult mergeProgress(
  ServerProgressState server,
  PendingProgressSync pending,
) {
  final current = server.progress;
  final incoming = pending.progress;
  if (current.levelId != incoming.levelId ||
      current.levelVersion != incoming.levelVersion ||
      current.levelChecksum != incoming.levelChecksum ||
      current.cellCount != incoming.cellCount) {
    throw const FormatException('Cannot merge different level versions.');
  }
  if (pending.baseServerRevision > server.serverRevision) {
    throw const FormatException('Client references a future server revision.');
  }
  if (pending.baseGeneration != current.generation) {
    return ProgressSyncResult._(
      server,
      ProgressSyncStatus.staleGeneration,
    );
  }

  final nextBits = Uint8List.fromList(
    pending.isReset ? incoming.bits : current.bits,
  );
  var changed = pending.isReset;
  if (!pending.isReset) {
    for (var i = 0; i < nextBits.length; i++) {
      final union = nextBits[i] | incoming.bits[i];
      if (union != nextBits[i]) changed = true;
      nextBits[i] = union;
    }
  }
  if (!changed) {
    return ProgressSyncResult._(
      server,
      ProgressSyncStatus.unchanged,
    );
  }

  final latestLocalRevision = current.revision > incoming.revision
      ? current.revision
      : incoming.revision;
  final result = ProgressSnapshot(
    levelId: current.levelId,
    levelVersion: current.levelVersion,
    levelChecksum: current.levelChecksum,
    cellCount: current.cellCount,
    generation: current.generation + (pending.isReset ? 1 : 0),
    revision: latestLocalRevision + 1,
    bits: nextBits,
  );
  return ProgressSyncResult._(
    ServerProgressState(
      progress: result,
      serverRevision: server.serverRevision + 1,
    ),
    ProgressSyncStatus.applied,
  );
}
