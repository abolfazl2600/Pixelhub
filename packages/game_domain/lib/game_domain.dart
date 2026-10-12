import 'package:level_schema/level_schema.dart';

abstract interface class LevelRepository {
  Future<LevelDefinition> loadPreview();
}

/// Contract only in V1. No progress is persisted by the technical preview.
abstract interface class ProgressRepository {
  Future<Set<int>> readCompletedCells(String levelId, int contentVersion);
  Future<void> writeCompletedCells(
    String levelId,
    int contentVersion,
    Set<int> cells,
  );
}

/// Future account and billing ports; no production adapters in V1.
abstract interface class AuthAdapter {
  Future<String?> currentUserId();
}

abstract interface class BillingAdapter {
  Future<bool> hasEntitlement(String productId);
}
