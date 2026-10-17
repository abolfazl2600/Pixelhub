import 'dart:async';
import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:persistence/persistence.dart';

import '../gallery/library_controller.dart';

const badgeContentRoot =
    'https://abolfazl2600.github.io/Pixelhub/online/badges/';

/// A mission definition is delivered separately from the installed game.
/// Stable IDs let awards survive new releases and temporary disconnections.
@immutable
class BadgeDefinition {
  const BadgeDefinition({
    required this.id,
    required this.titleFa,
    required this.titleEn,
    required this.descriptionFa,
    required this.descriptionEn,
    required this.category,
    required this.requiredCount,
    required this.image,
    required this.bytes,
    required this.sha256,
  });

  final String id;
  final String titleFa;
  final String titleEn;
  final String descriptionFa;
  final String descriptionEn;
  final String category;
  final int requiredCount;
  final String image;
  final int bytes;
  final String sha256;

  String titleFor(bool persian) => persian ? titleFa : titleEn;
  String descriptionFor(bool persian) =>
      persian ? descriptionFa : descriptionEn;

  factory BadgeDefinition.fromJson(Map<String, dynamic> raw) {
    final id = raw['id'];
    final image = raw['image'];
    final category = raw['category'];
    final needed = raw['required'];
    final size = raw['bytes'];
    final hash = raw['sha256'];
    final fa = raw['titleFa'];
    final en = raw['titleEn'];
    final descriptionFa = raw['descriptionFa'];
    final descriptionEn = raw['descriptionEn'];
    const categories = {
      'animals',
      'nature',
      'objects',
      'masterpieces',
      'persian_architecture',
      'patterns',
      'space',
    };
    if (id is! String ||
        !RegExp(r'^[a-z][a-z0-9_]{2,49}$').hasMatch(id) ||
        image != 'images/$id.png' ||
        !categories.contains(category) ||
        needed is! int ||
        needed < 1 ||
        needed > 1000 ||
        size is! int ||
        size < 50 ||
        size > 32768 ||
        hash is! String ||
        !RegExp(r'^[a-f0-9]{64}$').hasMatch(hash) ||
        fa is! String ||
        en is! String ||
        descriptionFa is! String ||
        descriptionEn is! String ||
        fa.isEmpty ||
        en.isEmpty ||
        fa.length > 100 ||
        en.length > 100 ||
        descriptionFa.length > 200 ||
        descriptionEn.length > 200) {
      throw const FormatException('Invalid achievement definition');
    }
    return BadgeDefinition(
      id: id,
      titleFa: fa,
      titleEn: en,
      descriptionFa: descriptionFa,
      descriptionEn: descriptionEn,
      category: category as String,
      requiredCount: needed,
      image: image as String,
      bytes: size,
      sha256: hash,
    );
  }
}

List<BadgeDefinition> parseBadgeCatalog(String source) {
  final decoded = jsonDecode(source);
  if (decoded is! Map<String, dynamic> ||
      decoded['version'] != 1 ||
      decoded['badges'] is! List) {
    throw const FormatException('Invalid achievement catalog');
  }
  final badges = decoded['badges'] as List<dynamic>;
  if (badges.isEmpty || badges.length > 64) {
    throw const FormatException('Invalid achievement catalog size');
  }
  final result = badges
      .map(
        (value) =>
            BadgeDefinition.fromJson(Map<String, dynamic>.from(value as Map)),
      )
      .toList(growable: false);
  if (result.map((badge) => badge.id).toSet().length != result.length) {
    throw const FormatException('Duplicate achievement ID');
  }
  return result;
}

/// Completion criteria run locally; metadata and badge images are fetched
/// remotely. Awarded IDs and verified images are durable on the device.
class BadgeController extends ChangeNotifier {
  BadgeController(
    this.library,
    this.storage, {
    Uri? baseUrl,
    http.Client? client,
  }) : _baseUrl = baseUrl ?? Uri.parse(badgeContentRoot),
       _client = client ?? http.Client(),
       _ownsClient = client == null {
    library.addListener(_onLibraryChanged);
  }

  final LibraryController library;
  final BadgeStorage storage;
  final Uri _baseUrl;
  final http.Client _client;
  final bool _ownsClient;
  List<BadgeDefinition> badges = [];
  final Set<String> _earned = {};
  final Map<String, Uint8List> _images = {};
  final Set<String> _loadingImages = {};
  final Set<String> recentlyEarned = {};
  Future<void> _awardQueue = Future<void>.value();
  bool _initialized = false;
  bool refreshing = false;
  bool loadFailed = false;
  Object? lastLoadError;
  bool _disposed = false;
  int _generation = 0;

  bool get hasCatalog => badges.isNotEmpty;
  bool isEarned(BadgeDefinition badge) => _earned.contains(badge.id);
  Uint8List? imageFor(BadgeDefinition badge) => _images[badge.id];
  int get earnedCount =>
      badges.where((badge) => _earned.contains(badge.id)).length;

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  bool _validImage(BadgeDefinition badge, Uint8List bytes) {
    if (bytes.length != badge.bytes || bytes.length < 8) return false;
    const png = [137, 80, 78, 71, 13, 10, 26, 10];
    for (var i = 0; i < png.length; i++) {
      if (bytes[i] != png[i]) return false;
    }
    return sha256.convert(bytes).toString() == badge.sha256;
  }

  void _onLibraryChanged() {
    if (!_initialized || _disposed) return;
    _awardQueue = _awardQueue
        .then((_) => _evaluateAwards())
        .catchError((Object _) {});
  }

  /// Starts with the cached catalog, then updates it in the background.
  /// A fresh install can earn an award as soon as its first catalog arrives.
  Future<void> initialize() async {
    if (_initialized || _disposed) return;
    try {
      _earned.addAll(await storage.readEarnedBadges());
    } on Object {
      // Damaged optional state must not prevent normal coloring.
    }
    try {
      final saved = await storage.readBadgeCatalog();
      if (saved != null) badges = parseBadgeCatalog(saved);
    } on Object {
      // Next successful online refresh replaces damaged metadata.
    }
    if (_disposed) return;
    _initialized = true;
    _notify();
    _onLibraryChanged();
    for (final badge in badges.where(isEarned)) {
      unawaited(_loadIcon(badge));
    }
    unawaited(refresh());
  }

  Future<void> refresh() async {
    if (refreshing || _disposed) return;
    refreshing = true;
    loadFailed = false;
    lastLoadError = null;
    final generation = _generation;
    _notify();
    try {
      final response = await _client
          .get(_baseUrl.resolve('catalog.json'))
          .timeout(const Duration(seconds: 8));
      if (response.statusCode != 200 || response.bodyBytes.length > 32768) {
        throw const FormatException('Achievement catalog unavailable');
      }
      final source = utf8.decode(response.bodyBytes);
      final parsed = parseBadgeCatalog(source);
      if (_disposed || generation != _generation) return;
      await storage.writeBadgeCatalog(source);
      if (_disposed || generation != _generation) return;
      badges = parsed;
      _notify();
      _onLibraryChanged();
      for (final badge in badges.where(isEarned)) {
        unawaited(_loadIcon(badge));
      }
    } on Object catch (error) {
      if (!_disposed && generation == _generation) {
        loadFailed = true;
        lastLoadError = error;
      }
    } finally {
      if (!_disposed && generation == _generation) {
        refreshing = false;
        _notify();
      }
    }
  }

  int progressFor(BadgeDefinition badge) {
    final completed = <String>{};
    for (final level in library.levels) {
      if (library.category(level) == badge.category &&
          library.isComplete(level)) {
        completed.add(level.id);
      }
    }
    return completed.length;
  }

  Future<void> _evaluateAwards() async {
    if (_disposed || badges.isEmpty) return;
    final fresh = <String>{};
    for (final badge in badges) {
      if (!_earned.contains(badge.id) &&
          progressFor(badge) >= badge.requiredCount) {
        fresh.add(badge.id);
      }
    }
    if (fresh.isEmpty) return;
    final next = {..._earned, ...fresh};
    final generation = _generation;
    // Write before displaying the award: interrupted saves never show
    // a badge that cannot be restored after restart.
    await storage.writeEarnedBadges(next);
    if (_disposed || generation != _generation) return;
    _earned.addAll(fresh);
    recentlyEarned.addAll(fresh);
    _notify();
    for (final badge in badges.where((item) => fresh.contains(item.id))) {
      unawaited(_loadIcon(badge));
    }
  }

  Future<void> _loadIcon(BadgeDefinition badge) async {
    if (_disposed ||
        !_earned.contains(badge.id) ||
        _images.containsKey(badge.id) ||
        !_loadingImages.add(badge.id)) {
      return;
    }
    final generation = _generation;
    try {
      final saved = await storage.readBadgeImage(badge.id);
      if (saved != null && _validImage(badge, saved)) {
        if (_disposed || generation != _generation) return;
        _images[badge.id] = saved;
        _notify();
        return;
      }
      final response = await _client
          .get(_baseUrl.resolve(badge.image))
          .timeout(const Duration(seconds: 8));
      final bytes = response.bodyBytes;
      if (response.statusCode != 200 || !_validImage(badge, bytes)) {
        throw const FormatException('Invalid achievement image');
      }
      if (_disposed || generation != _generation) return;
      await storage.writeBadgeImage(badge.id, bytes);
      if (_disposed || generation != _generation) return;
      _images[badge.id] = bytes;
      _notify();
    } on Object {
      // Award remains earned; retry its optional artwork next refresh.
    } finally {
      _loadingImages.remove(badge.id);
    }
  }

  /// Complete pending award writes before clearing the application's data.
  Future<void> settle() => _awardQueue;

  void resetAfterClear() {
    ++_generation;
    _earned.clear();
    _images.clear();
    recentlyEarned.clear();
    _initialized = true;
    _notify();
  }

  @override
  void dispose() {
    _disposed = true;
    ++_generation;
    library.removeListener(_onLibraryChanged);
    if (_ownsClient) _client.close();
    super.dispose();
  }
}
