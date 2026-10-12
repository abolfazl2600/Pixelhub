## V6 early local UX and tools groundwork (unreleased)

- Added functional, locally free Hint highlighting and Bomb filling up to five matching cells as one undoable action. No coins, wallet consumption or purchases.
- Added Guest Profile with local completion/favorite counts, disabled inventory/coins with "Coming soon" messaging in Persian and English.
- Home and Gallery surface local completion progress, profile navigation and filter result counts.
- Added ephemeral on-device aggregate session diagnostics (screen opens, tool use, completion, framework error counts and catalog-load timing). Remote crash reporting and retention analytics stay disabled pending provider, consent and privacy review.
- Added source-level regression cases for local tools. No tests or builds were run locally under project development policy.

# Changelog

## Unreleased — V4 progress-sync domain groundwork

- Added a pure per-level, server-epoch-aware bitset reconciliation contract for concurrent device painting.
- Reset creates a new authoritative generation; stale offline paints cannot resurrect cleared cells. Concurrent ordinary painting retains the union of completed cells.
- Added source-level regression tests and ADR 0004 covering conflict handling, stable operation IDs and required server-side transactional deduplication.
- Drafted a versioned OpenAPI contract and additive PostgreSQL V4 identity/progress/idempotency schema with row-level scope policies; neither is deployed or executed.
- Added a bounded per-account, durable FIFO outbox using Android/Web local preferences, strict JSON bitset validation, explicit acknowledgments and an in-memory testing adapter. No network sync is enabled.
- Hardened the outbox: invalid outgoing payloads are rejected before persistence; concurrent in-memory operations cannot overwrite each other; regression cases cover FIFO, malformed progress and stale Reset preservation.
- This is **not** account login or cloud sync: backend, secure authentication, guest migration, network coordination and cross-device validation remain pending. No local tests or builds were run for this development increment.

## 0.3.0 — local gallery and photo import (source implementation)

- 40 original bundled pictures, category/tag metadata, bilingual search and artwork details.
- My Gallery with favorites, in-progress/completed and private-picture filters; local library storage and confirmed deletion.
- Private JPEG/PNG/WebP input, EXIF orientation normalization, square crop/rotation, 32/64/128 difficulty presets, controlled 2–24 color quantization and a preview before saving.
- UUID-based personal schema-2 levels, saved locally with conversion metadata; original photos and location metadata are not persisted or uploaded.
- Completed PNG export through Android's share sheet or Web download; bilingual About and confirmed local-data clearing.
- Versioned public-resource offline packaging for Web, readiness/retry in Settings and updates after previous tabs close. Manual Android builds remain separate.
- Owner workflow recorded in AGENTS.md: no local tests, analyzer, browser checks or builds, and no wait for CI. V3 runtime, offline, memory and device acceptance remain pending.

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
