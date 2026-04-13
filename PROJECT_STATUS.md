# Project Status

## Current Baseline

- Branch: `zti-migration-checkpoint`
- Checkpoint baseline: `b347e33`
- Last pushed checkpoint before this handoff-doc pass: `f01936f`
- Repository status at checkpoint baseline `b347e33`: clean

## What Is In Place

- The website is on a barn-first, single-source workflow.
- Authored website source lives in `dev/site/_src`.
- The website builder lives at `dev/site/build.py`.
- The only website artifact is `dev/site/_dist`.
- Barn preview serves the built artifact.
- Plesk is serve-only and is intended to receive full artifact replacement deploys.
- The demo is now a deterministic compiler with canonical artifacts under `resources/demo`.
- The landing page now embeds `/assets/zti-demo.mp4`.

## Canonical Sources of Truth

- Website source of truth: `dev/site/_src`
- Website artifact: `dev/site/_dist`
- Demo source of truth:
  - `resources/demo/session_model.py`
  - `resources/demo/generate.py`
- Canonical demo artifacts:
  - `resources/demo/terminal-output.md`
  - `resources/demo/recording-script.md`
  - `resources/demo/zti-demo.cast`
  - `resources/demo/demo.sha256`
- Derived demo outputs:
  - `resources/demo/build/zti-demo.mp4`
  - `resources/demo/build/zti-demo.gif`

## What Was Done

- Removed the legacy `site/` workflow from normal website operations.
- Introduced the barn-first build, verify, and deploy workflow.
- Added the deterministic demo compiler and proof artifacts.
- Added demo ops scripts for record, verify, play, and render.
- Replaced the homepage video placeholder with the rendered MP4 asset.

## Known Gaps / Consistency Risks

- `AGENTS.md` previously said transcript artifacts came from runtime output; that wording must stay aligned to the compiler model going forward.
- `resources/demo/script.md` is still produced by legacy narrative helpers and should either be formally retained as a maintained artifact or retired.
- `zti/demo/narrative.py` and `ops/verify.sh` still reflect older runtime-shaped assumptions and should be consolidated behind the compiler.
- CI currently validates markdown demo docs and the deterministic site build, but does not explicitly diff `resources/demo/zti-demo.cast` and `resources/demo/demo.sha256`.
- The site build depends on `resources/demo/build/zti-demo.mp4` existing, so `./ops/render-demo.sh` remains a prerequisite when the video asset must be staged into the site artifact.

## Next Steps

- Make compiler outputs the only authority used by verify paths and helper docs.
- Extend CI to validate `zti-demo.cast` and `demo.sha256`.
- Decide whether `resources/demo/script.md` remains a maintained artifact or is retired.
- Verify barn-to-Plesk deployment with the MP4 included in the website artifact.

## Operator Commands

- `./ops/record-demo.sh`
- `./ops/verify-demo.sh`
- `./ops/play-demo.sh`
- `./ops/render-demo.sh`
- `python3 dev/site/build.py --out dev/site/_dist`
- `./ops/verify.sh`
- `./ops/deploy.sh`

## Do Not Do

- Do not edit `dev/site/_dist`.
- Do not recreate `site/`.
- Do not edit transcript, cast, or hash artifacts manually.
- Do not edit Plesk by hand.
