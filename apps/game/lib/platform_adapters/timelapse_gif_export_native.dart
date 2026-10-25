import 'dart:io';

import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

/// Save writes the GIF to Pictures/PixelHub on Android 10+, or the user-selected
/// destination on older Android, without broad storage permissions.
const _gifStorageChannel = MethodChannel('pixelhub/timelapse_gif');

Future<bool> saveTimelapseGif(Uint8List bytes, String name, Rect origin) async {
  if (bytes.isEmpty ||
      bytes.length > 16 * 1024 * 1024 ||
      !RegExp(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,119}\.gif$').hasMatch(name)) {
    throw ArgumentError('Invalid GIF file.');
  }
  return await _gifStorageChannel.invokeMethod<bool>('save', {
        'name': name,
        'bytes': bytes,
      }) ??
      false;
}

/// Share offers a system sheet and uses a temporary source file.

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
    if (await file.exists()) {
      await file.delete();
    }
  }
}
