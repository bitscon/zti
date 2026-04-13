# AGENTS

## Website Source of Truth

The website uses a single-source build workflow.

All agents MUST follow these rules:

1. Website authoring is allowed ONLY in:

   `/dev/site/_src/`

2. The website builder lives at:

   `/dev/site/build.py`

3. Generated website outputs are NEVER hand-authored:
   - `/dev/site/_preview/`
   - `/dev/site/_dist_prod/`
   - `/dev/site/_generated/`

4. The legacy production render tree at:

   `/site/`

   is deprecated and MUST NOT be edited directly.

5. CI is the authority for production website artifacts.

6. Production deployment is artifact-based and full-replace only.

7. Any emergency hotfix made outside `/dev/site/_src/` MUST be backported into source immediately or the repo is out of policy.

## Demo Transcript Source of Truth

The terminal output is the only source of truth for the demo.

1. Demo transcript artifacts are generated from runtime output.
2. Manual edits to generated transcript artifacts are forbidden.
3. The canonical generated transcript path is:

   `/dev/site/_generated/demo-output.txt`

4. The builder stages that transcript into preview and production artifacts.

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
- `AGENTS.md`
- `.github/workflows/*`
- `.gitignore`
- runtime/export/test files required to keep the transcript and build workflow consistent

### Step 3 — Explicit Validation Statement

The agent MUST output a validation statement before proceeding.

Example:

`Validation passed: website source edits are confined to /dev/site/_src/, with only required repo-level workflow files updated outside that tree.`

### Step 4 — Failure Behavior

If a requested website change targets legacy render output or production render trees, the agent MUST:

- stop immediately
- not perform the modification
- report the violation
- ask for confirmation before proceeding

### Step 5 — Post-Execution Confirmation

After completing changes, the agent MUST confirm:

- website authoring changes were applied only in `/dev/site/_src/`
- any outside changes were limited to required build/governance/runtime enforcement files
- no direct edits were made to `/site/`
