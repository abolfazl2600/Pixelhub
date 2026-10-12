# ADR 0001: V1 state, routing, packages and storage

Date: 2026-10-12. Status: accepted for the V1 technical preview.

## Context

V1 loads one bundled fixture and shows two screens. Android and Web share a mobile UI capped at 430 logical pixels. There are no sessions, accounts, network catalogs or purchases. Later milestones need injectable ports and a UI-independent data contract.

## Decision

- Use Flutter's `ChangeNotifier` with `ListenableBuilder`, and constructor injection. This standard Flutter state mechanism covers bootstrap/loading/error/retry without a third-party state dependency. A generation counter rejects stale requests; disposed controllers do not notify.
- Use `go_router` 16.2.4 with Flutter's default Web hash URL strategy. `/` and `/painting` are stable routes; the preview is nested under Home, preserving Android system Back as well as browser Back/Forward. Both button navigation and direct hash deep links use the same declarative route stack. Do not call `usePathUrlStrategy`, because Pages has no SPA rewrite service.
- Implement `level_schema` as pure Dart and `game_domain` as pure Dart ports. `persistence` implements bundled-asset reads; `design_system` contains shared tokens, theme and the mobile frame. Application features stay in `apps/game`. Painting engine, converter and network packages are deferred to their milestones.
- Bundle Persian Vazirmatn, engine fallback Roboto and original fixtures. No font CDN or catalog request is required at runtime. Bundle CanvasKit with the Web build.
- V1 has no local database. For V2, choose a versioned JSON session file through `ProgressRepository`, using a platform storage adapter (app documents on Android, browser storage on Web); atomic writes and persistence/restart tests must precede implementation. SQLite/Drift is an alternative when query needs justify it. This is a future decision, not an implemented store or durability claim.
- Pin Flutter 3.35.7 and the app lockfile. Keep `ProgressRepository`, `AuthAdapter` and `BillingAdapter` as contracts only.
- Internal release APKs use Android's standard debug signing configuration. No publication keystore is generated or committed; Play Store signing belongs to V6.

## Consequences

Bootstrap and navigation can be tested independently of platform services. There is no data migration in V1. If shared feature state expands in V2/V3, reconsider Riverpod and route structure in a new ADR; avoid a parallel state ownership model.

Web initial download still needs connectivity. V1 does not promise installed-PWA offline reopening; service worker caching is disabled to avoid stale technical-preview assets. Android assets are local after installation.
