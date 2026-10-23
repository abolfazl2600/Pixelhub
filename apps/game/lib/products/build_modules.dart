/// Compile-time gates supplied by tool/products/module_bundle.py.
///
/// These constants allow Dart AOT tree shaking to discard route-only modules
/// that are disabled for a built product. Direct "flutter run" defaults to
/// the existing runtime feature behavior; production builds always pass all
/// flags explicitly from the selected product manifest.
abstract final class BuildModules {
  static const museum = bool.fromEnvironment(
    'MODULE_MUSEUM',
    defaultValue: true,
  );
  static const badges = bool.fromEnvironment(
    'MODULE_BADGES',
    defaultValue: true,
  );
  static const imageImport = bool.fromEnvironment(
    'MODULE_IMAGE_IMPORT',
    defaultValue: true,
  );
  static const profile = bool.fromEnvironment(
    'MODULE_PROFILE',
    defaultValue: true,
  );
  static const animations = bool.fromEnvironment(
    'MODULE_ANIMATIONS',
    defaultValue: true,
  );
  static const sounds = bool.fromEnvironment(
    'MODULE_SOUNDS',
    defaultValue: true,
  );
  static const diamond = bool.fromEnvironment(
    'MODULE_DIAMOND',
    defaultValue: true,
  );
  static const canvas = bool.fromEnvironment(
    'MODULE_CANVAS',
    defaultValue: true,
  );
  static const online = bool.fromEnvironment(
    'MODULE_ONLINE',
    defaultValue: true,
  );
}
