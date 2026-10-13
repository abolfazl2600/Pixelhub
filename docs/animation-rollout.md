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
| Online 07 | iran-abstract-brickwork, iran-abstract-iwan, iran-blue-mosque-tabriz, iran-khaju-bridge, iran-ali-qapu, iran-chehel-sotoun, iran-shah-cheragh, iran-fin-garden, iran-eram-garden, iran-masuleh-village | glimmer, ripple, sway |
| Online 08 | iran-kandovan, iran-lut-kaluts, iran-anzali-lagoon, iran-damavand, iran-persian-carpet, iran-minakari-plate, iran-khatam-box, iran-samovar-tea, iran-santur, iran-tombak | float, glimmer, pulse, ripple |
| Online 09 | iran-haft-sin, iran-yalda-pomegranate, landscape-sunset-mountains, landscape-alpine-lake, landscape-waterfall, landscape-cottage, landscape-golden-desert, landscape-tropical-beach, landscape-misty-forest, landscape-river-bridge | glimmer, ripple, sway |
| Online 10 | landscape-moonlit-night, landscape-flower-valley, classic-birth-venus, classic-creation-adam, classic-last-supper, classic-school-athens, classic-night-watch, classic-milkmaid, classic-las-meninas, classic-third-may | glimmer, ripple, sway |
| Online 11 | classic-liberty-leading, classic-wanderer-fog, classic-fighting-temeraire, classic-hay-wain, classic-impression-sunrise, classic-water-lilies, classic-moulin-galette, classic-grande-jatte, classic-klimt-kiss, classic-card-players | glimmer, ripple, sway |
| Online 12 | classic-wheatfield-crows, classic-sleeping-gypsy, mona-lisa, starry-night, the-scream, sunflowers, girl-pearl, great-wave, object-alarm-clock, object-vintage-camera | glimmer, pulse, ripple, sway |

CI and Pages results must be checked before describing a batch as verified or
published. Online animation assets are generated during Pages publication and
must remain independent of the immutable released paintings.
