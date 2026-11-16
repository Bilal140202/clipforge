# ARCHITECTURE_DECISIONS.md — architecture decisions record

Companion to root `DECISIONS.md` (project/process decisions live there).
Format: context → decision → consequences. Append-only.

## AD-001 — Discovery engine sits beside, then above, the single-moment picker
Context: upstream picks ONE moment per run via Ollama prompt or a
speech-density fallback (`clipforge/pick.py`); master prompt requires ranked,
explainable, deduplicated candidates combining SupoClip + PeakCut ideas.
Decision: new module `clipforge/discover.py` with its own public function
`discover_moments()` and CLI (`python -m clipforge.discover`); pipeline gains
opt-in `--use-discover`/`--top-n`; default behavior untouched.
Consequences: pick.py stays the default until discovery is validated on
varied corpora; both engines write the same downstream artifacts
(moment.json / candidates.json); future LLM re-ranking plugs into discovery
as an additional evidence signal, not a replacement of the schema.

## AD-002 — Pure-function core, evidence-carrying edges
Context: scores must be testable without models/network and explainable to
humans and agents.
Decision: discovery core is pure (transcript dict in → candidates out);
audio RMS is an optional side-input (`--audio`); every candidate carries its
evidence (sub-scores, window origin, audio refs) and honesty markers
(`score_basis`, `transcription_confidence: null`, `review_status`).
Consequences: unit tests run anywhere (21 green, <1s); swapping the
heuristic for model-based scoring changes only `score_candidate()`;
agents can audit why a moment ranked where it did from candidates.json alone.

## AD-003 — Media engine stays on ffmpeg/ffprobe subprocesses
Context: upstream uses ffmpeg subprocesses with argument arrays; master
prompt allows any justified pipeline.
Decision: keep ffmpeg/ffprobe CLI subprocess pattern (no new heavy
dependencies; discovery's RMS uses `ffmpeg -f f32le` pipe, 0.5 s hop).
Consequences: no python media libs added; RMS evidence is cheap
(2 min audio < 1 s CPU in the e2e run); later GPU/hwaccel flags slot into
the same command builders.

## AD-004 — av pinned <15 until faster-whisper supports it
Context: fresh installs broke at transcribe time with av 15
(KI-001, observed).
Decision: `av>=14.2,<15` in requirements.txt with an explanatory comment.
Consequences: fresh installs work; revisit when faster-whisper >1.2.1
releases.

## AD-005 — Fork-first persistence
Context: token cannot push to upstream; addendum requires GitHub-first
persistence with commit-after-task discipline.
Decision: `Bilal140202/clipforge` is the active remote for all work; issues
live on the fork; upstream reconciliation is an owner action.
Consequences: history preserved via fork relationship; no force-push to
anyone else's repo; CI runs on the fork.
