import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:persistence/persistence.dart';

import '../platform_adapters/game_sound_player_native.dart'
    if (dart.library.js_interop) '../platform_adapters/game_sound_player_web.dart'
    as platform;
import 'sound_cue.dart';

export 'sound_cue.dart';

/// Optional local audio: a playback problem never blocks painting or the wallet.
class GameSounds extends ChangeNotifier {
  GameSounds({
    SoundEffectsPreferences? preferences,
    SoundEffectPlayer? player,
    this.available = true,
  }) : _preferences = preferences,
       _player = player ?? platform.createSoundEffectPlayer();

  final bool available;
  final SoundEffectsPreferences? _preferences;
  final SoundEffectPlayer _player;
  Future<void> _tail = Future<void>.value();
  bool _enabled = true;
  bool _prepared = false;
  bool _disposed = false;

  bool get enabled => available && _enabled;

  Future<void> initialize() async {
    if (!available) return;
    final preferences = _preferences;
    if (preferences != null) {
      try {
        final saved = await preferences.readSoundEffectsEnabled();
        if (!_disposed && saved != null) {
          _enabled = saved;
          notifyListeners();
        }
      } on Object {
        // Damaged optional preferences use the sound-on default.
      }
    }
    try {
      await _player.preload();
      if (!_disposed) _prepared = true;
    } on Object {
      // Unsupported platforms and failed assets stay silent.
    }
  }

  Future<void> setEnabled(bool value) async {
    if (!available || _disposed || _enabled == value) return;
    _enabled = value;
    notifyListeners();
    try {
      await _preferences?.writeSoundEffectsEnabled(value);
    } on Object {
      // Playback remains usable even if the preference cannot be saved.
    }
  }

  /// Serialize cues so the coin reward does not mask the completion melody.
  Future<void> play(SoundCue cue) {
    if (!available || !_prepared || !_enabled || _disposed) {
      return Future<void>.value();
    }
    final next = _tail.then((_) async {
      if (_disposed || !_enabled) return;
      try {
        await _player.play(cue);
      } on Object {
        return;
      }
      if (cue == SoundCue.paintingCompleted) {
        await Future<void>.delayed(cue.duration);
      }
    });
    _tail = next.catchError((Object _) {});
    return next;
  }

  @override
  void dispose() {
    _disposed = true;
    _player.dispose();
    super.dispose();
  }
}
