import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

enum LibraryStatus { loading, ready, error }

class LibraryController extends ChangeNotifier {
  LibraryController(this.repository, this.progressRepository);
  final ArtworkRepository repository;
  final ProgressRepository progressRepository;
  ArtworkLibrary library = ArtworkLibrary();
  LibraryStatus status = LibraryStatus.loading;
  List<LevelDefinition> catalog = [];
  List<LevelDefinition> onlineLevels = [];
  Map<String, CatalogMetadata> metadata = {};
  final Map<String, ProgressSnapshot> progress = {};
  final Set<String> damagedProgress = {};
  final Map<String, int> _revisions = {};
  Future<void> _operations = Future.value();
  bool busy = false;
  bool storageError = false;
  bool _disposed = false;
  int _generation = 0;

  List<LevelDefinition> get levels => [
    ...catalog,
    ...onlineLevels,
    ...library.artworks.reversed.map((art) => art.level),
  ];

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  void setCatalog(
    List<LevelDefinition> levels,
    Map<String, CatalogMetadata> details,
  ) {
    catalog = levels;
    metadata = details;
    _notify();
    unawaited(_readProgress());
  }

  void setDownloadedOnline(List<LevelDefinition> levels) {
    if (onlineLevels.length == levels.length &&
        onlineLevels.every((current) => levels.any(
          (incoming) => incoming.id == current.id &&
              incoming.contentVersion == current.contentVersion &&
              incoming.checksum == current.checksum,
        ))) return;
    onlineLevels = levels.where(
      (level) => !catalog.any((original) => original.id == level.id),
    ).toList(growable: false);
    _notify();
    unawaited(_readProgress());
  }

  Future<void> load() async {
    final generation = ++_generation;
    status = LibraryStatus.loading;
    storageError = false;
    _notify();
    try {
      final result = await repository.readLibrary();
      if (_disposed || generation != _generation) {
        return;
      }
      library = result;
      status = LibraryStatus.ready;
      unawaited(_readProgress());
    } on Object {
      if (_disposed || generation != _generation) {
        return;
      }
      status = LibraryStatus.error;
    }
    _notify();
  }

  Future<void> _readProgress() async {
    final generation = _generation;
    for (final level in levels) {
      if (_disposed || generation != _generation) {
        return;
      }
      final revision = _revisions[level.id] ?? 0;
      try {
        final saved = await progressRepository.read(level);
        if (_disposed || generation != _generation) {
          return;
        }
        if (revision == (_revisions[level.id] ?? 0)) {
          damagedProgress.remove(level.id);
          if (saved == null) {
            progress.remove(level.id);
          } else {
            progress[level.id] = saved;
          }
        }
      } on Object {
        if (!_disposed &&
            generation == _generation &&
            revision == (_revisions[level.id] ?? 0)) {
          damagedProgress.add(level.id);
        }
      }
    }
    _notify();
  }

  void updateProgress(ProgressSnapshot snapshot) {
    final old = progress[snapshot.levelId];
    if (old?.revision == snapshot.revision &&
        old?.generation == snapshot.generation &&
        old?.levelChecksum == snapshot.levelChecksum) {
      return;
    }
    _revisions[snapshot.levelId] = (_revisions[snapshot.levelId] ?? 0) + 1;
    progress[snapshot.levelId] = snapshot;
    damagedProgress.remove(snapshot.levelId);
    _notify();
  }

  String category(LevelDefinition level) => level.id.startsWith('private-')
      ? 'personal'
      : metadata[level.id]?.category ?? 'patterns';
  bool isFavorite(LevelDefinition level) =>
      library.favorites.contains(level.id);
  int completed(LevelDefinition level) =>
      progress[level.id]?.completedCount ?? 0;
  bool isComplete(LevelDefinition level) =>
      completed(level) == level.cells.length;

  Future<void> _mutate(
    Future<void> Function() action, {
    bool requireReady = true,
  }) {
    final result = _operations.then((_) async {
      if (requireReady && status != LibraryStatus.ready) {
        throw StateError('Library unavailable.');
      }
      busy = true;
      storageError = false;
      _notify();
      try {
        await action();
      } on Object {
        storageError = true;
        rethrow;
      } finally {
        busy = false;
        _notify();
      }
    });
    _operations = result.catchError((Object _) {});
    return result;
  }

  Future<void> toggleFavorite(LevelDefinition level) => _mutate(() async {
    final favorites = {...library.favorites};
    if (!favorites.remove(level.id)) {
      favorites.add(level.id);
    }
    final next = ArtworkLibrary(
      artworks: library.artworks,
      favorites: favorites,
    );
    await repository.writeLibrary(next);
    library = next;
  });

  Future<void> add(PrivateArtwork artwork) => _mutate(() async {
    final next = ArtworkLibrary(
      artworks: [...library.artworks, artwork],
      favorites: library.favorites,
    );
    await repository.writeLibrary(next);
    library = next;
  });

  Future<void> delete(LevelDefinition level) => _mutate(() async {
    if (!level.id.startsWith('private-')) {
      throw StateError('Only private artwork can be deleted.');
    }
    final next = ArtworkLibrary(
      artworks: library.artworks.where((art) => art.level.id != level.id),
      favorites: library.favorites.where((id) => id != level.id),
    );
    await repository.writeLibrary(next);
    library = next;
    progress.remove(level.id);
    _revisions[level.id] = (_revisions[level.id] ?? 0) + 1;
    await repository.removeProgress(level);
  });

  Future<void> clear() => _mutate(() async {
    ++_generation;
    await repository.clearPixelhubData();
    library = ArtworkLibrary();
    onlineLevels = [];
    progress.clear();
    damagedProgress.clear();
    _revisions.clear();
    status = LibraryStatus.ready;
  }, requireReady: false);

  @override
  void dispose() {
    _disposed = true;
    ++_generation;
    super.dispose();
  }
}
