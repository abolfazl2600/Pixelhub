import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:shared_preferences/shared_preferences.dart';

final class AssetLevelRepository
    implements LevelRepository, CatalogMetadataRepository {
  AssetLevelRepository({AssetBundle? bundle}) : _bundle = bundle ?? rootBundle;
  final AssetBundle _bundle;

  Future<LevelDefinition> _load(String path) async {
    final source = await _bundle.loadString(path);
    final decoded = jsonDecode(source);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a level object.');
    }
    return LevelDefinition.fromJson(decoded);
  }

  @override
  Future<LevelDefinition> loadPreview() => _load(LevelAssets.sunflower);

  @override
  Future<List<LevelDefinition>> loadLevels() async {
    final decoded = jsonDecode(await _bundle.loadString(LevelAssets.catalog));
    if (decoded is! List<Object?> || decoded.isEmpty || decoded.length > 200) {
      throw const FormatException('Invalid local catalog.');
    }
    final result = <LevelDefinition>[];
    for (final value in decoded) {
      if (value is! String || !RegExp(r'^[a-z0-9-]+\.json$').hasMatch(value)) {
        throw const FormatException('Invalid asset path.');
      }
      result.add(await _load('assets/levels/$value'));
    }
    if (result.map((level) => level.id).toSet().length != result.length) {
      throw const FormatException('Duplicate level IDs.');
    }
    return List.unmodifiable(result);
  }

  @override
  Future<Map<String, CatalogMetadata>> loadMetadata() async {
    final decoded =
        jsonDecode(await _bundle.loadString('assets/levels/metadata.json'))
            as Map<String, Object?>;
    return Map.unmodifiable(
      decoded.map((id, value) {
        final data = value! as Map<String, Object?>;
        final category = data['category']! as String;
        if (!{
          'nature',
          'animals',
          'objects',
          'patterns',
          'space',
        }.contains(category)) {
          throw const FormatException('Invalid catalog category.');
        }
        return MapEntry(
          id,
          CatalogMetadata(
            category: category,
            tags: List.unmodifiable(
              (data['tags']! as List<Object?>).cast<String>(),
            ),
          ),
        );
      }),
    );
  }
}

/// Native: Android DataStore. Web: localStorage. No cached read of progress.
final class LocalPreferences
    implements
        ProgressRepository,
        PreferencesRepository,
        ArtworkRepository,
        ProgressSyncOutboxRepository {
  LocalPreferences({SharedPreferencesAsync? preferences})
    : _preferences = preferences ?? SharedPreferencesAsync();
  final SharedPreferencesAsync _preferences;
  Future<void> _writes = Future.value();

  String _key(String id, int version) => 'pixelhub.progress.v1.$id.$version';

  @override
  Future<ProgressSnapshot?> read(LevelDefinition level) async {
    await _writes;
    final source = await _preferences.getString(
      _key(level.id, level.contentVersion),
    );
    if (source == null) return null;
    final decoded = jsonDecode(source);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Invalid saved progress.');
    }
    return ProgressSnapshot.fromJson(decoded, level);
  }

  @override
  Future<void> write(ProgressSnapshot progress) {
    final source = jsonEncode(progress.toJson());
    final write = _writes.then(
      (_) => _preferences.setString(
        _key(progress.levelId, progress.levelVersion),
        source,
      ),
    );
    // Preserve failure for the caller, while keeping the storage queue usable.
    _writes = write.catchError((Object _) {});
    return write;
  }

  String _outboxKey(String accountId) {
    // The verified account scope is encoded in the key and the document.
    ProgressSyncOutbox(accountId: accountId);
    final encoded = base64UrlEncode(utf8.encode(accountId));
    return 'pixelhub.sync.outbox.v1.$encoded';
  }

  Future<ProgressSyncOutbox> _loadOutbox(String accountId) async {
    final source = await _preferences.getString(_outboxKey(accountId));
    if (source == null) return ProgressSyncOutbox(accountId: accountId);
    if (utf8.encode(source).length > ProgressSyncOutbox.maxBytes) {
      throw const FormatException('Sync outbox is too large.');
    }
    final decoded = jsonDecode(source);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Invalid sync outbox document.');
    }
    return ProgressSyncOutbox.fromJson(decoded, accountId: accountId);
  }

  @override
  Future<ProgressSyncOutbox> readSyncOutbox(String accountId) async {
    await _writes;
    return _loadOutbox(accountId);
  }

  /// Serialize outbox writes with existing painting and clear-data writes.
  /// Storage failures propagate and never count as a successful enqueue.
  Future<ProgressSyncOutbox> _changeOutbox(
    String accountId,
    ProgressSyncOutbox Function(ProgressSyncOutbox) transform,
  ) {
    final result = _writes.then((_) async {
      final current = await _loadOutbox(accountId);
      final next = transform(current);
      if (identical(next, current)) return current;
      final source = jsonEncode(next.toJson());
      if (utf8.encode(source).length > ProgressSyncOutbox.maxBytes) {
        throw const FormatException('Sync outbox capacity reached.');
      }
      await _preferences.setString(_outboxKey(accountId), source);
      return next;
    });
    _writes = result.then<void>((_) {}, onError: (Object _) {});
    return result;
  }

  @override
  Future<ProgressSyncOutbox> enqueueSyncOperation(
    String accountId,
    PendingProgressSync operation,
  ) => _changeOutbox(accountId, (outbox) => outbox.enqueue(operation));

  @override
  Future<ProgressSyncOutbox> acknowledgeSyncOperation(
    String accountId,
    String operationId,
  ) => _changeOutbox(accountId, (outbox) => outbox.acknowledge(operationId));

  @override
  Future<String?> readLanguage() => _preferences.getString('pixelhub.language');

  @override
  Future<void> writeLanguage(String language) =>
      _enqueue(() => _preferences.setString('pixelhub.language', language));

  Future<void> _enqueue(Future<void> Function() operation) {
    final result = _writes.then((_) => operation());
    _writes = result.catchError((Object _) {});
    return result;
  }

  @override
  Future<ArtworkLibrary> readLibrary() async {
    await _writes;
    final source = await _preferences.getString('pixelhub.library.v1');
    if (source == null) return ArtworkLibrary();
    return ArtworkLibrary.fromJson(jsonDecode(source) as Map<String, Object?>);
  }

  @override
  Future<void> writeLibrary(ArtworkLibrary library) {
    final source = jsonEncode(library.toJson());
    if (utf8.encode(source).length > 2 * 1024 * 1024) {
      return Future<void>.error(
        const FormatException('Local library capacity reached.'),
      );
    }
    return _enqueue(
      () => _preferences.setString('pixelhub.library.v1', source),
    );
  }

  @override
  Future<void> removeProgress(LevelDefinition level) =>
      _enqueue(() => _preferences.remove(_key(level.id, level.contentVersion)));

  @override
  Future<void> clearPixelhubData() => _enqueue(() async {
    // Do not clear unrelated plugin/application preferences on the same origin.
    final keys = await _preferences.getKeys();
    for (final key in keys.where((key) => key.startsWith('pixelhub.'))) {
      await _preferences.remove(key);
    }
  });
}

/// Explicit ephemeral adapter for tests. Production always injects LocalPreferences.
final class MemoryPreferences
    implements
        ProgressRepository,
        PreferencesRepository,
        ArtworkRepository,
        ProgressSyncOutboxRepository {
  final Map<String, ProgressSnapshot> _records = {};
  String? language;
  ArtworkLibrary _library = ArtworkLibrary();
  final Map<String, ProgressSyncOutbox> _outboxes = {};
  String _key(String id, int version) => '$id:$version';

  @override
  Future<ProgressSyncOutbox> readSyncOutbox(String accountId) async =>
      _outboxes[accountId] ?? ProgressSyncOutbox(accountId: accountId);

  @override
  Future<ProgressSyncOutbox> enqueueSyncOperation(
    String accountId,
    PendingProgressSync operation,
  ) async {
    // Keep this read-modify-write synchronous before returning the Future:
    // concurrent test enqueues must not both read the same stale snapshot.
    final current =
        _outboxes[accountId] ?? ProgressSyncOutbox(accountId: accountId);
    final updated = current.enqueue(operation);
    _outboxes[accountId] = updated;
    return updated;
  }

  @override
  Future<ProgressSyncOutbox> acknowledgeSyncOperation(
    String accountId,
    String operationId,
  ) async {
    final current =
        _outboxes[accountId] ?? ProgressSyncOutbox(accountId: accountId);
    final updated = current.acknowledge(operationId);
    _outboxes[accountId] = updated;
    return updated;
  }

  @override
  Future<ProgressSnapshot?> read(LevelDefinition level) async =>
      _records[_key(level.id, level.contentVersion)];
  @override
  Future<void> write(ProgressSnapshot progress) async {
    _records[_key(progress.levelId, progress.levelVersion)] = progress;
  }

  @override
  Future<String?> readLanguage() async => language;
  @override
  Future<void> writeLanguage(String value) async {
    language = value;
  }

  @override
  Future<ArtworkLibrary> readLibrary() async => _library;
  @override
  Future<void> writeLibrary(ArtworkLibrary library) async {
    _library = library;
  }

  @override
  Future<void> removeProgress(LevelDefinition level) async {
    _records.remove(_key(level.id, level.contentVersion));
  }

  @override
  Future<void> clearPixelhubData() async {
    _records.clear();
    _outboxes.clear();
    _library = ArtworkLibrary();
    language = null;
  }
}
