# Artwork difficulty

Difficulty is presentation metadata calculated at runtime; it is not stored in
level JSON, progress records, imported artwork settings, IDs, or checksums.

## Calculation

The reusable helper in
`apps/game/lib/features/gallery/artwork_difficulty.dart` scores an artwork as:

`score = sqrt(width × height) × 4 + distinctUsedColors × 24`

Distinct colors means the number of color indices actually present in the cell
matrix, not the number of unused entries in the palette. The thresholds are:

- **Easy:** score ≤ 175
- **Medium:** score > 175 and ≤ 230
- **Hard:** score > 230

The thresholds are intentionally based on the current catalog's common 16×16
and 32×32 grids. They keep a small 16×16, four-color design Easy; common 32×32
three- or four-color designs Medium; and larger/more colorful designs Hard.
The grid side is used instead of raw area so doubling the side increases
estimated work without making every 32×32 artwork automatically Hard.

## Online and personal artwork

- Bundled and downloaded levels use the same helper and count colors actually
  used by their cells.
- The online catalog publishes an optional `colorCount` derived from the
  immutable level JSON. It is catalog-only metadata; pack contents, IDs,
  versions, and checksums are unchanged.
- Older catalog entries without `colorCount` use a stable four-color estimate
  until their level is downloaded. This preserves compatibility with existing
  Releases and avoids blocking the gallery on network requests.
- Personal/imported artwork is classified only for display/filtering. Its
  existing import-time difficulty selection and stored level data are not
  changed.
- Filtering is applied before online pagination and composes with category,
  search, favorites, and progress filters. The compact badge is secondary
  metadata and uses neutral theme colors with semantic labels for screen readers.

These are deterministic estimates of coloring effort, not a claim that all
artworks of a given grid size are equally difficult. Thresholds can be
recalibrated against future catalog distributions without migrating saved data.
