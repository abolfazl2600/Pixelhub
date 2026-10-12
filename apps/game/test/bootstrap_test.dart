import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';
import 'package:pixelhub/app/bootstrap_controller.dart';

LevelDefinition fixture() => LevelDefinition(
  id: 'sample',
  title: 'آفتابگردان',
  schemaVersion: 1,
  contentVersion: 1,
  width: 2,
  height: 2,
  palette: [0xfff8edb7, 0xff316349],
  cells: [0, 1, 1, 0],
);

class TestRepository implements LevelRepository {
  final requests = <Completer<LevelDefinition>>[];

  @override
  Future<LevelDefinition> loadPreview() {
    final request = Completer<LevelDefinition>();
    requests.add(request);
    return request.future;
  }
}

void main() {
  test('loads local preview, then recovers from failure on retry', () async {
    final repository = TestRepository();
    final controller = BootstrapController(repository);
    addTearDown(controller.dispose);
    final first = controller.load();
    expect(controller.status, BootstrapStatus.loading);
    repository.requests[0].completeError(const FormatException('asset'));
    await first;
    expect(controller.status, BootstrapStatus.error);
    final retry = controller.load();
    final level = fixture();
    repository.requests[1].complete(level);
    await retry;
    expect(controller.status, BootstrapStatus.ready);
    expect(controller.level, same(level));
  });

  test('an older request cannot overwrite a newer result', () async {
    final repository = TestRepository();
    final controller = BootstrapController(repository);
    addTearDown(controller.dispose);
    final oldRequest = controller.load();
    final newRequest = controller.load();
    final level = fixture();
    repository.requests[1].complete(level);
    await newRequest;
    repository.requests[0].completeError(StateError('stale request'));
    await oldRequest;
    expect(controller.status, BootstrapStatus.ready);
    expect(controller.level, same(level));
  });

  test('a pending load can complete after disposal', () async {
    final repository = TestRepository();
    final controller = BootstrapController(repository);
    final pending = controller.load();
    controller.dispose();
    repository.requests.single.complete(fixture());
    await pending;
  });
}
