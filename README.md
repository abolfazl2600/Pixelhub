# Pixelhub

Pixelhub is an Android-first, mobile-style Web pixel-coloring game in development.

> **Current status:** V1 technical preview implemented in `apps/game`: Persian Home, local sunflower fixture and a read-only painting preview. Web and internal Android APK builds are available locally. Public Pages deployment, GitHub CI results and physical-device acceptance still need verification. The coloring engine starts in V2; there is no backend yet.

## Develop and test V1

Use **Flutter 3.35.7 / Dart 3.9.2**, JDK 17 and Android SDK (API 36, build tools 35.0.0, NDK 27.0.12077973, CMake 3.22.1). Android minimum is API 24. Flutter and CI pins must be updated together. The application lockfile is committed.

From an already prepared Linux cloud machine:

```bash
cd /workspace/Pixelhub
source tool/cloud_env.sh
bash tool/validate.sh
bash tool/run_web_cloud.sh 8080
```

To prepare or refresh this cloud machine, run `bash tool/cloud_setup.sh` first. Tools and caches live outside the checkout under `/workspace/.tools` and `/workspace/.cache`; no Git worktree is needed. This helper uses the environment's existing HTTPS proxy and system CA trust. Required destinations are GitHub release/Git hosts, `storage.googleapis.com`, `pub.dev`, `dl.google.com`, Gradle and Maven repositories. There are no app secrets or runtime API variables in V1.

On another machine, install the pinned Flutter and Android toolchains, add Flutter to PATH, and run `bash tool/validate.sh` from the repo. The cloud-specific environment helper is optional there.

The cloud Web launcher uses a separate Flutter configuration profile to avoid ADB device discovery against this machine's read-only home. Android builds use the normal profile and remain enabled. On a normal development host, use `flutter run -d chrome` or `flutter run -d web-server` from `apps/game`.

```bash
# From repository root:
bash tool/build_web.sh
cd apps/game
flutter build apk --release --no-pub
```

Web output: `apps/game/build/web/`. Internal APK: `apps/game/build/app/outputs/flutter-apk/app-release.apk`. The APK uses a debug signing key and is for internal testing, not Play Store submission. There is no production keystore.

The production Web build uses `/Pixelhub/` as its base path. To test that build locally, serve it under that path rather than opening the HTML as a file:

```bash
cd /workspace/Pixelhub/apps/game
ln -sfn web build/Pixelhub
python3 -m http.server 8080 --bind 127.0.0.1 --directory build
```

Home is `/Pixelhub/` and preview is `/Pixelhub/#/painting`. Hash routes survive static-host refresh. The Web build bundles CanvasKit and fonts; first download needs connectivity, and V1 does not promise offline browser reopening or progress persistence.

## CI, Pages and APK artifacts

`.github/workflows/ci.yml` checks formatting, analyzes the application and shared packages, and runs tests. Web and APK jobs build the same checked-out commit and upload `pixelhub-web-v0.1.0-<SHA>` / `pixelhub-apk-v0.1.0-<SHA>` artifacts with `commit.txt`. It runs for PRs, main pushes, version tags and manual dispatches.

`web-pages.yml` downloads that exact Web artifact after a successful main CI run. It never rebuilds a different commit or deploys PR artifacts. In GitHub **Settings → Pages → Build and deployment**, select **GitHub Actions**, then push the implementation through your normal PR workflow. Deployment requires Pages permissions and the `github-pages` environment. CI/APK build needs no signing secret.

- [CI runs and downloadable APK/Web artifacts](https://github.com/abolfazl2600/Pixelhub/actions/workflows/ci.yml) — after these workflows reach GitHub.
- [Expected Pages address](https://abolfazl2600.github.io/Pixelhub/) — availability is unverified until deployment succeeds.
- [V1 architecture decisions](docs/adr/0001-v1-foundation.md)
- [Manual device/browser checklist](docs/qa/v1-manual-checklist.md)
- [Cloud validation evidence and remaining gates](docs/qa/v1-validation.md)
- [Changelog](CHANGELOG.md)

## Implemented boundaries

`packages/level_schema` and `packages/game_domain` contain pure Dart contracts. `packages/persistence` reads the bundled fixture, and `packages/design_system` owns the shared theme and mobile frame. Features and bootstrap state are in `apps/game/lib`. The desktop browser uses the same one-column mobile UI, capped at 430 logical pixels.

Known limitations: read-only preview; no painting, saves, image import, accounts, payments or backend. Physical Android acceptance and public deployment remain outstanding. Assets and font licenses are documented in [asset provenance](apps/game/assets/README.md).

## Browser regression check

After serving the production build under `/Pixelhub/`, run:

```bash
cd tool/browser
npm ci
npx playwright install chromium
npm test
```

In this cloud machine, Chromium is already installed: use `CHROMIUM_PATH=/usr/bin/chromium npm test` after `npm ci`. The check exercises real rendering, button and browser history navigation, hash refresh, short-height scrolling, centered desktop controls and local-only asset requests. CI runs it before uploading Web artifacts. Screenshots go to ignored `tool/browser/artifacts/`.

## Product and development roadmap (فارسی)

**[Open the complete project production plan: docs/product-plan/README.md](./docs/product-plan/README.md)**

The plan covers seven explicitly scoped versions (V1–V7), their included/excluded features, acceptance criteria, design rules, Android/Web architecture, data models, CI/CD, security, operational content production, and future scaling.

## Core decisions
- Flutter/Dart, shared Android & Web codebase.
- On desktop browsers, render the **same mobile UI** centered; no separate desktop-responsive design.
- GitHub Actions for automated Web and Android builds; GitHub Pages for static Web hosting when configured.
- Offline-first painting; accounts/Cloud Sync introduced progressively.
- Production Backend, billing and public community are implemented only in their planned milestones.

## Version map
| Milestone | Target release | Scope |
|---|---|---|
| V1 | v0.1.0 | App scaffold + CI, Pages, Android APK |
| V2 | v0.2.0 | Core coloring engine + local progress |
| V3 | v0.3.0 | Gallery + personal photo to Pixel Art |
| V4 | v0.4.0 | Accounts, backend and cross-device sync |
| V5 | v0.5.0 | Content admin, cloud catalog and CDN |
| V6 | v1.0.0 | Public release, optional ads and commerce |
| V7 | v1.1.0 | Moderated community and scale |

**Start here:** [Project plan index](./docs/product-plan/README.md).
