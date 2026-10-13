import 'dart:typed_data';

import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

/// One shared Android/Web engine, independent of Flutter and storage plugins.
final class PaintingSession {
  PaintingSession(this.level, {ProgressSnapshot? progress})
    : _bits = Uint8List((level.cells.length + 7) ~/ 8),
      _remaining = List<int>.filled(level.palette.length, 0) {
    if (progress != null) {
      if (progress.levelId != level.id ||
          progress.levelVersion != level.contentVersion ||
          progress.levelChecksum != level.checksum ||
          progress.cellCount != level.cells.length) {
        throw const FormatException('Session/level mismatch.');
      }
      _bits.setAll(0, progress.bits);
      generation = progress.generation;
      revision = progress.revision;
      completedCount = progress.completedCount;
    }
    for (var index = 0; index < level.cells.length; index++) {
      if (!isCompleted(index)) _remaining[level.cells[index]]++;
    }
  }

  final LevelDefinition level;
  final Uint8List _bits;
  final List<int> _remaining;
  List<int>? _stroke;
  int _selectedColor = 0;
  int completedCount = 0;
  int generation = 0;
  int revision = 0;

  List<int> get remaining => List.unmodifiable(_remaining);
  int get selectedColor => _selectedColor;

  bool get isComplete => completedCount == level.cells.length;
  double get fraction => completedCount / level.cells.length;
  bool isCompleted(int index) => _bits[index ~/ 8] & (1 << (index % 8)) != 0;

  void selectColor(int color) {
    if (color < 0 || color >= level.palette.length) {
      throw RangeError.index(color, _remaining);
    }
    _selectedColor = color;
  }

  void beginStroke() {
    endStroke();
    _stroke = [];
  }

  void endStroke() {
    _stroke = null;
  }

  bool paintCell(int index) {
    if (index < 0 ||
        index >= level.cells.length ||
        isCompleted(index) ||
        level.cells[index] != _selectedColor) {
      return false;
    }
    _stroke ??= [];
    _bits[index ~/ 8] |= 1 << (index % 8);
    _stroke!.add(index);
    completedCount++;
    _remaining[_selectedColor]--;
    revision++;
    return true;
  }

  /// Bresenham interpolation includes cells between sparse pointer events.
  int paintLine(int fromX, int fromY, int toX, int toY) {
    if (fromX < 0 ||
        fromY < 0 ||
        toX < 0 ||
        toY < 0 ||
        fromX >= level.width ||
        toX >= level.width ||
        fromY >= level.height ||
        toY >= level.height) {
      return 0;
    }
    final dx = (toX - fromX).abs();
    final dy = -(toY - fromY).abs();
    final sx = fromX < toX ? 1 : -1;
    final sy = fromY < toY ? 1 : -1;
    var error = dx + dy;
    var x = fromX;
    var y = fromY;
    var changed = 0;
    while (true) {
      if (x >= 0 &&
          x < level.width &&
          y >= 0 &&
          y < level.height &&
          paintCell(y * level.width + x)) {
        changed++;
      }
      if (x == toX && y == toY) break;
      final twice = 2 * error;
      if (twice >= dy) {
        error += dy;
        x += sx;
      }
      if (twice <= dx) {
        error += dx;
        y += sy;
      }
    }
    return changed;
  }

  /// Paint up to [maxCells] unfinished cells matching the selected color.
  /// Paints matching cells locally without undo history or wallet charges.
  int paintBurst({int maxCells = 5}) {
    if (maxCells < 1 || maxCells > 64) {
      throw RangeError.range(maxCells, 1, 64, 'maxCells');
    }
    endStroke();
    beginStroke();
    var painted = 0;
    for (var i = 0; i < level.cells.length && painted < maxCells; i++) {
      if (paintCell(i)) painted++;
    }
    endStroke();
    return painted;
  }

  void _erase(List<int> cells) {
    for (final index in cells) {
      _bits[index ~/ 8] &= ~(1 << (index % 8));
      completedCount--;
      _remaining[level.cells[index]]++;
    }
    if (cells.isNotEmpty) revision++;
  }

  bool cancelStroke() {
    final stroke = _stroke;
    _stroke = null;
    if (stroke == null || stroke.isEmpty) return false;
    _erase(stroke);
    return true;
  }

  void reset() {
    _stroke = null;
    _bits.fillRange(0, _bits.length, 0);
    _remaining.fillRange(0, _remaining.length, 0);
    for (final color in level.cells) {
      _remaining[color]++;
    }
    completedCount = 0;
    generation++;
    revision++;
  }

  ProgressSnapshot get snapshot => ProgressSnapshot(
    levelId: level.id,
    levelVersion: level.contentVersion,
    levelChecksum: level.checksum,
    cellCount: level.cells.length,
    generation: generation,
    revision: revision,
    bits: _bits,
  );
}
