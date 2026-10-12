import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';

enum PaintingStatus { loading, ready, error }

enum SaveStatus { saved, saving, error }

class PaintingController extends ChangeNotifier {
  PaintingController(this.level, this.repository, {this.onCompleted});

  final LevelDefinition level;
  final ProgressRepository repository;
  final VoidCallback? onCompleted;
  bool _completionReported = false;
  PaintingStatus status = PaintingStatus.loading;
  SaveStatus saveStatus = SaveStatus.saved;
  PaintingSession? session;
  ProgressSnapshot? _pendingSave;
  int? hintIndex;
  Future<void>? _draining;
  bool _disposed = false;
  int _loadGeneration = 0;

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> load() async {
    final request = ++_loadGeneration;
    status = PaintingStatus.loading;
    _notify();
    try {
      final progress = await repository.read(level);
      if (_disposed || request != _loadGeneration) return;
      session = PaintingSession(level, progress: progress);
      _completionReported = session!.isComplete;
      hintIndex = null;
      status = PaintingStatus.ready;
    } on Object {
      if (_disposed || request != _loadGeneration) return;
      status = PaintingStatus.error;
    }
    _notify();
  }

  void selectColor(int color) {
    session!.selectColor(color);
    _notify();
  }

  void beginStroke() => session!.beginStroke();
  void endStroke() {
    session!.endStroke();
    _notify();
  }

  bool paintLine(int x1, int y1, int x2, int y2) {
    if (session!.paintLine(x1, y1, x2, y2) == 0) return false;
    hintIndex = null;
    _changed();
    return true;
  }

  /// Reveal a still-uncolored cell. This never alters saved progress.
  /// If the selected color has none left, select the next useful color.
  int? showHint() {
    final active = session;
    if (active == null || status != PaintingStatus.ready) return null;
    int? candidate;
    for (var i = 0; i < level.cells.length; i++) {
      if (!active.isCompleted(i) &&
          level.cells[i] == active.selectedColor) {
        candidate = i;
        break;
      }
    }
    if (candidate == null) {
      for (var i = 0; i < level.cells.length; i++) {
        if (!active.isCompleted(i)) {
          candidate = i;
          active.selectColor(level.cells[i]);
          break;
        }
      }
    }
    hintIndex = candidate;
    _notify();
    return candidate;
  }

  /// Local free demo. Paid charges, inventory and coins are not activated.
  int useBomb() {
    final active = session;
    if (active == null || status != PaintingStatus.ready) return 0;
    final painted = active.paintBurst();
    if (painted > 0) {
      hintIndex = null;
      _changed();
    }
    return painted;
  }

  void cancelStroke() {
    if (session!.cancelStroke()) _changed();
  }

  void undo() {
    if (session!.undo()) {
      hintIndex = null;
      _changed();
    }
  }

  /// Called only after an explicit reset confirmation, including damaged saves.
  void reset() {
    session ??= PaintingSession(level);
    session!.reset();
    _completionReported = false;
    hintIndex = null;
    status = PaintingStatus.ready;
    _changed();
  }

  void _changed() {
    if (session!.isComplete && !_completionReported) {
      _completionReported = true;
      onCompleted?.call();
    }
    _pendingSave = session!.snapshot;
    saveStatus = SaveStatus.saving;
    _notify();
    unawaited(flush());
  }

  /// Coalesces queued changes but never writes an old snapshot after a reset.
  Future<void> flush() {
    if (_draining != null) return _draining!;
    final done = Completer<void>();
    _draining = done.future;
    unawaited(() async {
      while (_pendingSave != null) {
        final snapshot = _pendingSave!;
        _pendingSave = null;
        saveStatus = SaveStatus.saving;
        _notify();
        try {
          await repository.write(snapshot);
        } on Object {
          _pendingSave ??= snapshot;
          saveStatus = SaveStatus.error;
          break;
        }
      }
      if (_pendingSave == null) saveStatus = SaveStatus.saved;
      _draining = null;
      _notify();
      done.complete();
    }());
    return done.future;
  }

  @override
  void dispose() {
    // Keep an already initiated storage write alive; stop UI notifications.
    _disposed = true;
    super.dispose();
  }
}
