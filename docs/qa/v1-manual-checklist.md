# V1 manual acceptance checklist

Record commit, artifact SHA, device/browser, viewport, text size, outcome and evidence. Automated results do not replace physical-device checks.

- [ ] Install the internal APK on an Android device (Android 7.0 / API 24 or newer), launch it, and confirm the local fixture opens in airplane mode.
- [ ] Splash resolves to Home; malformed/missing asset presents a safe retry rather than a crash.
- [ ] Open the sunflower preview and return with the app button and Android system Back.
- [ ] Compare Android and Web: same hierarchy, font, colors, palette and single mobile column.
- [ ] At widths 360, 390, 430 and a desktop width, frame is centered and never wider than 430 logical pixels.
- [ ] Rotate/resize to a short landscape height. Scroll to the Home action and preview note; no clipping or unreachable controls.
- [ ] Check display cutouts, bottom gesture inset, larger system text, RTL and screen-reader labels. Controls have at least 48 logical pixel targets.
- [ ] On Pages, open `#/painting` directly and refresh; preview loads without a server 404 and can return to Home.
- [ ] Browser Back/Forward work after opening the preview; Tab focus and Enter/Space activate buttons.
- [ ] Fixture and palette are read-only; no painting, Undo, progress saving, accounts, import or commerce appears in V1.
- [ ] Compare Web `commit.txt` and APK artifact `commit.txt`; both equal the tested CI commit.

Pages publication, artifact availability and physical-device installation are outstanding until performed on GitHub and a real phone. Use the validation report for the current cloud checks.
