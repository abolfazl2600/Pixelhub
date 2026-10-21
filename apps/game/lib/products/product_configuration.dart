import 'package:flutter/material.dart';

import 'products.g.dart';

@immutable
class ProductFeatures {
  const ProductFeatures({
    required this.coins,
    required this.achievements,
    required this.animations,
    required this.imageImport,
    required this.diamondPainting,
    required this.canvasPainting,
    required this.soundEffects,
    required this.onlineCatalog,
    required this.profile,
    required this.museum,
  });
  final bool coins, achievements, animations, imageImport;
  final bool diamondPainting, canvasPainting, soundEffects, onlineCatalog;
  final bool profile, museum;
}

@immutable
class ProductConfiguration {
  const ProductConfiguration({
    required this.id,
    required this.name,
    required this.displayNameFa,
    required this.applicationId,
    required this.versionName,
    required this.versionCode,
    required this.storageScope,
    required this.icon,
    required this.primary,
    required this.secondary,
    required this.background,
    required this.themeMode,
    required this.fontFamily,
    required this.homeLayout,
    required this.defaultStyle,
    required this.largeControls,
    required this.navigation,
    required this.offlineManifest,
    required this.onlineRoot,
    required this.onlineManifest,
    required this.categories,
    required this.defaultCategories,
    required this.maxDimension,
    required this.features,
  });
  final String id,
      name,
      displayNameFa,
      applicationId,
      versionName,
      storageScope;
  final int versionCode, maxDimension;
  final String icon,
      fontFamily,
      homeLayout,
      defaultStyle,
      offlineManifest,
      onlineRoot,
      onlineManifest;
  final Color primary, secondary, background;
  final ThemeMode themeMode;
  final bool largeControls;
  final List<String> navigation, categories, defaultCategories;
  final ProductFeatures features;

  bool allowsPage(String page) => switch (page) {
    'import' => features.imageImport,
    'profile' => features.profile,
    'badges' => features.achievements,
    'museum' => features.museum,
    _ => true,
  };
  bool allowsStyle(String style) => switch (style) {
    'canvas' => features.canvasPainting,
    'diamond' => features.diamondPainting,
    'pixel' => true,
    _ => false,
  };
}

ProductConfiguration productById(String id) =>
    productRegistry[id] ??
    (throw StateError('Unknown or unready product: $id'));

final selectedProduct = productById(
  const String.fromEnvironment('PRODUCT_ID', defaultValue: 'pixelhub'),
);

class ProductScope extends InheritedWidget {
  const ProductScope({required this.product, required super.child, super.key});
  final ProductConfiguration product;
  static ProductConfiguration of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<ProductScope>()?.product ??
      selectedProduct;
  @override
  bool updateShouldNotify(ProductScope oldWidget) =>
      product != oldWidget.product;
}
