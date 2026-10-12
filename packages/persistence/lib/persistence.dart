import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:game_domain/game_domain.dart';
import 'package:level_schema/level_schema.dart';

final class AssetLevelRepository implements LevelRepository {
  AssetLevelRepository({AssetBundle? bundle}) : _bundle = bundle ?? rootBundle;

  final AssetBundle _bundle;

  @override
  Future<LevelDefinition> loadPreview() async {
    final source = await _bundle.loadString(LevelAssets.sunflower);
    final decoded = jsonDecode(source);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a level object.');
    }
    return LevelDefinition.fromJson(decoded);
  }
}
