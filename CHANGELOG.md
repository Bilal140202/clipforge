# Changelog

All notable changes. Dates are UTC. Issue numbers reference
`Bilal140202/clipforge` on GitHub.

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
