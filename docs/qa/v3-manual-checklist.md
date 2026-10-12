# V3 manual checklist — pending, not executed

The owner requests source development without local tests/builds or waiting for CI. The following acceptance work is recorded for a later explicit validation request; no V3 pass result is claimed.

- [ ] Browse all 40 pictures, categories and bilingual search. Confirm existing V2 IDs still restore progress.
- [ ] Favorite/unfavorite, paint, finish, reopen and review every My Gallery filter.
- [ ] Import JPEG/PNG/WebP on Web and Android through the platform picker without requesting broad storage permission. Cancel/retry and verify an existing preview is retained on picker cancellation/error.
- [ ] Compare crop preview and converted output after all four rotations, including RTL, wide/tall and EXIF-oriented photos.
- [ ] Change name, difficulty, colors and crop; verify the prior converted preview becomes unavailable until regenerated.
- [ ] Reject oversized dimensions/files, malformed, unsupported and animated inputs. Check transparent/16-bit PNG handling and memory use on a real phone.
- [ ] Save 32/64/128 personal pictures, resume after restart and verify photos/location metadata never enter storage or network requests.
- [ ] Trigger library limits, browser quota and corrupted records. Verify errors/retry preserve existing data and that explicit clearing can recover a damaged library.
- [ ] Export a completed picture to PNG on Web and through the Android share sheet. Cancel sharing and retry; verify incomplete pictures offer no export action.
- [ ] Confirm deletion, favorite cleanup and other pictures' progress preservation. Confirm full clear resets language to Persian and preserves bundled pictures.
- [ ] On the production Web artifact, wait for Settings' offline-ready message, close all tabs, disable networking, reopen and play/import/export. Verify an update waits for old tabs to close and failed caching remains recoverable.
- [ ] Review art readability and color choices. The 40-image implementation is below the optional 80–120 planning target; no artistic QA pass is claimed.
- [ ] Confirm only Web builds automatically and Android requires manual Run workflow.
