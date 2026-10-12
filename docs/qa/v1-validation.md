# V1 validation — 2026-10-12

V1 implementation is validated in the current cloud machine. The public release gate remains pending GitHub CI/Pages and real Android device acceptance.

## Source and toolchain

The local checks were performed on the V1 implementation before committing, based on `c4770d7e8e7621a795a8c0332916330c446a77e4`. These results describe the source included with this report; they are not GitHub Actions results. CI is configured to build both platforms from the same checkout SHA and include `commit.txt` in both artifacts.

Linux x86_64; Flutter 3.35.7 (`adc901062556672b4138e18a4dc62a4be8f4b3c2`), Dart 3.9.2, Temurin JDK 17.0.20.1+1, Android API 36, build tools 35.0.0, NDK 27.0.12077973 and CMake 3.22.1. Android SDK licenses were accepted. Installation kept TLS/checksum validation and used the machine's existing proxy and trusted CA certificates.

## Completed checks

| Check | Result |
|---|---|
| `bash tool/cloud_setup.sh` | Passed, including repeated setup and dependency installation |
| `bash tool/validate.sh` | Passed: formatting, analysis of app + 4 shared packages, **16 tests** |
| `bash tool/build_web.sh` | Passed: release Web with `/Pixelhub/`, bundled renderer/fonts |
| `flutter build apk --release --no-pub` | Passed: internal APK, approximately 45.1 MB |
| Android `apksigner verify --verbose` | Passed, APK Signature Scheme v2, one signer |
| Android manifest inspection | Package `io.github.abolfazl2600.pixelhub`, version `0.1.0+1`, minimum API 24, target API 36 |
| `CHROMIUM_PATH=/usr/bin/chromium npm test` in `tool/browser` | Passed: buttons, browser Back/Forward, hash refresh, desktop bounds, short-height scroll; no page errors, failed requests or runtime CDN requests |
| `bash tool/run_web_cloud.sh 8081` + the same browser suite with its base URL | Passed: development server, navigation/history, refresh and layouts; local-only resources, no page errors |
| `actionlint` 1.7.7 | Passed for both workflows |
| Shell syntax and `git diff --check` | Passed |

The 16 tests exercise loading/error/retry, stale request protection, disposal during load, real bundled fixture parsing, invalid schema rejection, RTL, button and system Back navigation, deep links, unknown-route recovery, widths 360/390/430, desktop centering, short landscape height, safe insets and 150% text scale. No painting test is claimed in V1.

APK output: `apps/game/build/app/outputs/flutter-apk/app-release.apk`.

SHA-256: `e0bb30ef90b176cc22912cbc6fb6ac93c5c011fa6b2f3e8253be3f7551edbbec`.

Web output: `apps/game/build/web/`. Build outputs and development caches are ignored rather than committed.

## Browser evidence

Real Chromium screenshots of the release build:

- [Home, 390 × 844](images/v1-home-mobile.png)
- [Read-only preview, 390 × 844](images/v1-preview-mobile.png)
- [Home, 1440 × 900 with centered mobile frame](images/v1-home-desktop.png)

The browser test also exercises 800 × 360. The Flutter host HTML uses LTR DOM geometry while Flutter provides Persian RTL; the refresh/bounds test guards against offscreen rendering caused by inherited host RTL.

## Outstanding release acceptance

- GitHub workflows have been linted and their build/test commands run locally; no GitHub Actions run is claimed before these changes are pushed.
- Pages source/permissions and successful public deployment are not verified. The anticipated Pages address is not evidence of a live app.
- APK download from Actions and installation/appearance on a physical phone are not verified. Use the [manual checklist](v1-manual-checklist.md).
- Desktop Linux builds and Android Studio are outside this Android/Web workflow. There is no attached Android device. ADB's default home preferences are unwritable here; the cloud Web launcher uses a separate configuration to avoid device discovery, while APK builds remain enabled.
- V1 is a read-only technical preview. Painting, durable progress, import, backend, accounts and monetization remain in later milestones. Browser first download needs connectivity; offline reopening is not promised.

Reusable dependency setup and startup instructions are saved for cloud configuration review; publication and restoration in a new cloud task must be verified separately.
