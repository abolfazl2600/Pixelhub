import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/features/painting/painting_controller.dart';
import 'package:pixelhub/features/painting/timelapse_gif_button.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

class _DoneProgress implements ProgressRepository {
  _DoneProgress(this.saved);
  final ProgressSnapshot saved;

  @override
  Future<ProgressSnapshot?> read(LevelDefinition level) async => saved;

  @override
  Future<void> write(ProgressSnapshot snapshot) async {}
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferencesAsyncPlatform.instance =
        InMemorySharedPreferencesAsync.empty();
  });

  testWidgets('completion action refuses missing timelapse history safely', (
    tester,
  ) async {
    final level = LevelDefinition(
      id: 'no-history',
      title: 'تست',
      titleEn: 'Test',
      schemaVersion: 2,
      contentVersion: 1,
      width: 2,
      height: 2,
      palette: [0xff123456],
      cells: [0, 0, 0, 0],
    );
    final completed = ProgressSnapshot(
      levelId: level.id,
      levelVersion: level.contentVersion,
      levelChecksum: level.checksum,
      cellCount: 4,
      generation: 0,
      revision: 1,
      bits: Uint8List.fromList([15]),
    );
    final controller = PaintingController(level, _DoneProgress(completed));
    addTearDown(controller.dispose);
    await controller.load();

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: TimelapseGifButton(controller: controller)),
      ),
    );
    await tester.tap(find.byKey(const ValueKey('create-timelapse-gif')));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('timelapse-preview')), findsNothing);
    expect(find.textContaining('unexpired painting replay'), findsOneWidget);
    expect(find.byKey(const ValueKey('timelapse-save')), findsNothing);
    await tester.tap(find.byKey(const ValueKey('timelapse-close')));
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsNothing);
  });
}
