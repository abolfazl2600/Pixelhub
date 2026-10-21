import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

class RecordingPreferences extends SharedPreferencesAsync {
  final values = <String, Object>{};
  @override
  Future<String?> getString(String key) async => values[key] as String?;
  @override
  Future<bool?> getBool(String key) async => values[key] as bool?;
  @override
  Future<void> setString(String key, String value) async {
    values[key] = value;
  }

  @override
  Future<void> setBool(String key, bool value) async {
    values[key] = value;
  }

  @override
  Future<void> remove(String key) async {
    values.remove(key);
  }

  @override
  Future<Set<String>> getKeys({Set<String>? allowList}) async => values.keys
      .where((key) => allowList == null || allowList.contains(key))
      .toSet();
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() {
    SharedPreferencesAsyncPlatform.instance =
        InMemorySharedPreferencesAsync.empty();
  });
  test(
    'legacy data remains readable and clearing one product preserves the rest',
    () async {
      final backend = RecordingPreferences();
      backend.values['pixelhub.language'] = 'en';
      backend.values['unrelated.key'] = 'safe';
      final main = LocalPreferences(preferences: backend);
      final kids = LocalPreferences(
        preferences: backend,
        scope: 'pixelhub_kids',
      );
      final art = LocalPreferences(preferences: backend, scope: 'pixelhub_art');
      expect(await main.readLanguage(), 'en');
      expect(await kids.readLanguage(), isNull);
      await kids.writeLanguage('fa');
      await art.writeLanguage('en');
      await kids.writeLibrary(ArtworkLibrary(coins: 12));
      await main.clearPixelhubData();
      expect(await kids.readLanguage(), 'fa');
      expect((await kids.readLibrary()).coins, 12);
      await kids.clearPixelhubData();
      expect(await kids.readLanguage(), isNull);
      expect(await art.readLanguage(), 'en');
      expect(backend.values['unrelated.key'], 'safe');
    },
  );

  test('progress, online caches and badges are product scoped', () async {
    final backend = RecordingPreferences();
    final main = LocalPreferences(preferences: backend);
    final kids = LocalPreferences(preferences: backend, scope: 'pixelhub_kids');
    final level = LevelDefinition(
      id: 'online-test',
      title: 'نمونه',
      titleEn: 'Test',
      schemaVersion: 2,
      contentVersion: 1,
      width: 2,
      height: 2,
      palette: [0xff000000],
      cells: [0, 0, 0, 0],
    );
    final snapshot = ProgressSnapshot(
      levelId: level.id,
      levelVersion: level.contentVersion,
      levelChecksum: level.checksum,
      cellCount: 4,
      generation: 0,
      revision: 1,
      bits: Uint8List.fromList([1]),
    );
    await kids.write(snapshot);
    expect(await main.read(level), isNull);
    expect((await kids.read(level))!.completedCount, 1);
    await main.write(snapshot);
    expect(
      backend.values.containsKey('pixelhub.progress.v1.online-test.1'),
      isTrue,
    );
    expect((await main.read(level))!.completedCount, 1);
    await kids.saveDownloadedLevel(level, category: 'animals');
    await kids.writeEarnedBadges({'test'});
    expect(await main.readDownloadedLevels(), isEmpty);
    expect(await main.readEarnedBadges(), isEmpty);
    expect((await kids.readDownloadedLevels()).single.id, level.id);
    expect(await kids.readEarnedBadges(), {'test'});
    expect(backend.values.containsKey('pixelhub_kids.online.index.v1'), isTrue);
    await main.writeLanguage('fa');
    expect(backend.values.containsKey('pixelhub.language'), isTrue);
    expect(() => LocalPreferences(scope: 'pixelhub.kids'), throwsArgumentError);
  });
}
