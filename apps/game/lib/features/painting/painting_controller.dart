import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:painting_engine/painting_engine.dart';

enum PaintingStatus { loading, ready, error }

enum SaveStatus { saved, saving, error }

class PaintingController extends ChangeNotifier {
  PaintingController(this.level, this.repository);

  final LevelDefinition level;
  final ProgressRepository repository;
  PaintingStatus status = PaintingStatus.loading;
  SaveStatus saveStatus = SaveStatus.saved;
  PaintingSession? session;
  ProgressSnapshot? _pendingSave;
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
    _changed();
    return true;
  }

  void cancelStroke() {
    if (session!.cancelStroke()) _changed();
  }

  void undo() {
    if (session!.undo()) _changed();
  }

  /// Called only after an explicit reset confirmation, including damaged saves.
  void reset() {
    session ??= PaintingSession(level);
    session!.reset();
    status = PaintingStatus.ready;
    _changed();
  }

  void _changed() {
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
