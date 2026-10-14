import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/gallery/artwork_categories.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';
import 'package:pixelhub/features/gallery/online_catalog_controller.dart';

LevelDefinition categoryFixture(String id) => LevelDefinition(
  id: id,
  title: 'نمونه',
  titleEn: 'Example',
  schemaVersion: 2,
  contentVersion: 1,
  width: 2,
  height: 2,
  palette: [0xff000000, 0xffffffff],
  cells: [0, 1, 1, 0],
);

void main() {
  test('seven public categories are distinct from personal artwork', () {
    expect(publicArtworkCategories, hasLength(7));
    expect(publicArtworkCategories.toSet(), onlinePictureCategories);
    expect(publicArtworkCategories, isNot(contains('personal')));
  });

  test(
    'historic collections are classified by IDs, never localized titles',
    () {
      for (final id in [
        'online-mona-lisa',
        'online-starry-night',
        'online-the-scream',
        'online-sunflowers',
        'online-girl-pearl',
        'online-great-wave',
        'online-classic-birth-venus',
        'online-classic-creation-adam',
        'online-classic-last-supper',
        'online-classic-school-athens',
        'online-classic-night-watch',
        'online-classic-milkmaid',
        'online-classic-las-meninas',
        'online-classic-third-may',
        'online-classic-liberty-leading',
        'online-classic-wanderer-fog',
        'online-classic-fighting-temeraire',
        'online-classic-hay-wain',
        'online-classic-impression-sunrise',
        'online-classic-water-lilies',
        'online-classic-moulin-galette',
        'online-classic-grande-jatte',
        'online-classic-klimt-kiss',
        'online-classic-card-players',
        'online-classic-wheatfield-crows',
        'online-classic-sleeping-gypsy',
      ]) {
        expect(displayArtworkCategory(id, 'patterns'), 'masterpieces');
      }
      for (final id in [
        'online-iran-azadi-tower',
        'online-iran-milad-tower',
        'online-iran-persepolis',
        'online-iran-imam-mosque',
        'online-iran-sio-se-pol',
        'online-iran-nasir-ol-molk',
        'online-iran-arg-e-bam',
        'online-iran-hafez-tomb',
        'online-iran-amir-chakhmaq',
        'online-iran-golestan-palace',
        'online-iran-abstract-muqarnas',
        'online-iran-abstract-dome',
        'online-iran-abstract-orsi',
        'online-iran-abstract-eslimi',
        'online-iran-abstract-arches',
        'online-iran-abstract-windcatcher',
        'online-iran-abstract-shamsa',
        'online-iran-abstract-mosque',
        'online-iran-abstract-brickwork',
        'online-iran-abstract-iwan',
        'online-iran-pasargadae-cyrus-tomb',
        'online-iran-chogha-zanbil',
        'online-iran-soltaniyeh-dome',
        'online-iran-karim-khan-citadel',
        'online-iran-borujerdi-house',
        'online-iran-tabatabaei-house',
        'online-iran-vank-cathedral',
        'online-iran-falak-ol-aflak',
        'online-iran-tabriz-bazaar',
        'online-iran-yazd-jameh-mosque',
        'online-iran-gonbad-qabus',
        'online-iran-naqsh-e-rostam',
      ]) {
        expect(displayArtworkCategory(id, 'patterns'), 'persian_architecture');
      }
      expect(
        displayArtworkCategory('online-general-mosaic', 'patterns'),
        'patterns',
      );
      expect(displayArtworkCategory('online-iran-tree', 'nature'), 'nature');
    },
  );

  test(
    'saved legacy categories migrate when reopening completely offline',
    () async {
      final store = MemoryPreferences();
      final art = categoryFixture('online-mona-lisa');
      final building = categoryFixture('online-iran-persepolis');
      final pattern = categoryFixture('online-decorative-pattern');
      for (final level in [art, building, pattern]) {
        await store.saveDownloadedLevel(level, category: 'patterns');
      }
      final controller = OnlineCatalogController(store);
      addTearDown(controller.dispose);
      await controller.loadDownloaded();
      expect(controller.pictures, isEmpty);
      expect(controller.categories[art.id], 'masterpieces');
      expect(controller.categories[building.id], 'persian_architecture');
      expect(controller.categories[pattern.id], 'patterns');
      expect(await store.readDownloadedCategories(), {
        art.id: 'masterpieces',
        building.id: 'persian_architecture',
        pattern.id: 'patterns',
      });
      final library = LibraryController(store, store);
      addTearDown(library.dispose);
      library.setDownloadedOnline(controller.downloaded);
      library.setOnlineCategories(controller.categories);
      expect(library.category(art), 'masterpieces');
      expect(library.category(building), 'persian_architecture');
      expect(library.category(pattern), 'patterns');
      final reopened = OnlineCatalogController(store);
      addTearDown(reopened.dispose);
      await reopened.loadDownloaded();
      expect(reopened.categories[art.id], 'masterpieces');
      expect(reopened.categories[building.id], 'persian_architecture');
    },
  );

  test('original online catalog metadata remains compatible', () {
    final painting = categoryFixture('online-mona-lisa');
    final oldRecord = <String, Object>{
      'id': painting.id,
      'version': 1,
      'title': painting.title,
      'titleEn': painting.titleEn,
      'category': 'patterns',
      'width': painting.width,
      'height': painting.height,
      'bytes': 256,
      'checksum': painting.checksum,
    };
    expect(OnlinePicture.fromJson(oldRecord).category, 'masterpieces');
    expect(
      OnlinePicture.fromJson({
        ...oldRecord,
        'id': 'online-future-masterwork',
        'category': 'masterpieces',
      }).category,
      'masterpieces',
    );
    expect(
      OnlinePicture.fromJson({
        ...oldRecord,
        'id': 'online-decorative-pattern',
      }).category,
      'patterns',
    );
  });
}
