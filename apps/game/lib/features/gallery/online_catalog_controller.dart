import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

/// Public, versioned files served by the same repository's GitHub Pages site.
/// The base URL is replaceable without changing level IDs or saved progress.
const onlineContentRoot = 'https://abolfazl2600.github.io/Pixelhub/online/';

enum OnlineCatalogStatus { idle, checking, ready, error }

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
        version is! int || version < 1 || version > 100000 ||
        title is! String || title.isEmpty || title.length > 100 ||
        titleEn is! String || titleEn.isEmpty || titleEn.length > 100 ||
        category is! String ||
        !{'nature', 'animals', 'objects', 'patterns', 'space'}.contains(category) ||
        width is! int || width < 1 || width > 256 ||
        height is! int || height < 1 || height > 256 ||
        bytes is! int || bytes < 1 || bytes > 262144 ||
        checksum is! String || !RegExp(r'^[a-f0-9]{64}$').hasMatch(checksum)) {
      throw const FormatException('Invalid online picture entry.');
    }
    return OnlinePicture._(
      id: id, version: version, title: title, titleEn: titleEn,
      category: category, width: width, height: height,
      bytes: bytes, checksum: checksum,
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

  String get stem => '$id-v$version';
  String titleFor(String language) => language == 'en' ? titleEn : title;
}

class OnlineCatalogController extends ChangeNotifier {
  OnlineCatalogController(this.storage, {Uri? baseUrl})
      : _baseUrl = baseUrl ?? Uri.parse(onlineContentRoot);

  final OnlineLevelStorage storage;
  final Uri _baseUrl;
  final Map<String, LevelDefinition> _downloaded = {};
  List<OnlinePicture> pictures = [];
  OnlineCatalogStatus status = OnlineCatalogStatus.idle;
  bool isLoaded = false;
  String? downloadingId;
  String? failedDownloadId;
  bool _disposed = false;

  List<LevelDefinition> get downloaded => List.unmodifiable(_downloaded.values);
  List<OnlinePicture> get available => pictures.where(
    (picture) => !_downloaded.containsKey(picture.id),
  ).toList(growable: false);

  Uri previewUrl(OnlinePicture picture) =>
      _baseUrl.resolve('previews/${picture.stem}.png');

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> loadDownloaded() async {
    try {
      for (final level in await storage.readDownloadedLevels()) {
        if (level.id.startsWith('online-')) _downloaded[level.id] = level;
      }
    } on Object {
      // Keep built-in pictures playable if optional downloaded storage fails.
    } finally {
      isLoaded = true;
      _notify();
    }
  }

  /// Called on gallery entry, not app startup. Only metadata is fetched.
  Future<void> checkForUpdates() async {
    if (status == OnlineCatalogStatus.checking) return;
    status = OnlineCatalogStatus.checking;
    _notify();
    try {
      final cacheBuster = DateTime.now().millisecondsSinceEpoch;
      final bundle = NetworkAssetBundle(_baseUrl);
      final source = await bundle.loadString('catalog.json?v=$cacheBuster')
          .timeout(const Duration(seconds: 12));
      if (utf8.encode(source).length > 4 * 1024 * 1024) {
        throw const FormatException('Catalog too large.');
      }
      final json = jsonDecode(source);
      if (json is! Map<String, dynamic> || json['schemaVersion'] != 1 ||
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
        if (!ids.add(entry.id)) throw const FormatException('Duplicate picture.');
        result.add(entry);
      }
      if (_disposed) return;
      pictures = List.unmodifiable(result);
      status = OnlineCatalogStatus.ready;
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
      final bundle = NetworkAssetBundle(_baseUrl);
      final source = await bundle.loadString('levels/${picture.stem}.json')
          .timeout(const Duration(seconds: 25));
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
      await storage.saveDownloadedLevel(level);
      if (_disposed) return;
      _downloaded[level.id] = level;
    } on Object {
      if (!_disposed) failedDownloadId = picture.id;
    } finally {
      downloadingId = null;
      _notify();
    }
  }

  void clearDownloaded() {
    _downloaded.clear();
    pictures = [];
    status = OnlineCatalogStatus.idle;
    _notify();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
