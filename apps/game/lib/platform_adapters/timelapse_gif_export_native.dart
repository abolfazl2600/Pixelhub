import 'dart:io';
import 'dart:typed_data';
import 'dart:ui';

import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

/// Android's Sharesheet offers Files/Drive and compatible save destinations.
/// Only the temporary source file is deleted; saved destination files persist.
Future<bool> saveTimelapseGif(Uint8List bytes, String name, Rect origin) =>
    shareTimelapseGif(bytes, name, origin);

Future<bool> shareTimelapseGif(
  Uint8List bytes,
  String name,
  Rect origin,
) async {
  final directory = await getTemporaryDirectory();
  final file = File(
    '${directory.path}/pixelhub-gif-${DateTime.now().microsecondsSinceEpoch}.gif',
  );
  try {
    await file.writeAsBytes(bytes, flush: true);
    final result = await SharePlus.instance.share(
      ShareParams(
        files: [XFile(file.path, mimeType: 'image/gif', name: name)],
        fileNameOverrides: [name],
        sharePositionOrigin: origin,
      ),
    );
    return result.status != ShareResultStatus.dismissed;
  } finally {
    if (await file.exists()) await file.delete();
  }
}
