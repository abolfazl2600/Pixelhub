/// Short, locally bundled cues for game economy and painting milestones.
enum SoundCue {
  coinPurchase('coin_purchase', Duration(milliseconds: 460)),
  coinsEarned('coins_earned', Duration(milliseconds: 690)),
  paintingCompleted('painting_completed', Duration(milliseconds: 1600));

  const SoundCue(this.assetName, this.duration);

  final String assetName;
  final Duration duration;
}

/// Platform playback is injectable, so the economy can be tested without audio.
abstract interface class SoundEffectPlayer {
  Future<void> preload();
  Future<void> play(SoundCue cue);
  void dispose();
}
