# Android package size investigation — PixelHub

## Evidence available

- Previous successful **manual preview-apk** GitHub Actions run:
  [38305453410](https://github.com/abolfazl2600/Pixelhub/actions/runs/38305453410).
- The archived GitHub Actions artifact containing `app-debug.apk` and
  `commit.txt` is **77,807,919 bytes** as a ZIP download (about **74.2 MiB**).
  This is the **archive size, not a verified per-device Play download**.
- `preview-apk` runs `flutter build apk --debug --no-pub`. Debug Flutter
  builds ship additional runtime/development components, and the fat APK can
  contain native libraries for multiple CPU architectures. It is **not**
  an appropriate size proxy for the Play Store release.
- Bundled JSON catalog (40 levels) is small, fonts together are around
  730 KB in source, and the original launcher asset is under 50 KB;
  these do **not** plausibly explain a roughly 74 MiB debug archive.
  The likely size contributors are Flutter engine/native libraries,
  Flutter/Dart debug-mode payloads, and architecture duplication.

## Get exact, release-relevant measurements

The separate, **manually dispatched** `android-build.yml` workflow now
prints package byte size, twelve largest compressed ZIP entries and
compressed native-library bytes grouped by ABI in a step called
**Print Android package size breakdown**. It requires a new owner-requested
Android run; old artifacts do not include this output.

- For Play, select `build_kind: play-aab`, which builds an upload-key-signed
  `flutter build appbundle --release --no-pub` (requires private secrets).
- Android App Bundles let Google Play deliver architecture-specific packages
  instead of making each device download every ABI in a fat APK.
- Compare the estimated download size in **Play Console → App bundle explorer**,
  not the on-disk size of the GitHub Actions artifact ZIP.
- Optionally, during **explicit manual local Android QA**, run
  `flutter build apk --release --split-per-abi` with an appropriate signing
  configuration to estimate per-ABI standalone APK sizes.
- Inspect `lib/arm64-v8a/`, `lib/armeabi-v7a/`, `lib/x86_64/`, bundled
  `assets/flutter_assets/`, and snapshot libraries separately.
- Prioritize image, font, and asset trimming only if release measurements
  identify those as significant. Never remove native ABIs solely to
  optimize a single debug APK, since it would break other devices.
- This repository has not performed an Android release build or
  analyzed a signed production AAB in this source-editing session.

## Android QA still needed

Manually verify small/large phones, portrait and landscape tablets, touch
painting, pinch-to-zoom, safe insets, 16 KB page-size support, and the
release AAB in Google Play's pre-launch checks. Web CI is not evidence
that native Flutter layout and distribution passed physical-device QA.
