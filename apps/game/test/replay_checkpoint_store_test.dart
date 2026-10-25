import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';
import 'package:pixelhub/features/painting/replay_checkpoint_store.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferencesAsyncPlatform.instance =
        InMemorySharedPreferencesAsync.empty();
  });

  test(
    'records immutable checkpoint payloads and deduplicates milestone keys',
    () async {
      final store = ReplayCheckpointStore();
      final snapshot = ProgressSnapshot(
        levelId: 'sample',
        levelVersion: 1,
        levelChecksum: 'checksum',
        cellCount: 8,
        generation: 0,
        revision: 1,
        bits: Uint8List.fromList([1]),
      );
      await store.record(
        levelId: 'sample',
        generation: 0,
        milestonePercent: 12,
        attainedPercent: 12,
        snapshot: snapshot,
      );
      final laterSnapshot = ProgressSnapshot(
        levelId: 'sample',
        levelVersion: 1,
        levelChecksum: 'checksum',
        cellCount: 8,
        generation: 0,
        revision: 2,
        bits: Uint8List.fromList([3]),
      );
      await store.record(
        levelId: 'sample',
        generation: 0,
        milestonePercent: 12,
        attainedPercent: 12,
        snapshot: laterSnapshot,
      );

      final records = await store.readValid('sample');
      expect(records, hasLength(1));
      expect(records.single['milestonePercent'], 12);
      final progress = records.single['progress'] as Map<String, dynamic>;
      expect(progress['completedCells'], base64Encode([1]));
    },
  );

  test(
    'purges only expired replay records and leaves normal progress untouched',
    () async {
      final preferences = SharedPreferencesAsync();
      final now = DateTime.utc(2026, 10, 25, 12);
      await preferences.setString('pixelhub.progress.v1.sample.1', 'keep-me');
      await preferences.setString(
        'pixelhub.replay_checkpoint.v1.sample.0.1',
        jsonEncode({
          'capturedAt': now
              .subtract(const Duration(hours: 121))
              .toIso8601String(),
        }),
      );
      await preferences.setString(
        'pixelhub.replay_checkpoint.v1.sample.0.2',
        jsonEncode({
          'capturedAt': now
              .subtract(const Duration(hours: 119))
              .toIso8601String(),
        }),
      );

      await ReplayCheckpointStore(
        preferences: preferences,
      ).purgeExpired(now: now);
      expect(
        await preferences.getString('pixelhub.progress.v1.sample.1'),
        'keep-me',
      );
      expect(
        await preferences.getString('pixelhub.replay_checkpoint.v1.sample.0.1'),
        isNull,
      );
      expect(
        await preferences.getString('pixelhub.replay_checkpoint.v1.sample.0.2'),
        isNotNull,
      );
    },
  );
}
