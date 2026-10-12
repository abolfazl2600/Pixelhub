# Data Safety — review worksheet for PixelHub Android

**Status: proposed answers only; not submitted to Google Play.**
Review the **final signed AAB**, merged manifest and transitive SDK/plugin
behavior before entering anything in Play Console. Google treats data
transmitted by third-party SDKs as collection even if the developer does
not receive it.

| Data flow | Current app implementation | Proposed Play response |
|---|---|---|
| Original user photos | Explicit local file picker, on-device conversion; original and EXIF location not retained or uploaded | No automatic off-device collection |
| Converted private pixel grids | Persisted locally with progress; max personal library limits | Local storage is **not** a transmitted data category |
| Coloring progress, favorites, language | Local Android preferences; cloud Sync backend is **inactive** | No automatic collection |
| Error and tool counters | Ephemeral in-memory session counters; no remote reporting | No remote crash/usage collection |
| Share/export PNG | User explicitly invokes native share sheet; chooses recipient | User-initiated transfer, not automatic developer sharing |
| Payments, ads, analytics | No active billing, ads SDK or remote analytics service | No advertising-ID-based collection |

## Preliminary questions

- **Does the current app collect or share user data off-device?**
  Proposed **No**, subject to checking the final dependency tree, outbound
  traffic, Android merged manifest and distribution version. An Android
  store listing still requires the Data Safety form.
- **Privacy policy:** https://abolfazl2600.github.io/Pixelhub/privacy.html
  (publish and verify accessibility before submission).
- **Account creation:** **not available** in the shipping local-only version.
  An inactive cloud-sync API design is not a production account system.
- **Deletion:** Settings → Clear local data deletes PixelHub-managed local
  artwork/progress/favorites/language. Uninstalling can clear local data.
  Other apps' copies of shared PNG files are beyond PixelHub's control.
- **Encryption in transit, independent security review, and other Console
  follow-up questions:** Answer based on actual current behavior and
  Google's exact prompts; do **not** claim independently audited security.

## Required final verification

1. Inspect `AndroidManifest.xml` **after** Gradle merges all library
   manifests. Deny unintended `READ_MEDIA_*`, `CAMERA`, `RECORD_AUDIO`,
   `ACCESS_*_LOCATION`, and advertising `AD_ID` permissions.
2. Confirm network behavior of the final Android artifact and plugin SDKs;
   an optional external website opened by the user is different from a
   background collection SDK.
3. Review changed versions of `file_selector`, `share_plus`,
   `shared_preferences` and all transitive dependencies before release.
4. Keep all statements aligned with the privacy policy and Play disclosures;
   if Auth/Sync, telemetry, cloud photo storage or ads are enabled, redo
   the worksheet and policy **before** shipping.
5. Final answers belong in **Google Play Console**, not YAML in this repo.

References:
- https://support.google.com/googleplay/android-developer/answer/10787469
- https://support.google.com/googleplay/android-developer/answer/9859455
