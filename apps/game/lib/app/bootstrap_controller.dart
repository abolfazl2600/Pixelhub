import 'package:flutter/foundation.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

enum BootstrapStatus { loading, ready, error }

/// Loads the local catalog. Injected ports keep loading/retry testable.
class BootstrapController extends ChangeNotifier {
  BootstrapController(this.repository);

  final LevelRepository repository;
  BootstrapStatus status = BootstrapStatus.loading;
  LevelDefinition? level;
  List<LevelDefinition> levels = [];
  bool _disposed = false;
  int _generation = 0;

  Future<void> load() async {
    final generation = ++_generation;
    status = BootstrapStatus.loading;
    notifyListeners();
    try {
      final result = await repository.loadLevels();
      if (_disposed || generation != _generation) return;
      if (result.isEmpty) throw const FormatException('Empty level catalog.');
      levels = result;
      level = result.first;
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
