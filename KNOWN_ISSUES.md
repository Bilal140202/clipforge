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

## KI-007 — Bilingual 2-line translation can graze the karaoke caption
Trans style (MarginV=320) sits above Caption (MarginV=220); when the
translated line wraps to 2 lines its lower edge can touch the caption
block (observed on real-footage e2e, frame at ~20s). Fix in the caption
polish pass: raise Trans MarginV or cap translations at 1 line with
ellipsize-and-review. Cosmetic; not blocking.

## KI-008 — Base-model ASR artifacts on compressed low-res audio
Real-footage e2e (NASA 320px preview, AAC compressed) produced plausible
commentary but some fragmentary phrases ("Now filter converge."). Not a
bug: faster-whisper `base` on 320p audio + heuristic discovery limits
(issues #7/#8 cover LLM re-ranking + corpus validation). Mitigations:
prefer higher-quality sources; switch --whisper-model to small/medium.
