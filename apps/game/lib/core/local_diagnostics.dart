import 'package:flutter/material.dart';

/// Aggregate on-device counters for this app session only.
/// No user identifiers, stacks, photos or progress bitsets are retained.
final class LocalDiagnostics extends ChangeNotifier {
  int screenOpens = 0;
  int hints = 0;
  int bombs = 0;
  int completions = 0;
  int frameworkErrors = 0;
  int? catalogLoadMilliseconds;

  /// Remains disabled until an approved provider and consent are configured.
  bool get remoteCrashReportingEnabled => false;

  void recordScreen() {
    screenOpens++;
    notifyListeners();
  }

  void recordHint() {
    hints++;
    notifyListeners();
  }

  void recordBomb() {
    bombs++;
    notifyListeners();
  }

  void recordCompletion() {
    completions++;
    notifyListeners();
  }

  void recordCatalogLoad(int milliseconds) {
    catalogLoadMilliseconds ??= milliseconds;
    notifyListeners();
  }

  void recordError() {
    frameworkErrors++;
    notifyListeners();
  }
}

class LocalNavigationObserver extends NavigatorObserver {
  LocalNavigationObserver(this.diagnostics);
  final LocalDiagnostics diagnostics;

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    diagnostics.recordScreen();
    super.didPush(route, previousRoute);
  }
}
