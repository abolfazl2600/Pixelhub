# Pixelhub

Pixelhub is a shared Flutter pixel-coloring game for Android and Web. V2 adds a playable numbered canvas, local progress and **Persian/English UI, with Persian as the default**. Desktop browsers keep the same centered mobile frame, at most 430 logical pixels wide.

## Play and language

Pick one of ten original bundled pictures, then **Start / resume coloring**. Choose a numbered color and tap or drag over matching cells. A fast stroke fills the intervening matching cells. Wrong colors never count.

Use **Move / zoom** to pan, pinch with two fingers to zoom, or use the zoom/fit buttons. Pinching does not paint. Undo reverts a whole stroke, with up to 50 recent strokes retained during the current session. Reset requires confirmation. A completion screen appears after every cell is colored, including background color 1.

Use **English** / **فارسی** in the header to switch language. Text, direction, numbers, image titles and dialogs update together; the choice is remembered. A fresh installation starts in Persian regardless of the device/browser language.

Progress is autosaved per picture/version: Android DataStore via SharedPreferencesAsync, or browser localStorage. Wait for **Saved** before closing; pending/failed writes are shown with retry. Interrupted writes can only guarantee the last acknowledged save. Browser/app data deletion or storage eviction removes local progress; there is no cloud backup or account yet. Undo history and viewport zoom are not persisted across process restarts.

## GitHub Actions: automatic Web, manual Android

- **[Checks and Web artifacts](https://github.com/abolfazl2600/Pixelhub/actions/workflows/ci.yml)** runs formatting, package analysis, unit/widget tests, Web build and browser checks automatically on PRs, main pushes and version tags. **It does not build an APK.**
- **[Build Android APK (manual)](https://github.com/abolfazl2600/Pixelhub/actions/workflows/android-build.yml)** has only `workflow_dispatch`. Open it in Actions, choose **Run workflow**, select your branch, optionally enter an exact commit SHA/tag in `ref`, and run. Download `pixelhub-apk-v<VERSION>-<SHA>` from that run's **Artifacts**, extract the ZIP and install `app-release.apk` on Android. The optional `ref` lets you match a particular Web commit; the artifact includes the actual source `commit.txt`.
- **Publish verified Web artifact** deploys the exact Web artifact after a successful main Web CI run. In **Settings → Pages → Build and deployment**, select **GitHub Actions**. No PR artifact is published.

Expected Pages address: **https://abolfazl2600.github.io/Pixelhub/**. Check Actions for actual deployment status. Painting deep links use `#/painting/sunflower` (or another picture ID); static-host refresh works with hash routes.

The internal APK uses Android debug signing, is not a Play Store submission and needs no production signing secret. Android 7.0 / API 24 or newer is required. Nothing triggers an Android build automatically in the current workflows.

## Development

Pinned tools: Flutter **3.35.7**, Dart **3.9.2**, JDK 17, Android API 36/build tools 35.0.0, NDK 27.0.12077973 and CMake 3.22.1. App and browser-tool lockfiles are committed. No app secrets or backend services are needed.

In this cloud machine:

```bash
cd /workspace/Pixelhub
bash tool/cloud_setup.sh       # install/refresh only when needed
source tool/cloud_env.sh
bash tool/validate.sh
bash tool/run_web_cloud.sh 8081
```

The Web launcher has an isolated Flutter configuration to avoid ADB discovery against the read-only cloud home. Normal Android builds remain enabled. It serves CanvasKit locally. Tools/caches live under `/workspace/.tools` and `/workspace/.cache`; use the existing isolated checkout, without creating a worktree.

On another host, install the pinned SDKs, add Flutter to PATH, run `bash tool/validate.sh`, then `flutter run -d chrome` or `flutter run -d web-server --no-web-resources-cdn` from `apps/game`. Flutter generates localization classes from `apps/game/lib/l10n/app_fa.arb` and `app_en.arb` during dependency/build preparation; generated classes are ignored. Use `flutter gen-l10n` after editing translations.

```bash
# From the repository root:
bash tool/build_web.sh
# Android is also an explicit local command, never part of validate.sh:
cd apps/game
flutter build apk --release --no-pub
```

Outputs: `apps/game/build/web/` and `apps/game/build/app/outputs/flutter-apk/app-release.apk`.

To test the production Web build under its `/Pixelhub/` base path:

```bash
cd /workspace/Pixelhub/apps/game
ln -sfn web build/Pixelhub
python3 -m http.server 8080 --bind 127.0.0.1 --directory build
```

From another shell:

```bash
cd /workspace/Pixelhub/tool/browser
npm ci
npx playwright install chromium
npm test
# This cloud machine already has Chromium:
CHROMIUM_PATH=/usr/bin/chromium npm test
```

The browser suite covers both languages, real localStorage writes, wrong-color rejection, fast strokes, Undo/Reset/completion, application recreation and refresh, history, large-grid zoom/pan and viewport constraints. Build resources/fonts are local; Web first download needs connectivity and offline browser reopening is not promised.

## Boundaries and evidence

- `packages/level_schema`: schema 2, immutable levels and canonical SHA-256 validation.
- `packages/game_domain`: versioned progress bitsets and repository ports.
- `packages/painting_engine`: shared pure Dart stroke/undo/completion engine.
- `packages/persistence`: bundled catalog and platform storage adapters.
- `packages/design_system`: shared tokens, theme and mobile frame.
- `apps/game`: localization, state, renderer and screens.

[Product plan](docs/product-plan/README.md) · [V2 decisions](docs/adr/0002-v2-painting-and-localization.md) · [V2 validation](docs/qa/v2-validation.md) · [Manual checklist](docs/qa/v2-manual-checklist.md) · [Asset provenance](apps/game/assets/README.md) · [Changelog](CHANGELOG.md).

V2 has no photo import, online gallery, accounts/sync, ads, purchases or community. Physical-phone behavior/performance and current public deployment need separate verification; cloud builds and tests do not establish those release gates.
