import 'artwork_difficulty.dart';
import 'online_catalog_controller.dart';

/// Only undownloaded online pictures reach this filter. Category, difficulty,
/// and gallery search apply before pagination so the visible slice is stable.
List<OnlinePicture> matchingOnlinePictures(
  Iterable<OnlinePicture> pictures, {
  required String category,
  required String search,
  String difficulty = 'all',
}) {
  final query = search.trim().toLowerCase();
  return pictures
      .where((picture) {
        if (category != 'all' && picture.category != category) return false;
        if (difficulty != 'all' &&
            difficultyForOnlineGrid(
                  width: picture.width,
                  height: picture.height,
                  colorCount: picture.colorCount,
                ).name !=
                difficulty) {
          return false;
        }
        if (query.isEmpty) return true;
        return '${picture.title} ${picture.titleEn}'.toLowerCase().contains(
          query,
        );
      })
      .toList(growable: false);
}
