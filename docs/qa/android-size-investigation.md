# PixelHub Android size investigation

**Analysis of existing artifacts only; no new build.**

The previous successful manually dispatched preview run `38305453410` produced a GitHub Actions ZIP artifact of **77,807,919 bytes (74.2 MiB)**. The ZIP includes a **debug APK** and a tiny `commit.txt`. It is **not** the release Play download size.

- The `preview-apk` option runs `flutter build apk --debug --no-pub`. A debug Flutter runtime is not representative of the release AAB, and APKs can contain native engine binaries for multiple ABIs.
- Tracked `apps/game/assets` content totals about **0.91 MB**, including `Roboto.ttf` (~489 KB), `Vazirmatn.ttf` (~241 KB) and level JSON assets. The separate repository `docs/qa/images` screenshots are **not** declared in Flutter assets.
- **Exact bytes-by-component have not been determined.** The updated manually triggered Android workflow prints the actual APK/AAB size, twelve largest compressed ZIP members and native library bytes by ABI on its next successful run.
- Select manual `play-aab` for a release-size comparison and device-specific Google Play delivery. No Android build has been automatically started or verified here.
