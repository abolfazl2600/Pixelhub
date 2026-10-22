# PixelHub Kids: theme and signed Android releases

## Theme

The **Kids-only** manifest `products/kids.yaml` defines its visual identity:

- Primary purple: `#7054D7`
- Secondary sunshine yellow: `#FFC857`
- Background cream: `#FFF9F1`
- Supporting mint accent: `#35BBA5` (Kids theme only)

Kids uses large rounded controls, pastel onboarding panels, and soft artwork
cards. The painting palette's selected outline and completion icon follow the
Kids theme. PixelHub and Art preserve their original themes. The generated Dart
registry and Gradle brand configuration must always be regenerated after edits:

```bash
python3 tool/products/generate.py
```

## Signed Android output

An APK/AAB is **not** signed for publication merely because its source is in
main. GitHub Actions must use the owner's real release keystore.

1. Prepare and securely back up a dedicated Kids upload keystore. Keep its
   passwords and base64 encoding outside source control. Do not commit the file.
2. In GitHub `Settings > Secrets and variables > Actions` store:
   `KIDS_UPLOAD_KEYSTORE_BASE64`, `KIDS_UPLOAD_STORE_PASSWORD`,
   `KIDS_UPLOAD_KEY_ALIAS`, `KIDS_UPLOAD_KEY_PASSWORD`.
   Repository secrets or protected environment `release-kids` may be used.
3. Open `Actions > Build products > Run workflow` on `main`.
   Set `application=kids`, `build_type=release-all`, and leave
   `source_ref` empty to build the selected workflow revision.
4. The workflow refuses a release if signing credentials are missing.
   On success, download the `kids-release-all-<SHA>` artifact within its
   retention period. It contains a signed release APK, signed Play AAB and
   `manifest.json` with signer fingerprint, SHA-256, package and version.
5. Verify the package `io.github.abolfazl2600.pixelhub.kids`, version
   `1.0.0+1`, signature and installability on an Android device. Upload
   the AAB to the separate Kids Play Console listing only after review.
   Future versions must increment Kids `version_code` independently.

Preview builds (`preview-apk`) use debug signing and are **not** store-ready.
No store upload is implicit in this workflow. This document does not claim
that a signed build or on-device test has already succeeded.
