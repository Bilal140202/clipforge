# KNOWN_ISSUES.md — verified issues and limitations

Newest first.

## KI-001 — PyAV >= 15 breaks faster-whisper transcription
`TypeError: open() got an unexpected keyword argument 'metadata_errors'`
(observed session 1). Pinned `av>=14.2,<15` in requirements.txt + pyproject.
Re-visit when faster-whisper >1.2.1 ships.

## KI-002 — mediapipe pinned 0.10.14 (legacy)
Works on py3.12 (import verified). Upgrade requires a reframe verification
run on real footage. Not touched yet.

## KI-003 — Discovery v1 is heuristic-only
No LLM re-ranking yet; `transcription_confidence` stays null; language is
per-transcript; `visual_evidence_refs` empty. By design for v1; tracked in
Issues.

## KI-004 — CI not yet observed on the fresh repo
`.github/workflows/tests.yml` from session 1 must be re-homed and its first
green run observed before issue #1 closes. (Session-1 CI failed twice on
the fork; root cause of run 2 undiagnosed — do not assume the dep-subset
fix was sufficient.)

## KI-005 — Cloud provider privacy boundary
z-ai provider sends transcript text to a cloud service. Acceptable for
sandbox operation; for end users this must stay opt-in (it is: no provider
is auto-selected for cloud unless configured; Ollama is preferred by
`get_provider`).

## KI-006 — cli.py `subtitles --out` mixes JSON and plain text outputs
`_write_out` handles both, but the ops contract would be cleaner with
explicit --format. Cosmetic; tracked for the CLI polish pass.
