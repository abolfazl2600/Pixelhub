#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
expected_version="$(cat .flutter-version)"
flutter --version --machine | python3 -c 'import json,sys; version=json.load(sys.stdin)["frameworkVersion"]; expected=sys.argv[1]; print("Flutter:", version); sys.exit(0 if version == expected else "Use Flutter " + expected)' "$expected_version"
cd apps/game
flutter pub get --enforce-lockfile
cd "$repo_root"
dart --suppress-analytics format --output=none --set-exit-if-changed apps/game/lib apps/game/test packages
for package in level_schema game_domain persistence design_system painting_engine; do
  cd "$repo_root/packages/$package"
  flutter pub get
  flutter analyze --no-pub
done
cd "$repo_root/apps/game"
flutter analyze --no-pub
flutter test --no-pub --reporter expanded
