import 'dart:convert';

import 'package:game_domain/game_domain.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Local-only, bounded replay checkpoints. Keys are isolated from gameplay saves.
final class ReplayCheckpointStore {
  ReplayCheckpointStore({SharedPreferencesAsync? preferences})
    : _preferences = preferences ?? SharedPreferencesAsync();

  static const _prefix = 'pixelhub.replay_checkpoint.v1.';
  static const retention = Duration(hours: 120);
  final SharedPreferencesAsync _preferences;
  Future<void> _writes = Future<void>.value();

  String _key(String levelId, int generation, int percent) =>
      '$_prefix$levelId.$generation.$percent';

  Future<void> record({
    required String levelId,
    required int generation,
    required int milestonePercent,
    required int attainedPercent,
    required ProgressSnapshot snapshot,
  }) async {
    if (milestonePercent < 1 ||
        milestonePercent > 100 ||
        attainedPercent < milestonePercent ||
        attainedPercent > 100 ||
        snapshot.levelId != levelId ||
        snapshot.generation != generation)
      return;
    final now = DateTime.now().toUtc();
    final record = jsonEncode(<String, Object>{
      'schemaVersion': 1,
      'levelId': levelId,
      'generation': generation,
      'milestonePercent': milestonePercent,
      'attainedPercent': attainedPercent,
      'capturedAt': now.toIso8601String(),
      'progress': snapshot.toJson(),
    });
    // A per-key write makes repeated updates idempotent. Errors are swallowed:
    // replay is optional and must never interrupt painting or autosave.
    try {
      await _enqueue(() async {
        final key = _key(levelId, generation, milestonePercent);
        // Preserve the first captured state for this generation/milestone.
        if (await _preferences.getString(key) != null) return;
        await _preferences.setString(key, record);
      });
    } on Object {
      // Storage quota or platform failures disable this checkpoint only.
    }
  }

  Future<List<Map<String, Object?>>> readValid(String levelId) async {
    await purgeExpired();
    final result = <Map<String, Object?>>[];
    try {
      final keys = await _preferences.getKeys();
      for (final key in keys.where((key) => key.startsWith(_prefix))) {
        final raw = await _preferences.getString(key);
        if (raw == null) continue;
        try {
          final value = jsonDecode(raw);
          if (value is Map<String, dynamic> && value['levelId'] == levelId) {
            result.add(Map<String, Object?>.from(value));
          }
        } on Object {
          // Corrupt optional records are ignored; purge handles them separately.
        }
      }
    } on Object {
      return const [];
    }
    result.removeWhere(
      (item) =>
          item['milestonePercent'] is! int ||
          (item['milestonePercent'] as int) < 1 ||
          (item['milestonePercent'] as int) > 100,
    );
    result.sort(
      (a, b) => (a['milestonePercent'] as int).compareTo(
        b['milestonePercent'] as int,
      ),
    );
    return List.unmodifiable(result);
  }

  /// Purges only this store's namespace. Invalid records are also removed.
  Future<void> purgeExpired({DateTime? now}) async {
    final cutoff = (now ?? DateTime.now().toUtc()).toUtc().subtract(retention);
    try {
      final keys = await _preferences.getKeys();
      for (final key in keys.where((key) => key.startsWith(_prefix))) {
        var expired = false;
        final raw = await _preferences.getString(key);
        if (raw == null) {
          expired = true;
        } else {
          try {
            final value = jsonDecode(raw);
            final captured = value is Map<String, dynamic>
                ? DateTime.tryParse(value['capturedAt'] as String? ?? '')
                : null;
            expired = captured == null || !captured.toUtc().isAfter(cutoff);
          } on Object {
            expired = true;
          }
        }
        if (expired) await _preferences.remove(key);
      }
    } on Object {
      // Cleanup is best-effort and cannot affect regular saves.
    }
  }

  Future<void> _enqueue(Future<void> Function() operation) {
    final next = _writes.then((_) => operation());
    _writes = next.catchError((Object _) {});
    return next;
  }
}
