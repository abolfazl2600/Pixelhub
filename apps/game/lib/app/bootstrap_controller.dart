import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

enum BootstrapStatus { loading, ready, error }

/// The sole V1 state owner. Injected ports keep loading/retry testable.
class BootstrapController extends ChangeNotifier {
  BootstrapController(this.repository);

  final LevelRepository repository;
  BootstrapStatus status = BootstrapStatus.loading;
  LevelDefinition? level;
  bool _disposed = false;
  int _generation = 0;

  Future<void> load() async {
    final generation = ++_generation;
    status = BootstrapStatus.loading;
    notifyListeners();
    try {
      final result = await repository.loadPreview();
      if (_disposed || generation != _generation) return;
      level = result;
      status = BootstrapStatus.ready;
    } on Object {
      if (_disposed || generation != _generation) return;
      status = BootstrapStatus.error;
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
