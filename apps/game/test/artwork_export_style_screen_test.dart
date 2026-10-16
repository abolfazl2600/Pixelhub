import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/core/pixel_art_preview.dart';
import 'package:pixelhub/features/gallery/artwork_screen.dart';
import 'package:pixelhub/features/gallery/export_button.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';

import 'bootstrap_test.dart' show fixture;

class _SingleLevelRepository implements LevelRepository {
  const _SingleLevelRepository(this.level);

  final LevelDefinition level;

  @override
  Future<LevelDefinition> loadPreview() async => level;

  @override
  Future<List<LevelDefinition>> loadLevels() async => [level];
}

void main() {
  testWidgets('artwork detail preview and PNG export follow the saved style', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 1200);
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final level = fixture();
    final storage = MemoryPreferences();
    final session = PaintingSession(level);
    for (var index = 0; index < level.cells.length; index++) {
      session.selectColor(level.cells[index]);
      session.paintCell(index);
    }
    session.endStroke();
    await storage.write(session.snapshot);

    for (final style in ArtworkRenderStyle.values) {
      await storage.writeArtworkStyle(style.storageId);
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pumpWidget(
        PixelhubApp(
          repository: _SingleLevelRepository(level),
          preferences: storage,
          progressRepository: storage,
          initialRoute: '/artwork/${level.id}',
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(ArtworkScreen), findsOneWidget);
      expect(
        tester.widget<ArtworkScreen>(find.byType(ArtworkScreen)).renderStyle,
        style,
      );
      expect(
        tester.widget<PixelArtPreview>(find.byType(PixelArtPreview)).renderStyle,
        style,
      );
      expect(
        tester.widget<ExportButton>(find.byType(ExportButton)).renderStyle,
        style,
      );
    }
  });
}
