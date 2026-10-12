# Changelog

## 0.2.0 — playable local demo

- Persian/English UI, default Persian, saved language selection, translated titles/digits and RTL/LTR layout.
- Manual-only Android Actions workflow with optional exact ref; automatic CI/Pages builds Web only.
- Checksummed schema 2 and ten original local pictures, including 32/64/128 grids; V1 fixture preserved.
- Matching-color tap/fast strokes, numbered grid, highlight/counts, pinch/pan/zoom, stroke Undo, confirmed Reset and completion screen.
- Per-picture/version bitset autosaves, restore, failure/retry and generation-safe ordered writes through Android DataStore/browser localStorage.
- Domain, persistence, language, gesture and real-browser regression coverage. Physical-device profiling remains outstanding.

## 0.1.0 — V1 technical preview (implementation; release gate pending)

- Shared Flutter Android/Web application with Persian RTL, bundled fonts, tokens and a centered mobile frame capped at 430 logical pixels.
- Asset bootstrap, loading/error/retry, Home and a read-only painting placeholder with an original sunflower fixture and numbered palette.
- Pure Dart schema/domain ports and asset/design packages; state and storage ADR.
- Automated bootstrap, fixture, navigation, viewport, short-height, safe-inset and larger-text tests.
- Pinned Flutter/app dependencies; CI validation and same-commit Web/internal APK artifacts. Pages deploys the verified Web artifact after successful main CI.
- Issue/PR templates, development helpers and manual acceptance checklist.

No painting or progress persistence yet. GitHub CI, public Pages publication and physical Android testing must be recorded before marking the V1 release gate complete.
