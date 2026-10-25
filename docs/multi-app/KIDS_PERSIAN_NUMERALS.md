# Persian numerals ۱–۲۰ in PixelHub Kids

This feature adds twenty **online-only**, bilingual, playable pixel-coloring
levels. Every digit painting is exactly **32 × 32 cells**, has a different
immutable `online-kids-persian-number-01` … `-20` ID, and uses
`levelVersion: 1`. The cheerful pixel borders, sparkles and bold glyph
silhouettes are designed for the existing Kids painting engine. They are
not flattened screenshots: every cell has a palette index.

## Publication and product isolation

- Source recipe: `tool/online_kids_persian_numbers_pack.py`.
- The verified Web publication workflow creates the immutable Release
  `pixelhub-content-kids-persian-numbers-20-v1` with a `content.zip` asset.
- `online_release.py assemble` validates the shared-format JSON/PNG assets,
  publishes the files under `online/levels` and `online/previews`, and
  writes separate `online/products/kids/numbers.json` metadata.
- `tool/products/publish_catalogs.py` includes that metadata only in
  `online/products/kids/catalog.json`. PixelHub's original public
  `online/catalog.json` excludes these Kids-only IDs.
- This uses Kids' existing `patterns` category, so it requires no new
  navigation/category or application version bump. The artworks appear
  after a successful verified Web CI + Pages publication; repository commits
  alone do not make the Release assets available.

On the Kids home screen, paint buttons display **«نقاشی کن»** / **Paint**
instead of the longer start/continue labels. Original PixelHub labels remain
unchanged.
