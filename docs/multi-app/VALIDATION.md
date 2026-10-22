# Implementation validation

Validated against Flutter **3.35.7**, Dart **3.9.2**. This is development validation;
no store release or production Web deployment has been performed.

| Check | Actual result |
| --- | --- |
| Original Python immutable-content suite | **74 passed** |
| Product registry/build/publishing tests | **10 passed locally**; initial CI passed the original 9 before the scaffold-race regression test was added |
| `bash tool/validate.sh` | **Passed**: formatting, all five package analyses, app analysis, package storage tests, **163 app tests** |
| Additional product online-controller tests | **4 passed**: identity, shared asset paths, disabled network, cached content isolation |
| Scoped persistence with legacy keys/progress and cross-product clear-data | **2 passed**, including final added progress assertions |
| Final Dart formatting check | **99 files, no changes** at the initial local checkpoint; CI subsequently formatted 98 app/test/package files with no changes |
| GitHub Actions definition checks | **actionlint 1.7.7 passed** |
| Python source compilation / JavaScript syntax | Passed |
| Web release Art | **Built successfully** |
| Web release Kids | **Built successfully** |
| Web release PixelHub | **Built successfully locally and in CI** |
| Browser smoke in GitHub Actions | **Passed** for main, Kids and Art; navigation, painting, responsive layouts, existing online downloads and shared-origin storage checks |
| Browser smoke locally | **Blocked by environment**: Chromium `socket() failed: Operation not permitted`; no browser pass claimed |
| Android preview | **Not verified**. Local attempts reached the Android task graph and exposed/fixed a Kotlin callback error. Further local Flutter execution was rejected by automatic security review because the command accessed the infrastructure metadata endpoint. No successful APK is claimed. |
| Real release APK/AAB signatures | **Not verified**: private upload keys are unavailable in the local workspace; repository secret state was not inspected |
| Physical Android/device/store testing | Not performed |

The `products.cjs` browser checks are added to CI for the real built specialized
apps. The existing PixelHub browser regression suite is preserved. These require
an environment that permits launching Chromium.

Initial local Android attempts exposed (and did not hide) network proxy setup,
a Kotlin Gradle task-graph callback error, and the initial runtime-only Java
installation. External SDK/toolchain preparation is outside the repository;
GitHub Actions provisions Java 17 using `setup-java`. The local rejection was not bypassed. Manual Android workflow execution remains the next validation step; the connector used for this work does not expose workflow dispatch.

Release validation rejects missing signing inputs, debug certificates, incorrect
signers, wrong package/version identity, unsigned AABs and unsigned payloads added
to a signed JAR. Unit tests verify fail-closed behavior, but this does **not**
substitute for verification of an actual release signed with the owner's key.

GitHub Actions run [39577443183](https://github.com/abolfazl2600/Pixelhub/actions/runs/39577443183) passed all three jobs: `validate`, `web` and `product-web`. It verifies feature commit `a24de221f45aba57f2fe27c9294ec8eec8b88c39` through the PR merge ref.

Remaining gates: manually exercise Android preview builds/matrix for each ready flavor and run real signed release builds in the repository's protected signing environment. PR #87 remains unmerged while Android validation is outstanding. Draft product
configs and pending checks must not be described as released applications.

## Follow-up hardening

The product scaffold now removes a failed draft only if that invocation created
the file. An exclusive-create race can no longer delete another invocation's
product manifest. A regression test verifies that existing file contents survive.
