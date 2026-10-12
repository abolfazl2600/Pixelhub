import 'dart:convert';

import 'package:crypto/crypto.dart';

abstract final class LevelAssets {
  static const sunflower = 'assets/levels/sunflower-v2.json';
  static const catalog = 'assets/levels/catalog.json';
  static const currentSchemaVersion = 2;
}

/// Immutable, versioned level. Index zero is a real color, not transparency.
final class LevelDefinition {
  LevelDefinition({
    required this.id,
    required this.title,
    required this.titleEn,
    required this.schemaVersion,
    required this.contentVersion,
    required this.width,
    required this.height,
    required List<int> palette,
    required List<int> cells,
  }) : palette = List.unmodifiable(palette),
       cells = List.unmodifiable(cells) {
    if (schemaVersion != LevelAssets.currentSchemaVersion ||
        contentVersion < 1 ||
        !RegExp(r'^[a-z0-9-]+$').hasMatch(id) ||
        title.isEmpty ||
        titleEn.isEmpty ||
        width < 1 ||
        height < 1 ||
        width > 256 ||
        height > 256 ||
        palette.isEmpty ||
        palette.length > 48 ||
        palette.any((color) => color < 0xff000000 || color > 0xffffffff) ||
        cells.length != width * height ||
        cells.any((index) => index < 0 || index >= palette.length)) {
      throw const FormatException('Unsupported or invalid level.');
    }
  }

  factory LevelDefinition.fromJson(Map<String, Object?> json) {
    try {
      final titles = json['titles']! as Map<String, Object?>;
      final level = LevelDefinition(
        id: json['levelId']! as String,
        title: titles['fa']! as String,
        titleEn: titles['en']! as String,
        schemaVersion: json['schemaVersion']! as int,
        contentVersion: json['levelVersion']! as int,
        width: json['width']! as int,
        height: json['height']! as int,
        palette: (json['palette']! as List<Object?>)
            .map((color) => int.parse(color! as String, radix: 16))
            .toList(),
        cells: (json['cells']! as List<Object?>).cast<int>(),
      );
      if (json['checksum'] != level.checksum) {
        throw const FormatException('Level checksum mismatch.');
      }
      return level;
    } on TypeError {
      throw const FormatException('Malformed level.');
    }
  }

  final String id;
  final String title;
  final String titleEn;
  final int schemaVersion;
  final int contentVersion;
  final int width;
  final int height;
  final List<int> palette;
  final List<int> cells;

  String titleFor(String language) => language == 'en' ? titleEn : title;

  /// Canonical UTF-8 JSON array, in this fixed order, excluding the checksum.
  List<Object> get canonicalPayload => [
    schemaVersion,
    id,
    contentVersion,
    title,
    titleEn,
    width,
    height,
    palette
        .map((color) => color.toRadixString(16).padLeft(8, '0').toUpperCase())
        .toList(),
    cells,
  ];

  late final String checksum = sha256
      .convert(utf8.encode(jsonEncode(canonicalPayload)))
      .toString();

  Map<String, Object> toJson() => {
    'schemaVersion': schemaVersion,
    'levelId': id,
    'levelVersion': contentVersion,
    'titles': {'fa': title, 'en': titleEn},
    'width': width,
    'height': height,
    'palette': canonicalPayload[7],
    'cells': cells,
    'checksum': checksum,
  };
}
