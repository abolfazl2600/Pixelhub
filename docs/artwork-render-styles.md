# Artwork rendering styles

PixelHub's render style is presentation state, not artwork content.

- `pixel` is the stable default and retains the legacy cell-color rendering.
- `canvas` overlays a subtle deterministic procedural weave. It uses no image asset,
  network request, per-level file, palette entry, or artwork-schema field.
- The typed `ArtworkRenderStyle` enum and `artworkStylePainters` registry are the
  extension point for future looks such as paper or cross-stitch.
- The selected style is stored under `pixelhub.artworkStyle.v1` by the optional
  `ArtworkStylePreferences` contract. Unknown or malformed values resolve to
  `pixel`. It is independent of progress bitsets, favorites, artwork IDs,
  checksums, and downloaded level metadata.
- The same selection is applied to the live board, still/animated completion
  preview, and PNG export. The export's Pixel path remains the default legacy
  renderer; Canvas uses a deterministic low-opacity weave after nearest-neighbor
  scaling so cell edges remain crisp.
- The texture is drawn only within the visible board bounds and uses bounded
  procedural line drawing. It does not decode assets during gestures or zoom.

The UI selector is compact and localized inline for Persian RTL and English LTR.
Changing style only rebuilds presentation; it never touches the painting session.
No claim of device frame-time or APK-size improvement is made without a measured
release build on representative Android hardware. The regression suite covers
preference validation, Pixel fallback, style switching, unchanged progress,
offline persistence, and style-aware PNG dimensions/content.
