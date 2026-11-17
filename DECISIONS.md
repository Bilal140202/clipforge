# DECISIONS.md — project decisions with rationale

Append-only; newest at bottom. Architecture details in
`docs/architecture/ARCHITECTURE_DECISIONS.md`.

## D-001 — From-scratch repo replaces the fork
2026-11-17. Owner direction: "why forks when we are building from scratch".
The fork of `superz1402/clipforge` was deleted (HTTP 204) and a fresh
`Bilal140202/clipforge` created with Issues enabled. Session-1 code/docs
that were clean-room MIT work were re-homed; upstream-specific content
(content production, music licensing evidence) was left to the legacy repo.
Consequence: no fork relationship, no upstream reconciliation burden.

## D-002 — Provider adapter layer, translation optional
2026-11-17. `clipforge/providers.py` adapts Ollama (local, key-free,
default) and the z-ai CLI (cloud). Translation, re-ranking and any LLM
feature must go through this layer and must degrade with a clear message
when no provider exists. Privacy: cloud providers receive transcript text —
always opt-in (flag or env), documented in README and doctor output.

## D-003 — Subtitle gates are mechanical and clean-room
2026-11-17. perfect-srt (upstream inspiration) is unlicensed, so `subtitles.py`
is a clean-room implementation: five gates (duration, layout, timing/overlap,
content, order), a repair pass that merges/splits/clamps but never rewrites
text, and SRT/VTT I/O. Gate failures block "done" states downstream (the
pipeline records gate results in metadata.json).

## D-004 — av pinned >=14.2,<15
Carried from session 1 (KI-001): faster-whisper 1.2.1 needs PyAV's
`metadata_errors` kwarg, removed in av 15. Re-verify on faster-whisper >1.2.1.

## D-005 — Tests run offline
2026-11-17. Unit tests use synthetic transcripts and a fake provider class;
network/model calls are never exercised by the suite. Provider integrations
get e2e verification runs recorded in WORKLOG.md, not flaky unit tests.

## D-006 — UI direction (carried)
Dark-first graphite + terminal-cyan tokens per the owner's own systems;
binding rules in `docs/ui-research/UI_ENGINEERING_PLAYBOOK.md`.
