import 'dart:convert';
import 'dart:js_interop';

import 'package:flutter/services.dart';
import 'package:web/web.dart' as web;

import '../core/sound_cue.dart';

SoundEffectPlayer createSoundEffectPlayer() => _WebSoundEffectPlayer();

/// Data URLs keep these tiny audio assets usable in offline Flutter Web.
class _WebSoundEffectPlayer implements SoundEffectPlayer {
  final Map<SoundCue, web.HTMLAudioElement> _sounds = {};

  @override
  Future<void> preload() async {
    for (final cue in SoundCue.values) {
      final data = await rootBundle.load('assets/sounds/${cue.assetName}.wav');
      final bytes = data.buffer.asUint8List(
        data.offsetInBytes,
        data.lengthInBytes,
      );
      _sounds[cue] = web.HTMLAudioElement()
        ..src = 'data:audio/wav;base64,${base64Encode(bytes)}'
        ..preload = 'auto'
        ..volume = 0.45;
    }
  }

  @override
  Future<void> play(SoundCue cue) async {
    final audio = _sounds[cue];
    if (audio == null) return;
    audio.pause();
    audio.currentTime = 0;
    await audio.play().toDart;
  }

  @override
  void dispose() {
    for (final audio in _sounds.values) {
      audio.pause();
    }
    _sounds.clear();
  }
}
