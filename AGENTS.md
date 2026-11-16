# AGENTS.md — ClipForge agent operating instructions

This repo is built and operated by AI agents. Read this first.

## Identity

- Single, from-scratch repository: `Bilal140202/clipforge` (MIT).
- No fork lineage: an earlier fork of `superz1402/clipforge` was deleted
  2026-11-17; session-1 material is archived locally at `clipforge-arch/`
  (sandbox only) and its useful code was re-homed here cleanly.
- Upstream `superz1402/clipforge` is unrelated legacy (content-production
  repo); do not merge it.

## Startup sequence

1. `git fetch && git log --oneline -10 && git status`.
2. Read `PLAN.md`, `WORKLOG.md`, `DECISIONS.md`, `KNOWN_ISSUES.md`.
3. Read open GitHub Issues (they are enabled on this repo).
4. Resume the highest-priority open issue. Never duplicate finished work.

## Rules

- Commit after every completed task; verify the push (`git ls-remote` or
  API) before claiming persistence.
- Never print/commit/log tokens. The GitHub token lives outside the repo.
- Never claim success without observed evidence (test output, ffprobe,
  frames for UI/render work).
- Tests: `python -m pytest tests/ -q` must stay green without network.
- `requirements.txt` pins `av>=14.2,<15` (see KNOWN_ISSUES.md) — do not
  remove without re-running the e2e pipeline.
- Keep the provider layer swappable; never hard-depend on one LLM vendor.
- Translation sends transcript text to the chosen provider; keep it
  opt-in and document that in help text and docs.

## Layout

`clipforge/` package · `tests/` · `docs/` (research, ui-research,
architecture, capability map) · `scripts/` local ops scripts ·
`PLAN.md` `WORKLOG.md` `DECISIONS.md` `KNOWN_ISSUES.md`
`RELEASE_CHECKLIST.md`.
