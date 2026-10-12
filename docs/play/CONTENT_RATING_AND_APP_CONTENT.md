# Content rating and App Content — PixelHub Play Console worksheet

**Not a completed rating / age declaration.** Google Play's questionnaires
and official authorities issue the actual rating. The owner must choose
market and target-age groups; these are policy-sensitive product decisions.

## What the present Android app does

- Category: **Game**, pixel-art coloring (local-first, offline).
- Playable public catalog is bundled. Users may convert a photo selected by
  themselves into a **private local** pixel grid; there is **no public UGC
  feed**, messaging, follows or photo upload.
- **Ads:** No active ads. **In-app purchases:** No active purchase flow.
  Coins, wallet and online rewards show disabled / Coming Soon UI.
- **Account/sign-in:** Not active. No credentials necessary for app access.
- **User communication with strangers:** None in the shipping build.
- **Location permission / camera permission:** Not required. File import
  goes through the system picker, which does not require broad photo access.
- **External linking:** A public privacy policy URL is displayed/copyable.
  The native share sheet is invoked only by the user for exported artwork.

## Draft Play declarations to review

| Play Console section | Draft basis / user action |
|---|---|
| **Ads** | Proposed **No**, so long as the final AAB contains no ad serving |
| **App access** | All existing gameplay works without sign-in; no login instructions |
| **Content rating questionnaire** | Answer from **final bundled artwork** and gameplay; no auto-generated rating |
| **Target audience and content** | **Owner must select age groups**, considering local photo import and applicable Families policies |
| **Data safety** | Follow the separate draft worksheet; re-check any native libraries |
| **Sensitive permissions** | Check merged manifest; broad gallery/camera/audio/location/ad ID removal directives are in main manifest |
| **News app** | Not a news application |
| **Government app / health / finance** | No related service |
| **Payments, promotions, subscriptions** | Disabled; do not declare actual products unless implemented |
| **Account deletion** | Online accounts not yet offered; if implemented later, provide in-app and web deletion |

## Content-rating review (do not guess responses)

- Manually review all bundled level images (and assets updated for release)
  for violence, nudity, sexual themes, drugs/alcohol, gambling, frightening
  imagery and discriminatory content. Do not treat a source comment or a
  category name as proof of absence.
- Confirm that import of arbitrary **private** photos doesn't imply
  a public sharing/social feature.
- Answer the actual IARC/Play questionnaire truthfully and retain the
  issued ratings. Do not claim `Everyone` or `PEGI 3` before approval.
- Decide whether the title intentionally targets children. Selecting any
  child age group may impose Google Play Families policies even without ads.
- Revisit the forms if the app gains public content, account sync, advertising
  or billing.

## Still to do in Play Console

- Create/select the developer account, target countries and contact email.
- Complete Target audience, ads, app access, content rating, privacy and
  Data Safety; acknowledge other sections shown under App content.
- Keep screenshots and description accurate about disabled features.
- Submit the AAB to the required test tracks and obtain Play approval.
- These steps cannot be performed merely by writing to the repository.

References:
- https://support.google.com/googleplay/android-developer/answer/9859655
- https://support.google.com/googleplay/android-developer/answer/9867159
- https://support.google.com/googleplay/android-developer/answer/9859455
