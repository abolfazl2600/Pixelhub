# PixelHub multi-application platform

## Architecture and audit

The baseline is `079f4eb3ec634615e6faad4424d5f8bfc34a184c` on `main`.
The original app is `apps/game`, version **0.4.1+8**, Android application ID
`io.github.abolfazl2600.pixelhub`. Its Android namespace and Kotlin activity package
remain unchanged. The existing upload-key secret names remain supported.

One Flutter application now has independent Android product flavors. This avoids
copying painting/UI/business logic into separate apps. A separate Flutter app is
unnecessary for the initial products: composition, content policy, navigation,
theme and service configuration provide their differences.

The following existing packages remain product agnostic:

| Package | Shared responsibility |
| --- | --- |
| `painting_engine` | Painting sessions, strokes and tools |
| `game_domain` | Progress, artwork library, museum and storage interfaces |
| `level_schema` | Checksum-bound levels and compatible animation sidecars |
| `design_system` | Existing PixelHub theme and responsive frame |
| `persistence` | Catalog loading and scoped durable storage |

`products/*.yaml` are the authoritative product registry. They deliberately use
JSON syntax, a valid YAML subset, so Python's standard library suffices in CI.
`products/schema.json` rejects unknown properties, mistyped flags, invalid IDs,
versions, colors and build targets. Registry validation additionally checks unique
package/storage/Web identities, assets, content policy and feature dependencies.
The generator emits typed Dart configuration and Gradle flavor data. Run it after
editing a manifest; CI rejects stale generated files.

```bash
python3 tool/products/cli.py validate
python3 tool/products/generate.py
```

| Product | Registry status | Content and UX |
| --- | --- | --- |
| PixelHub | Ready for building | Existing catalog, economy, screens and features |
| Kids | Ready for building | 35 existing simple pictures, maximum dimension 32; large controls, visual instructions, no wallet/import/profile/paid textures |
| Art | Ready for building | Four existing classic paintings at 64–85 pixels; artist/context notes, studio home, museum, canvas and diamond rendering; no wallet/import |
| Animals | Draft, explicitly rejected by builders | Initial audience/content policy only |
| Relax | Draft, explicitly rejected by builders | Initial audience/content policy only |

“Ready” is a configuration/build eligibility state, not a claim of store release,
verified signing or completed device QA. No animals/relax artwork or empty app was
invented. The new Kids/Art marks are independent geometric product marks; the
owner's original rainbow-brush mark is unchanged.

## Runtime composition and features

`PRODUCT_ID` selects a generated `ProductConfiguration`. Unknown/unready IDs fail
explicitly. Android startup also checks that its actual flavor matches the Dart
product. `ProductScope` supplies the configuration to all route descendants.
`ProductHome` composes Kids' large picture grid/instructions or Art's studio cards.
The actual painting controller, rendering engine, gallery and durable progress
services are shared.

Features are real service/UI policies: coins, achievements, animations, image
import, canvas/diamond rendering, sound effects, online catalog, profile and
museum. Disabled pages reject direct links; controls disappear. A disabled wallet
allows painting/tools without spending or changing the reward ledger. Disabled
sound does not initialize playback, and disabled online content does not fetch.
Free painting and background music did not exist in the audited implementation;
these reserved flags must remain false and validation refuses to claim they work.
The current canvas rendering is the existing woven embroidery texture, not an
additional invented engine mode.

Appearance includes primary/secondary/background colors, theme mode, bundled
font family, layout, default style, large controls and navigation. The original
PixelHub light theme retains its existing behavior. Only bundled fonts are
accepted; adding another font requires adding its real asset to the pubspec.

## Content and isolation

Offline product manifests contain references to existing `assets/levels` files;
no level grid or animation data is copied. The original manifest/metadata/checksums
remain intact. `AssetLevelRepository(catalogPath: ...)` selects the product catalog.
All shared source assets are bundled by the current pubspec, but each audience
sees only its own catalog. This favors compatibility; per-product asset stripping
can be added later if application size justifies it.

The existing immutable release packs and root online catalog remain authoritative.
After normal Pages catalog assembly and animation publication:

```bash
python3 tool/products/publish_catalogs.py site/online
```

This writes `online/products/kids/catalog.json` and
`online/products/art/catalog.json`. Both reference the same immutable
`online/levels`, `online/previews` and animation files as PixelHub. The controller
uses a separate manifest path and shared asset root, validates the manifest's
product identity, filters category/dimension again and retains existing integrity
checks. Retirement entries are scoped to replacements in that product catalog.
Publishing one product manifest never rewrites the root catalog.

To add online artwork, use the existing immutable release-pack publishing tools,
assign a supported category and dimensions, then assemble and publish manifests.
For a new product, configure `online_manifest`, categories and maximum dimension.
New categories require extending the domain schema and localizations together.
Do not republish a changed image under an existing immutable ID/checksum.

`LocalPreferences` defaults to the **exact existing `pixelhub.*` keys**. New scopes
are `pixelhub_kids.*` and `pixelhub_art.*`, including downloads, animation caches,
badges, museum, wallet, language and progress. Original clear-data behavior cannot
match the new prefixes. No original data migration is required. Existing Android
updates use the same package and signing credentials. Browser products sharing
an origin have distinct durable keys.

## Android builds and signing

Open **Actions → Build products → Run workflow**.

- `application`: a validated registry ID or `all`; drafts fail with a clear error.
- `build_type`: `preview-apk`, `release-apk`, `play-aab`, or `release-all`.
- `source_ref`: optional branch, tag or commit; empty uses the selected workflow ref.

Planning resolves the ref once to an immutable SHA. `all` expands all ready
products into independent jobs, with `fail-fast: false`, maximum three parallel
jobs and separate artifact directories. Product selection is a string input so a
new registry entry does not require manually changing a Workflow dropdown.

Preview builds use Android debug signing and need no private signing secrets.
They retain the declared application ID; a debug-signed preview cannot upgrade
an existing store-signed installation with a different certificate.
Release builds fail before Flutter if any required upload-key input is missing.
There is no debug signing fallback. Gradle also refuses unsigned releases and
using a selected signing environment for another flavor.

For each product, define these repository secrets, or put the same names in its
protected GitHub Environment (`release-pixelhub`, `release-kids`, `release-art`):

```text
<PRODUCT>_UPLOAD_KEYSTORE_BASE64
<PRODUCT>_UPLOAD_STORE_PASSWORD
<PRODUCT>_UPLOAD_KEY_ALIAS
<PRODUCT>_UPLOAD_KEY_PASSWORD
```

`<PRODUCT>` is `PIXELHUB`, `KIDS`, or `ART`. Existing PixelHub secrets keep their
names and meaning. Environments can require a reviewer before exposing release
keys. Their protection settings must be configured by the repository owner; the
workflow does not bypass or fabricate approvals. Preview uses the `preview`
environment and never requires release credentials.

Locally, export the matching `<PRODUCT>_UPLOAD_*` variables and run:

```bash
python3 tool/products/build.py --product kids --type preview-apk --output artifacts/kids
python3 tool/products/build.py --product art --type release-all --output artifacts/art
```

The builder checks APK signatures with `apksigner`, verifies APK application ID
and both version fields with `aapt`, verifies AAB JAR digests with `jarsigner`,
checks the signer certificate against the selected keystore, and decodes the AAB
manifest to check its application ID/version. Temporary keystores have mode 0600
and are removed on exit. Passwords are passed through environment variables,
never command-line values or printed configuration. No keystore is committed.

Artifacts have product/type/version/code/short-SHA names. `manifest.json` includes
source SHA, UTC timestamp, expected application identity, version, SHA-256,
signature verification status, source-dirty indicator and public signer fingerprint. It contains no
private signing material. Signing a release build does not upload it to a store.

The legacy `android-build.yml` dispatch interface calls the shared implementation.
The existing CafeBazaar workflow still exists and uses the PixelHub flavor/output.
Its publication approval inputs are unchanged. No new automatic store publication
has been added, and Android builds remain manual dispatch only.

## Versions

Each product's manifest owns its version name/code. PixelHub's pubspec retains
`0.4.1+8` as a checked compatibility mirror for old tools. Never change the original
version merely to build a specialized product. Preview builds consume the declared
version without incrementing a release ledger. Release increments are explicit,
reviewed configuration changes, avoiding races between concurrent build jobs.

`check_versions.py --base <main-sha>` rejects code rollback and a changed version
name without a code increase. After an actual approved store release, record an
immutable tag `<product>/v<version-name>+<version-code>`. Build checks reject reuse
of a tagged code from a different commit, while permitting exact-source rebuilds.
Store history outside Git must be reconciled before first adopting these tags;
this code cannot infer unpublished Play/marketplace version history.

## Web builds and controlled hosting

```bash
bash tool/build_web.sh               # original /Pixelhub/ path
bash tool/build_web.sh kids          # /Pixelhub/kids/
python3 tool/products/build_web.py --product all
```

Independent outputs are in `apps/game/build/products/<product>`. The original
`build/web` output remains available to the existing CI/Pages pipeline. PWA IDs,
scopes, base hrefs, names, colors and icons match the product. The existing offline
worker cache already includes its registration scope; child navigation is now
excluded from a parent worker's cached index fallback. Application asset hashes
remain build-specific. User photos do not enter the public asset cache.

**Build independent Web products** produces downloadable artifacts without
publishing. Additional public Pages routes are disabled by default. To explicitly
enable and retain them on subsequent Pages deployments, set repository variable
`PIXELHUB_WEB_PRODUCTS` to `kids,art` (or one explicit ID). Pages builds those
allowlisted apps into their own directories alongside the original root artifact.
Keep it empty to preserve only the original public app. This opt-in also increases
Pages build time. Test the new paths on staging before enabling them publicly.

Old root service-worker tabs may keep their previous worker until closed. Close
those tabs once when first enabling a child app; new workers never force reload a
painting session. No new product Web deployment was enabled by this change.

## Branding and adding a product

Brand PNGs are square sources at least 128 pixels. The existing Dart icon tool
accepts a product ID and writes flavor launcher/adaptive/splash resources plus Web
icons. The main mark and namespace remain unchanged. Geometric Kids/Art sources
can be regenerated with `generate_brand_assets.py` (development dependency Pillow).

Create an explicitly non-buildable draft:

```bash
python3 tool/products/create_product.py \
  --id nature --name "PixelHub Nature" \
  --package-id io.github.abolfazl2600.pixelhub.nature
```

Supply real branding/content to create a ready product:

```bash
python3 tool/products/create_product.py \
  --id nature --name "PixelHub Nature" --name-fa "پیکسل‌هاب طبیعت" \
  --package-id io.github.abolfazl2600.pixelhub.nature --template kids \
  --icon apps/game/assets/brand/nature_mark.png \
  --catalog apps/game/assets/products/nature-catalog.json --ready
```

The command rejects duplicate IDs/packages, unsafe paths, missing assets and
invalid configuration, writes exclusively and rolls back failed validation.
Choose the feature policy, categories, home composition, texture and theme in the
new manifest; regenerate; add tests/content review; configure real release keys.
Registry discovery automatically includes a ready new flavor in `all` and accepts
its ID in the workflow. No application or shared engine is copied.

## Validation and resource use

`tool/validate.sh` validates registry/generated files, runs product-tool tests,
formats/analyzes packages/app, runs package tests where present and existing app
tests. Existing Python immutable-content tests remain in CI. Product tests cover
scoped storage/clear-data, legacy keys, UI composition, disabled wallet, feature
policies, missing signing, unsigned AAB rejection and online manifest isolation.
Automatic specialized Web builds use an affected-products calculation: shared
engine/app/tool changes rebuild dependent products; one product manifest/catalog
change selects that product. Android jobs remain exclusively manual.

Flutter/Pub caching comes from the existing pinned Flutter action. Android jobs
also use pinned Gradle caching, with read-only caches outside main. Artifacts,
private signing directories and jobs are isolated. No auto-increment commits,
parallel shared output directory or secret-bearing cache was introduced.

See [VALIDATION.md](VALIDATION.md) for actual commands/results and remaining
external verification gates. Configuration or code presence alone is never a
claim that a build passed, a product was published or a physical device was tested.
