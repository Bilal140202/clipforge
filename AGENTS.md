# AGENTS.md — ClipForge agent operating instructions

This repo is built and operated by AI agents. Read this first.

## Identity

- Single, from-scratch repository: `Bilal140202/clipforge` (MIT).
- No fork lineage: an earlier fork of `superz1402/clipforge` was deleted
  2026-11-17; session-1 material is archived locally at `clipforge-arch/`
  (sandbox only) and its useful code was re-homed here cleanly.
- Upstream `superz1402/clipforge` is unrelated legacy (content-production
  repo); do not merge it.

## Verify before work (addendum §0/§21 — non-negotiable)

Before ANY task: verify authenticated identity and token permissions
(`curl /user` + `GET /repos/{owner}/{repo}` → `.permissions`). Never
assume credentials are configured. Never begin substantial work without a
GitHub Issue (objective, criteria, evidence structure). Store tokens only
in the sandbox secrets path — never in chat, never in the repo.

## Session startup protocol (master prompt §10)

1. Verify GitHub identity + repo permissions (see above).
2. `git fetch && git log --oneline -10 && git status`.
3. Read `AGENTS.md`, `WORKLOG.md`, `PLAN.md`, `DECISIONS.md`,
   `KNOWN_ISSUES.md`, `docs/GOVERNANCE.md`.
4. Inspect open + recently closed GitHub Issues; identify the active task
   and any interrupted work; check the latest checkpoint in WORKLOG.md.
5. Resume the highest-priority open issue. Never duplicate finished work.
   Never overwrite remote progress with a stale local copy; reconcile
   divergence before editing.

## Session ending checklist (master prompt §11)

Before ending a session: run tests for completed work → update docs →
deeply update WORKLOG.md (results, failures, next action) → update
PLAN.md → update active Issues (evidence, exact remaining work) → commit
completed and coherent partial work → push → verify the remote branch
contains the commits → record commit SHAs. A session must never close
with completed work that exists only on the disposable server. See
`docs/RECOVERY.md` for the honest runtime capability inventory.

## Rules

- Commit after every completed task; verify the push (`git ls-remote` or
  API) before claiming persistence.
- Never print/commit/log tokens. The GitHub token lives outside the repo.
- Never claim success without observed evidence (test output, ffprobe,
  frames for UI/render work).
- Tests: `python -m pytest tests/ -q` must stay green without network.
- `requirements.txt` pins `av==14.2.0` (14.3+ has no py3.12 Linux wheels;
  see KNOWN_ISSUES.md) — do not change without re-running CI + the e2e.
- Keep the provider layer swappable; never hard-depend on one LLM vendor.
- Translation sends transcript text to the chosen provider; keep it
  opt-in and document that in help text and docs.
- UI surfaces follow the owner playbook (docs/ui-research/): no dead
  controls, honest states, one accent, tokens in one place.

## Layout

`clipforge/` package · `tests/` · `docs/` (research, ui-research,
architecture, capability map) · `scripts/` local ops scripts ·
`PLAN.md` `WORKLOG.md` `DECISIONS.md` `KNOWN_ISSUES.md`
`RELEASE_CHECKLIST.md`.
