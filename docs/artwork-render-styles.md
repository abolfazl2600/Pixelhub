# Artwork rendering styles

PixelHub's render style is presentation state, never painting content.

- `pixel` stays the original, flat and lossless pixel painting.
- `canvas` is **now woven threads / بافتنی**. Its stored identifier remains
  `canvas` for compatibility with existing user preferences. It renders actual
  over-under crossings of two rounded yarn strands, with recessed gaps, cast
  shadows and raised highlights. The previous linen grain and pigment streaks
  are removed.
- `diamond` preserves the separate gem-facet rendering.

## Woven fabric rendering

- Continuous horizontal and vertical yarns alternate over/under each other on
  a deterministic artwork-space grid. Yarn pitch is derived from the actual
  cell size, not downloaded content. No art JSON, palette, checksum or saved
  pixel changes are necessary.
- On the interactive board, the yarn surface is **clipped to completed cells**;
  numbered unfinished cells stay clear, so it remains easy to paint.
- Completed stills and animated frames use the same Flutter painter, while PNG
  export uses the shared pure-Dart intersection geometry and shade model.
- The pattern is fully offline and asset-free, so no texture downloads or
  extra packages are needed. Path batching avoids individual draw calls per
  yarn intersection. Only the visible board bounds are traversed.
- `ArtworkStylePreferences` continues to use the persisted
  `pixelhub.artworkStyle.v1` value; changing style does not alter completion,
  rewards, selected palette entry, animation frames, progress or favorites.
- Unknown stored style IDs safely fall back to Pixel.

This is a woven-thread visual effect, not physically simulated cloth.
Quality/performance should be verified on representative low-end Android
devices; unit and CI tests cover geometry, PNG integrity and style persistence.

## Consistent preview and PNG export

- The current persisted style is provided to the artwork details route,
  including its still/animated preview and its PNG export control. The
  completed-painting screen also exports with the active style.
- The PNG pipeline resides in `apps/game/lib/features/painting/artwork_png_export.dart`.
  `artworkPngRenderers` maps style storage IDs to pure-Dart raster functions.
  There is no hard-coded style switch in the export entry point.
- To add a style: add its `ArtworkRenderStyle` entry and persistence handling,
  implement the Flutter preview/painting rendering, and register a matching
  pure-Dart `ArtworkPngRenderer`. Both implementations should share pure
  geometry/color math, as the yarn and diamond renderers do today.
- The style-coverage test fails when a new enum entry has no PNG renderer.
  Unknown export IDs throw a `FormatException` rather than silently
  generating a Pixel-style PNG. Missing style metadata defaults to Pixel for
  older callers. PNG export remains offline with no additional assets.
