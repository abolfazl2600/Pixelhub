# Owner's development workflow

- Continue the seven-version roadmap in `docs/product-plan`, keeping Persian the default and providing English for every user-facing feature.
- The owner explicitly requests code development without running tests, automated analysis, browser checks or builds, and without waiting for CI results. Do not run those locally unless the owner explicitly asks for validation. Dependency resolution, localization generation and source formatting are development tasks and may run as needed.
- Keep automatic Web CI/Pages workflows. Android APK generation must remain exclusively in its separate `workflow_dispatch` workflow; never add an automatic Android build or dispatch it without a request.
- For the currently authorized development continuation, commit and push changes to `main` using normal Git push. Preserve unrelated edits and do not force-push.
- Update documentation honestly: implemented features are not verified or released merely because code has been pushed. The owner's instruction permits continuing development while roadmap testing/release gates remain pending.
- Personal photos are private and processed locally. Do not add photo uploads or external image-processing services.
