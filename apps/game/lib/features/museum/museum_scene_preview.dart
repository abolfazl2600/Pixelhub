import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import 'museum_scene_painters.dart';

/// The same scene painter as the full room, previewed with the user's actual
/// finished paintings. Empty slots are blank; no screenshot artwork is baked in.
class MuseumScenePreview extends StatelessWidget {
  const MuseumScenePreview({
    required this.theme,
    required this.levels,
    super.key,
  });

  final String theme;
  final List<LevelDefinition?> levels;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, dimensions) {
      final x = dimensions.maxWidth / 64;
      final y = dimensions.maxHeight / 88;
      final frameColor = switch (theme) {
        'royal' => const Color(0xffffd46c),
        'sky' => const Color(0xffddebf2),
        'botanical' => const Color(0xff855b3b),
        _ => const Color(0xffbd874b),
      };
      final wall = switch (theme) {
        'royal' => 'emerald',
        'sky' => 'blue',
        'botanical' => 'sage',
        _ => 'cream',
      };
      return Stack(
        clipBehavior: Clip.hardEdge,
        children: [
          Positioned.fill(
            child: CustomPaint(painter: MuseumComposedScenePainter(theme, wall)),
          ),
          for (var i = 0; i < 6; i++)
            Positioned(
              left: MuseumSceneLayout.left(i) * x,
              top: MuseumSceneLayout.top(theme, 'grid', i) * y,
              width: MuseumSceneLayout.frameWidth * x,
              height: MuseumSceneLayout.frameHeight * y,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  border: Border.all(
                    color: frameColor,
                    width: math.max(1, x * .9),
                  ),
                  color: const Color(0xfffff4e5),
                ),
                child: Padding(
                  padding: EdgeInsets.all(math.max(.5, x * .4)),
                  child: i < levels.length && levels[i] != null
                      ? PixelArtPreview(level: levels[i]!)
                      : const ColoredBox(color: Color(0xffe9d8c0)),
                ),
              ),
            ),

        ],
      );
    },
  );
}
