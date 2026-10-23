# Product-aware modular builds

Each PixelHub product shares the Flutter coloring engine while selecting its
own optional features, entry routes and packaged resources. This is implemented
in the existing monorepo, not through forks.

## What is actually excluded?

The source of truth is `products/<id>.yaml` in `features` and `content`.
`tool/products/module_bundle.py` reads that manifest and constructs a
deterministic, explicit list of assets:

- Only the selected product's launcher artwork and offline catalog.
- Only levels referenced by that catalog, plus shared level metadata.
- Only animations referenced by those levels when `animations` is enabled.
- Only sounds required by the selected product; reward/coin sounds require
  both `sound_effects` and `coins`.
- Assets for another product are not silently copied into an output.

The build temporarily rewrites Flutter's `pubspec.yaml` asset declaration
to the explicit list. It **always restores** the source file, including
when Flutter or signing fails. Do not run two local product builds concurrently
against the same checkout. GitHub Actions uses separate checkouts per job.

The Android build opens each finished APK/AAB and compares the actual
`flutter_assets` contents with the allowed list. Missing or extra product
assets fail the build. The Web build similarly checks `build/web/assets`.
The Android artifact's `manifest.json` (and Web `product.json`) includes
the selected modules, assets, asset bytes, and actual output size.

Dart `--dart-define=MODULE_...` flags are derived from the very same
manifest, rather than entered manually. Compile-time constant guards cover
the key optional routes and components. Flutter release AOT may tree-shake
unreachable code, **but a disabled feature is not proof that every shared Dart
dependency or native plugin has been eliminated**. For example, shared
painting/gallery flows still depend on portions of the gallery, photo/export
and styling code. Those need dedicated compile-time entry points and isolated
dependencies for further size savings.

## Create new modules

1. Implement the capability under `apps/game/lib/features/<feature>/`
   (or an independent Dart package). Keep its optional UI behind a constant
   build guard so the compiler can see when it is absent.
2. Declare the capability in `products/schema.json` and product manifests.
   Update `ProductFeatures` and `tool/products/generate.py` as necessary.
3. Register its compile-time flag in `COMPILED_MODULES` and the corresponding
   Dart constant in `BuildModules`. Add module-specific resource selection
   to `plan_assets`, with a validation error if required assets are missing.
4. Add its route only for products whose feature is enabled, guard all deep
   links, and add asset/isolation tests. An unimplemented feature must stay
   disabled in every product.
5. Verify Android APK/AAB file lists and compressed sizes through the
   `module_bundle` report. Compare release outputs on a fixed device/ABI
   before promising specific savings. Debug APK size is not representative.

**Sticker Album is not implemented yet.** When implemented, add the new
`sticker_album` feature and package its UI, data and sticker background
assets only for products enabling it (initially Kids).

## Build

Use the existing **Build products** GitHub Actions workflow (manual only).
Set `application=kids`, `art`, or `pixelhub` and select a build type.
The workflow uses the manifest's module flags automatically. Signed release
builds still require the selected product's private upload key.

For standalone Web products, `tool/products/build_web.py --product kids`
uses the same bundle selection. Publishing to Pages remains separate and
requires the repository's explicit `PIXELHUB_WEB_PRODUCTS` allowlist.

## Integrity

- Product identifiers, storage scopes and signing keys remain independent.
- Only the designated product's offline assets appear in its Android archive.
- User data is never sent to the build server or content CDN.
- No automatic Android release or version bump is introduced.
- Existing `flutter run` and development tests keep the full default
  source asset declaration unless using the product build scripts.
- Content downloaded by the user after installation is kept in local
  product-specific storage; it is not bundled with these offline assets.
