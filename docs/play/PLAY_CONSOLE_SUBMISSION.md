# PixelHub — Google Play submission preparation

**Scope:** Android **free, offline-first** build `0.3.2+5`, package
`io.github.abolfazl2600.pixelhub`. This is developer documentation,
**not a completed Play Console submission**.

## Reproducible, opt-in release workflow

- Android compile SDK and target SDK are pinned to **36** in
  `apps/game/android/app/build.gradle.kts`. Verify installation/build compatibility
  with Android SDK 36, Flutter 3.35.7, AGP and target-device behavior before release.
- `main` CI does **not** build Android. In GitHub Actions, manually run
  **Build Android (preview APK or signed store APK + Play AAB)**.
  - `preview-apk`: debug-signed installable APK, **not** for Play upload.
  - `play-aab` (**manual workflow default**): creates BOTH a Play-uploadable release AAB and a release APK for Android app stores, signed using the same private upload key. The job verifies the AAB JAR signature and the APK v2 signature, checks the AAB structure, and prints SHA-256 checksums.
- Generate a secure upload keystore **outside the repository**, e.g.:

  ```bash
  keytool -genkeypair -v -keystore pixelhub-upload.jks -alias pixelhub-upload \
    -keyalg RSA -keysize 4096 -validity 10000
  ```

- Store the keystore and passwords in a password manager / encrypted backup.
  Never commit or upload them to a public issue. Configure these GitHub
  Actions **repository secrets**:
  `PIXELHUB_UPLOAD_KEYSTORE_BASE64`,
  `PIXELHUB_UPLOAD_STORE_PASSWORD`,
  `PIXELHUB_UPLOAD_KEY_ALIAS`,
  `PIXELHUB_UPLOAD_KEY_PASSWORD`.
  The first is the **single-line base64** of the keystore bytes
  (`base64 -w 0 pixelhub-upload.jks` on Linux; on macOS use
  `base64 < pixelhub-upload.jks | tr -d '\\n'`).
  No signing material is in this repository. The Play AAB job fails closed
  when any secret is missing; it never falls back to a debug signature.
- Enroll in **Play App Signing**. Upload the resulting
  `app-release.aab` from the specific Actions artifact to Internal Testing.
  The companion `app-release.apk` is for other Android stores that accept APKs.
  Confirm the Google Play **app-signing** certificate matches the cross-store APK signing certificate if you require seamless updates across stores; Play may use a different app-signing key from the upload key.
  Play Console still needs its own app/account verification and approval.
- Confirm that Google Play accepts the bundle. In particular review 16 KB
  page-size compatibility / native libraries, final merged Android manifest,
  min/target SDK, Play signing certificate fingerprints and device coverage.
- `applicationId` is frozen at `io.github.abolfazl2600.pixelhub` unless the
  owner changes it **before** creating the listing. Each new upload must have
  a larger Android `versionCode` (currently **5**).

## Identity & listing

- App display name: **PixelHub**. In-app label and launcher use this branding.
- Current source version: **0.3.2+5**, **not** the completed V6 release.
- The selected blue easel-and-brush launcher icon is checked in as a small
  optimized source at `apps/game/assets/brand/pixelhub_mark.png`; Android,
  Web/PWA and the 512 × 512 Play listing PNG are generated before builds via
  `tool/generate_launcher_icons.dart`. Validate appearance on light/dark
  devices and mask shapes. The listing PNG is included in the signed AAB artifact.
- Prepare real game screenshots, a 512 × 512 store icon and a 1024 × 500
  feature graphic as distinct store assets; source launcher art alone is
  not proof they were uploaded to the Play listing.
- Prepare store description, support **email**, contact details, target
  countries, licensing and a current privacy URL.

## Public privacy statement

- Proposed Play policy URL:
  **https://abolfazl2600.github.io/Pixelhub/privacy.html**.
- Static source:
  `apps/game/web/privacy.html`; displayed offline in the Android app at
  **Settings → Privacy Policy** via `PrivacyScreen`. The page displays and
  copies the URL.
- The Web build requires `build/web/privacy.html` to exist, and the
  existing verified-artifact Pages workflow must successfully publish it.
  **Check the public URL in a normal browser** before pasting it into Play
  Console. Source files alone do not make an Internet URL accessible.
- The policy explains locally processed photos, local progress, voluntary
  exports, in-memory session counters and disabled ads/account/cloud sync.
  Review against the **final** shipping APK/AAB and SDK inventory.

## Console declarations (manual, not automatable in this repository)

1. Complete **App content → Data safety**, guided by
   [DATA_SAFETY_DRAFT.md](DATA_SAFETY_DRAFT.md). Double-check plugin behavior
   and merged manifests; do not blindly copy answers.
2. Complete **Content rating**, **Target audience and content**,
   **Ads**, **App access**, and other required declarations using
   [CONTENT_RATING_AND_APP_CONTENT.md](CONTENT_RATING_AND_APP_CONTENT.md).
3. Make the privacy policy accessible from the app and an active public URL.
   Confirm developer support address, country eligibility and any applicable
   Families policies for the target ages the owner chooses.
4. Complete the required closed testing and production-access process if the
   Play Console account is subject to those rules.
5. Test import/export, offline save, Reset and cancelled multi-touch strokes, 16 KB page devices,
   accessibility, permission flows, crashes and Play pre-launch report.
6. Do not enable login, rewards with money, purchases, ads or online
   diagnostics without revising code, privacy statement and declarations.

## Unverified / owner decisions

- **Verified Android release generated 2026-10-13:** GitHub Actions run
  [38364612667](https://github.com/abolfazl2600/Pixelhub/actions/runs/38364612667)
  produced a signed AAB and signed release APK for version `0.3.2+5`;
  `jarsigner` and `apksigner` checks passed. This does **not** establish
  physical-device QA, merged permission report, store acceptance,
  content rating certificate, accepted Data Safety form, or a production listing.
- The owner must create and retain the upload key, supply GitHub Secrets,
  choose the actual target ages/countries, provide the support email, verify
  the public policy URL and complete/submit the Console forms.
