# Pixelhub

Pixelhub is a shared Flutter pixel-coloring game for Android and Web. V3 adds a local gallery, private photo conversion, PNG export and **Persian/English UI, with Persian as the default**. The layout fills phone, tablet and Web viewports; gallery cards adapt to available width.

## Play and language

Pick one of 49 bundled pictures across all seven public categories (at least four in each), then **Start / resume coloring**. Nine of the pictures are new original pixel-art interpretations of famous paintings, Iranian landmarks and a traditional Shamsa ornament; they are included with the app and do **not** require downloading online picture packs. Choose a numbered color and tap or drag over matching cells. A fast stroke fills the intervening matching cells. Wrong colors never count.

Use **Move / zoom** to pan, pinch with two fingers to zoom, or use the zoom/fit buttons. Pinching does not paint. Undo history is no longer retained in the painting engine; Reset still requires confirmation. An in-progress touch stroke can still be cancelled to avoid accidental multi-touch marks. The engine keeps internal reversible stroke tracking for gesture cancellation and backward compatibility. A completion screen appears after every cell is colored, including background color 1.

**Player-facing currency:** Only earned coins are displayed in Home, Gallery and Profile; completion and artwork details describe rewards only in coins. Coins pay for picture unlocks and optional precision tools. The earlier `totalPoints` counter is kept in the persisted library for compatibility and possible future progression features, but it is not presented as a second currency. Completing each distinct artwork still grants its reward only once. Current balancing is unchanged: easy/medium/hard paintings give 40/75/125 coins and cost 20–35/45–65/80–120 coins to unlock, while Magic Wand/Color Splash cost 12/6. The free starter sunflower, free personally imported art, 120 starting coins, and free Hint/Bomb help prevent forced spending. No migration or reset is required.

**Precision coloring tools (local coin economy):** Select Magic Wand (12 coins) or Color Splash (6 coins), then tap an unfinished cell of the currently selected palette color. Magic Wand fills every unfinished cell in its 4-connected same-color region (completed cells can bridge a region); Color Splash fills up to nine matching unfinished cells in the 3×3 area around the tap. A wrong-color or already-finished region never charges coins. The wallet debit is persisted before painting changes; storage errors prevent the action, and progress uses the existing autosave/retry system. Dragging does not activate a paid tool, and tap the tool a second time to exit target mode. Hint and Bomb remain free. Earn coins by completing paintings; there are no real-money purchases.

Use **English** / **فارسی** in the header to switch language. Text, direction, numbers, image titles and dialogs update together; the choice is remembered. A fresh installation starts in Persian regardless of the device/browser language.

**Four playable museum designs:** The four concept proposals (Cozy Classic Gallery, Royal Emerald Gallery, Soft Sky Minimal Museum and Botanical Pixel Gallery) are available as selectable, locally rendered room themes. Open **My Museum → Museum designs** to see four pixel miniature previews and apply one. Classic adds brass ornaments, Royal uses emerald walls and gilded trim, Sky features a skylight and a light rug, and Botanical adds growing vines and an olive-green rug. All themes keep the six real completed-artwork slots, existing animations, artwork IDs, cat and room arrangement; a theme preset changes its default wall and frame only, and both can still be customized separately. The selected theme is an optional field in the existing version-one museum preference document, so existing saved museums load as Classic without migration or data loss. Scenes and previews are generated with pixel CustomPainters rather than rasterizing full promotional screenshots containing fake artworks or UI, and require no network downloads or new binary assets. Automated tests for selection and persistence have been authored but not manually executed in this development session.

**High-detail museum visuals:** The room uses a procedural **128×172** logical pixel grid (up from 64×86), with newly drawn wall masonry, recessed molding, stepped spotlight beams, carved skirting, woodgrain, geometric carpet, upholstered bench, planters and finer frame trims. The finished artwork thumbnails retain their own nearest-neighbor pixel style. A more legible sleeping cat is overlaid on the bench as a new, independently redrawn 104×56 pixel sprite (2× the former cat resolution), with smaller fur pixels, cat-shaped ears, closed eyes, whiskers, tabby stripes and detailed paws: its body is static, while only the tail's independent paint layer switches between three discrete poses on a slow 4.4-second loop. The cat's timer is disposed on navigation and respects reduced-motion preferences. The museum remains fully local with no new image downloads or persisted schema changes. Automated tests for the sprite and room were authored but not run manually in this development session.

**My Museum (offline pixel gallery):** The Home page now links to a new `/museum` screen. Its 2D room, wooden floor, lights, rug, frames and plants are drawn as crisp pixel blocks by Flutter CustomPainter, with no 3D engine or downloaded background. Tap one of six slots and choose only from completed, currently available pictures (including personal and downloaded artworks); tap again to replace or remove it. The artwork picker groups already-hung paintings separately from available pictures, labels their wall slot in Persian and English, and uses distinct status highlighting and icons; Selecting an artwork already hung in another slot moves it instead of cloning it; long-press a hung picture to view its completed preview and optional animation. The room offers three frame finishes (wood, gold, dark), three wall palettes (cream, blue, sage), and two arrangements (regular, staggered), all free for the first release. Completion has a direct **Add to museum** action that opens the room with the just-completed picture selected for manual slot placement. The layout is a separate compact, versioned, serialized local preference `pixelhub.museum.v1`, storing IDs and decor choices only, not image bytes or personal originals. Removed/incomplete paintings do not render even if their old slot IDs remain in the record. Clear PixelHub data also clears the museum. This source implementation has not been manually built or tested yet.

The Home screen features **one artwork card**, showing the most recently opened painting (including completed pictures and downloaded/personal art while available). Its progress and action label follow the saved state. New installs or unavailable/deleted recent pictures fall back to the bundled sunflower; the old second Continue card has been removed. The recent artwork ID persists locally across app restarts.

Progress is autosaved per picture/version: Android DataStore via SharedPreferencesAsync, or browser localStorage. Wait for **Saved** before closing; pending/failed writes are shown with retry. Interrupted writes can only guarantee the last acknowledged save. Browser/app data deletion or storage eviction removes local progress; there is no cloud backup or account yet. Viewport zoom is not persisted across process restarts.

## Gallery, photos and export

Open **Picture gallery** to browse categories or search Persian/English titles. Picture details show a preview, progress and favorites. **My gallery** filters in-progress, completed, favorite and personal pictures. Existing V2 progress stays in its original versioned records.

Choose **Import a photo**, then a local JPEG, PNG or WebP. Still images only, at most 12 MiB, 12 million pixels and 6000 pixels per side. Orientation is normalized; use square crop positioning and 90-degree rotation, choose easy/normal/hard (32/64/128 grids), adjust the maximum colors (2–24), then create a preview. Changes invalidate the preview. **Save and color** persists the converted grid before starting a game.

Photos are processed on this device. Original photos, file names and location metadata are not stored or uploaded. You can retain up to 20 personal pictures within a 2 MiB library document limit; storage failures are reported. Native processing uses an isolate; Web processing can briefly pause the UI. Names are user-provided, with a bilingual fallback. Personal artworks can be resumed, favorited or deleted with confirmation.

Completed pictures offer **Export PNG / share**: Android opens its share sheet, Web downloads a crisp PNG, at most 1024 pixels on its longest side. **Settings** includes About, offline readiness/retry and confirmed clearing of Pixelhub progress, private pictures, favorites and language. Unrelated preferences and bundled pictures are preserved.

Android's bundled catalog works without a content server. On the production Web artifact, wait for Settings' offline-ready message before relying on offline reopening; the first visit needs connectivity. A service worker caches only public app resources, fonts, CanvasKit and levels. Updates activate after previous tabs close. Private browsing, browser policy, quota or eviction can prevent offline availability. The development server lacks the generated offline manifest. This new behavior is implemented but has not been validated in this session.

## Optional online pictures (GitHub Releases)

The gallery now checks a public online catalog on entry. Users see new pictures
and explicitly choose which numbered-image JSON files to download; downloaded
levels are stored separately from personal photo conversions and then play
offline. The initial demo is a 24×24 hot-air balloon.

**Distribution:** only GitHub Releases in this same repository store remote
level files; `git clone` does not fetch those release assets. The Pages publish
workflow mirrors validated Release packs as `/Pixelhub/online/` content. A
successful Web CI and Pages run are required before the initial balloon becomes
public. No sample image binaries are checked into `main`.

Instructions for adding more pictures: [Online content publishing](docs/online-content.md).
Published assets and live download behavior have not been manually validated in
this development session; check GitHub Actions and the Pages catalog before
claiming the sample is publicly available.

## V4 development status

The next roadmap stage is account-based progress synchronization. A pure conflict-resolution contract now lives in `packages/game_domain/lib/progress_sync.dart` (ADR 0004): disjoint completed cells merge within the same server reset generation, while a Reset invalidates older-generation writes. This is **domain groundwork only**, not an online feature. The [backend contract files](backend/README.md) now include a draft OpenAPI document and unexecuted PostgreSQL migration with an idempotency ledger schema. A separate account-scoped durable FIFO outbox now persists queued operations on Android/Web, but no UI or network adapter uses it yet. Auth, a running API, network sync, guest migration, account deletion and cross-device verification are still pending. Personal photo originals remain local.

## GitHub Actions: automatic Web, manual Android

- **[Checks and Web artifacts](https://github.com/abolfazl2600/Pixelhub/actions/workflows/ci.yml)** runs formatting, package analysis, unit/widget tests, Web build and browser checks automatically on PRs, main pushes and version tags. **It does not build an APK.**
- **[Build Android (manual)](https://github.com/abolfazl2600/Pixelhub/actions/workflows/android-build.yml)** only runs by `workflow_dispatch`. Select `play-aab` (the default) for a signed release AAB with a post-build signature check, or explicitly select `preview-apk` for a debug-signed test APK. Both use **private GitHub Secrets** only for the signed build. Choose the exact commit SHA/tag in `ref` when necessary. The upload key is not stored in the repository. See [Google Play setup](docs/play/PLAY_CONSOLE_SUBMISSION.md).
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

The browser suite covers both languages, real localStorage writes, wrong-color rejection, fast strokes, Reset/completion, application recreation and refresh, history, large-grid zoom/pan and viewport constraints. Build resources/fonts are local; Web first download needs connectivity; V3 adds versioned public-resource caching for offline reopening once Settings reports readiness.

## Boundaries and evidence

- `packages/level_schema`: schema 2, immutable levels and canonical SHA-256 validation.
- `packages/game_domain`: versioned progress bitsets and repository ports.
- `packages/painting_engine`: shared pure Dart stroke/interpolation/completion engine; no Undo history.
- `packages/persistence`: bundled catalog and platform storage adapters.
- `packages/design_system`: shared tokens, theme and mobile frame.
- `apps/game`: localization, state, renderer and screens.

[V3 decisions](docs/adr/0003-v3-private-gallery-and-import.md) · [V3 pending acceptance](docs/qa/v3-manual-checklist.md) · [Product plan](docs/product-plan/README.md) · [V2 decisions](docs/adr/0002-v2-painting-and-localization.md) · [V2 validation](docs/qa/v2-validation.md) · [Manual checklist](docs/qa/v2-manual-checklist.md) · [Asset provenance](apps/game/assets/README.md) · [Changelog](CHANGELOG.md).

The original V3 bundle had no online gallery; the new optional release-backed online gallery is added in source. Accounts/sync, ads, purchases and community are still inactive. V3 has not been tested or built locally under the owner’s workflow; no CI, public deployment, offline or physical-phone result is claimed. Prior V2 validation applies to its historical implementation only.
