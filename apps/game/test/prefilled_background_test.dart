import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:image/image.dart' as img;
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:pixelhub/features/painting/timelapse_gif_renderer.dart';

void main() {
  LevelDefinition picture({bool preFill = true}) => LevelDefinition(
    id: 'prefilled-example',
    title: 'نمونه',
    titleEn: 'Example',
    schemaVersion: 2,
    contentVersion: 1,
    width: 5,
    height: 5,
    palette: [0xfff7f3e8, 0xff123456],
    cells: [
      0, 0, 0, 0, 0,
      0, 1, 1, 1, 0,
      0, 1, 0, 1, 0,
      0, 1, 1, 1, 0,
      0, 0, 0, 0, 0,
    ],
    preFilledBackground: preFill,
  );

  test('the exterior is prefilled, but an enclosed light detail is not', () {
    final level = picture();
    expect(level.preFilledCount, 16);
    expect(level.paintableCellCount, 9);
    expect(level.isPreFilled(0), isTrue);
    expect(level.isPreFilled(12), isFalse);
    expect(level.isPreFilled(6), isFalse);
    final session = PaintingSession(level);
    expect(session.fraction, 0);
    expect(session.completedCount, 16);
    expect(session.remaining, [1, 8]);
    expect(session.isComplete, isFalse);
    expect(session.paintCell(0), isFalse);
    session.beginStroke();
    expect(session.paintCell(12), isTrue);
    session.endStroke();
    expect(session.fraction, closeTo(1 / 9, 0.0001));
    expect(session.remaining, [0, 8]);
    expect(session.previewTool(PrecisionPaintTool.magicWand, 0, 0), isEmpty);
    expect(session.previewTool(PrecisionPaintTool.colorSplash, 0, 0), isEmpty);
    expect(session.paintBurst(maxCells: 5), 0);
  });

  test('reset restores filled background and the painted-percent zero', () {
    final session = PaintingSession(picture());
    session.beginStroke();
    expect(session.paintCell(12), isTrue);
    session.endStroke();
    session.reset();
    expect(session.fraction, 0);
    expect(session.completedCount, 16);
    expect(session.generation, 1);
    expect(session.isCompleted(0), isTrue);
    expect(session.isCompleted(12), isFalse);
    expect(session.snapshot.completedCount, 16);
  });

  test('older progress is retained when a level opts in to prefilling', () {
    final legacy = picture(preFill: false);
    final session = PaintingSession(legacy)..beginStroke();
    session.selectColor(1);
    expect(session.paintCell(6), isTrue);
    session.endStroke();
    final oldProgress = ProgressSnapshot.fromJson(session.snapshot.toJson(), legacy);
    final updated = picture();
    expect(updated.checksum, legacy.checksum);
    final restored = PaintingSession(updated, progress: oldProgress);
    expect(restored.isCompleted(6), isTrue);
    expect(restored.isCompleted(0), isTrue);
    expect(restored.isCompleted(12), isFalse);
    expect(restored.completedCount, 17);
    expect(restored.fraction, closeTo(1 / 9, 0.0001));
    expect(ProgressSnapshot.fromJson(restored.snapshot.toJson(), updated).completedCount, 17);
  });

  test('new JSON flag round trips; old checksum and defaults are stable', () {
    final level = picture();
    final json = level.toJson();
    expect(json['preFilledBackground'], isTrue);
    expect(LevelDefinition.fromJson(json).preFilledCount, 16);
    final old = picture(preFill: false);
    expect(old.toJson().containsKey('preFilledBackground'), isFalse);
    expect(old.preFilledCount, 0);
    expect(old.paintableCellCount, 25);
    expect(level.checksum, old.checksum);
    expect(
      () => LevelDefinition.fromJson({
        ...json,
        'preFilledBackground': 'true',
      }),
      throwsFormatException,
    );
    final blank = LevelDefinition(
      id: 'blank',
      title: 'سفید',
      titleEn: 'Blank',
      schemaVersion: 2,
      contentVersion: 1,
      width: 2,
      height: 2,
      palette: [0xffffffff],
      cells: [0, 0, 0, 0],
      preFilledBackground: true,
    );
    expect(blank.preFilledCount, 0);
  });

  test('GIF begins with already colored background and respects real progress', () {
    final level = picture();
    final session = PaintingSession(level);
    session.beginStroke();
    expect(session.paintCell(12), isTrue);
    session.endStroke();
    final partial = session.snapshot;
    session.selectColor(1);
    session.beginStroke();
    for (var index = 0; index < level.cells.length; index++) {
      session.paintCell(index);
    }
    session.endStroke();
    final complete = session.snapshot;
    expect(session.isComplete, isTrue);
    final now = DateTime.now().toUtc();
    final checkpoints = <Map<String, Object?>>[
      for (final entry in [
        (11, partial),
        (100, complete),
      ])
        <String, Object?>{
          'schemaVersion': 1,
          'levelId': level.id,
          'generation': entry.$2.generation,
          'milestonePercent': entry.$1,
          'attainedPercent': entry.$1,
          'capturedAt': now.toIso8601String(),
          'progress': entry.$2.toJson(),
        },
    ];
    final gif = renderTimelapseGif({
      'level': level.toJson(),
      'completed': complete.toJson(),
      'checkpoints': checkpoints,
      'maxSide': 64,
    });
    final decoded = img.decodeGif(gif)!;
    expect(decoded.numFrames, 3);
    final exterior = decoded.frames.first.getPixel(0, 0);
    expect(exterior.b.toInt(), lessThan(240));
    final center = decoded.frames.first.getPixel(16, 16);
    expect(center.b.toInt(), greaterThan(240));
  });

  test('opt-in fixture bitset never mutates shared mask', () {
    final level = picture();
    final bits = level.initialCompletedBits;
    expect(bits.length, 4);
    bits[0] = 0;
    expect(level.initialCompletedBits[0], isNot(0));
    expect(
      () => ProgressSnapshot(
        levelId: level.id,
        levelVersion: level.contentVersion,
        levelChecksum: level.checksum,
        cellCount: level.cells.length,
        generation: 0,
        revision: 0,
        bits: Uint8List.fromList([255, 255, 255, 255]),
      ),
      throwsFormatException,
    );
  });
}
