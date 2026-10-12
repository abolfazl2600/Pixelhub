#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$(uname -s)-$(uname -m)" != Linux-x86_64 ]]; then
  echo 'This helper targets the Linux x86_64 cloud machine; use README for other hosts.' >&2
  exit 1
fi
mkdir -p /workspace/.tools /workspace/.cache/android /workspace/.cache/gradle
if [[ ! -d /workspace/.tools/flutter ]]; then
  git clone --depth 1 --branch 3.35.7 https://github.com/flutter/flutter.git /workspace/.tools/flutter
fi
test "$(git -C /workspace/.tools/flutter rev-parse HEAD)" = adc901062556672b4138e18a4dc62a4be8f4b3c2

if [[ ! -x /workspace/.tools/jdk17/bin/javac ]]; then
  archive_name=OpenJDK17U-jdk_x64_linux_hotspot_17.0.20.1_1.tar.gz
  jdk_url="https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.20.1%2B1/$archive_name"
  download_dir="$(mktemp -d /tmp/pixelhub-jdk.XXXXXX)"
  curl --fail --location --retry 3 "$jdk_url.sha256.txt" -o "$download_dir/checksum.txt"
  curl --fail --location --retry 3 "$jdk_url" -o "$download_dir/$archive_name"
  (cd "$download_dir" && sha256sum --check checksum.txt)
  mkdir -p /workspace/.tools/jdk17
  tar -xzf "$download_dir/$archive_name" -C /workspace/.tools/jdk17 --strip-components=1
  rm -rf "$download_dir"
fi

# Trust the machine's existing system CAs, retaining TLS verification.
# The installed JDK is isolated under /workspace; system JDKs are untouched.
for cert in /usr/local/share/ca-certificates/*.crt; do
  [[ -f "$cert" ]] || continue
  alias_name="cloud-$(basename "$cert" .crt)"
  if ! /workspace/.tools/jdk17/bin/keytool -list -alias "$alias_name" -cacerts -storepass changeit >/dev/null 2>&1; then
    /workspace/.tools/jdk17/bin/keytool -importcert -noprompt -alias "$alias_name" -file "$cert" -cacerts -storepass changeit
  fi
done

if [[ ! -x /workspace/.tools/android/cmdline-tools/19.0/bin/sdkmanager ]]; then
  download_dir="$(mktemp -d /tmp/pixelhub-android.XXXXXX)"
  curl --fail --location --retry 3 https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip -o "$download_dir/tools.zip"
  # Published checksum from Google's repository2-1.xml for cmdline-tools;19.0.
  printf '%s  %s\n' 5fdcc763663eefb86a5b8879697aa6088b041e70 "$download_dir/tools.zip" | sha1sum --check -
  unzip -q "$download_dir/tools.zip" -d "$download_dir/unpacked"
  mkdir -p /workspace/.tools/android/cmdline-tools
  mv "$download_dir/unpacked/cmdline-tools" /workspace/.tools/android/cmdline-tools/19.0
  rm -rf "$download_dir"
fi
source "$repo_root/tool/cloud_env.sh"

# Gradle does not consume HTTPS_PROXY itself. Use proxy host/port only;
# do not persist credential values or edit tracked Gradle files.
python3 - <<'PY'
import os
from pathlib import Path
from urllib.parse import urlparse
proxy = urlparse(os.environ.get('HTTPS_PROXY', ''))
lines = ['org.gradle.workers.max=4', 'org.gradle.jvmargs=-Xmx3G -XX:MaxMetaspaceSize=1G']
if proxy.hostname:
    for protocol in ('https', 'http'):
        lines += [f'systemProp.{protocol}.proxyHost={proxy.hostname}', f'systemProp.{protocol}.proxyPort={proxy.port or 80}']
config = Path('/workspace/.cache/gradle/gradle.properties')
managed_keys = {line.split('=', 1)[0] for line in lines}
existing = config.read_text().splitlines() if config.exists() else []
retained = [line for line in existing if line.split('=', 1)[0] not in managed_keys]
config.write_text('\n'.join(retained + lines) + '\n')
PY

sdkmanager_path="$ANDROID_HOME/cmdline-tools/19.0/bin/sdkmanager"
set +o pipefail
yes | "$sdkmanager_path" --sdk_root="$ANDROID_HOME" --licenses > /workspace/.cache/android/licenses.log
license_status=${PIPESTATUS[1]}
set -o pipefail
if [[ "$license_status" -ne 0 ]]; then
  cat /workspace/.cache/android/licenses.log >&2
  exit "$license_status"
fi
"$sdkmanager_path" --sdk_root="$ANDROID_HOME" 'platform-tools' 'platforms;android-36' 'build-tools;35.0.0' 'ndk;27.0.12077973' 'cmake;3.22.1'
flutter precache --android --web
cd "$repo_root/apps/game"
flutter pub get --enforce-lockfile
for package in level_schema game_domain persistence design_system painting_engine; do
  cd "$repo_root/packages/$package"
  flutter pub get
done
cd "$repo_root/tool/browser"
npm ci --cache /workspace/.cache/npm
