import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

import 'artwork_categories.dart';
import 'artwork_economy.dart';

enum LibraryStatus { loading, ready, error }

class LibraryController extends ChangeNotifier {
  LibraryController(
    this.repository,
    this.progressRepository, {
    this.recentArtworkRepository,
  });
  final ArtworkRepository repository;
  final ProgressRepository progressRepository;
  final RecentArtworkRepository? recentArtworkRepository;
  ArtworkLibrary library = ArtworkLibrary();
  LibraryStatus status = LibraryStatus.loading;
  List<LevelDefinition> catalog = [];
  List<LevelDefinition> onlineLevels = [];
  Map<String, String> onlineCategories = {};
  Map<String, CatalogMetadata> metadata = {};
  final Map<String, ProgressSnapshot> progress = {};
  final Set<String> damagedProgress = {};
  final Map<String, int> _revisions = {};
  Future<void> _operations = Future.value();
  Future<void> _recentWrites = Future.value();
  String? _recentArtworkId;
  int _recentRevision = 0;
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

  void setOnlineCategories(Map<String, String> categories) {
    if (mapEquals(onlineCategories, categories)) return;
    onlineCategories = Map.unmodifiable(categories);
    _notify();
  }

  void setDownloadedOnline(List<LevelDefinition> levels) {
    if (onlineLevels.length == levels.length &&
        onlineLevels.every(
          (current) => levels.any(
            (incoming) =>
                incoming.id == current.id &&
                incoming.contentVersion == current.contentVersion &&
                incoming.checksum == current.checksum,
          ),
        )) {
      return;
    }
    onlineLevels = levels
        .where((level) => !catalog.any((original) => original.id == level.id))
        .toList(growable: false);
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

  /// Read the last opened artwork without overwriting a newer navigation.
  Future<void> loadRecentArtwork() async {
    final repository = recentArtworkRepository;
    if (repository == null) return;
    final revision = _recentRevision;
    try {
      final id = await repository.readRecentArtworkId();
      if (!_disposed && revision == _recentRevision) {
        _recentArtworkId = id;
        _notify();
      }
    } on Object {
      // Damaged optional preferences must not prevent painting offline.
    }
  }

  /// Called when a painting screen is opened, not on every widget rebuild.
  Future<void> markOpened(LevelDefinition level) {
    if (_recentArtworkId == level.id) return _recentWrites;
    _recentArtworkId = level.id;
    ++_recentRevision;
    _notify();
    final repository = recentArtworkRepository;
    if (repository != null) {
      _recentWrites = _recentWrites
          .then((_) => repository.writeRecentArtworkId(level.id))
          .catchError((Object _) {
            // Progress remains usable even when optional recency cannot save.
          });
    }
    return _recentWrites;
  }

  LevelDefinition? get continueLevel {
    bool unfinished(LevelDefinition level) {
      if (damagedProgress.contains(level.id)) return false;
      final snapshot = progress[level.id];
      return snapshot != null &&
          snapshot.levelVersion == level.contentVersion &&
          snapshot.levelChecksum == level.checksum &&
          snapshot.cellCount == level.cells.length &&
          snapshot.completedCount > 0 &&
          snapshot.completedCount < level.cells.length;
    }

    final available = levels;
    for (final level in available) {
      if (level.id == _recentArtworkId && unfinished(level)) return level;
    }
    for (final level in available) {
      if (unfinished(level)) return level;
    }
    return null;
  }

  int continuePercent(LevelDefinition level) =>
      ((completed(level) * 100) ~/ level.cells.length).clamp(1, 99);

  String category(LevelDefinition level) => level.id.startsWith('private-')
      ? 'personal'
      : displayArtworkCategory(
          level.id,
          onlineCategories[level.id] ??
              metadata[level.id]?.category ??
              'patterns',
        );
  bool isFavorite(LevelDefinition level) =>
      library.favorites.contains(level.id);
  int completed(LevelDefinition level) =>
      progress[level.id]?.completedCount ?? 0;
  bool isComplete(LevelDefinition level) =>
      completed(level) == level.cells.length;

  int get coins => library.coins;
  int get totalPoints => library.totalPoints;

  bool canPaint(LevelDefinition level) =>
      alwaysFreeArtwork(level.id) ||
      library.unlocked.contains(level.id) ||
      // Preserve access to levels started before the wallet was introduced.
      (progress[level.id]?.completedCount ?? 0) > 0;

  /// A single serialized library write atomically charges coins and unlocks
  /// the level. Failed/insufficient purchases never alter the balance.
  Future<void> unlock(LevelDefinition level) => _mutate(() async {
    if (canPaint(level)) return;
    final cost = priceForLevel(level);
    if (library.coins < cost) {
      throw StateError('Insufficient coins');
    }
    final next = library.copyWith(
      coins: library.coins - cost,
      unlocked: {...library.unlocked, level.id},
    );
    await repository.writeLibrary(next);
    library = next;
  });

  /// Once per level ID, even after reset or app relaunch. A failed wallet
  /// write can be retried safely without duplicating a reward.
  Future<void> rewardCompletion(LevelDefinition level) => _mutate(() async {
    if (library.rewarded.contains(level.id)) return;
    final reward = rewardForLevel(level);
    final next = library.copyWith(
      coins: library.coins + reward,
      totalPoints: library.totalPoints + reward,
      rewarded: {...library.rewarded, level.id},
    );
    await repository.writeLibrary(next);
    library = next;
  });

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
    final next = library.copyWith(favorites: favorites);
    await repository.writeLibrary(next);
    library = next;
  });

  Future<void> add(PrivateArtwork artwork) => _mutate(() async {
    final next = library.copyWith(artworks: [...library.artworks, artwork]);
    await repository.writeLibrary(next);
    library = next;
  });

  Future<void> delete(LevelDefinition level) => _mutate(() async {
    if (!level.id.startsWith('private-')) {
      throw StateError('Only private artwork can be deleted.');
    }
    final next = library.copyWith(
      artworks: library.artworks.where((art) => art.level.id != level.id),
      favorites: library.favorites.where((id) => id != level.id),
    );
    await repository.writeLibrary(next);
    library = next;
    progress.remove(level.id);
    _revisions[level.id] = (_revisions[level.id] ?? 0) + 1;
    await repository.removeProgress(level);
  });

  Future<void> forgetDownloadedOnline(LevelDefinition level) =>
      _mutate(() async {
        if (!level.id.startsWith('online-')) {
          throw StateError('Only downloaded online levels can be forgotten.');
        }
        final next = library.copyWith(
          favorites: library.favorites.where((id) => id != level.id),
        );
        await repository.writeLibrary(next);
        library = next;
        progress.remove(level.id);
        damagedProgress.remove(level.id);
        _revisions[level.id] = (_revisions[level.id] ?? 0) + 1;
        await repository.removeProgress(level);
      });

  Future<void> clear() => _mutate(() async {
    ++_generation;
    ++_recentRevision;
    await _recentWrites;
    await repository.clearPixelhubData();
    await recentArtworkRepository?.clearRecentArtworkId();
    _recentArtworkId = null;
    library = ArtworkLibrary();
    onlineLevels = [];
    onlineCategories = {};
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
