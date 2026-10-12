# V2 manual acceptance

Record source SHA, device/browser, viewport, language and observed result.

- [ ] A fresh installation opens in Persian even with an English OS. English switches every screen/dialog/title and LTR direction; reopening remembers the choice. Switch back to Persian and verify RTL.
- [ ] Open a 32, 64 and 128 grid. Zoom until numbers are readable; tap the intended cell at different scales.
- [ ] Wrong-color and repeated taps leave counts unchanged. Drag quickly along a row/diagonal without gaps.
- [ ] Two-finger pinch and Move mode never color cells. Pan stays within bounds; zoom/fit controls work.
- [ ] Undo reverses one stroke. Reset cancellation preserves all progress; confirmed Reset persists an empty new generation after reopening.
- [ ] Paint at least 50 cells, wait for Saved, kill/reopen the Android app and compare exact cells/count. Repeat with browser refresh/new page. Separately interrupt a pending save and document the last acknowledged state.
- [ ] Finish a picture, verify the result screen, reopen it and confirm it remains complete.
- [ ] Check quota/full/corrupt storage behavior: safe error/retry, no silent data deletion.
- [ ] Test 360/390/430, desktop centering, short landscape, cutouts, 150% text, mouse, touch and keyboard arrows/Enter.
- [ ] Profile the real Android device while zooming/panning/painting the 128 grid. Record frame timings and jank; cloud timing is not a phone benchmark.
- [ ] Confirm automatic Web CI creates no APK. Manually run Build Android APK, download/install the artifact and compare its commit.txt with the intended Web release.
