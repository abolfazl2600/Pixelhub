# ADR 0002: V2 painting, persistence and bilingual UI

Status: accepted. Date: 2026-10-12.

V2 implements the shared coloring engine and local sessions; the owner additionally requested English/Persian and manual-only Android builds. These requirements supersede the V1 combined automatic APK pipeline and provisional JSON-file storage proposal.

## Decisions

- Use Flutter ARB/gen-l10n for all application strings, with Persian on a fresh installation and an explicitly saved language choice. Locale does not follow OS defaults. Titles are bilingual in level data. Flutter owns RTL; host HTML stays LTR for correct canvas geometry, with its language attribute updated for accessibility.
- Schema 2 requires `titles`, `levelId`, `levelVersion`, opaque ARGB palette and a SHA-256. Hash the UTF-8 compact JSON array `[schemaVersion, levelId, levelVersion, titleFa, titleEn, width, height, paletteAsUppercase8DigitHex, cells]`. This fixed order avoids JSON-object key ordering differences. Palette index zero is a real background color and must be painted. Dimensions are capped at 256×256 and palettes at 48 colors.
- Keep the published V1 sunflower asset intact. V2 uses `sunflower-v2.json`, level version 2; new geometric fixtures have independent IDs/version 1. Assets and sessions are separate.
- `painting_engine` is pure Dart. Matching cells become completed monotonically within a stroke; Undo/canceled pinch remove that stroke. Fast input uses Bresenham interpolation. Undo retains 50 whole strokes; reset increments generation and revision.
- Paint mode uses one pointer; initial touch is deferred until movement/up. A second pointer cancels the pending stroke and switches to pinch without leaving painted cells. Move mode pans and never paints. InteractiveViewer supplies the transform/bounds; renderer hit testing uses its inverse. Numbers render when cells are large enough to read; high-zoom rendering culls invisible rows/columns and reuses labels per color per frame.
- Persist compact bitsets through `SharedPreferencesAsync` (Android DataStore, browser localStorage), not widget-level writes. The controller serializes writes and coalesces pending snapshots. An older save cannot overwrite a reset. Display saving/saved/error states; retry keeps the latest in-memory progress. Malformed or mismatched saved data is preserved until an explicit confirmed reset. Lifecycle changes request a flush. There is no guarantee for an unacknowledged write when the OS kills the process, nor against browser storage eviction.
- Restore progress via ID, version and level checksum. Undo history, selected palette and view transform are ephemeral. Language writes are separately ordered; a slow initial read cannot overwrite a user selection.
- Auto CI builds/tests Web only. The Android workflow has only `workflow_dispatch`, with an optional exact source ref and actual checked-out SHA/version in the artifact. Compare `commit.txt` with the Web artifact when a matching release is required.

Real-phone profiling and platform durability checks remain required before declaring the V2 release gate complete. Cloud/Chromium results are recorded separately.
