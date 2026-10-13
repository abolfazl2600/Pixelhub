import 'dart:io';

import 'package:image/image.dart' as img;

/// Regenerate platform icon sizes from the owner-selected, checked-in source.
/// Run from apps/game after flutter pub get, before Android or Web builds.
void main() {
  final sourceFile = File('assets/brand/pixelhub_mark.png');
  final source = img.decodePng(sourceFile.readAsBytesSync());
  if (source == null || source.width != 256 || source.height != 256) {
    throw StateError('Expected a valid 256 x 256 PixelHub launcher PNG.');
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
    final file = File(entry.key);
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
}
