import 'dart:async';
import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

import 'artwork_categories.dart';

/// Public, versioned files served by the same repository's GitHub Pages site.
/// The base URL is replaceable without changing level IDs or saved progress.
const onlineContentRoot = 'https://abolfazl2600.github.io/Pixelhub/online/';

enum OnlineCatalogStatus { idle, checking, ready, error }

/// Optional immutable companion downloaded together with a picture.
final class OnlineAnimationInfo {
  const OnlineAnimationInfo(this.bytes, this.sha256, this.frameCount);

  factory OnlineAnimationInfo.fromJson(Object? raw) {
    if (raw is! Map) {
      throw const FormatException('Invalid online animation metadata.');
    }
    final Object? bytes = raw['bytes'];
    final Object? checksum = raw['sha256'];
    final Object? frameCount = raw['frameCount'];
    if (bytes is! int ||
        bytes < 1 ||
        bytes > 2 * 1024 * 1024 ||
        checksum is! String ||
        !RegExp(r'^[a-f0-9]{64}$').hasMatch(checksum) ||
        frameCount is! int ||
        frameCount < 1 ||
        frameCount > 60) {
      throw const FormatException('Invalid online animation metadata.');
    }
    return OnlineAnimationInfo(bytes, checksum, frameCount);
  }

  final int bytes;
  final String sha256;
  final int frameCount;
}

final class OnlinePicture {
  OnlinePicture._({
    required this.id,
    required this.version,
    required this.title,
    required this.titleEn,
    required this.category,
    required this.width,
    required this.height,
    required this.bytes,
    required this.checksum,
    required this.animation,
  });

  factory OnlinePicture.fromJson(Map<String, Object?> value) {
    final id = value['id'];
    final version = value['version'];
    final title = value['title'];
    final titleEn = value['titleEn'];
    final category = value['category'];
    final width = value['width'];
    final height = value['height'];
    final bytes = value['bytes'];
    final checksum = value['checksum'];
    if (id is! String ||
        !RegExp(r'^online-[a-z0-9-]{1,64}$').hasMatch(id) ||
        version is! int ||
        version < 1 ||
        version > 100000 ||
        title is! String ||
        title.isEmpty ||
        title.length > 100 ||
        titleEn is! String ||
        titleEn.isEmpty ||
        titleEn.length > 100 ||
        category is! String ||
        !onlinePictureCategories.contains(category) ||
        width is! int ||
        width < 1 ||
        width > 256 ||
        height is! int ||
        height < 1 ||
        height > 256 ||
        bytes is! int ||
        bytes < 1 ||
        bytes > 262144 ||
        checksum is! String ||
        !RegExp(r'^[a-f0-9]{64}$').hasMatch(checksum)) {
      throw const FormatException('Invalid online picture entry.');
    }
    return OnlinePicture._(
      id: id,
      version: version,
      title: title,
      titleEn: titleEn,
      category: displayArtworkCategory(id, category),
      width: width,
      height: height,
      bytes: bytes,
      checksum: checksum,
      animation: value['animation'] == null
          ? null
          : OnlineAnimationInfo.fromJson(value['animation']),
    );
  }

  final String id;
  final int version;
  final String title;
  final String titleEn;
  final String category;
  final int width;
  final int height;
  final int bytes;
  final String checksum;
  final OnlineAnimationInfo? animation;

  String get stem => '$id-v$version';
  String titleFor(String language) => language == 'en' ? titleEn : title;
}

class OnlineCatalogController extends ChangeNotifier {
  OnlineCatalogController(this.storage, {Uri? baseUrl, http.Client? client})
    : _baseUrl = baseUrl ?? Uri.parse(onlineContentRoot),
      _client = client ?? http.Client(),
      _ownsClient = client == null;

  final OnlineLevelStorage storage;
  final Uri _baseUrl;
  final http.Client _client;
  final bool _ownsClient;
  final Map<String, LevelDefinition> _downloaded = {};
  final Map<String, String> _downloadedCategories = {};
  final Map<String, PixelAnimation> _animations = {};
  final Set<String> _pendingAnimations = {};
  bool _backfillingAnimations = false;
  List<OnlinePicture> pictures = [];
  OnlineCatalogStatus status = OnlineCatalogStatus.idle;
  bool isLoaded = false;
  String? downloadingId;
  String? failedDownloadId;
  bool _disposed = false;

  List<LevelDefinition> get downloaded => List.unmodifiable(_downloaded.values);
  Map<String, PixelAnimation> get animations => Map.unmodifiable(_animations);

  /// Online catalog metadata supplements local categories. A downloaded level
  /// must retain its saved category when connectivity is unavailable.
  Map<String, String> get categories => Map.unmodifiable({
    for (final picture in pictures) picture.id: picture.category,
    ..._downloadedCategories,
  });

  List<OnlinePicture> get available => pictures
      .where((picture) => !_downloaded.containsKey(picture.id))
      .toList(growable: false);

  Uri previewUrl(OnlinePicture picture) =>
      _baseUrl.resolve('previews/${picture.stem}.png');

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  /// Use package:http instead of Flutter's NetworkAssetBundle: on Web the
  /// latter constructs dart:io HttpClient, which is unsupported in browsers.
  /// http.get picks BrowserClient on Web and IOClient on Android.
  Future<String> _loadRemote(
    String path, {
    required Duration timeout,
    required int maxBytes,
  }) async {
    final uri = _baseUrl.resolve(path);
    final response = await _client.get(uri).timeout(timeout);
    if (response.statusCode != 200) {
      throw FormatException('Online content HTTP ${response.statusCode}.');
    }
    if (response.bodyBytes.length > maxBytes) {
      throw const FormatException('Online content is too large.');
    }
    return utf8.decode(response.bodyBytes, allowMalformed: false);
  }

  Future<PixelAnimation> _fetchAnimation(
    OnlinePicture picture,
    LevelDefinition level,
  ) async {
    final info = picture.animation!;
    if (storage is! OnlineAnimationStorage) {
      throw StateError('Animation storage is unavailable.');
    }
    final source = await _loadRemote(
      'animations/${picture.stem}.json',
      timeout: const Duration(seconds: 25),
      maxBytes: 2 * 1024 * 1024,
    );
    final payload = utf8.encode(source);
    if (payload.length != info.bytes ||
        sha256.convert(payload).toString() != info.sha256) {
      throw const FormatException('Animation integrity check failed.');
    }
    final decoded = jsonDecode(source);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('Invalid animation file.');
    }
    final animation = PixelAnimation.fromJson(decoded, level);
    if (animation.frameCount != info.frameCount) {
      throw const FormatException('Animation frame count mismatch.');
    }
    return animation;
  }

  Future<void> _backfillAnimations(List<OnlinePicture> catalog) async {
    if (storage is! OnlineAnimationStorage || _backfillingAnimations) return;
    _backfillingAnimations = true;
    final pending = catalog.where((picture) {
      final level = _downloaded[picture.id];
      return picture.animation != null &&
          !_animations.containsKey(picture.id) &&
          !_pendingAnimations.contains(picture.id) &&
          level != null &&
          level.contentVersion == picture.version &&
          level.checksum == picture.checksum;
    }).toList();
    Future<void> worker() async {
      while (!_disposed && pending.isNotEmpty) {
        final picture = pending.removeLast();
        final level = _downloaded[picture.id];
        if (level == null || !_pendingAnimations.add(picture.id)) continue;
        try {
          final animation = await _fetchAnimation(picture, level);
          if (_disposed || _downloaded[level.id] != level) continue;
          final animationStorage = storage as OnlineAnimationStorage;
          await animationStorage.saveDownloadedAnimation(level, animation);
          if (_downloaded[level.id] != level) {
            await animationStorage.removeDownloadedAnimation(level.id);
            continue;
          }
          if (_disposed) return;
          _animations[level.id] = animation;
          _notify();
        } on Object {
          // Keep existing paintings playable and retry on the next refresh.
        } finally {
          _pendingAnimations.remove(picture.id);
        }
      }
    }

    await Future.wait([for (var i = 0; i < 3; i++) worker()]);
    _backfillingAnimations = false;
  }

  Future<void> loadDownloaded() async {
    try {
      for (final level in await storage.readDownloadedLevels()) {
        if (level.id.startsWith('online-')) _downloaded[level.id] = level;
      }
      try {
        final saved = await storage.readDownloadedCategories();
        _downloadedCategories.clear();
        for (final id in _downloaded.keys) {
          final previous = saved[id];
          final historicCategory = historicOnlineArtworkCategory(id);
          // The known artworks work offline immediately even when old
          // installations still have 'patterns' category metadata.
          final category = historicCategory ?? previous;
          if (category == null) continue;
          _downloadedCategories[id] = category;
          if (historicCategory != null && category != previous) {
            try {
              await storage.saveDownloadedCategory(id, category);
            } on Object {
              // Retry persisting on the next launch; keep the UI correct.
            }
          }
        }
      } on Object {
        // Old or corrupt metadata must not hide downloaded paintings.
        for (final id in _downloaded.keys) {
          final category = historicOnlineArtworkCategory(id);
          if (category != null) _downloadedCategories[id] = category;
        }
      }
      if (storage is OnlineAnimationStorage) {
        try {
          _animations.clear();
          _animations.addAll(
            await (storage as OnlineAnimationStorage).readDownloadedAnimations(
              downloaded,
            ),
          );
        } on Object {
          // Invalid optional frames never hide a painting.
        }
      }
    } on Object {
      // Keep built-in pictures playable if optional downloaded storage fails.
    } finally {
      isLoaded = true;
      _notify();
    }
  }

  /// Gallery entry fetches metadata, then missing frames for existing downloads.
  Future<void> checkForUpdates() async {
    if (status == OnlineCatalogStatus.checking) return;
    status = OnlineCatalogStatus.checking;
    _notify();
    try {
      final cacheBuster = DateTime.now().millisecondsSinceEpoch;
      final source = await _loadRemote(
        'catalog.json?v=$cacheBuster',
        timeout: const Duration(seconds: 12),
        maxBytes: 4 * 1024 * 1024,
      );
      final json = jsonDecode(source);
      if (json is! Map<String, dynamic> ||
          json['schemaVersion'] != 1 ||
          json['pictures'] is! List) {
        throw const FormatException('Invalid online catalog.');
      }
      final raw = json['pictures'] as List;
      if (raw.length > 10000) {
        throw const FormatException('Catalog exceeds supported capacity.');
      }
      final result = <OnlinePicture>[];
      final ids = <String>{};
      for (final value in raw) {
        if (value is! Map<String, dynamic>) {
          throw const FormatException('Invalid picture.');
        }
        final entry = OnlinePicture.fromJson(value);
        if (!ids.add(entry.id)) {
          throw const FormatException('Duplicate picture.');
        }
        result.add(entry);
      }
      // Purge retired online downloads only after complete catalog validation.
      // Current native binaries ignore the optional hint until an app update.
      final retirement = json['retiredIds'];
      if (retirement != null && retirement is! List) {
        throw const FormatException('Invalid retired online IDs.');
      }
      final retired = <String>{};
      for (final id in (retirement as List? ?? const [])) {
        if (id is! String ||
            !RegExp(r'^online-[a-z0-9-]{1,64}$').hasMatch(id) ||
            ids.contains(id) ||
            !retired.add(id)) {
          throw const FormatException('Invalid retired online picture ID.');
        }
      }
      if (_disposed) return;
      for (final id in retired) {
        if (_disposed) return;
        if (_downloaded.containsKey(id)) {
          try {
            await removeDownloaded(id);
          } on Object {
            // Retry on the next valid catalog fetch.
          }
        }
      }
      if (_disposed) return;
      pictures = List.unmodifiable(result);
      status = OnlineCatalogStatus.ready;
      unawaited(_backfillAnimations(result));
      // Upgrade legacy downloads only when an authoritative catalog is
      // available. Failure to write metadata must not hide online pictures.
      for (final picture in result) {
        if (_disposed) return;
        if (_downloaded.containsKey(picture.id) &&
            _downloadedCategories[picture.id] != picture.category) {
          try {
            await storage.saveDownloadedCategory(picture.id, picture.category);
            _downloadedCategories[picture.id] = picture.category;
          } on Object {
            // Retry a missing category the next time the gallery refreshes.
          }
        }
      }
    } on Object {
      if (_disposed) return;
      status = OnlineCatalogStatus.error;
    }
    _notify();
  }

  Future<void> download(OnlinePicture picture) async {
    if (downloadingId != null || _downloaded.containsKey(picture.id)) return;
    downloadingId = picture.id;
    failedDownloadId = null;
    _notify();
    try {
      final source = await _loadRemote(
        'levels/${picture.stem}.json',
        timeout: const Duration(seconds: 25),
        maxBytes: 262144,
      );
      if (utf8.encode(source).length != picture.bytes) {
        throw const FormatException('Download length mismatch.');
      }
      final decoded = jsonDecode(source);
      if (decoded is! Map<String, dynamic>) {
        throw const FormatException('Invalid downloaded level.');
      }
      final level = LevelDefinition.fromJson(decoded);
      if (level.id != picture.id ||
          level.contentVersion != picture.version ||
          level.checksum != picture.checksum ||
          level.width != picture.width ||
          level.height != picture.height) {
        throw const FormatException('Downloaded level does not match catalog.');
      }
      PixelAnimation? animation;
      if (picture.animation != null) {
        animation = await _fetchAnimation(picture, level);
        await (storage as OnlineAnimationStorage).saveDownloadedAnimation(
          level,
          animation,
        );
      }
      try {
        await storage.saveDownloadedLevel(level, category: picture.category);
      } on Object {
        if (animation != null) {
          try {
            await (storage as OnlineAnimationStorage).removeDownloadedAnimation(
              level.id,
            );
          } on Object {
            // Orphan sidecars are ignored until the level is available.
          }
        }
        rethrow;
      }
      if (_disposed) return;
      if (animation != null) _animations[level.id] = animation;
      _downloaded[level.id] = level;
      _downloadedCategories[level.id] = picture.category;
    } on Object catch (error) {
      debugPrint('Online picture download failed: $error');
      if (!_disposed) failedDownloadId = picture.id;
    } finally {
      downloadingId = null;
      _notify();
    }
  }

  Future<void> removeDownloaded(String id) async {
    if (!_downloaded.containsKey(id)) return;
    await storage.removeDownloadedLevel(id);
    _downloaded.remove(id);
    _downloadedCategories.remove(id);
    _animations.remove(id);
    _notify();
  }

  void clearDownloaded() {
    _downloaded.clear();
    _downloadedCategories.clear();
    _animations.clear();
    pictures = [];
    status = OnlineCatalogStatus.idle;
    _notify();
  }

  @override
  void dispose() {
    _disposed = true;
    if (_ownsClient) _client.close();
    super.dispose();
  }
}
