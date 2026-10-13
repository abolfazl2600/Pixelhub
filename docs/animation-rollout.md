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
| Bundled 02 | flower, tulip, cactus, mountain, leaf, mushroom, apple, cherry, watermelon, butterfly | petal/leaf sway, drifting sun, cap stretch, fruit bob, wing flap |
| Bundled 03 | bird, fish, turtle, fox, bunny, owl, dog, bee, rocket, saturn | wings, swimming/walking bob, eye blinks, flutter, exhaust flicker, rotating rings |
| Bundled 04 | ufo, comet, sun, snowflake, umbrella, cup, book, kite, sailboat, diamond | hovering, drift, rotation, wind, steam, page flap, kite sway, boat bob, sparkles |
| Online 01 | lion, elephant, giraffe, penguin, dolphin, koala, flamingo, octopus, deer, parrot | eye blinks, trunk/neck sway, wings, swimming, tentacles |
| Online 02 | fox, wolf, brown-bear, zebra, tiger, cheetah, kangaroo, hippopotamus, rhinoceros, crocodile | blink, sway |
| Online 03 | toucan, peacock, hedgehog, raccoon, sloth, seal, whale, shark, frog, chameleon | blink, flap, float, sway |
| Online 04 | panda, bunny, turtle, owl, ice-cream, donut, coffee, cactus, autumn-tree, rain-cloud | blink, float, pulse, steam, sway |
| Online 05 | saturn, astronaut, iran-persepolis, iran-azadi-tower, iran-milad-tower, iran-imam-mosque, iran-sio-se-pol, iran-nasir-ol-molk, iran-arg-e-bam, iran-hafez-tomb | float, glimmer, ripple, spin |
| Online 06 | iran-amir-chakhmaq, iran-golestan-palace, iran-abstract-muqarnas, iran-abstract-dome, iran-abstract-orsi, iran-abstract-eslimi, iran-abstract-arches, iran-abstract-windcatcher, iran-abstract-shamsa, iran-abstract-mosque | glimmer |

CI and Pages results must be checked before describing a batch as verified or
published. Online animation assets are generated during Pages publication and
must remain independent of the immutable released paintings.
