import 'dart:ui' show PlatformDispatcher;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show appFlavor;

import 'core/local_diagnostics.dart';
import 'package:persistence/persistence.dart';

import 'app/pixelhub_app.dart';
import 'products/product_configuration.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final product = selectedProduct;
  if (appFlavor != null && appFlavor != product.id) {
    throw StateError(
      'Android flavor must match PRODUCT_ID; use tool/products/build.py',
    );
  }
  final storage = LocalPreferences(scope: product.storageScope);
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
      product: product,
      repository: AssetLevelRepository(catalogPath: product.offlineManifest),
      progressRepository: storage,
      preferences: storage,
      diagnostics: diagnostics,
    ),
  );
}
