import 'package:flutter_test/flutter_test.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/core/game_sounds.dart';

class _RecordingSoundPlayer implements SoundEffectPlayer {
  final List<SoundCue> played = [];
  @override
  Future<void> preload() async {}
  @override
  Future<void> play(SoundCue cue) async {
    played.add(cue);
  }

  @override
  void dispose() {}
}

void main() {
  test('sound effects are optional, local and remembered', () async {
    final preferences = MemoryPreferences();
    final player = _RecordingSoundPlayer();
    final sounds = GameSounds(preferences: preferences, player: player);
    await sounds.initialize();
    expect(sounds.enabled, isTrue);
    await sounds.setEnabled(false);
    await sounds.play(SoundCue.coinPurchase);
    expect(player.played, isEmpty);
    sounds.dispose();

    final reopened = GameSounds(
      preferences: preferences,
      player: _RecordingSoundPlayer(),
    );
    await reopened.initialize();
    expect(reopened.enabled, isFalse);
    reopened.dispose();
  });

  test('completed painting plays before earned coins', () async {
    final player = _RecordingSoundPlayer();
    final sounds = GameSounds(player: player);
    await sounds.initialize();
    await Future.wait([
      sounds.play(SoundCue.paintingCompleted),
      sounds.play(SoundCue.coinsEarned),
    ]);
    expect(player.played, [
      SoundCue.paintingCompleted,
      SoundCue.coinsEarned,
    ]);
    sounds.dispose();
  });
}
