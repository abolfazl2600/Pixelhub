import 'dart:async';
import 'dart:js_interop';

import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;

import 'offline_state.dart';

final offlineStatus = ValueNotifier(OfflineStatus.preparing);
Future<void>? _preparing;

Future<void> prepareOfflineApp() =>
    _preparing ??= _prepare().whenComplete(() => _preparing = null);

Future<void> _prepare() async {
  offlineStatus.value = OfflineStatus.preparing;
  try {
    final registration = await web.window.navigator.serviceWorker
        .register('offline-worker.js'.toJS)
        .toDart;
    final worker =
        registration.installing ?? registration.waiting ?? registration.active;
    if (worker == null) throw StateError('Offline worker unavailable.');
    final completion = Completer<void>();
    void check() {
      if (completion.isCompleted) return;
      if (worker.state == 'installed' || worker.state == 'activated') {
        completion.complete();
      } else if (worker.state == 'redundant') {
        completion.completeError(StateError('Offline installation failed.'));
      }
    }

    final listener = ((web.Event event) => check()).toJS;
    worker.addEventListener('statechange', listener);
    check();
    try {
      await completion.future.timeout(const Duration(seconds: 45));
    } finally {
      worker.removeEventListener('statechange', listener);
    }
    offlineStatus.value = OfflineStatus.ready;
  } on Object {
    // Browser policy/quota/private mode must never stop normal online play.
    offlineStatus.value = OfflineStatus.unavailable;
  }
}
