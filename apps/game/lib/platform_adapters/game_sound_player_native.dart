import 'package:flutter/services.dart';

import '../core/sound_cue.dart';

SoundEffectPlayer createSoundEffectPlayer() => _NativeSoundEffectPlayer();

/// Android registers this channel with SoundPool. Other native targets
/// safely fall back to silence until a platform implementation is added.
class _NativeSoundEffectPlayer implements SoundEffectPlayer {
  static const _channel = MethodChannel('pixelhub/sounds');

  @override
  Future<void> preload() async {
    for (final cue in SoundCue.values) {
      final data = await rootBundle.load(
        'assets/sounds/' + cue.assetName + '.wav',
      );
      await _channel.invokeMethod<void>('load', {
        'name': cue.assetName,
        'bytes': data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes),
      });
    }
  }

  @override
  Future<void> play(SoundCue cue) => _channel.invokeMethod<void>('play', {
    'name': cue.assetName,
  });

  @override
  void dispose() {}
}
