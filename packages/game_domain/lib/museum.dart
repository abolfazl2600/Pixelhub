/// The museum stores only artwork identifiers, not images or imported photos.
/// Its schema is intentionally independent of painting/progress versions.
final class MuseumLayout {
  MuseumLayout({
    this.wall = 'cream',
    this.theme = 'classic',
    this.frame = 'wood',
    this.arrangement = 'grid',
    List<String?>? slots,
  }) : slots = List<String?>.unmodifiable(
         slots ?? List<String?>.filled(6, null),
       ) {
    if (!themes.contains(theme) ||
        !walls.contains(wall) ||
        !frames.contains(frame) ||
        !arrangements.contains(arrangement) ||
        this.slots.length != 6 ||
        this.slots.any(
          (id) => id != null && !RegExp(r'^[a-z0-9-]+$').hasMatch(id),
        ) ||
        this.slots.whereType<String>().toSet().length !=
            this.slots.whereType<String>().length) {
      throw const FormatException('Invalid museum layout.');
    }
  }

  /// Four visual rooms from the original PixelHub museum concept designs.
  static const themes = {'classic', 'royal', 'sky', 'botanical'};
  static const walls = {'cream', 'blue', 'sage', 'emerald'};
  static const frames = {'wood', 'gold', 'dark'};
  static const arrangements = {'grid', 'staggered'};

  final String wall;
  final String theme;
  final String frame;
  final String arrangement;
  final List<String?> slots;

  factory MuseumLayout.fromJson(Map<String, Object?> json) {
    try {
      if (json['schemaVersion'] != 1) {
        throw const FormatException('Unsupported museum version.');
      }
      return MuseumLayout(
        wall: json['wall']! as String,
        // Legacy schema v1 layouts predate the selectable museum themes.
        theme: (json['theme'] ?? 'classic') as String,
        frame: json['frame']! as String,
        arrangement: json['arrangement']! as String,
        slots: (json['slots']! as List<Object?>).cast<String?>(),
      );
    } on TypeError {
      throw const FormatException('Malformed museum layout.');
    }
  }

  Map<String, Object?> toJson() => {
    'schemaVersion': 1,
    'wall': wall,
    'theme': theme,
    'frame': frame,
    'arrangement': arrangement,
    'slots': slots,
  };

  MuseumLayout copyWith({
    String? wall,
    String? theme,
    String? frame,
    String? arrangement,
    List<String?>? slots,
  }) => MuseumLayout(
    wall: wall ?? this.wall,
    theme: theme ?? this.theme,
    frame: frame ?? this.frame,
    arrangement: arrangement ?? this.arrangement,
    slots: slots ?? this.slots,
  );

  /// Artwork can hang in only one slot at a time. Re-hanging it elsewhere
  /// removes it from the previous slot rather than duplicating it.
  MuseumLayout place(int index, String? artworkId) {
    RangeError.checkValidIndex(index, slots);
    final updated = List<String?>.of(slots);
    if (artworkId != null) {
      for (var i = 0; i < updated.length; i++) {
        if (updated[i] == artworkId) updated[i] = null;
      }
    }
    updated[index] = artworkId;
    return copyWith(slots: updated);
  }

  MuseumLayout swap(int first, int second) {
    RangeError.checkValidIndex(first, slots);
    RangeError.checkValidIndex(second, slots);
    final updated = List<String?>.of(slots);
    final value = updated[first];
    updated[first] = updated[second];
    updated[second] = value;
    return copyWith(slots: updated);
  }
}

abstract interface class MuseumRepository {
  Future<MuseumLayout> readMuseum();
  Future<void> writeMuseum(MuseumLayout layout);
}
