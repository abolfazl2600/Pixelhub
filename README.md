# Pixelhub

Pixelhub is a shared Flutter pixel-coloring game for Android and Web. V3 adds a local gallery, private photo conversion, PNG export and **Persian/English UI, with Persian as the default**. Desktop browsers keep the same centered mobile frame, at most 430 logical pixels wide.

## Play and language

Pick one of 40 original bundled pictures, then **Start / resume coloring**. Choose a numbered color and tap or drag over matching cells. A fast stroke fills the intervening matching cells. Wrong colors never count.

Use **Move / zoom** to pan, pinch with two fingers to zoom, or use the zoom/fit buttons. Pinching does not paint. Undo reverts a whole stroke, with up to 50 recent strokes retained during the current session. Reset requires confirmation. A completion screen appears after every cell is colored, including background color 1.

Use **English** / **فارسی** in the header to switch language. Text, direction, numbers, image titles and dialogs update together; the choice is remembered. A fresh installation starts in Persian regardless of the device/browser language.

Progress is autosaved per picture/version: Android DataStore via SharedPreferencesAsync, or browser localStorage. Wait for **Saved** before closing; pending/failed writes are shown with retry. Interrupted writes can only guarantee the last acknowledged save. Browser/app data deletion or storage eviction removes local progress; there is no cloud backup or account yet. Undo history and viewport zoom are not persisted across process restarts.

## Gallery, photos and export

Open **Picture gallery** to browse categories or search Persian/English titles. Picture details show a preview, progress and favorites. **My gallery** filters in-progress, completed, favorite and personal pictures. Existing V2 progress stays in its original versioned records.

Choose **Import a photo**, then a local JPEG, PNG or WebP. Still images only, at most 12 MiB, 12 million pixels and 6000 pixels per side. Orientation is normalized; use square crop positioning and 90-degree rotation, choose easy/normal/hard (32/64/128 grids), adjust the maximum colors (2–24), then create a preview. Changes invalidate the preview. **Save and color** persists the converted grid before starting a game.

Photos are processed on this device. Original photos, file names and location metadata are not stored or uploaded. You can retain up to 20 personal pictures within a 2 MiB library document limit; storage failures are reported. Native processing uses an isolate; Web processing can briefly pause the UI. Names are user-provided, with a bilingual fallback. Personal artworks can be resumed, favorited or deleted with confirmation.

Completed pictures offer **Export PNG / share**: Android opens its share sheet, Web downloads a crisp PNG, at most 1024 pixels on its longest side. **Settings** includes About, offline readiness/retry and confirmed clearing of Pixelhub progress, private pictures, favorites and language. Unrelated preferences and bundled pictures are preserved.

Android's bundled catalog works without a content server. On the production Web artifact, wait for Settings' offline-ready message before relying on offline reopening; the first visit needs connectivity. A service worker caches only public app resources, fonts, CanvasKit and levels. Updates activate after previous tabs close. Private browsing, browser policy, quota or eviction can prevent offline availability. The development server lacks the generated offline manifest. This new behavior is implemented but has not been validated in this session.

## V4 development status

The next roadmap stage is account-based progress synchronization. A pure conflict-resolution contract now lives in `packages/game_domain/lib/progress_sync.dart` (ADR 0004): disjoint completed cells merge within the same server reset generation, while a Reset invalidates older-generation writes. This is **domain groundwork only**, not an online feature. The [backend contract files](backend/README.md) now include a draft OpenAPI document and unexecuted PostgreSQL migration with an idempotency ledger schema. A separate account-scoped durable FIFO outbox now persists queued operations on Android/Web, but no UI or network adapter uses it yet. Auth, a running API, network sync, guest migration, account deletion and cross-device verification are still pending. Personal photo originals remain local.

## GitHub Actions: automatic Web, manual Android

- **[Checks and Web artifacts](https://github.com/abolfazl2600/Pixelhub/actions/workflows/ci.yml)** runs formatting, package analysis, unit/widget tests, Web build and browser checks automatically on PRs, main pushes and version tags. **It does not build an APK.**
- **[Build Android (manual)](https://github.com/abolfazl2600/Pixelhub/actions/workflows/android-build.yml)** only runs by `workflow_dispatch`. Select `preview-apk` for a debug-signed test APK or `play-aab` for an AAB signed using **private GitHub Secrets**. Choose the exact commit SHA/tag in `ref` when necessary. The upload key is not stored in the repository. See [Google Play setup](docs/play/PLAY_CONSOLE_SUBMISSION.md).
- **Publish verified Web artifact** deploys the exact Web artifact after a successful main Web CI run. In **Settings → Pages → Build and deployment**, select **GitHub Actions**. No PR artifact is published.

Expected Pages address: **https://abolfazl2600.github.io/Pixelhub/**. Check Actions for actual deployment status. Painting deep links use `#/painting/sunflower` (or another picture ID); static-host refresh works with hash routes.

The preview APK uses Android debug signing and cannot be submitted to Google Play. The `play-aab` mode requires the owner's release upload key through GitHub Secrets and never falls back to debug signing. Android compile/target SDK is set to 36; compatibility and 16 KB native-library checks remain part of release QA. Nothing triggers an Android build automatically. A bilingual [privacy policy](https://abolfazl2600.github.io/Pixelhub/privacy.html) is stored under `apps/game/web/privacy.html` and shown in the app; public URL deployment needs verification.

## Development

The owner requests code development without local tests, automated analysis, browser checks or builds, and without waiting for CI. This is recorded in [AGENTS.md](AGENTS.md). The optional validation/build commands below are for a later explicit request; automatic Web CI remains in place.

Pinned tools: Flutter **3.35.7**, Dart **3.9.2**, JDK 17, Android API 36/build tools 35.0.0, NDK 27.0.12077973 and CMake 3.22.1. App and browser-tool lockfiles are committed. No app secrets or backend services are needed.

In this cloud machine:

```bash
cd /workspace/Pixelhub
bash tool/cloud_setup.sh       # install/refresh only when needed
source tool/cloud_env.sh
# Run tests/builds only when explicitly requested by the owner.
# Optional preview, when requested:
bash tool/run_web_cloud.sh 8081
```

The Web launcher has an isolated Flutter configuration to avoid ADB discovery against the read-only cloud home. Normal Android builds remain enabled. It serves CanvasKit locally. Tools/caches live under `/workspace/.tools` and `/workspace/.cache`; use the existing isolated checkout, without creating a worktree.

On another host, install the pinned SDKs, add Flutter to PATH, run `flutter pub get` in `apps/game`, then `flutter run -d chrome` or `flutter run -d web-server --no-web-resources-cdn` from `apps/game`. Flutter generates localization classes from `apps/game/lib/l10n/app_fa.arb` and `app_en.arb` during dependency/build preparation; generated classes are ignored. Use `flutter gen-l10n` after editing translations.

```bash
# From the repository root:
bash tool/build_web.sh
# Android is also an explicit local command, never part of validate.sh:
cd apps/game
flutter build apk --debug --no-pub  # local preview only
# For Play: configure private upload-key variables, then build appbundle --release
```

Outputs: `apps/game/build/web/`, debug preview `apps/game/build/app/outputs/flutter-apk/app-debug.apk`, and (only with signing credentials) release AAB `apps/game/build/app/outputs/bundle/release/app-release.aab`.

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

The browser suite covers both languages, real localStorage writes, wrong-color rejection, fast strokes, Undo/Reset/completion, application recreation and refresh, history, large-grid zoom/pan and viewport constraints. Build resources/fonts are local; Web first download needs connectivity; V3 adds versioned public-resource caching for offline reopening once Settings reports readiness.

## Boundaries and evidence

- `packages/level_schema`: schema 2, immutable levels and canonical SHA-256 validation.
- `packages/game_domain`: versioned progress bitsets and repository ports.
- `packages/painting_engine`: shared pure Dart stroke/undo/completion engine.
- `packages/persistence`: bundled catalog and platform storage adapters.
- `packages/design_system`: shared tokens, theme and mobile frame.
- `apps/game`: localization, state, renderer and screens.

[V3 decisions](docs/adr/0003-v3-private-gallery-and-import.md) · [V3 pending acceptance](docs/qa/v3-manual-checklist.md) · [Product plan](docs/product-plan/README.md) · [V2 decisions](docs/adr/0002-v2-painting-and-localization.md) · [V2 validation](docs/qa/v2-validation.md) · [Manual checklist](docs/qa/v2-manual-checklist.md) · [Asset provenance](apps/game/assets/README.md) · [Changelog](CHANGELOG.md).

V3 has no online gallery, accounts/sync, ads, purchases or community. V3 has not been tested or built locally under the owner’s workflow; no CI, public deployment, offline or physical-phone result is claimed. Prior V2 validation applies to its historical implementation only.
