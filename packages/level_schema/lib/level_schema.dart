/// Stable asset identifiers. Asset paths belong to the application bundle.
abstract final class LevelAssets {
  static const sunflower = 'assets/levels/sunflower.json';
  static const currentSchemaVersion = 1;
}

/// A local preview fixture; painting sessions and migrations begin in V2.
final class LevelDefinition {
  LevelDefinition({
    required this.id,
    required this.title,
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
        id.isEmpty ||
        title.isEmpty ||
        width < 1 ||
        height < 1 ||
        width > 256 ||
        height > 256 ||
        palette.isEmpty ||
        palette.any((color) => color < 0 || color > 0xffffffff) ||
        cells.length != width * height ||
        cells.any((index) => index < 0 || index >= palette.length)) {
      throw const FormatException('Unsupported or invalid level fixture.');
    }
  }

  factory LevelDefinition.fromJson(Map<String, Object?> json) {
    try {
      return LevelDefinition(
        id: json['id']! as String,
        title: json['title']! as String,
        schemaVersion: json['schemaVersion']! as int,
        contentVersion: json['contentVersion']! as int,
        width: json['width']! as int,
        height: json['height']! as int,
        palette: (json['palette']! as List<Object?>)
            .map((color) => int.parse(color! as String, radix: 16))
            .toList(),
        cells: (json['cells']! as List<Object?>).cast<int>(),
      );
    } on TypeError {
      throw const FormatException('Malformed level fixture.');
    } on FormatException {
      rethrow;
    }
  }

  final String id;
  final String title;
  final int schemaVersion;
  final int contentVersion;
  final int width;
  final int height;
  final List<int> palette;
  final List<int> cells;
}
