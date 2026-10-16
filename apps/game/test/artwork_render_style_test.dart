import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/import/photo_converter.dart';
import 'package:pixelhub/features/painting/artwork_render_style.dart';
import 'package:pixelhub/features/painting/artwork_png_export.dart'
    show artworkPngRenderers;

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

      await storage.writeArtworkStyle('diamond');
      expect(await storage.readArtworkStyle(), 'diamond');
      expect(
        ArtworkRenderStyle.fromStorage(await storage.readArtworkStyle()),
        ArtworkRenderStyle.diamond,
      );
      expect(ArtworkRenderStyle.diamond.storageId, 'diamond');

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

  test('PNG export leaves Pixel flat and draws woven yarn only on opt-in', () {
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

    // Interlaced raised cores at the same point in two palette regions are
    // brighter than the recessed cloth. Pitch is 12px in a 4x4 export.
    final lightRecess = canvasImage.getPixel(120, 120);
    final lightRaised = canvasImage.getPixel(126, 126);
    expect(lightRaised.r.toInt() - lightRecess.r.toInt(), greaterThan(20));
    final darkRecess = canvasImage.getPixel(768, 120);
    final darkRaised = canvasImage.getPixel(774, 126);
    expect(darkRaised.r.toInt() - darkRecess.r.toInt(), greaterThan(14));
    // Pixel mode must stay completely flat even where the yarn would rise.
    expect(pixelImage.getPixel(120, 120).r, pixelImage.getPixel(126, 126).r);
    expect(pixelImage.getPixel(768, 120).r, pixelImage.getPixel(774, 126).r);

    // Diamond mode exports individual facets, gaps, and light direction,
    // while leaving the classic Pixel and Canvas encoders intact.
    final diamond = renderLevelPng({...level, 'renderStyle': 'diamond'});
    expect(diamond, isNotEmpty);
    expect(diamond, isNot(equals(pixel)));
    expect(diamond, isNot(equals(canvas)));
    final gemImage = img.decodePng(diamond)!;
    expect(gemImage.width, 1024);
    expect(gemImage.height, 1024);
    // Pixel (0,0) samples the mounting border, the center samples a gem.
    final mount = gemImage.getPixel(0, 0);
    final center = gemImage.getPixel(128, 128);
    expect(mount.r.toInt(), isNot(center.r.toInt()));
    expect(mount.g.toInt(), isNot(center.g.toInt()));
    // The same palette keeps distinctly colored gem centers.
    expect(
      gemImage.getPixel(640, 128).g.toInt(),
      isNot(gemImage.getPixel(128, 128).g.toInt()),
    );
    expect(
      renderLevelPng({...level, 'renderStyle': 'diamond'}),
      orderedEquals(diamond),
    );

    // The procedural weave is stable across exports, with no extra asset.
    expect(
      renderLevelPng({...level, 'renderStyle': 'canvas'}),
      orderedEquals(canvas),
    );
  });
  test('all painting styles have a registered PNG renderer', () {
    expect(
      artworkPngRenderers.keys.toSet(),
      ArtworkRenderStyle.values.map((style) => style.storageId).toSet(),
    );
    final level = _level().toJson();
    expect(
      () => renderLevelPng({...level, 'renderStyle': 'future-texture'}),
      throwsFormatException,
    );
    expect(
      () => renderLevelPng({...level, 'renderStyle': 123}),
      throwsFormatException,
    );
    // Older call sites without a style keep the original Pixel format.
    expect(
      renderLevelPng(level),
      orderedEquals(renderLevelPng({...level, 'renderStyle': 'pixel'})),
    );
  });
}
