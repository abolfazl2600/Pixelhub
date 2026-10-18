# PixelHub — manual Cafe Bazaar publication

This is a **standalone** GitHub Actions workflow for Cafe Bazaar. It does
**not** replace or modify the Google Play AAB / preview APK workflow and
**never** runs on push, tag, pull request or a schedule.

- Workflow: [Publish Cafe Bazaar (manual)](https://github.com/abolfazl2600/Pixelhub/actions/workflows/cafebazaar-publish.yml)
- Implementation: [tool/publish_cafebazaar.py](../tool/publish_cafebazaar.py)
- Provider: [Cafe Bazaar Pishkhan API](https://developers.cafebazaar.ir/fa/guidelines/feature/pishkhan-api)

## One-time setup

1. Create/verify the `io.github.abolfazl2600.pixelhub` app listing in
   [Pishkhan](https://pishkhan.cafebazaar.ir/) before attempting an upload.
   The Pishkhan API secret is scoped to a **particular Bazaar app**.
2. In GitHub **Settings → Secrets and variables → Actions**, add a new
   *repository secret* called `CAFEBAZAAR_PISHKHAN_API_SECRET` containing
   the secret from that app's Pishkhan API page. Do not add it to git or
   workflow inputs.
3. Keep the existing Android release signing secrets:
   `PIXELHUB_UPLOAD_KEYSTORE_BASE64`,
   `PIXELHUB_UPLOAD_STORE_PASSWORD`,
   `PIXELHUB_UPLOAD_KEY_ALIAS`,
   `PIXELHUB_UPLOAD_KEY_PASSWORD`.
   These are used to sign the actual APK; the workflow never uses debug signing.
4. Ensure the APK signing **certificate matches any already-published
   Cafe Bazaar version** of the same package. The Google Play *upload key*
   is not necessarily the same as Play's *app-signing key*.
5. Increase `version: x.y.z+N` in `apps/game/pubspec.yaml` before submitting
   an update; Bazaar requires a higher Android version code.

## Publish a version

1. Open [Publish Cafe Bazaar (manual)](https://github.com/abolfazl2600/Pixelhub/actions/workflows/cafebazaar-publish.yml).
2. Choose **Run workflow**, select branch **main**.
3. Enter **Persian release notes** (required), optional English release notes
   and an optional private reviewer note. These are manually provided at
   dispatch, not read from commits or changelogs.
4. Check **I authorize submission AND automatic publication after Bazaar approval**.
5. Leave **resume_existing_draft** unchecked for a new publication. Check it
   **only after manually confirming the existing uncommitted release in
   Pishkhan** (e.g., after a previous run created a draft but upload failed).
6. Click **Run workflow**.

The workflow runs the existing release validation, builds **only one
release APK**, verifies its APK signature and Android package ID, and
retains the exact signed artifact and commit SHA for 14 days. It then:

1. Checks the uncommitted Pishkhan release state. For an ordinary
   publication it **refuses to change an existing draft**; if the
   `resume_existing_draft` checkbox was explicitly selected, it requires an
   existing draft and does **not** create a second one.
2. Creates a Pishkhan release only when there is no draft and resume is off.
3. Uploads only `app-release.apk` with architecture `all`.
4. Commits the release with **auto_publish=true** and
   **staged_rollout_percentage=100**, including the manually entered notes.

**Important:** The API success result confirms the submission and request
for automatic publication *after Bazaar approval*, not that the app is
already live in the store. Check review and publication status in Pishkhan.
The workflow deliberately cannot bypass Bazaar review or policy checks.

## Operational safeguards and troubleshooting

- Only a workflow dispatch from **main** can progress; no untrusted SHA or
  tag input is accepted for the release source.
- Publishing is disabled unless the explicit confirmation box is checked.
- The secret is never written to the repository or artifacts.
- The uploader does **not** automatically retry state-changing HTTP POSTs.
  If a network failure happens *after* draft creation, visit Pishkhan to
  inspect the draft before manually rerunning.
- If an APK upload fails with HTTP 400, the workflow now shows the provider's
  structured error message (if present) without dumping raw response headers
  or bodies. Check that message for the exact reason (package/ABI/version
  code/signature or other validation).
- **Specific recovery for run 39099143415:** a signed version 0.4.0+6 APK
  was built and a Bazaar draft was created, but the upload returned HTTP 400.
  Do **not** start a new release blindly. Inspect that draft in Pishkhan, then
  select **resume_existing_draft** for a new manually-dispatched run to retry
  the upload to that draft. If the draft was discarded in Pishkhan instead,
  leave that checkbox off.
- Resume is an operator-approved mutation of an existing uncommitted release;
  do not select it when a different release is being edited in Pishkhan.
- A missing/invalid Pishkhan token, conflicting draft, invalid version code,
  wrong signing certificate or package not registered in Pishkhan will stop
  the submission. The API is the final authority on release acceptance.
- Output APK: `apps/game/build/app/outputs/flutter-apk/app-release.apk`.
- This flow intentionally publishes an **APK** (no .bin generation needed).
  An AAB release is a different integration requiring Bazaar's bundle
  signer and AAB/BIN upload endpoints; do not submit the Google Play AAB
  through this APK API.
- To change publication to a review-only draft, explicitly update the
  uploader's `auto_publish` flag in a code review. This workflow currently
  requests automatic publication after approval by design.

No Cafe Bazaar live release, Android build or Actions run is triggered
merely by adding these source files.
