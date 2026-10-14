import 'package:flutter_test/flutter_test.dart';
import 'package:pixelhub/features/gallery/gallery_filters.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';

OnlinePicture picture(
  String id, {
  required String category,
  required String title,
  required String titleEn,
  int width = 16,
  int height = 16,
  int? colorCount,
}) => OnlinePicture.fromJson({
  'id': id,
  'version': 1,
  'title': title,
  'titleEn': titleEn,
  'category': category,
  'width': width,
  'height': height,
  if (colorCount != null) 'colorCount': colorCount,
  'bytes': 128,
  'checksum': List.filled(64, 'a').join(),
});

void main() {
  final animals = picture(
    'online-fox-filter',
    category: 'animals',
    title: 'روباه',
    titleEn: 'Fox',
  );
  final objects = picture(
    'online-chair-filter',
    category: 'objects',
    title: 'صندلی',
    titleEn: 'Chair',
    width: 32,
    height: 32,
    colorCount: 4,
  );
  final masterpiece = picture(
    'online-classic-canvas-filter',
    category: 'patterns',
    title: 'شاهکار',
    titleEn: 'Masterpiece',
    width: 32,
    height: 32,
    colorCount: 5,
  );

  test('a category chip filters undownloaded online pictures', () {
    final source = [animals, objects, masterpiece];
    expect(matchingOnlinePictures(source, category: 'animals', search: ''), [
      animals,
    ]);
    expect(matchingOnlinePictures(source, category: 'objects', search: ''), [
      objects,
    ]);
    expect(
      matchingOnlinePictures(source, category: 'masterpieces', search: ''),
      [masterpiece],
    );
    expect(matchingOnlinePictures(source, category: 'all', search: ''), source);
    expect(masterpiece.category, 'masterpieces');
  });

  test('search matches both languages and combines with category', () {
    final source = [animals, objects, masterpiece];
    expect(matchingOnlinePictures(source, category: 'all', search: ' FOX '), [
      animals,
    ]);
    expect(matchingOnlinePictures(source, category: 'all', search: 'صندلی'), [
      objects,
    ]);
    expect(
      matchingOnlinePictures(source, category: 'animals', search: 'chair'),
      isEmpty,
    );
    expect(
      matchingOnlinePictures(
        source,
        category: 'masterpieces',
        search: 'Master',
      ),
      [masterpiece],
    );
  });

  test('difficulty filtering composes with category and bilingual search', () {
    final source = [animals, objects, masterpiece];
    expect(
      matchingOnlinePictures(
        source,
        category: 'all',
        search: '',
        difficulty: 'easy',
      ),
      [animals],
    );
    expect(
      matchingOnlinePictures(
        source,
        category: 'all',
        search: 'chair',
        difficulty: 'medium',
      ),
      [objects],
    );
    expect(
      matchingOnlinePictures(
        source,
        category: 'animals',
        search: 'fox',
        difficulty: 'hard',
      ),
      isEmpty,
    );
    expect(
      matchingOnlinePictures(
        source,
        category: 'patterns',
        search: 'شاهکار',
        difficulty: 'hard',
      ),
      [masterpiece],
    );
    expect(matchingOnlinePictures(source, category: 'all', search: ''), source);
  });

  test('the visible slice is calculated after filtering', () {
    final source = [
      for (var i = 0; i < 24; i++)
        picture(
          'online-filter-$i',
          category: i.isEven ? 'animals' : 'objects',
          title: 'طرح $i',
          titleEn: 'Painting $i',
        ),
    ];
    final filtered = matchingOnlinePictures(
      source,
      category: 'animals',
      search: '',
    );
    expect(filtered, hasLength(12));
    expect(filtered.take(6), hasLength(6));
    expect(filtered.skip(6).take(12), hasLength(6));
  });
}
