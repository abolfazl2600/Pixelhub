import 'dart:async';
import 'dart:js_interop';
import 'dart:typed_data';
import 'dart:ui';

import 'package:web/web.dart' as web;

Future<bool> exportTimelapse(Uint8List bytes, String name, Rect origin) async {
  final blob = web.Blob([bytes.toJS].toJS, web.BlobPropertyBag(type: 'image/gif'));
  final url = web.URL.createObjectURL(blob);
  final link = web.HTMLAnchorElement()
    ..href = url
    ..download = name;
  web.document.body!.appendChild(link);
  link.click();
  link.remove();
  unawaited(Future<void>.delayed(const Duration(seconds: 30),
      () => web.URL.revokeObjectURL(url)));
  return true;
}
