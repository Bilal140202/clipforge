# Changelog

All notable changes. Dates are UTC. Issue numbers reference
`Bilal140202/clipforge` on GitHub.

## [0.4.2] — 2026-11-17

### Fixed — shot detection actually works; crop motion is now cut-aligned
- `shots.py`: showinfo writes at INFO level, and the previous
  `-v error` capture silenced it — scene detection ALWAYS returned []
  and every source looked single-take. Detection now runs without
  `-v error` and warns loudly on failure (verified on a 33.6-min
  fast-cut source: 703 cuts / 20.9 per min, where the old code
  claimed 0).
- `reframe.py`: the 9:16 crop now changes framing ONLY at the source's
  own camera cuts (the snap is masked by the cut); between cuts it is
  dead-zoned (10% width) and velocity-capped (6% width/s). The crop
  never invents motion the source doesn't have — measured: rendered
  frame-diff spikes now coincide exactly with the source's cut
  timestamps.
- `reframe.py`: fixed a crash when real faces appear (`rects or []` is
  truthy-ambiguous for numpy arrays; `detectMultiScale` results are
  now length-checked). Found on the first real-faces render.

## [0.4.1] — 2026-11-17

### Fixed — the "cuts camera angles every few seconds" reframe bug
- Measured root cause: the MediaPipe face-track EMA could teleport the
  9:16 crop between (often false-positive) detections with no speed
  limit — delivered clips measured 6-9x the source's own motion
  (median inter-frame change 33.4 vs 3.8-10.2 in the raw segment).
- `reframe.py` rewritten: OpenCV Haar cascade (mediapipe dependency
  removed), nearest-face stickiness (never bounces across the frame),
  a 6%-width dead-zone and a hard glide cap (10% of width per second).
  The fixed render measures 3.98 median change, 0 jump spikes.
- Shot-aware discovery: new `clipforge/shots.py` (ffmpeg scene-change
  detection); candidates gain the `shot_stability` sub-score, window
  edges snap onto camera cuts (open on a fresh take, close before the
  camera cuts away), and `internal_cuts` / `shot_evidence` are recorded
  per candidate. 7 new unit tests (76 total).

## [0.4.0] — 2026-11-17

### Added — permanent caption-language rule (#17)
- `clipforge/langrule.py`: one pure decision function + `CaptionPlan`.
  Same language → karaoke captions. English chosen → **full English
  only** (translated cues AND translated hook; nothing in the source
  language appears). Any other requested language → the tool asks:
  same-language or English (TTY prompt; exit code 2 + exact question for
  agents). Unknown source language handled explicitly.
- `--caption-lang` flag on `render`; `--translate-lang` still accepted.
  `--caption-mode` is now a legacy knob: the rule overrides it whenever
  English captions are chosen, with a loud note in the output.
- Rule wired into BOTH `cli.py render` and the legacy `pipeline.py`
  (decision made before any heavy work; pipeline metadata records the
  plan note as `caption_rule`).
- `translate.translate_hook` + `translate.fit_hook`: the hook line is
  translated and fitted for the 104px Hook style on English-only clips.
  Provider failure is a hard error there — never a silent fallback to a
  source-language hook.
- 13 decision-table tests (`tests/test_langrule.py`) + 4 hook tests.

### Changed
- README rewritten: rule section with decision table, CLI reference,
  gates explained in plain words, FAQ.

## [0.3.0] — 2026-11-17

### Added — translation-only caption mode (#16)
- `render --caption-mode translation`: main output carries ONLY the
  translated line + hook (TransSolo style, caption zone); no
  source-language karaoke. Default `bilingual` preserved old behavior
  (now superseded by the #17 rule).
- `translate._fit_subtitle`: deterministic G2 layout enforcement
  (word-wrap at 42 chars, hard-slice for spaceless CJK, 2-line cap with
  ellipsis). Added when the translated SRT was gated for the first time
  and flagged a 44-char cue.

## [0.2.0] — 2026-11-17

- Owner Korean footage clipped end-to-end (#15); KI-007 caption
  collision fixed (clearance between caption block and raised
  translation); recycle-wipe recovered from GitHub with zero loss.

## [0.1.0] — 2026-11-16

- First working loop: local transcription, multi-signal discovery with
  explainable ranking, cut, face-tracked 9:16 reframe, karaoke captions
  + hook, subtitle gates, repair, SRT/VTT export, provider adapters.
