# Diamond painting / نقاشی الماسی

## What users see

The **Diamond painting / نقاشی الماسی** chip is a third presentation
mode beside **Pixel / پیکسلی** and **Canvas / بوم نقاشی**.
Switch styles at any time during painting; the grid coordinates, selected
color, coins, hints, zoom, and saved completed pixels remain unchanged.

**Each completed color-by-number cell gets one raised resin-like gem** in
that exact palette color, over a separate dark socket:

- Octagonal silhouette, cut corners, a dark outer rim and subtle shadow
  create a physical gap between adjacent drills rather than a flat tile.
- Eight asymmetric polygon facets around a polished top table provide
  fixed top-left illumination, darker bottom/right faces, and highlights.
- A deterministic micro-glint breaks the repeated pattern without random
  flickering while zooming, scrolling, returning or playing animations.
- Unfilled cells retain the existing selection preview and color numbers.
  A subtle empty mount outline does not change their painting behavior.
- For very small on-screen drills (below ~5 logical pixels), an inexpensive
  circular/glint proxy preserves color and bead separation. Zooming into a
  large 70, 80 or 128 cell picture reveals full facet geometry even when
  the underlying unzoomed cell is smaller than that threshold.
- The same appearance is used on the interactive painting board, completed
  still pictures, and every downloaded animation frame.
- PNG export uses a pure-Dart, isolate-safe raster equivalent of the
  geometry. It renders a new diamond image at the existing 1024-pixel
  nominal export resolution, without exposing or uploading any user data.

There are no network texture lookups, image assets or animation timers, so
diamond style does not increase the content pack size. Pixel and Canvas
output remain available and unchanged.

## Persistence and safety

Style is a global **display preference only**, stored in the existing
`pixelhub.artworkStyle.v1` key using the additional value `diamond`.
Old `pixel`/`canvas` values still work. Invalid or absent values fall
back to Pixel. Preferences are local; painting progress and online level
JSON schemas are not migrated or rewritten.

Files:
- `apps/game/lib/features/painting/diamond_gem_painter.dart`: gem renderer
  and empty sockets, with zoom-aware cut detail
- `apps/game/lib/features/import/diamond_photo_renderer.dart`: corresponding
  RGB raster generator for the exported PNG
- `apps/game/lib/features/painting/artwork_render_style.dart`: style registry
- `apps/game/lib/features/painting/painting_board.dart`: per-cell painting
- `apps/game/lib/core/pixel_art_preview.dart`: completed still image
- `apps/game/lib/features/painting/completed_artwork_preview.dart`: animations
- `apps/game/lib/features/painting/painting_preview_screen.dart`: mode chip
- Persian and English ARB files: display labels
- `packages/persistence/lib/persistence.dart`: preference whitelist

Tests were **added but not locally executed**, following the repository
owner's AGENTS.md instructions. GitHub CI remains configured to test and
build web artifacts; no automatic Android build was introduced.

## Suggested visual QA for release

1. Paint the same light- and dark-colored level in Pixel, Canvas and Diamond;
   verify gem edges and highlights are visible without changing palette.
2. Switch styles mid-stroke and reopen the app; check stored progress, selected
   style and accessibility labels.
3. Zoom a dense 80×80 or 128×128 painting. Confirm visible facets at zoom,
   pan stability, readable empty-cell numbers and responsive movement.
4. Complete a still and an animated level; verify diamonds remain per-cell and
   animation frames change without flicker.
5. Export PNG in all three styles and compare it with the completed preview.
6. Verify Persian default and English locale both display the Diamond chip.
