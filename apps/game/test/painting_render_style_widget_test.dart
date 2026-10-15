import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/app/pixelhub_app.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';
import 'package:pixelhub/features/painting/painting_board.dart';
import 'package:pixelhub/features/painting/painting_preview_screen.dart';

import 'bootstrap_test.dart' show fixture;

class _StyleTestLevels implements LevelRepository {
  _StyleTestLevels(this.level);
  final LevelDefinition level;

  @override
  Future<LevelDefinition> loadPreview() async => level;

  @override
  Future<List<LevelDefinition>> loadLevels() async => [level];
}

void main() {
  testWidgets(
    'Canvas style toggles mid-paint without changing progress and persists offline',
    (tester) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = const Size(390, 1200);
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      final level = fixture();
      final storage = MemoryPreferences();

      Future<void> openApp() async {
        await tester.pumpWidget(
          PixelhubApp(
            repository: _StyleTestLevels(level),
            preferences: storage,
            progressRepository: storage,
            initialRoute: '/painting/${level.id}',
          ),
        );
        await tester.pumpAndSettle();
      }

      await openApp();
      final controller = tester
          .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
          .controller;
      final boardRect = tester.getRect(
        find.byKey(const ValueKey('painting-board')),
      );
      await tester.tapAt(
        boardRect.topLeft +
            Offset(boardRect.width * .25, boardRect.height * .25),
      );
      await tester.pumpAndSettle();
      final completedBeforeSwitch = controller.session!.completedCount;
      expect(completedBeforeSwitch, greaterThan(0));
      controller.selectColor(1);
      controller.showHint();
      final selectedBeforeSwitch = controller.session!.selectedColor;
      final hintBeforeSwitch = controller.hintIndex;
      final viewer = tester.widget<InteractiveViewer>(
        find.byType(InteractiveViewer),
      );
      viewer.transformationController!.value = Matrix4.diagonal3Values(2, 2, 1);
      await tester.pump();
      final zoomBeforeSwitch = viewer.transformationController!.value
          .getMaxScaleOnAxis();

      await tester.ensureVisible(find.byKey(const ValueKey('style-canvas')));
      await tester.tap(find.byKey(const ValueKey('style-canvas')));
      await tester.pumpAndSettle();
      expect(storage.artworkStyle, 'canvas');
      expect(controller.session!.completedCount, completedBeforeSwitch);
      expect(controller.session!.selectedColor, selectedBeforeSwitch);
      expect(controller.hintIndex, hintBeforeSwitch);
      expect(
        tester
            .widget<InteractiveViewer>(find.byType(InteractiveViewer))
            .transformationController!
            .value
            .getMaxScaleOnAxis(),
        zoomBeforeSwitch,
      );
      expect(
        tester.widget<PaintingBoard>(find.byType(PaintingBoard)).renderStyle,
        ArtworkRenderStyle.canvas,
      );

      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      await openApp();
      await tester.ensureVisible(find.byKey(const ValueKey('style-canvas')));
      expect(
        tester
            .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
            .renderStyle,
        ArtworkRenderStyle.canvas,
      );
      expect(storage.artworkStyle, 'canvas');
      final reopened = tester
          .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
          .controller;
      expect(reopened.session!.completedCount, completedBeforeSwitch);

      // Diamond is a presentation-only toggle, including saved sessions.
      await tester.ensureVisible(find.byKey(const ValueKey('style-diamond')));
      await tester.tap(find.byKey(const ValueKey('style-diamond')));
      await tester.pumpAndSettle();
      expect(storage.artworkStyle, 'diamond');
      expect(reopened.session!.completedCount, completedBeforeSwitch);
      expect(
        tester.widget<PaintingBoard>(find.byType(PaintingBoard)).renderStyle,
        ArtworkRenderStyle.diamond,
      );

      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      await openApp();
      await tester.ensureVisible(find.byKey(const ValueKey('style-diamond')));
      expect(
        tester
            .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
            .renderStyle,
        ArtworkRenderStyle.diamond,
      );
      expect(storage.artworkStyle, 'diamond');
      expect(
        tester
            .widget<PaintingPreviewScreen>(find.byType(PaintingPreviewScreen))
            .controller
            .session!
            .completedCount,
        completedBeforeSwitch,
      );
    },
  );
}
