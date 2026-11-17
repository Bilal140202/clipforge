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

## KI-007 — RESOLVED 2026-11-17: translation/karaoke caption collision
Originally: Trans (MarginV=320) could touch the caption block when the
karaoke caption wrapped to 3 display lines (observed on owner footage,
frame ~2s; and on NASA footage at ~20s as a graze). Fixed in
`clipforge/captions.py`: Caption fontsize 78→64 with side margins
60→110 (forces ≤2 display lines), Trans MarginV 320→520. Regression
test `test_style_layout_keeps_trans_clear_of_captions` enforces a 40px
clearance between the Trans bottom and the 3-line caption worst case
(an intermediate fix at 440 failed in practice — a 2-line Trans met a
3-line caption exactly at the boundary — so the test forbids
boundary-touching, not just overlap). Verified on re-rendered frames.

## KI-008 — Base-model ASR artifacts on compressed low-res audio
Real-footage e2e (NASA 320px preview, AAC compressed) produced plausible
commentary but some fragmentary phrases ("Now filter converge."). Not a
bug: faster-whisper `base` on 320p audio + heuristic discovery limits
(issues #7/#8 cover LLM re-ranking + corpus validation). Mitigations:
prefer higher-quality sources; switch --whisper-model to small/medium.
