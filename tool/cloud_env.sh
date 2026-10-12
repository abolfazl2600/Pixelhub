#!/usr/bin/env bash
# Source this in each cloud shell. Processes and shell exports do not survive snapshots.
export PATH="/workspace/.tools/flutter/bin:/workspace/.tools/android/platform-tools:$PATH"
export JAVA_HOME=/workspace/.tools/jdk17
export ANDROID_HOME=/workspace/.tools/android
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_USER_HOME=/workspace/.cache/android
export GRADLE_USER_HOME=/workspace/.cache/gradle
export PUB_CACHE=/workspace/.cache/pub
export XDG_CONFIG_HOME=/workspace/.cache/config
export ANALYZER_STATE_LOCATION_OVERRIDE=/workspace/.cache/dart-analysis
# Prevent analytics from trying to write to the cloud machine's read-only home.
export CI=true
export CHROME_EXECUTABLE=/usr/bin/chromium
