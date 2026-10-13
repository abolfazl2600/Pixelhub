# Painting animation rollout

Animation is an optional, palette-only companion shown after completion. Level
IDs, checksums, versions and saved painting progress remain unchanged. Each loop
starts and ends on the original image. Still-image controls and reduced-motion
preferences remain supported. Bundled sidecars load only when opening their
painting; the startup catalog contains paths rather than frame grids.

Recipes live in `tool/animation_batches/`; each batch records up to ten pictures.
`tool/pixel_animation_recipes.py` renders deterministic independent sparse frames.

## Registered batches

| Batch | Pictures | Motions |
| --- | --- | --- |
| Bundled 01 | sunflower, heart, rainbow, moon, tree, star, gem, cat, house, planet | flower/tree sway, heartbeat, light glints, stars, rotation, eye blink |

CI and Pages results must be checked before describing a batch as verified or
published. Online animation assets are generated during Pages publication and
must remain independent of the immutable released paintings.
