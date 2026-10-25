import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pixelhub/platform_adapters/timelapse_gif_export_native.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('pixelhub/timelapse_gif');
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;

  tearDown(() => messenger.setMockMethodCallHandler(channel, null));

  test('Save GIF invokes the native storage channel, not sharing', () async {
    MethodCall? received;
    messenger.setMockMethodCallHandler(channel, (call) async {
      received = call;
      return true;
    });
    final bytes = Uint8List.fromList([71, 73, 70, 56, 57, 97]);
    final saved = await saveTimelapseGif(
      bytes,
      'pixelhub-kids-timelapse.gif',
      Rect.zero,
    );
    expect(saved, isTrue);
    expect(received?.method, 'save');
    expect(received?.arguments['name'], 'pixelhub-kids-timelapse.gif');
    expect(received?.arguments['bytes'], bytes);
  });

  test('Cancelled device picker does not claim to have saved', () async {
    messenger.setMockMethodCallHandler(channel, (call) async => false);
    final saved = await saveTimelapseGif(
      Uint8List.fromList([71, 73, 70]),
      'pixelhub-kids-timelapse.gif',
      Rect.zero,
    );
    expect(saved, isFalse);
  });

  test('Invalid save name or missing data is rejected before channel call', () {
    expect(
      saveTimelapseGif(Uint8List(0), 'picture.gif', Rect.zero),
      throwsArgumentError,
    );
    expect(
      saveTimelapseGif(Uint8List.fromList([71]), '../outside.gif', Rect.zero),
      throwsArgumentError,
    );
  });
}
