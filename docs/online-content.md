# Online pictures from GitHub Releases

PixelHub uses the **same GitHub repository** for its application and remote
catalog. The **online level data and previews are Release assets**, not tracked
files on `main`. A standard `git clone` does **not** download Release assets.

## Experience

- Opening **Picture gallery** requests only
  `https://abolfazl2600.github.io/Pixelhub/online/catalog.json`.
- The catalog contains titles, dimensions, checksum and byte length, **not the
  full painting grid**.
- Preview PNG files are public and may be fetched for visible catalog cards.
- **Download picture** explicitly fetches the selected JSON, checks its
  identity/version/size/checksum, and stores it under its own device key.
- Downloaded pictures appear in the normal gallery, work without a connection,
  keep per-picture local progress and survive application restarts.
- The category of each downloaded picture is stored alongside its level ID in
  local preferences. Gallery category filtering works after a full offline
  restart, without loading the remote catalog. Legacy downloads without
  category metadata remain playable (falling back to `patterns` if unknown)
  and receive their category automatically after a successful online catalog
  refresh. The painting's immutable JSON and saved progress are not modified.
- Removing a downloaded picture removes its local JSON, saved category, and
  progress. Clearing application data removes all `pixelhub.*` preferences,
  including downloaded category metadata. Neither operation removes the
  published online picture from the remote catalog.
- Failed connectivity leaves bundled and previously downloaded levels usable.
- Browser localStorage and device storage have quotas; failed writes are
  reported. This initial adapter caps locally downloaded levels at 1000.
  A future move to IndexedDB/files can retain the same repository interface.

## Seven gallery categories without breaking published catalogs (Issue #17)

The new client presents seven public categories: `nature`, `animals`,
`objects`, `masterpieces`, `persian_architecture`, `patterns`, and
`space`. Imported personal artwork remains separate.

Historic classic painting IDs (the six original masterworks and
`online-classic-*` collection) display as `masterpieces`, and the
`online-iran-*` landmark/architecture collection displays as
`persian_architecture`, although immutable published manifests still
say `patterns`. The overlay uses stable IDs rather than translated names.
It works for undownloaded catalog entries, downloads, and offline restarts.
Existing downloaded metadata is migrated on-device without redownloading
artwork, editing level files, or losing progress and favorites.

**Backward compatibility:** The shared `/online/catalog.json` endpoint
must continue publishing only the five old category values. Older app
versions reject unknown values and can lose the entire online catalog.
The Release aggregator rejects incompatible pack categories to guard this.
Do not republish existing ZIPs. Publishing new categories from the server
requires a separate versioned/backwards-compatible catalog rollout first.

## Immutable publication policy (Issue #3)

**Every new picture gets a previously unused `online-...` ID and
`levelVersion: 1`, permanently.** Do not publish updated pixels,
previews, titles, or a higher version under an existing ID. For a correction,
higher-detail remake, or similar picture, publish another `id` with
`levelVersion: 1` in a new immutable Release; retain the previous asset
and its ID. Reuse of an ID (even with a different version) causes the Pages
aggregator to fail. The pack generators also check the version and
duplicates within each new pack. Existing downloads and painting progress
remain untouched: the app only offers pictures not already downloaded.

`schemaVersion` is independent: the level JSON currently uses schema 2,
while `catalog.json` uses schema 1. Neither is a picture update version.
The `version` field in the catalog matches the level's `levelVersion`,
which must be **1 for new pictures**.

**Historical exception only:** before this policy, the original Azadi Tower
was published as `online-iran-azadi-tower` v1 in
`pixelhub-content-iran-landmarks-10-v1`, and a redesigned v2 with the
same ID was published in `pixelhub-content-iran-z-architecture-11-v1`.
To preserve already-published URLs, existing downloads and progress, the
aggregator accepts **exactly this release-tag/ID/version pair**, keeps
both v1 and v2 files, and continues listing v2 in the catalog.
It does not migrate or overwrite device data, and no other duplicated ID
or higher version is accepted. New Azadi Tower revisions must use a new ID.

## Optional animated pixel art

Online pictures may publish an optional animation companion without changing the
immutable level JSON or existing painting progress. New catalog entries can
include `animation: {"bytes":N,"sha256":"...","frameCount":N}`.
The matching immutable Release ZIP must contain
`animations/<levelId>-v<version>.json` in addition to the level and preview.
Older entries have no `animation` field and remain regular still paintings.
Older clients ignore the extra catalog field and continue downloading the still
level.

The sidecar schema is:

```json
{
  "schemaVersion": 1,
  "levelId": "online-example",
  "levelVersion": 1,
  "levelChecksum": "<the level checksum>",
  "frameDurationMs": 180,
  "frames": [
    {"changes": []},
    {"changes": [[15, 2], [16, 0]]}
  ]
}
```

Each frame specifies palette-index replacements at zero-based cell positions
**relative to the completed original image**, not relative to the previous
frame. One frame is valid (a still pose); frame counts range from 1 to 60 and
the frame interval is 60–2000 ms. The checked sidecar must not exceed 2 MiB.
All changes must be within the original grid and palette. The pack validator
checks size, SHA-256, level identity/checksum, timing and every patch.

The app downloads and verifies the entire sidecar **during picture download**,
then stores it locally alongside the original level. A missing/corrupt sidecar
fails that download rather than creating an incomplete animated picture.
Stored animations can replay offline after app restart; removing the
download also removes its frames. Progress and reset remain tied to the
original immutable level only. The app shows animation after completing the
picture (including returning to an already completed painting), with a
still/animated switch. Unfinished or non-animated paintings never animate.

The original bundled `sunflower` v2 has a waving companion under
`apps/game/assets/animations/sunflower-v2.json`. A separate **online**
`online-dancing-sunflower` v1 with eight downloadable frames is generated by
`tool/online_animated_sunflower_pack.py` and published as a new immutable
Release when the Pages workflow runs successfully. Do not modify the bundled
level file or replace an already published online ID to add animation: publish
a fresh ID/pack for any corrected painting. Adding a first animation to an
existing still painting uses a separate checksum-bound companion recipe in
`tool/animation_batches/online-*.json`, with at most ten entries per commit.
Pages renders these frames after validating all original Release packs. The
original ZIPs, levels, previews, IDs, versions and painting checksums are never
changed. Existing Release animations are never overwritten. Recipes pin both
the painting checksum and the generated animation SHA-256; a changed recipe
fails publication instead of replacing previously published frames.

After a successful gallery refresh, the client fetches missing companions for
already downloaded matching paintings in the background, with at most three
requests in flight. Progress is preserved; failed transfers retry on the next
refresh, and saved companions work offline. Actual
public availability depends on completion of the GitHub Pages job.

## Initial sample

After successful Web CI on `main`, the existing **Publish verified Web
artifact** workflow creates `pixelhub-content-sample-v1` once if it does not
exist. Its asset `content.zip` is generated in the Actions runner from
`tool/online_release.py` and contains:

- `catalog.json` (a list of entries)
- `levels/online-balloon-v1.json` (playable 24×24 numbered picture)
- `previews/online-balloon-v1.png` (small preview)

Generated picture files are **not committed to Git**. The sample is an
original hot-air balloon, titled «بالن رنگی» / “Colorful balloon”.

The Pages job combines public `pixelhub-content-*` Release packs and serves
them alongside the independently built Web application under `/Pixelhub/online/`.
The sample only becomes publicly available **after the Pages job completes**.
GitHub Pages must use **Settings → Pages → Build and deployment → GitHub Actions**.

## Six-design collection (October 2026)

The repository now includes reproducible design instructions in
`tool/online_starter_pack.py`. After a **successful Web CI run on main**, the
Pages workflow creates a separate Release named
[`pixelhub-content-starter-6-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-starter-6-v1)
if it does not already exist, attaching one generated `content.zip` with
six schema-v2 numbered level JSON files, six small PNG previews and a pack
catalog. The files are generated in the runner, **not committed to main**:

| Stable level ID | فارسی | English | Category | Canvas |
| --- | --- | --- | --- | --- |
| `online-tulip` | لاله صورتی | Pink Tulip | nature | 16×16 |
| `online-mushroom` | قارچ جنگلی | Forest Mushroom | nature | 16×16 |
| `online-cat-face` | صورت گربه | Cat Face | animals | 24×24 |
| `online-watermelon` | قاچ هندوانه | Watermelon Slice | objects | 16×16 |
| `online-rocket` | موشک کوچک | Little Rocket | space | 24×24 |
| `online-butterfly` | پروانه بنفش | Purple Butterfly | animals | 24×24 |

The existing `online-balloon` sample remains a separate Release. Once both
Release packs have been assembled and Pages deployment has **actually
completed successfully**, the aggregated online catalog should list seven
pictures. A code push alone does not mean the new pack is published. Users
who have the online-gallery-enabled app can then discover the pictures by
opening Gallery and download each on demand.

To author the pack without adding binaries to Git history:
`python3 tool/online_starter_pack.py /tmp/content.zip`. Do not modify a
published pack in place; a redesign requires a fresh ID and version 1.

## Second online collection: 12 additional pictures

`tool/online_collection_pack.py` contains only original drawing instructions,
not the generated art assets. The GitHub Pages workflow generates the
[collection Release](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-collection-12-v1)
`pixelhub-content-collection-12-v1` once, after successful main-branch Web
CI. Its `content.zip` contains 12 versioned JSON levels, 12 PNG previews,
and their metadata manifest; no level files are committed to Git.

| Level ID | فارسی | English | Category | Canvas |
| --- | --- | --- | --- | --- |
| `online-panda` | پاندای بامزه | Cute Panda | animals | 24×24 |
| `online-bunny` | خرگوش سفید | White Bunny | animals | 24×24 |
| `online-turtle` | لاک‌پشت سبز | Green Turtle | animals | 24×24 |
| `online-owl` | جغد کوچک | Little Owl | animals | 24×24 |
| `online-ice-cream` | بستنی توت‌فرنگی | Strawberry Ice Cream | objects | 16×16 |
| `online-donut` | دونات صورتی | Pink Donut | objects | 24×24 |
| `online-coffee` | فنجان قهوه | Coffee Cup | objects | 24×24 |
| `online-cactus` | کاکتوس گلدانی | Potted Cactus | nature | 24×24 |
| `online-autumn-tree` | درخت پاییزی | Autumn Tree | nature | 32×32 |
| `online-rain-cloud` | ابر بارانی | Rain Cloud | nature | 24×24 |
| `online-saturn` | سیاره زحل | Planet Saturn | space | 32×32 |
| `online-astronaut` | فضانورد | Astronaut | space | 32×32 |

The first one-picture sample and the earlier six-picture Release are
preserved; after successful publication and Pages deployment, the public
catalog should contain **19 online pictures in total**. Current users
discover the catalog automatically on gallery entry; full level grids are
downloaded only on approval. The app's online section displays 12 undownloaded
entries initially and offers a control to reveal more.

To regenerate the package outside the repo working tree:
`python3 tool/online_collection_pack.py /tmp/content.zip`.
Publication status must be confirmed from GitHub Actions/Releases;
committing these instructions alone is not proof of live availability.

## Classic masterworks: six hand-drawn pixel-art interpretations

Six new original, simplified 24×24 or 32×32 pixel-art coloring levels are
defined in `tool/online_masterworks_pack.py`. The source creates the
art programmatically without embedding copied painting scans or JPEG/PNG
references. Each level is independently numbered and contains a versioned
schema-v2 grid, ARGB palette, SHA-256 checksum and its own PNG preview.

| Level ID | فارسی | English | Canvas |
| --- | --- | --- | --- |
| `online-mona-lisa` | مونالیزا | Mona Lisa | 32×32 |
| `online-starry-night` | شب پرستاره | The Starry Night | 32×32 |
| `online-the-scream` | جیغ | The Scream | 32×32 |
| `online-sunflowers` | آفتابگردان‌ها | Sunflowers | 24×24 |
| `online-girl-pearl` | دختر با گوشواره مروارید | Girl with a Pearl Earring | 32×32 |
| `online-great-wave` | موج بزرگ | The Great Wave | 32×32 |

**Compatibility:** The entries use the existing `patterns` category instead
of adding a new `masterworks` category. Existing deployed clients enforce a
fixed online category allowlist and reject unknown categories, which would
otherwise break the *entire* online catalog. The painting titles identify
each classic, and the existing Persian/English category label remains valid.

Upon a successful `main` Web CI run, the existing Pages workflow creates
`pixelhub-content-masterworks-6-v1` with one `content.zip` containing the
manifest plus all six JSON grids and PNG previews. The Release is public
and stored **outside git history**, so `git clone` and ordinary APK/AAB
builds do not include the generated art. The Pages publisher aggregates this
pack alongside the existing sample, six-design, and twelve-design Releases.

[GitHub Release page](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-masterworks-6-v1)

After all four pack Releases are published and GitHub Pages deployment
succeeds, there should be **25 online pictures**. This is a target count,
not a claim of live availability until the GitHub Actions run completes.
Download remains an explicit per-picture choice, and saved local progress
and older packs are unaffected.

Generate the package outside the repository with
`python3 tool/online_masterworks_pack.py /tmp/content.zip`. Once published,
do not overwrite version 1 files; improvements require a new level ID with version 1.

## Ten new animals: original pixel-art collection

The source file `tool/online_animals_pack.py` contains reproducible drawing
instructions for **10 additional original animal pictures**. The GitHub Pages
workflow creates the immutable Release
[`pixelhub-content-animals-10-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-animals-10-v1)
after a successful main-branch Web CI run. Its `content.zip` contains
ten schema-v2 color-by-number JSON levels, ten tiny PNG previews and bilingual
catalog metadata. No level assets are committed to Git or bundled in Android.

| ID | فارسی | English | Canvas |
| --- | --- | --- | --- |
| `online-lion` | شیر طلایی | Golden Lion | 32×32 |
| `online-elephant` | فیل مهربان | Gentle Elephant | 32×32 |
| `online-giraffe` | زرافه خال‌دار | Spotted Giraffe | 32×32 |
| `online-penguin` | پنگوئن برفی | Snowy Penguin | 24×24 |
| `online-dolphin` | دلفین بازیگوش | Playful Dolphin | 32×32 |
| `online-koala` | کوآلای خواب‌آلود | Sleepy Koala | 24×24 |
| `online-flamingo` | فلامینگوی صورتی | Pink Flamingo | 32×32 |
| `online-octopus` | اختاپوس بنفش | Purple Octopus | 32×32 |
| `online-deer` | گوزن جنگلی | Forest Deer | 32×32 |
| `online-parrot` | طوطی رنگارنگ | Colorful Parrot | 32×32 |

All ten entries use the already-supported `animals` category, unique IDs and
level version 1, so existing clients do not require an APK rebuild. The
previous 25 online levels are preserved. **35 total pictures** is the
expected catalog count after all five Release packs exist and GitHub Pages
has deployed successfully; a source commit alone does not verify publication.

To generate outside the repository:
`python3 tool/online_animals_pack.py /tmp/content.zip`.
Never overwrite version 1 after publication.

## Iranian landmarks: ten architectural pixel-art pictures

Ten new **original, hand-designed simplified pixel-art representations** of
famous Iranian structures are authored in `tool/online_iran_landmarks_pack.py`.
The drawing instructions, not their JSON/PNG art files, are committed to Git.

After a successful main-branch Web CI run, the existing GitHub Pages workflow
creates the immutable
[`pixelhub-content-iran-landmarks-10-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-iran-landmarks-10-v1)
Release with one `content.zip`. It contains ten schema-v2 numbered JSON levels,
ten PNG previews and a bilingual `catalog.json`. All ten are 48×48 grids for
architectural detail.

| Stable level ID | فارسی | English | Canvas |
| --- | --- | --- | --- |
| `online-iran-persepolis` | تخت جمشید | Persepolis | 48×48 |
| `online-iran-azadi-tower` | برج آزادی | Azadi Tower | 48×48 |
| `online-iran-milad-tower` | برج میلاد | Milad Tower | 48×48 |
| `online-iran-imam-mosque` | مسجد امام اصفهان | Imam Mosque, Isfahan | 48×48 |
| `online-iran-sio-se-pol` | سی‌وسه‌پل | Si-o-se-pol Bridge | 48×48 |
| `online-iran-nasir-ol-molk` | مسجد نصیرالملک | Nasir ol-Molk Mosque | 48×48 |
| `online-iran-arg-e-bam` | ارگ بم | Bam Citadel | 48×48 |
| `online-iran-hafez-tomb` | آرامگاه حافظ | Tomb of Hafez | 48×48 |
| `online-iran-amir-chakhmaq` | میدان امیرچخماق | Amir Chakhmaq Complex | 48×48 |
| `online-iran-golestan-palace` | کاخ گلستان | Golestan Palace | 48×48 |

**Compatibility:** All ten entries use the existing `patterns` category.
Currently deployed clients only accept a fixed category allowlist and would
reject an unrecognized new `landmarks` category. The distinct Persian and
English titles identify each Iranian monument without a client update.

The five existing content packs and their 35 online picture IDs stay intact.
The expected overall catalog total becomes **45 pictures** once all six
Release packs are successfully published and Pages deployment finishes.
Neither code commit nor Release generation alone establishes public
availability. No Android APK/AAB rebuild is needed to fetch compatible new
online content.

To create the ZIP independently, without placing generated pictures in the
working tree:
`python3 tool/online_iran_landmarks_pack.py /tmp/content.zip`.
Published level IDs and versions must remain immutable.

## Detailed landscape collection: ten 64×64 nature paintings

`tool/online_landscapes_pack.py` defines ten fully original landscape drawings
with separate color palettes, layered scenery, and detailed foregrounds. At
**64×64 pixels per painting (4,096 colorable cells)**, these contain more than
the previous 48×48 landmark pictures (2,304 cells). They are simplified
color-by-number pixel art, not rasterized stock photographs.

| Stable level ID | فارسی | English | Canvas |
| --- | --- | --- | --- |
| `online-landscape-sunset-mountains` | غروب کوهستان | Mountain Sunset | 64×64 |
| `online-landscape-alpine-lake` | دریاچه و جنگل | Alpine Lake and Forest | 64×64 |
| `online-landscape-waterfall` | آبشار جنگلی | Forest Waterfall | 64×64 |
| `online-landscape-cottage` | مزرعه و کلبه | Countryside Cottage | 64×64 |
| `online-landscape-golden-desert` | کویر و تپه‌های شنی | Golden Desert Dunes | 64×64 |
| `online-landscape-tropical-beach` | ساحل و دریا | Tropical Beach | 64×64 |
| `online-landscape-misty-forest` | جنگل مه‌آلود | Misty Forest | 64×64 |
| `online-landscape-river-bridge` | رودخانه و پل سنگی | River and Stone Bridge | 64×64 |
| `online-landscape-moonlit-night` | آسمان شب و ماه | Moonlit Mountain Night | 64×64 |
| `online-landscape-flower-valley` | دشت گل‌ها | Wildflower Valley | 64×64 |

A successful **main** Web CI run triggers the existing Pages publisher to
create a new immutable GitHub Release, if missing:
[`pixelhub-content-landscapes-10-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-landscapes-10-v1).
Its `content.zip` contains ten schema-v2 numbered JSON grids, ten PNG
previews and the bilingual catalog. No generated art goes into the git tree
or Android app binary. All ten entries use the existing compatible `nature`
category; this preserves compatibility with existing online-capable Android
and Web clients without shipping a new APK/AAB. Pictures are downloaded on
demand, remain usable offline after download and keep independent progress.

The 45 existing online picture IDs and their Release packs are preserved.
After **all seven** Release packs are published and Pages deployment has
succeeded, the aggregate catalog should contain **55 online pictures**.
A Git commit alone does not prove that the public catalog has updated.

To reproduce the release-only asset from the repository root, outside Git
history: `python3 tool/online_landscapes_pack.py /tmp/content.zip`.
Do not overwrite published version 1 assets; future design edits need
a fresh level ID and version 1.

## Persian architectural abstractions and the redesigned Azadi Tower

`tool/online_iran_architecture_pack.py` authors **11 original numbered
pixel-art levels** for the online gallery. Ten are new 64×64 abstract
interpretations of Iranian architecture. The eleventh is a full redesign of
Azadi Tower at 80×80 pixels (6,400 colorable cells), with a taller,
recognizable open pointed arch, four flared marble pier faces, glazed
turquoise lattice details and perspective plaza paving.

**Archived Azadi Tower redesign (historical exception):** This pack already
published `online-iran-azadi-tower` at `levelVersion: 2` with its
own checksum and v2 files. The original v1 remains in the prior Release.
For compatibility only, the assembler allows these two specific, unchanged
Releases and continues to show v2 in the aggregated catalog. Do not use
this pattern for any newly authored or revised picture.

| Stable level ID | Version | فارسی | English | Grid |
| --- | --- | --- | --- | --- |
| `online-iran-azadi-tower` | **2** | برج آزادی - بازطراحی | Azadi Tower - Redesigned | **80×80** |
| `online-iran-abstract-muqarnas` | 1 | مقرنس فیروزه‌ای | Turquoise Muqarnas | 64×64 |
| `online-iran-abstract-dome` | 1 | گنبد هندسی ایرانی | Geometric Persian Dome | 64×64 |
| `online-iran-abstract-orsi` | 1 | پنجره ارسی رنگی | Colorful Orsi Window | 64×64 |
| `online-iran-abstract-eslimi` | 1 | کاشی‌کاری اسلیمی | Arabesque Tile Scroll | 64×64 |
| `online-iran-abstract-arches` | 1 | قوس‌های متقارن ایرانی | Receding Persian Arches | 64×64 |
| `online-iran-abstract-windcatcher` | 1 | هندسه بادگیر | Windcatcher Geometry | 64×64 |
| `online-iran-abstract-shamsa` | 1 | شمسه هشت‌پر | Eight-Point Shamsa | 64×64 |
| `online-iran-abstract-mosque` | 1 | نمای هندسی مسجد ایرانی | Symmetrical Persian Mosque | 64×64 |
| `online-iran-abstract-brickwork` | 1 | آجر و کاشی ایرانی | Persian Brick and Tile Weave | 64×64 |
| `online-iran-abstract-iwan` | 1 | ایوان و حیاط ایرانی | Abstract Iwan Courtyard | 64×64 |

The content pack uses the existing **`patterns`** category, bilingual
titles, unique stable IDs for new drawings, palette-indexed cells and
canonical SHA-256 level checksums. After a successful main Web CI run, the
Pages workflow creates the immutable Release
[`pixelhub-content-iran-z-architecture-11-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-iran-z-architecture-11-v1)
with a downloadable `content.zip` containing 11 schema-v2 JSON levels,
11 PNG previews and one bilingual manifest. These assets are never placed
in Git history or bundled into an APK. The tag intentionally sorts
lexicographically *after* `pixelhub-content-iran-landmarks-10-v1`,
so the assembler can recognize the sole archived v1-to-v2 exception,
not because future content versions may replace one another.

The previous **55 unique online pictures** are preserved. The target
aggregate is **65 unique pictures**, not 66, because Azadi v2 supersedes
the v1 listing with the same ID. Both underlying numbered version assets
remain available. Web CI, Release creation and GitHub Pages deployment
must finish successfully before the upgraded gallery is publicly visible;
committing this code does not confirm its deployment.

**Important for prior downloads:** devices with Azadi v1 or v2 keep their
local painting and progress. The gallery does not offer updates to an
already-downloaded ID. Users retain their copy; new designs appear only
as separate IDs. No Android rebuild is required for newly published art.

Reproducible release-only command:
`python3 tool/online_iran_architecture_pack.py /tmp/content.zip`.
Never modify a published release in place; subsequent revisions require
a new level ID, `levelVersion: 1`, and a new Release tag.

## More unique animal pictures: twenty 48×48 levels

`tool/online_animals_more_pack.py` authors a further **20 original
color-by-number animal designs**, each with its own hand-drawn pixel
illustration, a 48×48 canvas (2,304 numbered cells), a dedicated ARGB
color palette, and titles in Persian and English. These are **new species**
not present in the starter, collection or original ten-animal packs.

| Stable ID | فارسی | English |
| --- | --- | --- |
| `online-fox` | روباه نارنجی | Red Fox |
| `online-wolf` | گرگ خاکستری | Gray Wolf |
| `online-brown-bear` | خرس قهوه‌ای | Brown Bear |
| `online-zebra` | گورخر راه‌راه | Striped Zebra |
| `online-tiger` | ببر نارنجی | Orange Tiger |
| `online-cheetah` | یوزپلنگ خال‌دار | Spotted Cheetah |
| `online-kangaroo` | کانگوروی بازیگوش | Playful Kangaroo |
| `online-hippopotamus` | اسب آبی | Hippopotamus |
| `online-rhinoceros` | کرگدن خاکستری | Gray Rhinoceros |
| `online-crocodile` | تمساح سبز | Green Crocodile |
| `online-toucan` | توکان رنگارنگ | Colorful Toucan |
| `online-peacock` | طاووس پرنقش | Bright Peacock |
| `online-hedgehog` | جوجه‌تیغی | Hedgehog |
| `online-raccoon` | راکون نقاب‌دار | Masked Raccoon |
| `online-sloth` | تنبل درختی | Tree Sloth |
| `online-seal` | فک دریایی | Harbor Seal |
| `online-whale` | نهنگ آبی | Blue Whale |
| `online-shark` | کوسه اقیانوس | Ocean Shark |
| `online-frog` | قورباغه سبز | Green Frog |
| `online-chameleon` | آفتاب‌پرست | Chameleon |

All use the existing compatible `animals` category, unique
`online-` IDs and `levelVersion: 1`. On the next successful main
Web CI run, the Pages publisher will create immutable Release
[`pixelhub-content-animals-more-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-animals-more-20-v1)
with `content.zip`: 20 schema-v2 JSON levels, 20 PNG previews,
and one bilingual `catalog.json`. The aggregator combines this with
existing Releases; generated assets are not stored in the Git repository
or included in an APK. Pictures downloaded once remain locally available
without an internet connection.

The expected number of **distinct online pictures increases from 65
to 85** when all prior packs and this new pack are published and Pages
deployment succeeds. No Android release or APK rebuild is necessary.
A git commit only installs the *publishing instructions*: it does not
verify that release generation or public delivery succeeded.

Create an asset independently, outside the tracked source tree:
`python3 tool/online_animals_more_pack.py /tmp/content.zip`.
Published artwork version 1 must remain unchanged.

## Twenty additional classic painting interpretations (64×64)

`tool/online_masterworks_20_pack.py` hand-draws **20 more original,
simplified interpretations of well-known historical paintings** in pixel
art, without redistributing scanned originals or third-party raster imagery.
Every artwork has its own custom ARGB palette, **64×64 numbered canvas
(4,096 cells)**, Persian and English title, stable ID, version-1 schema-v2
JSON, checksum and small generated PNG preview.

| Stable level ID | فارسی | Original title | Artist |
| --- | --- | --- | --- |
| `online-classic-birth-venus` | زایش ونوس | The Birth of Venus | Sandro Botticelli |
| `online-classic-creation-adam` | آفرینش آدم | The Creation of Adam | Michelangelo |
| `online-classic-last-supper` | شام آخر | The Last Supper | Leonardo da Vinci |
| `online-classic-school-athens` | مکتب آتن | The School of Athens | Raphael |
| `online-classic-night-watch` | نگهبان شب | The Night Watch | Rembrandt |
| `online-classic-milkmaid` | زن شیرفروش | The Milkmaid | Johannes Vermeer |
| `online-classic-las-meninas` | ندیمه‌ها | Las Meninas | Diego Velázquez |
| `online-classic-third-may` | سوم ماه مه ۱۸۰۸ | The Third of May 1808 | Francisco Goya |
| `online-classic-liberty-leading` | آزادی هدایتگر مردم | Liberty Leading the People | Eugène Delacroix |
| `online-classic-wanderer-fog` | مسافر بر فراز دریای مه | Wanderer above the Sea of Fog | Caspar David Friedrich |
| `online-classic-fighting-temeraire` | تمریر جنگجو | The Fighting Temeraire | J. M. W. Turner |
| `online-classic-hay-wain` | گاری علف خشک | The Hay Wain | John Constable |
| `online-classic-impression-sunrise` | برداشت، طلوع آفتاب | Impression, Sunrise | Claude Monet |
| `online-classic-water-lilies` | نیلوفرهای آبی | Water Lilies | Claude Monet |
| `online-classic-moulin-galette` | رقص در مولن دو لا گالت | Dance at Le Moulin de la Galette | Pierre-Auguste Renoir |
| `online-classic-grande-jatte` | یکشنبه در جزیره گراند ژات | A Sunday Afternoon on La Grande Jatte | Georges Seurat |
| `online-classic-klimt-kiss` | بوسه | The Kiss | Gustav Klimt |
| `online-classic-card-players` | ورق‌بازان | The Card Players | Paul Cézanne |
| `online-classic-wheatfield-crows` | مزرعه گندم با کلاغ‌ها | Wheatfield with Crows | Vincent van Gogh |
| `online-classic-sleeping-gypsy` | کولی خفته | The Sleeping Gypsy | Henri Rousseau |

All twenty IDs are unique and deliberately avoid the six existing
masterpiece interpretations (Mona Lisa, The Starry Night, The Scream,
Sunflowers, Girl with a Pearl Earring and The Great Wave). The catalog
category remains the supported `patterns` value, since adding a new
`masterworks` category would be rejected by existing online clients.

Upon a successful **main** Web CI run, the existing Pages workflow creates
the immutable Release
[`pixelhub-content-masterworks-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-masterworks-20-v1)
and uploads its `content.zip` containing 20 JSON levels, 20 previews
and the bilingual catalog. The release aggregator preserves all previous
IDs and progress; assets are generated outside git and never included
in Android APK/AAB bundles.

The target is **105 distinct online paintings**, up from 85, once all
releases exist and the Pages deployment completes. Adding the publisher
code to git alone does not verify the Release exists or that the online
gallery has updated. No Android rebuild is required for new online content.

To reproduce only the release artifact outside the working tree:
`python3 tool/online_masterworks_20_pack.py /tmp/content.zip`.
Do not overwrite a published picture; use a new ID at version 1.

## Thirty original everyday objects (48×48)

`tool/online_objects_30_pack.py` contains **30 independent, hand-authored pixel-art pictures** of everyday objects. Each is a numbered 48×48 grid (2,304 coloring cells), with a bilingual Persian/English title, twelve ARGB palette entries, checksum, and a PNG preview. All IDs are unique, use level version 1, and use the existing compatible `objects` category rather than introducing an unsupported client category.

| Stable level ID | فارسی | English |
| --- | --- | --- |
| `online-object-alarm-clock` | ساعت زنگ‌دار | Alarm Clock |
| `online-object-vintage-camera` | دوربین عکاسی | Vintage Camera |
| `online-object-headphones` | هدفون | Headphones |
| `online-object-electric-guitar` | گیتار برقی | Electric Guitar |
| `online-object-retro-radio` | رادیوی قدیمی | Retro Radio |
| `online-object-desk-lamp` | چراغ مطالعه | Desk Lamp |
| `online-object-porcelain-teapot` | قوری چینی | Porcelain Teapot |
| `online-object-rainbow-umbrella` | چتر رنگی | Rainbow Umbrella |
| `online-object-backpack` | کوله‌پشتی | Backpack |
| `online-object-running-sneaker` | کفش کتانی | Running Sneaker |
| `online-object-city-bicycle` | دوچرخه | City Bicycle |
| `online-object-sailboat` | قایق بادبانی | Sailboat |
| `online-object-steam-train` | قطار بخار | Steam Train |
| `online-object-travel-suitcase` | چمدان سفر | Travel Suitcase |
| `online-object-treasure-chest` | صندوقچه گنج | Treasure Chest |
| `online-object-hourglass` | ساعت شنی | Hourglass |
| `online-object-telescope` | تلسکوپ | Telescope |
| `online-object-microscope` | میکروسکوپ | Microscope |
| `online-object-toy-robot` | ربات اسباب‌بازی | Toy Robot |
| `online-object-game-controller` | دسته بازی | Game Controller |
| `online-object-typewriter` | ماشین تحریر | Typewriter |
| `online-object-camping-lantern` | فانوس کمپ | Camping Lantern |
| `online-object-world-globe` | کره جغرافیا | World Globe |
| `online-object-magnetic-compass` | قطب‌نمای سفر | Compass |
| `online-object-paint-palette` | پالت نقاشی | Paint Palette |
| `online-object-book-stack` | کتاب‌های رنگی | Stacked Books |
| `online-object-birthday-gift` | جعبه هدیه | Gift Box |
| `online-object-table-fan` | پنکه رومیزی | Table Fan |
| `online-object-sewing-machine` | چرخ خیاطی | Sewing Machine |
| `online-object-fountain-pen` | خودنویس | Fountain Pen |

After a successful `main` Web CI run, the Pages publisher creates the immutable `pixelhub-content-objects-30-v1` Release (if absent): [Release page](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-objects-30-v1). The `content.zip` asset contains 30 numbered JSON levels, 30 previews, and `catalog.json`. The aggregation step merges them into the public catalog along with all older Release packs, without modifying earlier artwork or saved progress.

The expected total becomes **135 distinct online pictures**, up from 105, after all content Releases have been created and GitHub Pages has deployed successfully. Adding source code is **not** evidence that the Release, public catalog, or app deployment is already live. Check Actions/Pages and the public online catalog for confirmation. Generated art stays outside Git history and Android APK/AAB packages; compatible clients can download the pictures without an app rebuild.

To create the pack manually outside the tracked working tree: `python3 tool/online_objects_30_pack.py /tmp/content.zip`. Once published, never overwrite an immutable version-1 picture; publish a new ID with level version 1 for redesigned art.

## Twenty playful miniatures (48×48)

`tool/online_playful_20_pack.py` defines **20 distinct original, whimsical
color-by-number illustrations**, each with a 48×48 pixel grid, a bilingual
Persian/English title, a stable unused `online-playful-...` ID and
`levelVersion: 1`. They are playful toys, emoji-like characters, sweets
and cheerful motifs, designed for the mobile gallery.

| ID | فارسی | English | Online category |
| --- | --- | --- | --- |
| `online-playful-smiling-sun` | خورشید خندان | Smiling Sun | `nature` |
| `online-playful-rainbow-cloud` | ابر رنگین‌کمانی | Rainbow Cloud | `nature` |
| `online-playful-heart-smile` | قلب مهربان | Smiling Heart | `patterns` |
| `online-playful-lucky-clover` | شبدر خوش‌شانس | Lucky Clover | `nature` |
| `online-playful-friendly-ghost` | روح بازیگوش | Friendly Ghost | `patterns` |
| `online-playful-one-eyed-monster` | هیولای یک‌چشم | One-Eyed Monster | `patterns` |
| `online-playful-flying-saucer` | بشقاب‌پرنده بامزه | Cute UFO | `space` |
| `online-playful-magic-wand` | چوب جادویی | Magic Wand | `objects` |
| `online-playful-party-hat` | کلاه جشن | Party Hat | `objects` |
| `online-playful-birthday-cake` | کیک تولد رنگی | Birthday Cake | `objects` |
| `online-playful-popcorn-carton` | پاپ‌کورن خندان | Smiling Popcorn | `objects` |
| `online-playful-bubble-tea` | بابل‌تی بامزه | Bubble Tea | `objects` |
| `online-playful-rubber-duck` | اردک اسباب‌بازی | Rubber Duck | `objects` |
| `online-playful-teddy-bear` | خرس عروسکی | Teddy Bear | `objects` |
| `online-playful-rainbow-yo-yo` | یویوی رنگی | Rainbow Yo-yo | `objects` |
| `online-playful-paper-kite` | بادبادک خندان | Paper Kite | `objects` |
| `online-playful-smiling-moon` | ماه خندان | Smiling Moon | `space` |
| `online-playful-star-buddy` | ستاره بامزه | Cute Star Buddy | `patterns` |
| `online-playful-neon-jellyfish` | عروس دریایی نئونی | Neon Jellyfish | `animals` |
| `online-playful-candy-land` | سرزمین آب‌نبات | Candy Land | `patterns` |

The categories are intentionally limited to the five values older online
clients understand (`nature`, `animals`, `objects`, `patterns`, and
`space`). The currently deployed app does not need a dedicated `playful`
category or any migration to discover these additions.

The Pages workflow generates an immutable Release named
[`pixelhub-content-playful-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-playful-20-v1)
**only after successful main Web CI**, provided the tag does not exist.
Its `content.zip` has 20 numbered schema-v2 JSON files, 20 small PNG previews
and a catalog manifest. All art bytes remain Release-only, off the git tree
and out of the Android bundle. Each painting can be downloaded independently,
then colored offline; all existing levels and saved progress are preserved.

The target becomes **155 distinct online pictures**, up from 135, *after*
the Release is actually created, assembled and GitHub Pages deployment succeeds.
A Git commit alone does not establish public availability. Check the
[Pages publishing workflow](https://github.com/abolfazl2600/Pixelhub/actions/workflows/web-pages.yml)
and live `/Pixelhub/online/catalog.json` for confirmed publication.

Generate the new archive outside the tracked tree:
`python3 tool/online_playful_20_pack.py /tmp/content.zip`.
Once published, never change the bytes or identifiers of this Release; a
redesign requires a fresh ID and its own new immutable Release.

## Twenty new Iranian landmarks, neighborhoods, landscapes and crafts (64×64)

`tool/online_iranian_mix_20_pack.py` contains twenty **independently
drawn, original 64×64 pixel-art coloring pictures**, rather than copies
of historic photos or previous online levels. The collection combines
additional Iranian architectural landmarks, natural scenery, craftwork,
traditional music and seasonal ceremonies.

| Stable level ID | فارسی | English | Public category |
| --- | --- | --- | --- |
| `online-iran-blue-mosque-tabriz` | مسجد کبود تبریز | Blue Mosque of Tabriz | `patterns` |
| `online-iran-khaju-bridge` | پل خواجو | Khaju Bridge | `patterns` |
| `online-iran-ali-qapu` | عمارت عالی‌قاپو | Ali Qapu Palace | `patterns` |
| `online-iran-chehel-sotoun` | کاخ چهل‌ستون | Chehel Sotoun Palace | `patterns` |
| `online-iran-shah-cheragh` | شاه‌چراغ | Shah Cheragh Shrine | `patterns` |
| `online-iran-fin-garden` | باغ فین کاشان | Fin Garden | `nature` |
| `online-iran-eram-garden` | باغ ارم شیراز | Eram Garden | `nature` |
| `online-iran-masuleh-village` | خانه‌های ماسوله | Masuleh Village | `patterns` |
| `online-iran-kandovan` | روستای کندوان | Kandovan Village | `patterns` |
| `online-iran-lut-kaluts` | کلوت‌های کویر لوت | Lut Desert Kaluts | `nature` |
| `online-iran-anzali-lagoon` | تالاب انزلی | Anzali Lagoon | `nature` |
| `online-iran-damavand` | قله دماوند | Mount Damavand | `nature` |
| `online-iran-persian-carpet` | فرش ایرانی | Persian Carpet Medallion | `patterns` |
| `online-iran-minakari-plate` | بشقاب میناکاری | Minakari Plate | `objects` |
| `online-iran-khatam-box` | جعبه خاتم‌کاری | Khatamkari Box | `objects` |
| `online-iran-samovar-tea` | سماور و استکان چای | Samovar and Tea Glass | `objects` |
| `online-iran-santur` | سنتور | Santur | `objects` |
| `online-iran-tombak` | تنبک | Tombak Drum | `objects` |
| `online-iran-haft-sin` | سفره هفت‌سین | Haft-Seen Table | `objects` |
| `online-iran-yalda-pomegranate` | انار شب یلدا | Yalda Pomegranate | `objects` |

Every image has `schemaVersion: 2`, `levelVersion: 1`, a bilingual
title, distinct identifier, a numbered 64×64 grid, checksum, and a
PNG preview. Existing published artworks and local painting progress
are not changed. Architecture and carpet motifs deliberately use the
legacy `patterns` category; natural landscapes use `nature`; crafts and
cultural objects use `objects`. These values remain compatible with
old online clients even though the current gallery renders some old
architecture under its own visual filter.

The Pages workflow publishes these illustrations through the immutable
[`pixelhub-content-iranian-mix-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-iranian-mix-20-v1)
Release after a **successful Web CI run on `main`**, provided that
Release does not already exist. Its generated `content.zip` contains
20 schema-v2 JSON levels, 20 PNG previews, and a `catalog.json`.
Generated assets belong to the Release, **not the Git repository or
APK/AAB**. Online clients can download the paintings individually
and retain them offline.

The expected aggregate catalog total becomes **175** online images,
up from 155, once all content packs exist and GitHub Pages deploys.
Committing source code alone does not establish that the Release is
public or that the deployed catalog already contains these entries.
Confirm publication via the Pages workflow and live catalog endpoint.

To generate the Release-only asset outside the working tree:
`python3 tool/online_iranian_mix_20_pack.py /tmp/content.zip`.
Never overwrite the immutable v1 art; future improvements need a new ID.

## Publish more pictures

1. Create one or more schema-v2 level JSON files with unique `online-...`
   IDs not used by any earlier Release, `levelVersion: 1`, titles in Persian and English, ARGB palette,
   pixel indices and the canonical SHA-256 checksum already used by PixelHub.
2. Make a PNG preview for each picture. Use consistent names:
   `levels/<id>-v1.json` and `previews/<id>-v1.png`.
3. Create a ZIP named **`content.zip`** containing these files and a
   `catalog.json` whose entries contain `id`, `version`, `title`,
   `titleEn`, `category`, `width`, `height`, `bytes`, `checksum`.
   `bytes` is the UTF-8 JSON byte count; checksum is the schema-v2 level
   checksum, **not a hash of the JSON file**.
4. Create a new, published **GitHub Release** on this same repository, with a
   tag starting `pixelhub-content-`, attach the ZIP, and publish it.
5. The Pages workflow is triggered by Release publishing. Never edit or
   replace a previously published Release asset. If a deployment fails,
   rerun the existing **Publish verified Web artifact** workflow without
   modifying published content.
6. Open the Pages `online/catalog.json` endpoint and check that the intended
   levels appear; opening the gallery will then discover them automatically.

**No Android APK or AAB rebuild is required** to publish compatible pictures.
The Web site is republished to mirror the new content, but its Web application
artifact remains the last verified build. Android builds only through their
separate manual workflow.

Release packs are immutable. No picture is republished under the same ID,
even with a higher `levelVersion`. All new pictures have their own ID and
`levelVersion: 1`. Local progress is keyed to ID, version and checksum;
keep every published file and checksum unchanged. Avoid deleting Releases
that may still be used by users.

The publisher checks picture content against catalog metadata and writes the
aggregate catalog **after** copying the referenced files. There is deliberately
no client token, authentication service, dedicated database or Cloudflare
dependency. This lightweight static distribution can later be moved behind a
CDN without changing saved level IDs.

## Known constraints

- This version lists at most 10,000 remote catalog entries and does not have
  paging yet; for a larger library add paginated catalogs.
- Web downloaded files currently use per-level browser storage, which is quota
  limited; Android likewise has a local 1000-level safety limit.
- Downloaded IDs remain hidden from the online download list; new pictures
  always use new IDs. A deliberately narrow `retiredIds` hint is supported for
  replacing obsolete art, but there is no generic per-picture update flow.
- Public GitHub Releases/Pages have their own fair-use, size and bandwidth
  limits. Move distribution to a dedicated CDN when traffic justifies it.

## Issue #23: artwork quality corrections without an application release (October 2026)

Six bundled paintings have been redrawn **in their existing file paths with
their existing stable IDs**. They are: `planet` (128×128, fully redesigned
recognizable world and orbital ring), `tree` (32×32, organic foliage/trunk),
`star` (32×32, five-point silhouette instead of a plus sign), `gem` (64×64,
distinct faceted gemstone), `mountain` (increased from 16×16 to 32×32 with
snow peaks and depth), and `owl` (increased from 16×16 to 32×32 with large eyes,
ear tufts and feathers). Their corresponding `animations/*-v1.json` files
were rebuilt against the new checksums, and each has a visible highlight
pose that returns to the base pixels.

**Bundled content cannot be hot-swapped on already installed Android
binaries.** Replacing it in the repository changes future builds and the
next verified Web deployment only. This issue intentionally does not bump
`pubspec.yaml` version or trigger a new Android release. Existing Android
installations retain their former six built-in paintings until a future
app update; prior saved progress for these six may reset on that update
because their checksums changed. No data migration is required.

The original published 32×32 `online-starry-night` is an immutable Release
asset. It is **not overwritten**: `tool/online_starry_night_replacement_pack.py`
generates a new, hand-drawn **80×80** painting with layered sky strokes,
double spirals, luminous stars, crescent moon, village, church and cypress.
It is published as a content-only Release named
`pixelhub-content-starry-night-detailed-1-v1` and has the internal ID
`online-classic-starry-night-detailed`, but retains the existing bilingual gallery
title and category. No app release/version bump is involved. The publisher
keeps old immutable file URLs intact and **excludes the old ID from the
public catalog**, with `retiredIds: ["online-starry-night"]` in the refreshed
catalog. It refuses publication if the replacement is missing. The new file
path guarantees that immutable edge caches cannot return the obsolete grid.

Updated Web/newly built app clients validate `retiredIds` and, after a
successful catalog fetch, remove a locally downloaded obsolete ID, including
its progress and animation, before exposing the replacement. A failed or
malformed catalog never deletes downloaded art. **Previously distributed
Android APKs cannot read this new retirement hint**, so a user who already
downloaded the original Starry Night on an old binary may temporarily see
both their old local copy and the new online listing until they remove their
old download or install a future app update. This limitation is intrinsic to
the no-new-APK requirement and is not silently concealed.

Audit scope: the remaining bundled and online painting IDs/definitions were
left unchanged unless they were among the seven specified references. This
avoids introducing accidental new duplicates or losing unrelated saved
work. New content availability still depends on a successful
`Checks and Web artifacts` workflow, content-only Release publication,
`Publish verified Web artifact` assembly, and Pages deployment. The
regression suite checks all six redraw checksums and animation companions,
the 80×80 online grid, correct replacement catalog behavior and preservation
of original archived content.


## Ten animated abstract patterns on an exact 8×8 grid

The reproducible generator `tool/online_abstract_8_pack.py` defines ten simple,
distinct abstract patterns: Color Orbit, Geometric Wave, Pixel Bloom, Color
Spiral, Floating Bars, Shimmer Diamond, Cross Weave, Pixel Burst, Concentric
Ripple, and Pixel Kaleidoscope. Each artwork is exactly 8×8 (64 discrete cells),
uses the existing `patterns` category, has Persian/English titles and a crisp
PNG preview, and includes an eight-frame animation sidecar.

Each design has its own written motion scenario in the generated
`animation-scenarios.json` (also inside the immutable Release ZIP). Motion is
limited to controlled accent-color changes; cell geometry and the original
numbered level remain fixed. Frames use 180 ms timing and a symmetric looping
sequence. The sidecars are checksum-bound to their exact level, downloaded with
the picture, and remain available offline after download.

After a successful main Web CI run, Pages workflow creates the immutable
`pixelhub-content-abstract-mini-10-v1` Release and aggregates its catalog,
previews, levels, and animation sidecars into the online gallery. Source code
being merged is not proof of public availability: confirm the Pages workflow
and the deployed `/Pixelhub/online/catalog.json` before announcing release.

Generate a pack locally with:
`python3 tool/online_abstract_8_pack.py /tmp/content.zip`.

## Twenty animated 12×12 online mini pictures

The `tool/online_animated_12_pack.py` generator authors **20 new** and
independently drawn 12×12 color-by-number mini pictures. It produces a
single immutable `pixelhub-content-animated-mini-12-20-v1` Release asset,
`content.zip`, through the Pages publication workflow after successful main
CI. Generated assets are not bundled with the app or committed to the repo.
Existing paintings and user progress are unchanged.

| English | فارسی | Animation |
| --- | --- | --- |
| Traffic Light | چراغ راهنمایی | Traffic lights change |
| Charging Battery | باتری شارژی | Charge meter fills |
| Wi-Fi Signal | علامت وای‌فای | Signal waves pulse |
| Notification Bell | زنگ اعلان | Bell rings |
| Puzzle Piece | قطعه پازل | Interlocking sparkle |
| Pixel Pointer | اشاره‌گر پیکسلی | Click sparkle |
| Gumball Machine | دستگاه آدامس | Candy ball drops |
| Watering Can | آبپاش کوچک | Falling drops |
| Mailbox | صندوق نامه | Raising flag |
| Little Padlock | قفل کوچک | Opening shackle |
| Mini Joystick | جوی‌استیک | Tilting handle |
| Singing Microphone | میکروفون آواز | Sound waves |
| Snow Globe | گوی برفی | Falling snow |
| Camping Tent | چادر شبانه | Twinkling stars |
| Satellite Dish | بشقاب ماهواره‌ای | Radiating signal |
| Fish Bowl | تنگ ماهی | Swimming fish |
| Lighthouse Beam | فانوس دریایی | Sweeping beam |
| Spinning Top | فرفره چرخان | Wobble and sparkles |
| Little Snail | حلزون کوچولو | Antenna wiggle |
| Color Pinwheel | فرفره رنگی | Rotating blade highlights |

All pictures have **144 numbered cells**, six ARGB palette entries,
Persian/English labels, unique `online-mini12-*` IDs and `levelVersion: 1`.
The legacy-compatible categories are `objects`, `animals`, `nature` and
`space`. Animation companions provide exactly eight frames (180 ms each),
computed as palette-index patches relative to the unchanged base picture
and bound to its checksum. The first frame has no changes. Playback starts
after the picture is completed and is replayable offline. A bilingual
`animation-scenarios.json` describes each motion.

Build and test:

    python3 tool/online_animated_12_pack.py /tmp/content.zip
    python3 -m unittest discover -s tool/tests -p 'test_online_animated_12_pack.py' -v

The source change alone is not proof of a live release. Confirm successful
main CI and Pages deployment and check `/Pixelhub/online/catalog.json`.

## Ten animated 64x64 public-domain masterpieces

New authoring source `tool/online_animated_masterworks_64_pack.py` creates
ten independently drawn, **exactly 64×64** color-by-number interpretations.
The source does not embed or resize painting scans. The generator writes
a **release-only immutable** `content.zip` containing bilingual JSON levels,
PNG previews, downloadable checksum-bound animation companions, and
bilingual `animation-scenarios.json`. Pictures keep `levelVersion: 1` and
fresh IDs prefixed `online-classic-animated64-`, which the client displays
in the `masterpieces` gallery using its existing category overlay. The
legacy online catalog value remains `patterns` for older client support.

| New ID suffix | Persian title | Original painting | Artist | Animation |
| --- | --- | --- | --- | --- |
| whistlers-mother | مادر ویسلر | Whistler's Mother | James McNeill Whistler | Curtain shimmer |
| arnolfini-portrait | پرتره آرنولفینی | The Arnolfini Portrait | Jan van Eyck | Mirror and chandelier glow |
| bedroom-arles | اتاق خواب در آرل | The Bedroom in Arles | Vincent van Gogh | Window light |
| cafe-terrace-night | تراس کافه در شب | Café Terrace at Night | Vincent van Gogh | Stars and lamps |
| almond-blossoms | شکوفه‌های بادام | Almond Blossoms | Vincent van Gogh | Moving petals |
| the-gleaners | خوشه‌چینان | The Gleaners | Jean-François Millet | Wheat shimmer |
| the-swing | تاب | The Swing | Jean-Honoré Fragonard | Rope and dress |
| woman-parasol | زن با چتر آفتابی | Woman with a Parasol | Claude Monet | Clouds and umbrella |
| lady-ermine | بانویی با قاقم | Lady with an Ermine | Leonardo da Vinci | Ermine blinking |
| bar-folies-bergere | بار در فولی‌برژر | A Bar at the Folies-Bergère | Édouard Manet | Mirror/bottle glimmer |

All paintings have eight 180 ms frames described as sparse replacements
from the original completed still, not incremental changes. Original
numbered grids and progress are never mutated. The existing animation
download and completed-painting viewer work offline after download.

To generate locally:

    python3 tool/online_animated_masterworks_64_pack.py /tmp/content.zip
    python3 -m unittest discover -s tool/tests -p 'test_online_animated_masterworks_64_pack.py' -v

After successful main CI, the Pages workflow publishes the
`pixelhub-content-animated-masterworks-64-10-v1` GitHub Release, if absent,
and assembles the online catalog. Verify the Release and successful Pages
deployment before claiming public availability. No existing release assets,
artwork IDs, download checksums or progress are replaced.

## Fifteen new animated 64×64 classic paintings

The reproducible generator `tool/online_animated_masterworks_64_15_pack.py`
creates fifteen new independently authored 64×64 color-by-number paintings.
Artwork instructions are maintained in
`tool/online_animated_masterworks_64_15_designs.py`. Painting scans and
generated grids/previews are not committed or bundled into the application.

| ID suffix | فارسی | English | Animated detail |
| --- | --- | --- | --- |
| primavera | بهار | Primavera | flowers and petals |
| tower-babel | برج بابل | The Tower of Babel | illuminated tiers and moving clouds |
| hunters-snow | شکارچیان در برف | Hunters in the Snow | falling snow and frozen pond |
| ophelia | اوفلیا | Ophelia | river ripples and floating blossoms |
| lady-shalott | بانوی شالوت | The Lady of Shalott | candles and moving water |
| olympia | المپیا | Olympia | curtain lighting and flowers |
| luncheon-grass | ناهار روی چمنزار | Luncheon on the Grass | dappled sunlight |
| childs-bath | حمام کودک | The Child's Bath | rippling bathwater |
| boating-party | مهمانی قایق‌سواری | The Boating Party | boat rocking and water shimmer |
| ballet-class | کلاس باله | The Ballet Class | tutu and studio light |
| blue-dancers | رقصندگان آبی | Blue Dancers | shimmering blue tutus |
| view-delft | نمای دلفت | View of Delft | canal reflections and clouds |
| astronomer | ستاره‌شناس | The Astronomer | window light on celestial globe |
| irises | زنبق‌ها | Irises | swaying iris petals |
| red-vineyard | تاکستان سرخ | The Red Vineyard | sunlit vines and reflected light |

Every picture uses a **previously unused** immutable ID with
`online-classic-animated64-` prefix and `levelVersion: 1`. Levels are
exactly 4096 cells with bilingual titles and individual palettes.
The published category remains the legacy-compatible `patterns`, and the
existing `online-classic-*` overlay presents them in `masterpieces`.
Each painting includes a downloadable checksum-bound sidecar with eight
independently delta-coded animation frames at 180 ms. Original completed
artwork and user painting progress are never overwritten; animations work
offline after downloading and only play on completed paintings.

A successful main CI triggers the Pages publication workflow to create the
immutable `pixelhub-content-animated-classics-64-15-v1` GitHub Release
and aggregate its `content.zip` into the online catalog. New content
availability requires a completed successful Release/Pages deployment.

Build/test:

    python3 tool/online_animated_masterworks_64_15_pack.py /tmp/content.zip
    python3 -m unittest discover -s tool/tests -p 'test_online_animated_masterworks_64_15_pack.py' -v


## Twenty new original Iranian illustrations on exact 65×65 grids (October 2026)

The reproducible source `tool/online_iran_more_20_pack.py` defines **20 unique
65×65 color-by-number pixel-art levels**, each with a bilingual title and an
immutable `online-iran-*-65` ID, `levelVersion: 1`, schema-v2 JSON, palette,
grid checksum, and corresponding lossless PNG preview. None of the existing
level IDs are replaced. These are new subjects not included in the earlier
Iranian landmarks, architectural abstracts, Iranian mix, or 23-heritage packs.

| Stable level ID | فارسی | English | Category |
| --- | --- | --- | --- |
| `online-iran-tabiat-bridge-65` | پل طبیعت تهران | Tabiat Bridge | patterns |
| `online-iran-quran-gate-65` | دروازه قرآن شیراز | Quran Gate | patterns |
| `online-iran-veresk-bridge-65` | پل ورسک | Veresk Bridge | patterns |
| `online-iran-white-bridge-ahvaz-65` | پل سفید اهواز | Ahvaz White Bridge | patterns |
| `online-iran-rudkhan-castle-65` | قلعه رودخان | Rudkhan Castle | patterns |
| `online-iran-alamut-castle-65` | قلعه الموت | Alamut Castle | patterns |
| `online-iran-babak-castle-65` | قلعه بابک | Babak Castle | patterns |
| `online-iran-shushtar-watermills-65` | سازه‌های آبی شوشتر | Shushtar Hydraulic System | patterns |
| `online-iran-shazdeh-garden-65` | باغ شاهزاده ماهان | Shazdeh Garden | nature |
| `online-iran-agha-bozorg-65` | مسجد آقابزرگ کاشان | Agha Bozorg Mosque | patterns |
| `online-iran-isfahan-jameh-65` | مسجد جامع اصفهان | Isfahan Jameh Mosque | patterns |
| `online-iran-yazd-fire-temple-65` | آتشکده زرتشتیان یزد | Yazd Fire Temple | patterns |
| `online-iran-saad-al-saltaneh-65` | کاروانسرای سعدالسلطنه | Sa'd al-Saltaneh | patterns |
| `online-iran-ali-sadr-cave-65` | غار علیصدر همدان | Ali-Sadr Cave | nature |
| `online-iran-badab-e-surt-65` | چشمه‌های باداب سورت | Badab-e Surt Springs | nature |
| `online-iran-chabahar-martian-65` | کوه‌های مریخی چابهار | Chabahar Martian Mountains | nature |
| `online-iran-boteh-jegheh-65` | بته‌جقه ایرانی | Boteh Jegheh Motif | patterns |
| `online-iran-lalejin-pottery-65` | سفال لالجین | Lalejin Pottery | objects |
| `online-iran-persian-tar-65` | ساز تار ایرانی | Persian Tar | objects |
| `online-iran-persian-gulf-lenj-65` | لنج سنتی جنوب ایران | Persian Gulf Lenj | objects |

**Packaging and availability:** On a successful `main` Web CI workflow
completion, GitHub Pages creates the immutable
[`pixelhub-content-iran-more-65-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-iran-more-65-20-v1)
Release if it does not yet exist, assembling its `content.zip` into the public
online catalog. Only source drawing instructions are in git; the 20 full grid
JSON files and 20 PNG previews remain Release assets rather than APK content.
Existing downloads, progress and published art are preserved.

Generate with
`python3 tool/online_iran_more_20_pack.py /tmp/content.zip`.
The current five allowed public online categories are preserved to remain
compatible with deployed clients; the in-app category overlay resolves the
`online-iran-` IDs into Persian architecture where applicable.

The new content becomes available to players **only after both the Release
publication and Pages deployment succeed**. Adding the source or merging the
branch does not itself confirm a successful publication.

## Twenty-five Persian-rug-inspired 65×65 coloring patterns (October 2026)

`tool/online_persian_rugs_25_pack.py` authors 25 **different, original**
geometric and floral rug-inspired coloring artworks, rather than using
copies of actual woven carpets. Each design is exactly **65×65 cells**
with a separate hand-designed composition and color palette.
All 25 have bilingual titles, distinct immutable online IDs,
`levelVersion: 1`, schema-v2 level JSON, checksum and individual PNG preview.

| ID | فارسی | English | Size |
| --- | --- | --- | --- |
| `online-persian-rug-tabriz-medallion-65` | فرش ترنج تبریز | Tabriz Medallion | 65×65 |
| `online-persian-rug-kashan-flowers-65` | فرش گل‌وبوته کاشان | Kashan Floral | 65×65 |
| `online-persian-rug-isfahan-arabesque-65` | فرش اسلیمی اصفهان | Isfahan Arabesque | 65×65 |
| `online-persian-rug-nain-ivory-65` | فرش لچک ترنج نائین | Nain Ivory | 65×65 |
| `online-persian-rug-qom-silk-65` | فرش ابریشمی قم | Qom Silk Bouquet | 65×65 |
| `online-persian-rug-heriz-geometric-65` | فرش هندسی هریس | Heriz Geometric | 65×65 |
| `online-persian-rug-bijar-herati-65` | فرش ماهی بیجار | Bijar Herati | 65×65 |
| `online-persian-rug-senneh-boteh-65` | فرش بته‌جقه سنه | Senneh Boteh | 65×65 |
| `online-persian-rug-bakhtiari-garden-65` | فرش خشتی بختیاری | Bakhtiari Garden | 65×65 |
| `online-persian-rug-qashqai-diamonds-65` | قالی سه‌ترنج قشقایی | Qashqai Triple-Diamond | 65×65 |
| `online-persian-rug-gabbeh-lion-65` | گبه شیر فارس | Fars Lion Gabbeh | 65×65 |
| `online-persian-rug-turkmen-gul-65` | قالی گل ترکمن | Turkmen Gul | 65×65 |
| `online-persian-rug-baluch-prayer-65` | قالی محرابی بلوچ | Baluch Prayer | 65×65 |
| `online-persian-rug-afshar-diamonds-65` | قالی لوزی افشار | Afshar Diamond | 65×65 |
| `online-persian-rug-kerman-tree-65` | فرش درخت زندگی کرمان | Kerman Tree of Life | 65×65 |
| `online-persian-rug-mashhad-medallion-65` | فرش ترنج مشهد | Mashhad Medallion | 65×65 |
| `online-persian-rug-ardabil-star-65` | فرش ستاره اردبیل | Ardabil Star | 65×65 |
| `online-persian-rug-varamin-minakhani-65` | فرش میناخانی ورامین | Varamin Mina Khani | 65×65 |
| `online-persian-rug-sarouk-roses-65` | فرش دسته‌گل ساروق | Sarouk Roses | 65×65 |
| `online-persian-rug-hamedan-stripes-65` | قالی راه‌راه همدان | Hamedan Stripes | 65×65 |
| `online-persian-rug-shiraz-cypress-65` | فرش سرو شیراز | Shiraz Cypress | 65×65 |
| `online-persian-rug-yazd-four-gardens-65` | فرش چهارباغ یزد | Yazd Four Gardens | 65×65 |
| `online-persian-rug-sistan-sun-65` | گلیم خورشیدی سیستان | Sistan Sun Kilim | 65×65 |
| `online-persian-rug-mazandaran-kilim-65` | گلیم راه‌راه مازندران | Mazandaran Striped Kilim | 65×65 |
| `online-persian-rug-lori-animals-65` | گلیم حیوانات لری | Lori Animal Motifs | 65×65 |

All these artworks belong to the existing `patterns` catalog category
to remain compatible with older clients. Their IDs intentionally start
with `online-persian-rug-` instead of `online-iran-` so the gallery's
historic Iranian-landmark category overlay does not mislabel rugs as
architectural landmarks.

On a **successful main-branch Web CI run**, the existing Pages workflow
creates the immutable GitHub Release
[`pixelhub-content-persian-rugs-65-25-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-persian-rugs-65-25-v1)
if absent, attaches the generated `content.zip`, and assembles the new
online catalog. Generate manually with
`python3 tool/online_persian_rugs_25_pack.py /tmp/content.zip`.
Generated level grids and previews are Release-only assets, not committed
to the repository or bundled in the Android app.

All previously published paintings and user downloads/progress are unchanged.
Source merge alone does **not** prove publication: the content becomes
visible only after successful release creation and GitHub Pages deployment.


## Twenty original country flag icons on exact 10×10 grids (October 2026)

`tool/online_flags_20_pack.py` contains original hand-authored compact pixel
rendering recipes for **20 countries**:
Iran, France, Germany, Italy, Russia, Ukraine, Netherlands, Poland, Japan,
Turkey, United States, United Kingdom, Canada, Brazil, India, China, Sweden,
Norway, Finland, and Switzerland. Iran is included as
`online-flag-iran-10` / «پرچم ایران».

All levels use **exactly 10×10 color-by-number cells** with bilingual titles,
new immutable `online-flag-<country>-10` IDs, `levelVersion: 1`,
schema-v2 level JSON, checksum and PNG preview. All use the existing
`patterns` public catalog category to preserve backwards compatibility with
older Android clients and will appear in the online pictures section.
The small flags are generally drawn in a 10×6 region centered on the 10×10
canvas; Switzerland uses a square 6×6 motif. Fine heraldic details,
inscriptions and star patterns have to be simplified at this pixel resolution,
so these are recognizable pixel-art interpretations rather than official
vector-accurate national flag artwork.

The successful `main` Web CI workflow triggers the Pages job, which creates
[`pixelhub-content-country-flags-10-20-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-country-flags-10-20-v1)
as a new immutable Release with `content.zip`, unless it already exists,
and includes all 20 pictures in the assembled public online catalog.
The level JSON files and PNG previews are generated only in the workflow
runner and stored as Release assets—not committed to Git or bundled in APKs.

Build the pack manually with
`python3 tool/online_flags_20_pack.py /tmp/content.zip`.
Older published artworks, downloaded progress and existing IDs are preserved.
Merely committing this recipe does not establish live availability: the
Release creation and Pages deployment must complete successfully.


## Twenty-five additional country flags on exact 35×35 grids (October 2026)

The reproducible source `tool/online_flags_35_25_pack.py` defines **25 new**
national flag-inspired pixel-art paintings, all exactly **35×35 cells**,
with a 35×23 flag field centered vertically on a neutral 35×35 canvas.
These add to the earlier 20 exact-10×10 country flag pictures **without any
country overlap**.

| Country | Persian title | ID |
| --- | --- | --- |
| Spain | پرچم اسپانیا | `online-flag-spain-35` |
| Portugal | پرچم پرتغال | `online-flag-portugal-35` |
| Belgium | پرچم بلژیک | `online-flag-belgium-35` |
| Austria | پرچم اتریش | `online-flag-austria-35` |
| Denmark | پرچم دانمارک | `online-flag-denmark-35` |
| Greece | پرچم یونان | `online-flag-greece-35` |
| Ireland | پرچم ایرلند | `online-flag-ireland-35` |
| Czechia | پرچم چک | `online-flag-czechia-35` |
| Slovakia | پرچم اسلواکی | `online-flag-slovakia-35` |
| Hungary | پرچم مجارستان | `online-flag-hungary-35` |
| Romania | پرچم رومانی | `online-flag-romania-35` |
| Bulgaria | پرچم بلغارستان | `online-flag-bulgaria-35` |
| Croatia | پرچم کرواسی | `online-flag-croatia-35` |
| Serbia | پرچم صربستان | `online-flag-serbia-35` |
| South Korea | پرچم کره جنوبی | `online-flag-south-korea-35` |
| Australia | پرچم استرالیا | `online-flag-australia-35` |
| New Zealand | پرچم نیوزیلند | `online-flag-new-zealand-35` |
| Mexico | پرچم مکزیک | `online-flag-mexico-35` |
| Argentina | پرچم آرژانتین | `online-flag-argentina-35` |
| Chile | پرچم شیلی | `online-flag-chile-35` |
| Colombia | پرچم کلمبیا | `online-flag-colombia-35` |
| Peru | پرچم پرو | `online-flag-peru-35` |
| South Africa | پرچم آفریقای جنوبی | `online-flag-south-africa-35` |
| Egypt | پرچم مصر | `online-flag-egypt-35` |
| Saudi Arabia | پرچم عربستان سعودی | `online-flag-saudi-arabia-35` |

Each flag uses a unique immutable `online-flag-*-35` ID, bilingual titles,
schema-v2 numbered JSON, SHA-256 checksum, version 1, and a PNG preview.
The manifest category is the supported legacy `patterns`, enabling the
existing online gallery to display the flags without a client update. Small
coats of arms, stars and calligraphy are simplified; the Saudi design uses an
abstract non-textual motif instead of depicting Arabic religious lettering.

The GitHub Pages workflow creates the immutable
[`pixelhub-content-country-flags-35-25-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-country-flags-35-25-v1)
Release after a **successful `main` CI run**, attaches its generated
`content.zip`, and assembles it into the downloadable online gallery catalog.
Generate manually with
`python3 tool/online_flags_35_25_pack.py /tmp/content.zip`.
Only drawing instructions and tests are committed; the grid JSON and preview
PNG assets remain Release-only and are not bundled into APKs. Previously
published level IDs and existing user progress remain untouched.

Code merge alone does not establish publication: the Release and GitHub Pages
deployment must both complete successfully before users see these flags.

## Twenty-five iconic world landmarks, exact 50×50 originals (October 2026)

`tool/online_world_landmarks_25_pack.py` authors **25 visually distinct, original**
pixel-art interpretations of famous buildings and monuments around the world.
Every level contains an exact **50×50 color-by-number cell grid**, its own
hand-composed landmark silhouette and detail, Persian and English titles,
a fresh immutable `online-world-*-50` level ID, `levelVersion: 1`, and a
checksum-bound PNG preview. Existing artwork IDs and saved progress are unchanged.

| Level ID | فارسی | English | Country |
| --- | --- | --- | --- |
| `online-world-eiffel-tower-50` | برج ایفل | Eiffel Tower | France |
| `online-world-taj-mahal-50` | تاج محل | Taj Mahal | India |
| `online-world-colosseum-50` | کولوسئوم رم | Roman Colosseum | Italy |
| `online-world-giza-pyramids-50` | اهرام جیزه | Giza Pyramids | Egypt |
| `online-world-great-wall-china-50` | دیوار بزرگ چین | Great Wall of China | China |
| `online-world-big-ben-50` | بیگ بن لندن | Big Ben | United Kingdom |
| `online-world-statue-liberty-50` | مجسمه آزادی | Statue of Liberty | United States |
| `online-world-sydney-opera-50` | اپرای سیدنی | Sydney Opera House | Australia |
| `online-world-leaning-pisa-50` | برج کج پیزا | Leaning Tower of Pisa | Italy |
| `online-world-sagrada-familia-50` | ساگرادا فامیلیا | Sagrada Família | Spain |
| `online-world-christ-redeemer-50` | تندیس مسیح منجی | Christ the Redeemer | Brazil |
| `online-world-machu-picchu-50` | ماچو پیچو | Machu Picchu | Peru |
| `online-world-petra-treasury-50` | خزانه پترا | Petra Treasury | Jordan |
| `online-world-angkor-wat-50` | انگکور وات | Angkor Wat | Cambodia |
| `online-world-burj-khalifa-50` | برج خلیفه | Burj Khalifa | United Arab Emirates |
| `online-world-golden-gate-50` | پل گلدن گیت | Golden Gate Bridge | United States |
| `online-world-london-tower-bridge-50` | تاور بریج لندن | Tower Bridge | United Kingdom |
| `online-world-stonehenge-50` | استون‌هنج | Stonehenge | United Kingdom |
| `online-world-chichen-itza-50` | چیچن ایتزا | Chichén Itzá | Mexico |
| `online-world-easter-island-moai-50` | مجسمه‌های موآی | Easter Island Moai | Chile |
| `online-world-parthenon-50` | معبد پارتنون | Parthenon | Greece |
| `online-world-brandenburg-gate-50` | دروازه براندنبورگ | Brandenburg Gate | Germany |
| `online-world-neuschwanstein-50` | قلعه نوی‌شوان‌شتاین | Neuschwanstein Castle | Germany |
| `online-world-saint-basils-50` | کلیسای سنت باسیل | Saint Basil's Cathedral | Russia |
| `online-world-marina-bay-sands-50` | مارینا بی سندز | Marina Bay Sands | Singapore |

The level JSON and PNG previews are generated by
`python3 tool/online_world_landmarks_25_pack.py /tmp/content.zip`.
The public catalog category remains `patterns` for compatibility with legacy
PixelHub clients; the artwork titles distinguish world landmarks from the
existing Iranian landmark paintings. Source art uses no external copyrighted
image assets. Some architectural details are simplified to fit 50 cells.

After a **successful `main` CI run**, the existing Pages workflow creates
the immutable [`pixelhub-content-world-landmarks-50-25-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-world-landmarks-50-25-v1)
Release with `content.zip` and integrates its catalog in the online gallery.
The generated assets remain in GitHub Release storage, not inside Git history
or the Android APK. Merging code does **not** establish a completed release
or Pages deployment; these must succeed independently.

## Twenty-five additional world-famous buildings and monuments (80×80)

The online gallery adds **25 entirely new landmark paintings**, each
hand-composed directly on an exact **80×80 integer-pixel grid** (6,400 cells).
These scenes are separate from the first pack's 25 world landmarks on 50×50
grids: new subjects, fresh IDs and richer tower, window, dome, arch, masonry
and landscaping detail—not enlargements or replacements of old levels.

| New ID | فارسی | English | Location |
| --- | --- | --- | --- |
| `online-world-more-hagia-sophia-80` | ایاصوفیه استانبول | Hagia Sophia | Türkiye |
| `online-world-more-notre-dame-paris-80` | کلیسای نوتردام پاریس | Notre-Dame de Paris | France |
| `online-world-more-arc-de-triomphe-80` | طاق پیروزی پاریس | Arc de Triomphe | France |
| `online-world-more-louvre-pyramid-80` | هرم موزه لوور | Louvre Pyramid | France |
| `online-world-more-mont-saint-michel-80` | مون سن میشل | Mont Saint-Michel | France |
| `online-world-more-empire-state-building-80` | ساختمان امپایر استیت | Empire State Building | United States |
| `online-world-more-space-needle-80` | برج اسپیس نیدل | Space Needle | United States |
| `online-world-more-gateway-arch-80` | طاق دروازه سنت لوئیس | Gateway Arch | United States |
| `online-world-more-cn-tower-80` | برج سی‌ان تورنتو | CN Tower | Canada |
| `online-world-more-forbidden-city-80` | شهر ممنوعه پکن | Forbidden City | China |
| `online-world-more-temple-of-heaven-80` | معبد آسمان پکن | Temple of Heaven | China |
| `online-world-more-potala-palace-80` | کاخ پوتالا | Potala Palace | China |
| `online-world-more-himeji-castle-80` | قلعه هیمه‌جی | Himeji Castle | Japan |
| `online-world-more-fushimi-inari-80` | دروازه‌های فوشیمی ایناری | Fushimi Inari | Japan |
| `online-world-more-gyeongbokgung-80` | کاخ گیونگ‌بوک‌گونگ | Gyeongbokgung Palace | South Korea |
| `online-world-more-taipei-101-80` | برج تایپه ۱۰۱ | Taipei 101 | Taiwan |
| `online-world-more-petronas-twin-towers-80` | برج‌های دوقلوی پتروناس | Petronas Twin Towers | Malaysia |
| `online-world-more-lotus-temple-80` | معبد نیلوفر آبی | Lotus Temple | India |
| `online-world-more-qutub-minar-80` | قطب منار دهلی | Qutub Minar | India |
| `online-world-more-sheikh-zayed-mosque-80` | مسجد شیخ زاید | Sheikh Zayed Grand Mosque | United Arab Emirates |
| `online-world-more-dome-of-the-rock-80` | قبةالصخره | Dome of the Rock | Jerusalem |
| `online-world-more-alhambra-80` | کاخ الحمرا | Alhambra | Spain |
| `online-world-more-florence-cathedral-80` | کلیسای جامع فلورانس | Florence Cathedral | Italy |
| `online-world-more-st-peters-basilica-80` | کلیسای سن پیترو | St. Peter's Basilica | Vatican City |
| `online-world-more-abu-simbel-80` | معبد ابوسمبل | Abu Simbel | Egypt |

The reproducible source is `tool/online_world_landmarks_more_25_pack.py`.
Each level has schema version 2, levelVersion 1, a Persian and an English
title, checksum-bound numbered cells, its own lossless PNG preview and a
fresh immutable `online-world-more-*-80` identifier. The online catalog
uses the existing legacy-compatible `patterns` category. Other published
levels, existing user progress, and APK size/content are unaffected.

Run `python3 tool/online_world_landmarks_more_25_pack.py /tmp/content.zip`
to generate the complete release ZIP (one catalog and 25 pairs of JSON and
PNG files). The successful main-branch Web CI triggers the Pages workflow,
which creates the immutable Release
[`pixelhub-content-world-landmarks-80-25-v1`](https://github.com/abolfazl2600/Pixelhub/releases/tag/pixelhub-content-world-landmarks-80-25-v1)
if absent and downloads all releases when rebuilding the online catalog.
The ZIP, numbered JSON grids, and PNG previews remain external to Git and
the Android package. Code merged on `main` is **not yet equivalent to online
publication**: a successful Release creation and Pages deployment are needed.
