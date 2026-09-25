#!/usr/bin/env bash
# setup_android.sh — Install Android SDK and build the Kotlin app.

set -euo pipefail

echo "=== LinkBridge Android Setup ==="

ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
GRADLE_VERSION="${GRADLE_VERSION:-8.5}"

echo "ANDROID_HOME=$ANDROID_HOME"

# Check for Java
if ! command -v java >/dev/null 2>&1; then
    echo "ERROR: Java not found. Install JDK 17+."
    exit 1
fi

echo "Using: $(java -version 2>&1 | head -1)"

echo ""
echo "=== Build app ==="
cd android
./gradlew assembleDebug
echo ""
echo "APK located at: app/build/outputs/apk/debug/app-debug.apk"
