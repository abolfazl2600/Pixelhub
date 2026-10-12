#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/tool/cloud_env.sh"
# A separate Web-only Flutter profile avoids ADB discovery in the cloud, where
# ADB's hard-coded home directory is read-only. Normal Android builds retain
# the standard profile from cloud_env.sh.
export XDG_CONFIG_HOME=/workspace/.cache/flutter-web-config
flutter config --no-enable-android
cd "$repo_root/apps/game"
exec flutter run -d web-server --web-hostname 127.0.0.1 --web-port "${1:-8080}" --no-web-resources-cdn
