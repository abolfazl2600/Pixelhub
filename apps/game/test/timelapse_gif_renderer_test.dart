import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/features/painting/timelapse_gif_renderer.dart';

void main() {
  final level = LevelDefinition(
    id: 'gif-test',
    title: 'آزمایش',
    titleEn: 'GIF test',
    schemaVersion: 2,
    contentVersion: 1,
    width: 2,
    height: 2,
    palette: [0xffff0000, 0xff0000ff],
    cells: [0, 1, 0, 1],
  );

  ProgressSnapshot snapshot(int bits, int revision, {int generation = 0}) =>
      ProgressSnapshot(
        levelId: level.id,
        levelVersion: level.contentVersion,
        levelChecksum: level.checksum,
        cellCount: level.cells.length,
        generation: generation,
        revision: revision,
        bits: Uint8List.fromList([bits]),
      );

  Map<String, Object?> checkpoint(
    int milestone,
    int attained,
    ProgressSnapshot progress, {
    DateTime? at,
  }) => <String, Object?>{
    'schemaVersion': 1,
    'levelId': level.id,
    'generation': progress.generation,
    'milestonePercent': milestone,
    'attainedPercent': attained,
    'capturedAt': (at ?? DateTime.now().toUtc()).toIso8601String(),
    'progress': progress.toJson(),
  };

  test('GIF encodes blank, intermediate and finished pixel frames', () {
    final first = snapshot(1, 1);
    final complete = snapshot(15, 3);
    final middle = snapshot(3, 2);
    final records = [
      checkpoint(25, 25, first),
      checkpoint(50, 50, middle),
      checkpoint(100, 100, complete),
    ];
    final bytes = renderTimelapseGif(<String, Object?>{
      'level': level.toJson(),
      'completed': complete.toJson(),
      'checkpoints': records,
      'maxSide': 64,
    });
    expect(ascii.decode(bytes.take(6).toList()), 'GIF89a');
    final decoded = img.decodeGif(bytes)!;
    expect(decoded.numFrames, 4);
    expect(decoded.width, 16);
    expect(decoded.height, 16);
    // Pixel-perfect nearest-neighbor scaling, with no UI screenshots.
    final firstPixel = decoded.frames.first.getPixel(0, 0);
    final finalPixel = decoded.frames.last.getPixel(0, 0);
    expect(firstPixel.r.toInt(), greaterThan(220));
    expect(finalPixel.r.toInt(), greaterThan(220));
    expect(finalPixel.g.toInt(), lessThan(40));
  });

  test('deduplicates multi-threshold strokes without invented frames', () {
    final complete = snapshot(15, 2);
    final early = snapshot(3, 1);
    final records = [
      for (var i = 1; i <= 50; i++) checkpoint(i, 50, early),
      for (var i = 51; i <= 100; i++) checkpoint(i, 100, complete),
    ];
    final frames = prepareTimelapseFrames(level, complete, records);
    expect(frames, hasLength(2));
    expect(frames.first.completedCount, 2);
    expect(frames.last.completedCount, 4);
  });

  test('rejects reset generations, missing 100%, and expired checkpoints', () {
    final complete = snapshot(15, 3, generation: 1);
    final old = snapshot(1, 1);
    expect(
      () => prepareTimelapseFrames(level, complete, [
        checkpoint(25, 25, old),
        checkpoint(100, 100, snapshot(15, 2)),
      ]),
      throwsFormatException,
    );
    expect(
      () => prepareTimelapseFrames(level, complete, [
        checkpoint(25, 25, snapshot(1, 1, generation: 1)),
      ]),
      throwsFormatException,
    );
    final expired = DateTime.now().toUtc().subtract(const Duration(hours: 121));
    expect(
      () => prepareTimelapseFrames(level, complete, [
        checkpoint(25, 25, snapshot(1, 1, generation: 1), at: expired),
        checkpoint(100, 100, complete, at: expired),
      ]),
      throwsFormatException,
    );
  });

  test('rejects non-monotonic cell states and excessive output limits', () {
    final complete = snapshot(15, 3);
    expect(
      () => prepareTimelapseFrames(level, complete, [
        checkpoint(25, 25, snapshot(1, 1)),
        checkpoint(50, 50, snapshot(6, 2)),
        checkpoint(100, 100, complete),
      ]),
      throwsFormatException,
    );
    expect(
      () => renderTimelapseGif(<String, Object?>{
        'level': level.toJson(),
        'completed': complete.toJson(),
        'checkpoints': [
          checkpoint(25, 25, snapshot(1, 1)),
          checkpoint(100, 100, complete),
        ],
        'maxSide': 1,
      }),
      throwsFormatException,
    );
  });
}
