import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:shared_preferences/shared_preferences.dart';

final class AssetLevelRepository implements LevelRepository {
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
    if (decoded is! List<Object?> || decoded.isEmpty || decoded.length > 20) {
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
}

/// Native: Android DataStore. Web: localStorage. No cached read of progress.
final class LocalPreferences
    implements ProgressRepository, PreferencesRepository {
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

  @override
  Future<String?> readLanguage() => _preferences.getString('pixelhub.language');

  @override
  Future<void> writeLanguage(String language) =>
      _preferences.setString('pixelhub.language', language);
}

/// Explicit ephemeral adapter for tests. Production always injects LocalPreferences.
final class MemoryPreferences
    implements ProgressRepository, PreferencesRepository {
  final Map<String, ProgressSnapshot> _records = {};
  String? language;
  String _key(String id, int version) => '$id:$version';
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
}
