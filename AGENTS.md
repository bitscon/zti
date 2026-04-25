# AGENTS

## System Identity and Boundary

zerotrustintelligence is a ZTI-side project. It is not a Billy Workspace project.
The boundary between this repo and Billy Workspace is governed by:
- `../BOUNDARY.md` (workspace root) — canonical separation contract
- `../docs/handoff/` — the only allowed cross-system interaction surface

This repo must be operable without Billy Workspace being present.

**Prohibited (boundary rules):**
- Importing or referencing Billy-internal documents (AGENT_OS.md, ACTIVE_RUNTIME.md, docs/changes/)
- Adding dependencies on Billy runtime state or governance logic
- Creating symlinks to Billy directories
- Any CI/CD configuration that requires Billy Workspace to be present

If any of the above are detected: report `BOUNDARY_VIOLATION` to operator before proceeding.

---

## Mandatory Context

All agents MUST read:

`/PROJECT_STATUS.md`

before making website or demo workflow changes.

`PROJECT_STATUS.md` is the canonical migration checkpoint, current-state summary,
and next-steps source for this repository's website and demo systems.

## Website Source of Truth

The website uses a barn-first, single-artifact workflow.

All agents MUST follow these rules:

1. Website authoring is allowed ONLY in:

   `/dev/site/_src/`

2. The website builder lives at:

   `/dev/site/build.py`

3. The only generated website artifact is:

   `/dev/site/_dist/`

   It is NEVER hand-authored.

4. The legacy production render tree at:

   `/site/`

   is removed from the workflow and MUST NOT be recreated or edited.

5. Barn is the authority for build, verify, and deploy.

6. CI is validation-only. It MUST NOT deploy the website.

7. Production deployment is artifact-based and full-replace only.

8. Plesk is serve-only and MUST NOT be edited manually.

9. Any emergency hotfix made outside `/dev/site/_src/` MUST be backported into source immediately or the repo is out of policy.

## Demo Transcript Source of Truth

The terminal output is the only source of truth for the demo.

1. Demo transcript artifacts are generated from the deterministic demo compiler / canonical session model.
2. Manual edits to generated transcript artifacts are forbidden.
3. The canonical generated transcript path is:

   `/dev/site/_dist/assets/demo-output.txt`

4. `resources/demo/terminal-output.md` and the site transcript asset MUST come from the same canonical export path.

## Agent Working Directory Requirement

All agents MUST explicitly report their working directory:

1. Upon initialization or loading
2. When asked by the user
3. Before performing file modifications

The response MUST clearly state the directory path being used.

Example:

`Current working directory: /home/billyb/workspaces/zerotrustintelligence`

## Hard Path Validation — Website Changes

All agents MUST validate file paths before performing website modifications.

### Step 1 — Declare Target Paths

Before making changes, the agent MUST explicitly list the files it intends to modify.

### Step 2 — Validate Paths

For website authoring changes, the agent MUST confirm that all authored website paths are within:

`/dev/site/_src/`

Allowed supporting files outside `_src/` are limited to repo-level enforcement files such as:
- `/dev/site/build.py`
- `/ops/*`
- `AGENTS.md`
- `.github/workflows/*`
- `.gitignore`
- runtime/export/test files required to keep the transcript and build workflow consistent

### Step 3 — Explicit Validation Statement

The agent MUST output a validation statement before proceeding.

Example:

`Validation passed: website source edits are confined to /dev/site/_src/, with only required repo-level workflow files updated outside that tree.`

### Step 4 — Failure Behavior

If a requested website change targets generated output, legacy render trees, or production hosts directly, the agent MUST:

- stop immediately
- not perform the modification
- report the violation
- ask for confirmation before proceeding

### Step 5 — Post-Execution Confirmation

After completing changes, the agent MUST confirm:

- website authoring changes were applied only in `/dev/site/_src/`
- any outside changes were limited to required build, ops, governance, runtime, or test enforcement files
- no direct edits were made to `/site/`
- no direct edits were made to Plesk-hosted production files
