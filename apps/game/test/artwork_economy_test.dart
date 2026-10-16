import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';
import 'package:painting_engine/painting_engine.dart';
import 'package:pixelhub/features/gallery/artwork_difficulty.dart';
import 'package:pixelhub/features/gallery/artwork_economy.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';

LevelDefinition _art(String id, int side, int colors) => LevelDefinition(
  id: id,
  title: 'تابلو',
  titleEn: 'Painting',
  schemaVersion: 2,
  contentVersion: 1,
  width: side,
  height: side,
  palette: List.generate(colors, (i) => 0xff123456 + i * 0x111),
  cells: List.generate(side * side, (i) => i % colors),
);

void main() {
  test(
    'prices vary per art; difficult pictures cost more; rewards keep play possible',
    () {
      final easy = _art('price-easy', 16, 4);
      final medium = _art('price-medium', 32, 4);
      final hard = _art('price-hard', 32, 5);
      expect(difficultyForLevel(easy), ArtworkDifficulty.easy);
      expect(difficultyForLevel(medium), ArtworkDifficulty.medium);
      expect(difficultyForLevel(hard), ArtworkDifficulty.hard);
      expect(priceForLevel(easy), lessThan(priceForLevel(medium)));
      expect(priceForLevel(medium), lessThan(priceForLevel(hard)));
      for (final level in [easy, medium, hard]) {
        expect(
          rewardForLevel(level),
          greaterThanOrEqualTo(priceForLevel(level)),
        );
      }
      expect(
        artworkPrice('abc', ArtworkDifficulty.easy),
        isNot(artworkPrice('abce', ArtworkDifficulty.easy)),
      );
      expect(alwaysFreeArtwork('sunflower'), isTrue);
      expect(alwaysFreeArtwork('private-own-art'), isTrue);
    },
  );

  test(
    'wallet survives restarting; spending, repeat purchase and rewards are atomic',
    () async {
      final storage = MemoryPreferences();
      final image = _art('coins-paid-art', 16, 4);
      final controller = LibraryController(storage, storage);
      addTearDown(controller.dispose);
      controller.setCatalog([image], {});
      await controller.load();
      expect(controller.coins, 120);
      expect(controller.totalPoints, 0);
      expect(controller.canPaint(image), isFalse);
      final cost = priceForLevel(image);
      await controller.unlock(image);
      expect(controller.coins, 120 - cost);
      expect(controller.canPaint(image), isTrue);
      await controller.unlock(image);
      expect(controller.coins, 120 - cost);
      final reward = rewardForLevel(image);
      await controller.rewardCompletion(image);
      await controller.rewardCompletion(image);
      expect(controller.coins, 120 - cost + reward);
      expect(controller.totalPoints, reward);
      await controller.toggleFavorite(image);

      final reopened = LibraryController(storage, storage);
      addTearDown(reopened.dispose);
      reopened.setCatalog([image], {});
      await reopened.load();
      expect(reopened.coins, controller.coins);
      expect(reopened.totalPoints, reward);
      expect(reopened.canPaint(image), isTrue);
      await reopened.rewardCompletion(image);
      expect(reopened.totalPoints, reward);
      await reopened.unlock(image);
      expect(reopened.coins, controller.coins);
      expect(reopened.isFavorite(image), isTrue);
    },
  );

  test(
    'insufficient coins cannot unlock art or produce negative balance',
    () async {
      final storage = MemoryPreferences();
      await storage.writeLibrary(ArtworkLibrary(coins: 0));
      final image = _art('expensive-art', 32, 5);
      final library = LibraryController(storage, storage);
      addTearDown(library.dispose);
      library.setCatalog([image], {});
      await library.load();
      await expectLater(library.unlock(image), throwsStateError);
      expect(library.coins, 0);
      expect(library.canPaint(image), isFalse);
      expect((await storage.readLibrary()).unlocked, isEmpty);
    },
  );

  test('precision tool charges serialize and persist without points loss', () async {
    final storage = MemoryPreferences();
    final wallet = LibraryController(storage, storage);
    addTearDown(wallet.dispose);
    await wallet.load();
    expect(precisionToolPrice(PrecisionPaintTool.magicWand), 12);
    expect(precisionToolPrice(PrecisionPaintTool.colorSplash), 6);
    expect(wallet.coins, 120);

    await Future.wait([
      wallet.spendToolCoins(precisionToolPrice(PrecisionPaintTool.magicWand)),
      wallet.spendToolCoins(precisionToolPrice(PrecisionPaintTool.colorSplash)),
    ]);
    expect(wallet.coins, 102);
    expect(wallet.totalPoints, 0);
    await expectLater(wallet.spendToolCoins(103), throwsStateError);
    await expectLater(wallet.spendToolCoins(0), throwsArgumentError);
    expect(wallet.coins, 102);
    expect((await storage.readLibrary()).coins, 102);

    final reopened = LibraryController(storage, storage);
    addTearDown(reopened.dispose);
    await reopened.load();
    expect(reopened.coins, 102);
    expect(reopened.totalPoints, 0);
  });

  test(
    'existing library migrates safely and in-progress old art stays playable',
    () async {
      final old = ArtworkLibrary.fromJson({
        'schemaVersion': 1,
        'artworks': <Object>[],
        'favorites': ['legacy-painting'],
      });
      expect(old.coins, 120);
      expect(old.totalPoints, 0);
      expect(old.unlocked, isEmpty);
      expect(old.rewarded, isEmpty);

      final store = MemoryPreferences();
      final level = _art('legacy-painting', 16, 4);
      await store.writeLibrary(old);
      final library = LibraryController(store, store);
      addTearDown(library.dispose);
      library.setCatalog([level], {});
      await library.load();
      expect(library.canPaint(level), isFalse);
      // Existing valid progress must grandfather previous users in.
      // In production it is also read from the repository on load.
      final bits = List<int>.filled((level.cells.length + 7) ~/ 8, 0);
      bits[0] = 1;
      library.updateProgress(
        ProgressSnapshot(
          levelId: level.id,
          levelVersion: level.contentVersion,
          levelChecksum: level.checksum,
          cellCount: level.cells.length,
          generation: 0,
          revision: 1,
          bits: Uint8List.fromList(bits),
        ),
      );
      expect(library.canPaint(level), isTrue);
    },
  );

  test(
    'clearing local game data resets coins, purchases and reward claims',
    () async {
      final storage = MemoryPreferences();
      final level = _art('clear-coin-level', 16, 4);
      final library = LibraryController(storage, storage);
      addTearDown(library.dispose);
      library.setCatalog([level], {});
      await library.load();
      await library.unlock(level);
      await library.rewardCompletion(level);
      expect(library.totalPoints, greaterThan(0));
      await library.clear();
      expect(library.coins, 120);
      expect(library.totalPoints, 0);
      expect(library.canPaint(level), isFalse);
      expect((await storage.readLibrary()).rewarded, isEmpty);
    },
  );
}
