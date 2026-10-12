# Asset provenance

- `levels/sunflower.json` (preserved V1 fixture): original 16 × 16 pixel fixture created for Pixelhub V1; licensed under the repository Apache-2.0 license. No competitor artwork or user photos.
- `fonts/Vazirmatn.ttf`: Vazirmatn by Saber Rastikerdar, distributed under the SIL Open Font License 1.1. Source: [Google Fonts](https://github.com/google/fonts/tree/main/ofl/vazirmatn). The unmodified font and its license are bundled locally; no runtime font service.
- `fonts/Roboto.ttf`: Flutter Web's engine fallback font, bundled to avoid remote font requests. Unmodified Google Fonts Roboto, SIL OFL 1.1; see `fonts/Roboto-OFL.txt`.
- Web and Android launcher icons: original geometric pixel flower, Apache-2.0, generated for this project.

V1 fixtures carry `schemaVersion` and `contentVersion`. A production level checksum and migrations are part of the V2 contract; V1 has no saved sessions.

V2 uses ten original geometric fixtures listed in `levels/catalog.json`, including `sunflower-v2.json` with a new content version. All are repository Apache-2.0 assets. Schema 2 SHA-256 canonical payload is defined in ADR 0002; existing versioned assets must remain immutable once published. No competitor art or generated-AI artwork is used.
