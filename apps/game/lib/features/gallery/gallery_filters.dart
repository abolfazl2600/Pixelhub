import 'online_catalog_controller.dart';

/// Only undownloaded online pictures reach this filter. Both the category chip
/// and gallery search apply to remote entries before pagination.
List<OnlinePicture> matchingOnlinePictures(
  Iterable<OnlinePicture> pictures, {
  required String category,
  required String search,
}) {
  final query = search.trim().toLowerCase();
  return pictures
      .where((picture) {
        if (category != 'all' && picture.category != category) return false;
        if (query.isEmpty) return true;
        return '${picture.title} ${picture.titleEn}'.toLowerCase().contains(
          query,
        );
      })
      .toList(growable: false);
}
