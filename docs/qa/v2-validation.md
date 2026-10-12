# V2 validation — 2026-10-12

V2 and the requested bilingual/manual-APK changes were validated in the cloud working tree. This report describes local checks; it does not claim a GitHub run, public deployment or physical-device acceptance.

| Check | Result |
|---|---|
| `bash tool/validate.sh` | Passed: formatting, app + five package analyses, **33 unit/widget tests** |
| Release Web build | Passed, `/Pixelhub/` base, local CanvasKit/fonts |
| Explicit local Android release build | Passed, internal APK approximately 48.1 MB; never invoked by automatic CI |
| APK signature check | Passed, v2 scheme, one signer |
| Real Chromium suite | Passed: default Persian with English browser locale, English/FA restore, stroke interpolation, wrong color, Undo, confirmed/canceled Reset, full completion, page recreation/refresh, browser history, painting on 32/64/128 grids, zoom/pan, desktop bounds and short height |
| Browser network/runtime | No page errors, failed asset requests or runtime CDN requests |
| `actionlint`, shell syntax, staged/diff whitespace | Passed |

The tests also cover bitset identity/count validation, checksum/schema rejection, immutable snapshots, corrupt-progress preservation, write failure/retry, old-save/reset ordering, random count invariants, canceled pinch, inverse zoom hit testing, language direction, system Back and completion state isolation between deep-linked pictures.

APK: `apps/game/build/app/outputs/flutter-apk/app-release.apk`.
SHA-256: `f9575ab7b04f74b778e71d3cab5e63db609cf5cbbab986f0094d5e23b23b36f6`.

## Evidence

- [Persian Home](images/v2-home-fa.png)
- [English Home](images/v2-home-en.png)
- [English numbered painting](images/v2-painting-en.png)
- [Completed picture](images/v2-completion-en.png)
- [128 grid at zoom](images/v2-planet-zoom.png)

These are real Chromium screenshots of the release build. The browser test uses actual localStorage and creates a fresh Flutter application in a new page while retaining that storage.

## Domain timing

Command from repo root:

```bash
source tool/cloud_env.sh
dart --suppress-analytics --packages=apps/game/.dart_tool/package_config.json tool/benchmark.dart
```

One recorded cloud Linux/Dart VM run used 5 warmups and 20 measured 128×128 runs. Median checksum/parse: **1.691 ms**. Median complete painting across all colors/rows: **0.950 ms**. Every run asserted all 16,384 cells were complete. These are domain timings, not rendering FPS or a phone benchmark. Chromium zoom/pan was functionally exercised; quantitative real-device render profiling remains pending.

## Remaining acceptance

- Run the new workflows on GitHub and confirm Pages deployment. Only the separate Android workflow can produce an APK, and only after manual dispatch.
- Download/install the manual artifact on a real Android device. Confirm exact progress after acknowledged saves and process termination, touch/pinch, cutouts/rotation and rendering performance using the [manual checklist](v2-manual-checklist.md).
- Async native storage only guarantees acknowledged saves. Browser/app data deletion or eviction removes local progress. There is no cloud sync and no persisted Undo history or zoom.
- Shared Flutter UI does not by itself prove physical Android behavior. GitHub/public release and fresh cloud restoration must be verified separately.
