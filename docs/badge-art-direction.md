# PixelHub achievement badges — visual standard and catalog roadmap

> **Decision (2026-10-17):** Use the last approved **large, detailed, crisp pixel-art medal** design as the canonical achievement-badge art direction. **Every shipped badge image MUST have a fully transparent background.** This is a design specification; adding this document does not generate, publish, or replace live badge images.

## 1. Approved art direction

The visual reference is the final 12-medal grid approved in the PixelHub design conversation on 2026-10-17: enlarged circular medals with a bold central emblem, multi-layered metallic rim, optional laurel wreath, top jewel, small bottom ribbons, selective highlights and deep, clean pixel-art shadows. Keep the rich detail **inside the badge silhouette**; remove the reference sheet's dark navy backdrop completely.

- **Individual asset, not a sprite sheet:** one medal per PNG. Sprite sheets are allowed for previews only.
- **Transparent canvas:** RGBA/alpha transparency, with alpha 0 **everywhere outside the badge silhouette** (including all four corners). No dark background, solid square, vignette, rectangular plate, halo, drop shadow on a canvas or checkerboard baked into the image. The colored circular/inner medallion backing **inside** the medal is permitted and is not a background.
- **Canvas and pixel geometry:** author on a **128×128 logical pixel grid**, export at **512×512 physical pixels** using **4× nearest-neighbor** scaling. Preserve hard, deliberate pixel edges and 1:1 square pixels; no smoothing, anti-aliased vector outlines, photo texture, gradients or blurred highlights. A different integer-multiple scale needs a documented exception.
- **Visual hierarchy:** a clearly readable central symbol occupies ~55–65% of the medal's inner disc; the rim and laurel wreath frame rather than overpower it. Medal silhouette should fill ~85–92% of the canvas with transparent padding for consistent sizing.
- **Craftsmanship:** layered gold/silver/bronze/colored metal using 2–4 hard-edged shade tones per material; crisp pixel-level sparkle, bevel, gemstone facets and short leaf segments. Use intentional light direction (upper-left) and one coherent outline thickness.
- **Consistency:** match circular silhouette, top jewel placement, ribbon size, pixel block scale, laurel style and lighting across categories. Subject changes should be legible even at 72×72 UI pixels.
- **Palette:** restrained, typically 16–32 colors plus transparency per badge; use category-appropriate accent colors. Gold, silver and bronze may indicate increasingly difficult missions, but existing IDs/rewards are authoritative.
- **No typography or numerals baked into PNG:** title, description, progress and required count remain localizable application text.

### Suggested symbolic motifs

| Theme | Primary symbol | Accent |
| --- | --- | --- |
| Animals | Paw print, fox, lion | Copper / warm gold |
| Nature | Leaf, sprout, tree | Emerald |
| Objects | Brush, camera, crafted object | Teal |
| Masterpieces | Painter palette, framed starry sky | Silver / indigo |
| Persian architecture | Azadi Tower or stylized Persian arch | Amethyst / gold |
| Patterns | Geometric rosette / shamsa | Pink / purple |
| Space | Rocket, crescent, Saturn | Sapphire |
| Milestones | Trophy / crown / diamond | Gold |
| Special challenges | Flame, thread, gem, curated frame | Distinct thematic color |

### Asset export and QA acceptance

1. Export separately as `images/<stable_badge_id>.png`, square **512×512**, PNG with transparency. Preserve exact sharp pixel boundaries with nearest-neighbor scaling.
2. Check corner alpha values = 0 and ensure that any outlying pixel outside the medal silhouette is transparent. Check for stray dark-background pixels around ribbons, wreath and jewel.
3. Inspect at **512, 128, 72 and 48 px** without smoothing; center motif must still be recognizable at 72 px and identifiable at 48 px.
4. Prefer palette-indexed PNG with an alpha entry, if supported, to reduce download size. The current client validates image byte length and SHA-256, and caps each PNG at **32,768 bytes**; **do not assume a 512×512 PNG is accepted unless the optimized file actually meets that limit**. If it does not, alter the asset-production strategy or explicitly update and validate the client/catalog limits before publication.
5. Update `badge_content/catalog.json` image size and checksum **together** with the final PNG and use a stable image/manifest deployment process. Do not claim publication simply because a Git commit exists.
6. Keep all images remotely distributed and cached on device for earned awards, with user-facing loading messages that do not name the content host.
7. Keep every badge's **title and useful description** visible in the collection, including unearned badges, alongside progress `x / required`; use “دریافت نشده” / “Not earned” rather than “هنوز کشف نشده” / “Undiscovered”. Do not treat the image's visual mystery treatment as permission to hide the mission's actual objective. **Note:** this is a desired UI guideline; the current implementation may still hide some metadata until a separate UI change.

### Reusable art brief

> Create a single large, collectible PixelHub achievement medal: richly detailed, crisp 128×128 logical-grid pixel art scaled to a 512×512 PNG by nearest-neighbor; ornate but controlled circular layered metal frame, compact laurel wreath, tiny jewel at the top, short ribbon tails, prominent instantly recognizable central symbol for [MISSION]. Carefully shaded metal and gem facets with hard-edged pixels. **Strictly transparent RGBA background (alpha 0 outside badge), no scenery, no square backdrop, no lettering, no blurry gradients, no anti-aliasing.** Match the established PixelHub 12-medal design family.

## 2. Current implementation and boundaries

The current remote achievement catalog (`badge_content/catalog.json`) contains **five existing mission definitions**: `animal_first` (1 animal), `animal_five` (5 animals), `animal_ten` (10 animals), `nature_five` (5 nature pictures) and `masterpieces_five` (5 masterpieces). These existing IDs must remain stable; redesigning their art is a separate asset and checksum update, not an award reset.

As of this specification, the badge engine counts **distinct completed pictures by a single category**. A catalog-only addition can introduce other category-count thresholds using the existing schema; **cross-category achievements, all-picture totals, texture/style-based goals, tool constraints, daily streaks, animation, and museum tasks require new tracking/rules and should not be represented as working via a catalog-only change**. New badge entries also require their actual optimized image files, correct hashes and successful publication. The remote catalog currently limits records to 64.

## 3. Proposed mission list (not yet implemented unless marked existing)

### A. Category progression — immediate/compatible target

| Category | Beginner (1) | Regular (5) | Expert (10) |
| --- | --- | --- | --- |
| Animals | اولین دوست حیوانات · `animal_first` **existing** | دوستدار حیوانات · `animal_five` **existing** | نگهبان حیات وحش · `animal_ten` **existing** |
| Nature | جوانه اول | دوست طبیعت · `nature_five` **existing** | نگهبان جنگل |
| Objects | کلکسیونر تازه‌کار | گردآورنده اشیا | استاد اشیا |
| Masterpieces | اولین شاهکار | هنردوست · `masterpieces_five` **existing** | استاد شاهکارها |
| Persian architecture | گردشگر ایران | کاشف معماری ایران | نگهبان میراث |
| Patterns | اولین نقش | نقش‌آفرین | استاد نقش‌ها |
| Space | مسافر فضا | کاوشگر کهکشان | فرمانده ستاره‌ها |

**Criterion for each column:** complete **1, 5 or 10 distinct paintings in that category**, respectively. Localized descriptions must say exactly that, and the UI must show progress. Preserve the existing five localized strings until deliberately edited. Use predictable new stable IDs of the form `<category>_<count>` once finalized; do not silently rename existing IDs.

### B. Special challenges — later rules/data work

| Suggested badge | Exact proposed condition | Visual |
| --- | --- | --- |
| اولین قدم | Complete any 1 painting | Gold star |
| ده اثر ماندگار | Complete 10 distinct paintings across all categories | Trophy |
| هنرمند پرتلاش | Complete 50 distinct paintings across all categories | Crown |
| رنگین‌کمان | Complete at least 1 painting in each of all 7 public categories | Rainbow palette |
| استاد الماس | Finish 5 distinct paintings using diamond texture/style | Diamond |
| هنرمند بافتنی | Finish 5 distinct paintings using knitting/yarn style | Yarn and needles |
| مدیر موزه | Fill all 6 museum display slots with completed, different artworks | Gilded frame / museum |
| جان‌بخش | Complete 5 distinct paintings that have an animation companion | Magic spark / moving star |
| نقاش دقیق | Complete 5 distinct paintings without using a hint/assist tool during those paintings | Precision brush |
| وفادار به هنر | Complete at least one painting on each of 7 consecutive local calendar days | Seven-day flame |

Challenge conditions need precisely defined event/progress persistence, an anti-double-counting rule and backwards-compatibility decisions before development. The catalog schema currently cannot express these conditions. The remote badge definition must not imply a goal exists before its tracking has been implemented.

## 4. Rollout recommendation

**Release 1 (art):** retain the five existing mission definitions and replace their tiny icons with optimized, individually exported, transparent PixelHub medals, after verifying size/hash and the live delivery pipeline.

**Release 2 (categories):** extend to 21 category badges (the seven categories × 1/5/10 threshold), preserving the five existing IDs and adding the other 16. Each badge has a unique center symbol and localized title/description.

**Release 3 (special):** add selected challenge badges only after the corresponding tracked gameplay events and test/acceptance criteria are implemented. Keep all current award IDs and previously earned records intact.
