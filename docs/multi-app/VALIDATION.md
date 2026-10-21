# Implementation validation

Validated against Flutter **3.35.7**, Dart **3.9.2**. This is development validation;
no store release or production Web deployment has been performed.

| Check | Actual result |
| --- | --- |
| Original Python immutable-content suite | **74 passed** |
| Product registry/build/publishing tests | **9 passed** |
| `bash tool/validate.sh` | **Passed**: formatting, all five package analyses, app analysis, package storage tests, **159 app tests** |
| Additional product online-controller tests | **4 passed**: identity, shared asset paths, disabled network, cached content isolation |
| Scoped persistence with legacy keys/progress and cross-product clear-data | **2 passed**, including final added progress assertions |
| Final Dart formatting check | **99 files, no changes** before adding the online-controller test; the added test was formatted separately |
| GitHub Actions definition checks | **actionlint 1.7.7 passed** |
| Python source compilation / JavaScript syntax | Passed |
| Web release Art | **Built successfully** |
| Web release Kids | **Built successfully** |
| Web release PixelHub | Running at initial PR checkpoint |
| Browser smoke locally | **Blocked by environment**: Chromium `socket() failed: Operation not permitted`; no browser pass claimed |
| Android preview | Gradle configuration reached Java compile task graph; Kotlin signing hook compilation error was corrected. Installing a complete JDK resolved the JRE-only environment limitation; retry running at initial PR checkpoint |
| Real release APK/AAB signatures | **Not verified**: private upload keys are unavailable in the local workspace; repository secret state was not inspected |
| Physical Android/device/store testing | Not performed |

The `products.cjs` browser checks are added to CI for the real built specialized
apps. The existing PixelHub browser regression suite is preserved. These require
an environment that permits launching Chromium.

Initial local Android attempts exposed (and did not hide) network proxy setup,
a Kotlin Gradle task-graph callback error, and the initial runtime-only Java
installation. External SDK/toolchain preparation is outside the repository;
GitHub Actions provisions Java 17 using `setup-java`.

Release validation rejects missing signing inputs, debug certificates, incorrect
signers, wrong package/version identity, unsigned AABs and unsigned payloads added
to a signed JAR. Unit tests verify fail-closed behavior, but this does **not**
substitute for verification of an actual release signed with the owner's key.

Remaining gates: finish actual Android previews for each ready flavor, finish the
original Web release build, pass GitHub browser regressions, and run real signed
release builds in the repository's protected signing environment. Draft product
configs and pending checks must not be described as released applications.
