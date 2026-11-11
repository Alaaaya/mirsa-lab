#!/bin/bash
set -euo pipefail
SDK="${ANDROID_HOME:-/home/kit/android-sdk}"
TOOLS="$SDK/build-tools/35.0.0"
JAR="$SDK/platforms/android-36/android.jar"
cd "$(dirname "$0")"
mkdir -p build/classes
javac -source 8 -target 8 -bootclasspath "$JAR" -d build/classes MainActivity.java
"$TOOLS/d8" --lib "$JAR" --output build build/classes/dev/mirsa/lab/sample/*.class
"$TOOLS/aapt" package -f -M AndroidManifest.xml -I "$JAR" -F build/unsigned.apk
(cd build; zip -q unsigned.apk classes.dex)
keytool -genkeypair -keystore build/sample.keystore -storepass android -keypass android -alias lab -keyalg RSA -validity 365 -dname "CN=Mirsa Lab" -noprompt 2>/dev/null || test -f build/sample.keystore
"$TOOLS/zipalign" -f 4 build/unsigned.apk build/aligned.apk
"$TOOLS/apksigner" sign --ks build/sample.keystore --ks-pass pass:android --key-pass pass:android --out build/MirsaLab.apk build/aligned.apk
"$TOOLS/apksigner" verify build/MirsaLab.apk
