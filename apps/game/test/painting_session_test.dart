import 'dart:math';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';

import 'bootstrap_test.dart' show fixture;

void main() {
  test('wrong colors and duplicate taps never change counts', () {
    final session = PaintingSession(fixture());
    session.beginStroke();
    expect(session.paintCell(1), isFalse);
    expect(session.paintCell(0), isTrue);
    expect(session.paintCell(0), isFalse);
    session.endStroke();
    expect(session.completedCount, 1);
    expect(session.remaining, [1, 2]);
  });

  test('fast drag interpolates 128 cells consistently', () {
    final level = LevelDefinition(
      id: 'line',
      title: 'خط',
      titleEn: 'Line',
      schemaVersion: 2,
      contentVersion: 1,
      width: 128,
      height: 1,
      palette: [0xff316349],
      cells: List.filled(128, 0),
    );
    final session = PaintingSession(level)..beginStroke();
    expect(session.paintLine(0, 0, 127, 0), 128);
    session.endStroke();
    expect(session.isComplete, isTrue);
    expect(session.completedCount, 128);
  });

  test(
    'diagonal strokes, cancel and reset preserve counters and generation',
    () {
      final session = PaintingSession(fixture())..beginStroke();
      session.paintLine(0, 0, 1, 1);
      expect(session.completedCount, 2);
      expect(session.cancelStroke(), isTrue);
      expect(session.completedCount, 0);
      session.beginStroke();
      session.paintCell(0);
      session.endStroke();
      final previousRevision = session.revision;
      session.reset();
      expect(session.generation, 1);
      expect(session.revision, greaterThan(previousRevision));
      expect(session.completedCount, 0);
    },
  );

  test('snapshot restores flags and validates identity and unused bits', () {
    final level = fixture();
    final session = PaintingSession(level)..beginStroke();
    session.paintCell(0);
    session.endStroke();
    final snapshot = session.snapshot;
    final restored = PaintingSession(
      level,
      progress: ProgressSnapshot.fromJson(snapshot.toJson(), level),
    );
    expect(restored.completedCount, 1);
    expect(restored.isCompleted(0), isTrue);
    expect(restored.remaining, [1, 2]);
    expect(() => snapshot.bits[0] = 0, throwsUnsupportedError);
    expect(
      () => ProgressSnapshot.fromJson({
        ...snapshot.toJson(),
        'levelVersion': 42,
      }, level),
      throwsFormatException,
    );
    expect(
      () => ProgressSnapshot.fromJson({
        ...snapshot.toJson(),
        'completedCount': 99,
      }, level),
      throwsFormatException,
    );
    expect(
      () => ProgressSnapshot(
        levelId: level.id,
        levelVersion: 1,
        levelChecksum: level.checksum,
        cellCount: 4,
        generation: 0,
        revision: 0,
        bits: Uint8List.fromList([255]),
      ),
      throwsFormatException,
    );
  });

  test('random paint and reset operations preserve count invariants', () {
    final session = PaintingSession(fixture());
    final random = Random(2600);
    for (var i = 0; i < 1000; i++) {
      switch (random.nextInt(4)) {
        case 0:
          session.reset();
        default:
          session.selectColor(random.nextInt(2));
          session.beginStroke();
          session.paintCell(random.nextInt(4));
          session.endStroke();
      }
      expect(session.completedCount, session.snapshot.completedCount);
      expect(
        session.remaining.reduce((a, b) => a + b) + session.completedCount,
        4,
      );
      expect(session.remaining.every((value) => value >= 0), isTrue);
    }
  });
  test('burst paints a limited number of matching cells', () {
    final level = LevelDefinition(
      id: 'bomb-test',
      title: 'بمب',
      titleEn: 'Bomb',
      schemaVersion: 2,
      contentVersion: 1,
      width: 4,
      height: 4,
      palette: [0xff000000, 0xffffffff],
      cells: List<int>.filled(16, 0),
    );
    final session = PaintingSession(level);
    expect(session.paintBurst(), 5);
    expect(session.completedCount, 5);
    expect(session.paintBurst(maxCells: 3), 3);
    expect(session.completedCount, 8);
    expect(() => session.paintBurst(maxCells: 0), throwsRangeError);
  });
}
