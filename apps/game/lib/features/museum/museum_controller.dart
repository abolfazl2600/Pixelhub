import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';

import '../gallery/library_controller.dart';

/// Durable, serialized local museum edits. Keeps art/progress untouched.
class MuseumController extends ChangeNotifier {
  MuseumController(this.repository, this.library);

  final MuseumRepository repository;
  final LibraryController library;
  MuseumLayout layout = MuseumLayout();
  bool ready = false;
  bool busy = false;
  bool failedToLoad = false;
  Future<void> _operations = Future<void>.value();
  bool _disposed = false;
  int _generation = 0;

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> load() async {
    final generation = ++_generation;
    failedToLoad = false;
    ready = false;
    _notify();
    try {
      final stored = await repository.readMuseum();
      if (_disposed || generation != _generation) return;
      layout = stored;
      ready = true;
    } on Object {
      if (_disposed || generation != _generation) return;
      failedToLoad = true;
    }
    _notify();
  }

  List<String?> get visibleSlots {
    final completedIds = library.levels
        .where(library.isComplete)
        .map((level) => level.id)
        .toSet();
    return [
      for (final id in layout.slots)
        if (id != null && completedIds.contains(id)) id else null,
    ];
  }

  Future<void> _edit(MuseumLayout Function(MuseumLayout) transform) {
    final result = _operations.then((_) async {
      if (_disposed || !ready) throw StateError('Museum unavailable');
      final next = transform(layout);
      busy = true;
      _notify();
      try {
        await repository.writeMuseum(next);
        if (!_disposed) layout = next;
      } finally {
        busy = false;
        _notify();
      }
    });
    _operations = result.then<void>((_) {}, onError: (Object _) {});
    return result;
  }

  Future<void> place(int index, String artworkId) => _edit((current) {
    final matches = library.levels.where(
      (level) => level.id == artworkId && library.isComplete(level),
    );
    if (matches.isEmpty) {
      throw StateError('Only completed, available art belongs in the museum');
    }
    return current.place(index, artworkId);
  });

  Future<void> remove(int index) =>
      _edit((current) => current.place(index, null));

  Future<void> swap(int first, int second) =>
      _edit((current) => current.swap(first, second));

  /// Theme presets update the room and frame but never change artwork slots
  /// or their saved positions. Individual wall/frame controls remain usable.
  Future<void> setTheme(String theme) => _edit((current) {
    final wall = switch (theme) {
      'royal' => 'emerald',
      'sky' => 'blue',
      'botanical' => 'sage',
      _ => 'cream',
    };
    final frame = switch (theme) {
      'classic' || 'royal' || 'sky' => 'gold',
      _ => 'wood',
    };
    return current.copyWith(theme: theme, wall: wall, frame: frame);
  });

  Future<void> setWall(String wall) =>
      _edit((current) => current.copyWith(wall: wall));

  Future<void> setFrame(String frame) =>
      _edit((current) => current.copyWith(frame: frame));

  Future<void> setArrangement(String arrangement) =>
      _edit((current) => current.copyWith(arrangement: arrangement));

  /// Wait before clearing the complete PixelHub local-storage namespace.
  Future<void> settle() => _operations;

  /// Called after the shared preferences namespace has been cleared.
  void resetAfterClear() {
    _generation++;
    layout = MuseumLayout();
    failedToLoad = false;
    ready = true;
    busy = false;
    _notify();
  }

  @override
  void dispose() {
    _disposed = true;
    _generation++;
    super.dispose();
  }
}
