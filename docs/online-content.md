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
