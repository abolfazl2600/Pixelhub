import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/features/painting/timelapse_gif_encoder.dart';

void main() {
  final level = LevelDefinition(
    id: 'gif-fixture',
    title: 'نمونه',
    titleEn: 'Sample',
    schemaVersion: 2,
    contentVersion: 1,
    width: 2,
    height: 2,
    palette: [0xffff0000, 0xff0000ff],
    cells: [0, 1, 0, 1],
  );

  Map<String, Object?> checkpoint(int percent, int bits, int generation) {
    final snapshot = ProgressSnapshot(
      levelId: level.id,
      levelVersion: level.contentVersion,
      levelChecksum: level.checksum,
      cellCount: 4,
      generation: generation,
      revision: percent,
      bits: Uint8List.fromList([bits]),
    );
    return {
      'generation': generation,
      'milestonePercent': percent,
      'attainedPercent': percent,
      'progress': snapshot.toJson(),
    };
  }

  test(
    'encodes actual colored cells in GIF and finishes with original colors',
    () {
      final encoded = encodePaintingTimelapse({
        'level': level.toJson(),
        'generation': 0,
        'checkpoints': [
          checkpoint(100, 15, 0),
          checkpoint(50, 3, 0),
          checkpoint(25, 1, 0),
        ],
      });
      expect(utf8.decode(encoded.take(3).toList()), 'GIF');
      final animation = img.decodeGif(encoded);
      expect(animation, isNotNull);
      expect(animation!.numFrames, greaterThanOrEqualTo(3));
      final last = animation.frames.last;
      expect(last.getPixel(0, 0).r.toInt(), 255);
      expect(last.getPixel(last.width - 1, 0).b.toInt(), 255);
    },
  );

  test(
    'rejects incomplete and mixed generations rather than fabricating replay',
    () {
      expect(
        () => encodePaintingTimelapse({
          'level': level.toJson(),
          'generation': 2,
          'checkpoints': [checkpoint(25, 1, 2), checkpoint(100, 15, 1)],
        }),
        throwsFormatException,
      );
    },
  );

  test('rejects non-monotonic colored bitsets', () {
    expect(
      () => encodePaintingTimelapse({
        'level': level.toJson(),
        'generation': 0,
        'checkpoints': [
          checkpoint(25, 1, 0),
          checkpoint(50, 2, 0),
          checkpoint(100, 15, 0),
        ],
      }),
      throwsFormatException,
    );
  });
}
