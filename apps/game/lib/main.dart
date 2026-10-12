import 'package:flutter/material.dart';
import 'package:persistence/persistence.dart';

import 'app/pixelhub_app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = LocalPreferences();
  runApp(
    PixelhubApp(
      repository: AssetLevelRepository(),
      progressRepository: storage,
      preferences: storage,
    ),
  );
}
