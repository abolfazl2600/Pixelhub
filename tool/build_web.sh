#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root/apps/game"
flutter pub get --enforce-lockfile
# Bundle CanvasKit locally; hash routes survive refresh on static Pages.
flutter build web --release --base-href /Pixelhub/ --no-web-resources-cdn --pwa-strategy=none
python3 ../../tool/prepare_offline_web.py build/web
