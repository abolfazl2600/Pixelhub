/// Display categories for historic releases, without editing their immutable
/// manifests. Recognize published collections by stable IDs, never titles.
const publicArtworkCategories = <String>[
  'nature',
  'animals',
  'objects',
  'masterpieces',
  'persian_architecture',
  'patterns',
  'space',
];

const _originalMasterpieceIds = <String>{
  'online-mona-lisa',
  'online-starry-night',
  'online-the-scream',
  'online-sunflowers',
  'online-girl-pearl',
  'online-great-wave',
};

/// Only the known historical online collections require an override.
String? historicOnlineArtworkCategory(String id) {
  if (_originalMasterpieceIds.contains(id) ||
      id.startsWith('online-classic-')) {
    return 'masterpieces';
  }
  if (id.startsWith('online-iran-')) {
    return 'persian_architecture';
  }
  return null;
}

/// Preserve any explicitly assigned non-pattern category.
String displayArtworkCategory(String id, String category) =>
    category == 'patterns'
    ? historicOnlineArtworkCategory(id) ?? category
    : category;
