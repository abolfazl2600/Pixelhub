import 'dart:async';
import 'dart:js_interop';
import 'dart:typed_data';
import 'dart:ui';

import 'package:share_plus/share_plus.dart';
import 'package:web/web.dart' as web;

Future<bool> saveTimelapseGif(
  Uint8List bytes,
  String name,
  Rect origin,
) async {
  final blob = web.Blob(
    [bytes.toJS].toJS,
    web.BlobPropertyBag(type: 'image/gif'),
  );
  final url = web.URL.createObjectURL(blob);
  try {
    final link = web.HTMLAnchorElement()
      ..href = url
      ..download = name;
    web.document.body!.appendChild(link);
    link.click();
    link.remove();
  } finally {
    // The browser consumes the object URL asynchronously after the click.
    unawaited(
      Future<void>.delayed(
        const Duration(seconds: 30),
        () => web.URL.revokeObjectURL(url),
      ),
    );
  }
  return true;
}

Future<bool> shareTimelapseGif(
  Uint8List bytes,
  String name,
  Rect origin,
) async {
  final result = await SharePlus.instance.share(
    ShareParams(
      files: [XFile.fromData(bytes, mimeType: 'image/gif', name: name)],
      fileNameOverrides: [name],
      sharePositionOrigin: origin,
    ),
  );
  return result.status != ShareResultStatus.dismissed;
}
