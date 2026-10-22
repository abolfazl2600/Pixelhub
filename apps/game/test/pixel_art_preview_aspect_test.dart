import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/core/pixel_art_preview.dart';
import 'package:pixelhub/l10n/generated/app_localizations.dart';

void main() {
  testWidgets('pixel previews keep proportions inside wide and tall cards', (
    tester,
  ) async {
    final level = LevelDefinition(
      id: 'preview-aspect',
      title: 'طرح',
      titleEn: 'Preview',
      schemaVersion: 2,
      contentVersion: 1,
      width: 6,
      height: 3,
      palette: [0xfff8edb7],
      cells: List.filled(18, 0),
    );

    Future<void> verify(Size card, Size expectedImage) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: card.width,
                height: card.height,
                child: PixelArtPreview(level: level),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final preview = find.byType(PixelArtPreview);
      final painter = find.descendant(
        of: preview,
        matching: find.byType(CustomPaint),
      );
      final previewRect = tester.getRect(preview);
      final imageRect = tester.getRect(painter.first);

      expect(imageRect.width, closeTo(expectedImage.width, 0.01));
      expect(imageRect.height, closeTo(expectedImage.height, 0.01));
      expect(imageRect.width / imageRect.height, closeTo(2, 0.001));
      expect(imageRect.center.dx, closeTo(previewRect.center.dx, 0.01));
      expect(imageRect.center.dy, closeTo(previewRect.center.dy, 0.01));
    }

    await verify(const Size(400, 180), const Size(360, 180));
    await verify(const Size(160, 260), const Size(160, 80));
  });
}
