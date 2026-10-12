import 'dart:ui' show PlatformDispatcher;

import 'package:flutter/material.dart';

import 'core/local_diagnostics.dart';
import 'package:persistence/persistence.dart';

import 'app/pixelhub_app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = LocalPreferences();
  final diagnostics = LocalDiagnostics();
  // Count error categories locally; preserve Flutter and platform reporting.
  FlutterError.onError = (details) {
    diagnostics.recordError();
    FlutterError.presentError(details);
  };
  PlatformDispatcher.instance.onError = (error, stack) {
    diagnostics.recordError();
    return false;
  };
  runApp(
    PixelhubApp(
      repository: AssetLevelRepository(),
      progressRepository: storage,
      preferences: storage,
      diagnostics: diagnostics,
    ),
  );
}
