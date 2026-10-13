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
- Failed connectivity leaves bundled and previously downloaded levels usable.
- Browser localStorage and device storage have quotas; failed writes are
  reported. This initial adapter caps locally downloaded levels at 1000.
  A future move to IndexedDB/files can retain the same repository interface.

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
published pack in place or reuse version 1 for different pixel data.

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
do not overwrite version 1 files; improvements require a new level version.

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

## Publish more pictures

1. Create one or more schema-v2 level JSON files with unique `online-...`
   IDs, stable `levelVersion`, titles in Persian and English, ARGB palette,
   pixel indices and the canonical SHA-256 checksum already used by PixelHub.
2. Make a PNG preview for each picture. Use consistent names:
   `levels/<id>-v<version>.json` and `previews/<id>-v<version>.png`.
3. Create a ZIP named **`content.zip`** containing these files and a
   `catalog.json` whose entries contain `id`, `version`, `title`,
   `titleEn`, `category`, `width`, `height`, `bytes`, `checksum`.
   `bytes` is the UTF-8 JSON byte count; checksum is the schema-v2 level
   checksum, **not a hash of the JSON file**.
4. Create a new, published **GitHub Release** on this same repository, with a
   tag starting `pixelhub-content-`, attach the ZIP, and publish it.
5. The Pages workflow is triggered by Release publishing. If updating assets
   on an already-published Release, manually run **Publish verified Web
   artifact** via `workflow_dispatch` because asset uploads do not
   necessarily emit the `release edited` event.
6. Open the Pages `online/catalog.json` endpoint and check that the intended
   levels appear; opening the gallery will then discover them automatically.

**No Android APK or AAB rebuild is required** to publish compatible pictures.
The Web site is republished to mirror the new content, but its Web application
artifact remains the last verified build. Android builds only through their
separate manual workflow.

Release packs are treated as immutable. Publish changes to an existing picture
with a higher `levelVersion`, and do not reuse a stable ID for a different
design: local progress is keyed to ID, version and checksum. Keep the checksum
for published versions unchanged. Avoid deleting Releases containing pictures
still used by users.

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
- New versions of an already downloaded ID are not auto-replaced. Progress is
  preserved, and content updates need a deliberate user-facing migration flow.
- Public GitHub Releases/Pages have their own fair-use, size and bandwidth
  limits. Move distribution to a dedicated CDN when traffic justifies it.
