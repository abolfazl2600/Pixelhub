#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root/apps/game"
flutter pub get --enforce-lockfile
dart run ../../tool/generate_launcher_icons.dart
# Bundle CanvasKit locally; hash routes survive refresh on static Pages.
flutter build web --release --base-href /Pixelhub/ --no-web-resources-cdn --pwa-strategy=none
# The public privacy URL must be part of every production Web artifact.
test -s build/web/privacy.html
python3 ../../tool/prepare_offline_web.py build/web
