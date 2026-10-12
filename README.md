# Pixelhub

Pixelhub is an Android-first, mobile-style Web pixel-coloring game in development.

> **Current status:** documentation / planning only. There is no Flutter application, GitHub Pages game, Android APK or running Backend yet.

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
