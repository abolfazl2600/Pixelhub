import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/import/photo_converter.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';

LevelDefinition _level() => LevelDefinition(
  id: 'sunflower',
  title: 'گل آفتابگردان',
  titleEn: 'Sunflower',
  schemaVersion: 2,
  contentVersion: 1,
  width: 4,
  height: 4,
  palette: [0xfff4e8d1, 0xff2f4b3a],
  cells: [0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0],
);

void main() {
  test(
    'style preferences are local, persistent, and fail safely to Pixel',
    () async {
      final storage = MemoryPreferences();
      expect(await storage.readArtworkStyle(), isNull);
      expect(
        ArtworkRenderStyle.fromStorage(await storage.readArtworkStyle()),
        ArtworkRenderStyle.pixel,
      );

      await storage.writeArtworkStyle('canvas');
      expect(await storage.readArtworkStyle(), 'canvas');
      expect(
        ArtworkRenderStyle.fromStorage(await storage.readArtworkStyle()),
        ArtworkRenderStyle.canvas,
      );

      storage.artworkStyle = 'unknown-corrupt-value';
      expect(await storage.readArtworkStyle(), isNull);
      expect(
        ArtworkRenderStyle.fromStorage(await storage.readArtworkStyle()),
        ArtworkRenderStyle.pixel,
      );
      await expectLater(
        storage.writeArtworkStyle('watercolor'),
        throwsFormatException,
      );
    },
  );

  test(
    'PNG export keeps legacy Pixel output and applies Canvas weave only on opt-in',
    () {
      final level = _level().toJson();
      final pixel = renderLevelPng({...level, 'renderStyle': 'pixel'});
      final canvas = renderLevelPng({...level, 'renderStyle': 'canvas'});
      expect(pixel, isNotEmpty);
      expect(canvas, isNotEmpty);
      expect(canvas, isNot(equals(pixel)));

      final pixelImage = img.decodePng(pixel)!;
      final canvasImage = img.decodePng(canvas)!;
      expect(canvasImage.width, pixelImage.width);
      expect(canvasImage.height, pixelImage.height);
      expect(pixelImage.width, 1024);
      expect(pixelImage.height, 1024);
    },
  );
}
