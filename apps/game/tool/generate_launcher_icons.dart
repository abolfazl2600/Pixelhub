import 'dart:io';
import 'dart:convert';

import 'package:image/image.dart' as img;

/// Regenerate platform icon sizes from the owner-selected rainbow brush source.
/// Run from apps/game after flutter pub get, before Android or Web builds.
void main(List<String> args) {
  final product = args.isEmpty ? 'pixelhub' : args.single;
  if (!RegExp(r'^[a-z][a-z0-9_]*$').hasMatch(product)) {
    throw ArgumentError('Invalid product');
  }
  final registry =
      (jsonDecode(
                File('../../products/android-products.json').readAsStringSync(),
              )
              as List)
          .cast<Map<String, dynamic>>();
  final configuration = registry.firstWhere(
    (entry) => entry['id'] == product,
    orElse: () => throw ArgumentError('Unknown or unready product'),
  );
  final sourceFile = File(configuration['icon'] as String);
  final source = img.decodePng(sourceFile.readAsBytesSync());
  if (source == null || source.width != source.height || source.width < 128) {
    throw StateError(
      'Expected a square PixelHub launcher PNG of at least 128 pixels.',
    );
  }

  final sizes = <String, int>{
    'android/app/src/main/res/mipmap-mdpi/ic_launcher.png': 48,
    'android/app/src/main/res/mipmap-hdpi/ic_launcher.png': 72,
    'android/app/src/main/res/mipmap-xhdpi/ic_launcher.png': 96,
    'android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png': 144,
    'android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png': 192,
    'android/app/src/main/res/drawable-nodpi/pixelhub_icon.png': 256,
    'web/favicon.png': 32,
    'web/icons/Icon-192.png': 192,
    'web/icons/Icon-512.png': 512,
    'web/icons/Icon-maskable-192.png': 192,
    'web/icons/Icon-maskable-512.png': 512,
    'build/play-listing/icon-512.png': 512,
  };
  for (final entry in sizes.entries) {
    final path = product == 'pixelhub'
        ? entry.key
        : entry.key.replaceFirst(
            'android/app/src/main/res/',
            'android/app/src/$product/res/',
          );
    final file = File(path);
    file.parent.createSync(recursive: true);
    final resized = img.copyResize(
      source,
      width: entry.value,
      height: entry.value,
      interpolation: img.Interpolation.cubic,
    );
    file.writeAsBytesSync(img.encodePng(resized));
    stdout.writeln('Launcher: ${entry.key} (${entry.value} x ${entry.value})');
  }
  if (product != 'pixelhub') {
    for (final path in ['mipmap-anydpi-v26/ic_launcher.xml']) {
      final source = File('android/app/src/main/res/$path');
      final target = File('android/app/src/$product/res/$path');
      target.parent.createSync(recursive: true);
      target.writeAsBytesSync(source.readAsBytesSync());
    }
    final colors = File('android/app/src/$product/res/values/colors.xml');
    colors.parent.createSync(recursive: true);
    colors.writeAsStringSync(
      '<resources><color name="pixelhub_canvas">${configuration['background']}</color><color name="pixelhub_icon_background">${configuration['primary']}</color></resources>',
    );
  }
}
