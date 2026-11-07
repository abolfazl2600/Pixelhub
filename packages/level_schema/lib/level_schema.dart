export 'animation.dart';

import 'dart:convert';
import 'dart:typed_data';

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
    this.preFilledBackground = false,
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
        preFilledBackground: json['preFilledBackground'] as bool? ?? false,
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

  /// Opt-in only: edge-connected, light-colored background cells start filled.
  /// This changes how a picture is played, not its immutable pixel artwork.
  /// Keeping the original checksum preserves previously saved user progress.
  final bool preFilledBackground;

  late final List<bool> preFilledMask = _findPreFilledBackground();
  late final int preFilledCount = preFilledMask.where((value) => value).length;
  int get paintableCellCount => cells.length - preFilledCount;

  bool isPreFilled(int index) =>
      preFilledMask.isNotEmpty && preFilledMask[index];

  /// Newly allocated bitset, so no caller can mutate shared level metadata.
  Uint8List get initialCompletedBits {
    final result = Uint8List((cells.length + 7) ~/ 8);
    for (var i = 0; i < cells.length; i++) {
      if (isPreFilled(i)) result[i ~/ 8] |= 1 << (i % 8);
    }
    return result;
  }

  /// Flood-fill the *exact* background palette color from all four edges.
  /// Internal white details remain paintable, unlike replacing color zero.
  /// A conservative light-color guard prevents prefilling dark scenery.
  List<bool> _findPreFilledBackground() {
    if (!preFilledBackground || cells.length < 2) return const [];
    final backgroundIndex = cells.first;
    final color = palette[backgroundIndex];
    final r = (color >> 16) & 0xff;
    final g = (color >> 8) & 0xff;
    final b = color & 0xff;
    if (r < 238 || g < 218 || b < 200) return const [];
    final mask = List<bool>.filled(cells.length, false);
    final queue = <int>[];
    void add(int index) {
      if (!mask[index] && cells[index] == backgroundIndex) {
        mask[index] = true;
        queue.add(index);
      }
    }

    for (var x = 0; x < width; x++) {
      add(x);
      add((height - 1) * width + x);
    }
    for (var y = 0; y < height; y++) {
      add(y * width);
      add(y * width + width - 1);
    }
    for (var head = 0; head < queue.length; head++) {
      final index = queue[head];
      final x = index % width;
      final y = index ~/ width;
      if (x > 0) add(index - 1);
      if (x + 1 < width) add(index + 1);
      if (y > 0) add(index - width);
      if (y + 1 < height) add(index + width);
    }
    // A blank picture must never start at 100% without user interaction.
    if (queue.length == cells.length) return const [];
    return List<bool>.unmodifiable(mask);
  }

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
    if (preFilledBackground) 'preFilledBackground': true,
    'checksum': checksum,
  };
}
