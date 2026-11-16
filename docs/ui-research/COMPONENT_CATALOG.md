# ClipForge Component Catalog — v0.1 specifications

Status: **PROPOSAL** grounded in audited patterns (`USER_PROJECT_UI_AUDIT.md`). Components are specified for ClipForge's workflow surfaces — the studio UI that wraps the existing pipeline (`clipforge/pick.py` moment picking, `clipforge/transcribe.py` transcription, `clipforge/translate.py` translation, `clipforge/captions.py` caption building, `clipforge/pipeline.py` render orchestration). Tokens referenced here are defined in `DESIGN_SYSTEM.md`; rules referenced here are defined in `UI_ENGINEERING_PLAYBOOK.md`.

---

## 0. Shared conventions (all components)

**Placeholder conventions — no fake data, ever (Rule 6, Rule 10):**

| Situation | Renders as | Never renders as |
|---|---|---|
| Media file not yet probed (duration/resolution/fps unknown) | timecode placeholder `--:--:--` in `--text-mono-small` | a guessed duration, a rounded estimate |
| Score/probability the moment picker did not output for an item | chip labeled `UNKNOWN` (mono label, `--status-neutral`) | a zero, a fabricated percentage, a grayed bar at a made-up width |
| Transcript/translation text not yet produced | skeleton lines matching final line rhythm (`Skeleton` pattern) | "Sample text", lorem, the previous clip's text |
| Count that is zero | zero **with its cause**: "not yet analyzed" / "no moments passed the threshold" / "filtered out by your review state" / "index failed to load" (Rule 2, zero-cause triad) | bare "0 items" on a filtered surface |
| Preview frame not yet extracted | skeleton block at final aspect ratio, 9:16 | a gray fake poster, a stock image, another clip's frame |
| Export size estimate | value labeled "estimate (bitrate-derived)" with provenance | a precise-looking fake number |

**Status vocabulary** (one `StatusChip` component, colors from `DESIGN_SYSTEM.md` §3, always color + text + screen-reader text): `queued` (neutral), `analyzing`/`running` (info), `done` (success), `failed` (error), `canceled` (warning), `unverified` (neutral) — the linuxify `StatusChip` pattern: dot + mono label + `contentDescription = "Status: X"` (audit-android §6).

**Icon set:** lucide only; no emoji in chrome (Rule 9). **All interactive targets ≥44px** (Rule 7) — visible handles may be thinner; hit areas may not. **Focus:** global `:focus-visible` ring from tokens, never removed (Rule 8).

---

## 1. CandidateMomentCard

**Purpose.** One candidate moment for review: a real preview frame, its timecode range, the picker's stated reason/score, and the accept / reject / edit decision. This is the heart of ClipForge's review workflow — the moment-picking stage produces candidates (Ollama local LLM by default, speech-density heuristic fallback per the repo README), and this card is where a human ratifies them.

**Primary action.** Accept (adds the moment to the clip plan). Exactly one primary button; reject and edit are secondary steps-down (Rule 3).

**Anatomy.**
- **Preview frame** — extracted by ffmpeg from the actual source video at the moment's start timestamp; 9:16 crop preview using the same reframe logic family as `clipforge/reframe.py`. Until extraction completes: skeleton block at final aspect ratio (Rule 10). The frame is the card's loud element.
- **Timecode range** — `--text-mono-body`, tabular numerals: `00:04:12.500 → 00:04:47.000`; before probe completes: `--:--:-- → --:--:--` (Rule 5).
- **Score breakdown as labeled bars** — one row per score component the picker actually emitted (from `metadata.json`'s reason/run details per the README), each row: label + horizontal bar + numeric value in tabular numerals. If the picker emitted no component scores (e.g. heuristic fallback), the section renders the chip `UNKNOWN` — no bars are drawn at invented widths.
- **Reason line** — the picker's stated reason, quoted verbatim from its output; never paraphrased into confidence the model did not express (Rule 6, Law 13: positive evidence before mercy).
- **Warnings area** — reserved strip below the reason: rendered only when a real warning exists (e.g. "source audio quiet in this span", "face-track confidence low — center-crop fallback used"). Warnings pair an icon with text (Rule 4); an empty warnings area renders nothing, not "no warnings".
- **Actions** — Accept (primary), Reject, Edit (opens trim handles for this moment). All ≥44px.

**States.**
- *Default* — surface-1 card, radius-md, outline hairline; preview frame + timecodes + score section.
- *Hover* — surface-2 elevation step (tonal, no shadow); 120ms.
- *Active/selected* — `--accent-container` wash at 8-12% alpha tint (momotts practice); accent hairline; announced via `aria-selected` when in a listbox.
- *Disabled* — actions disabled while the source file is missing or being probed; the card states why ("source not loaded yet") instead of silently dead buttons (Rule 2).
- *Loading* — full-card skeleton matching final layout: frame-sized block, two timecode lines, three bar rows (Rule 2; nexpdf Skeleton pattern).
- *Empty* — not applicable per-card; the rail's empty state distinguishes "not yet analyzed" / "no moments passed the threshold" / "filtered out" / "analysis failed" (Rule 2, Law 4).
- *Error* — frame extraction failure renders an error block inside the card frame area: what happened ("frame extraction failed"), why ("ffmpeg exited 1 on segment 00:04:12"), next action ("Retry frame" button + "Open source" link). Dead-end errors are bugs (Rule 2).

**A11y.** The review rail is `role="listbox"` with cards as `role="option"` `aria-selected`; each card has an accessible name of the form "Candidate 3, 00:04:12 to 00:04:47, suggested"; score bars are `role="img"` with a full aria-label describing label and value (the ahyeon-archive segmented-bar pattern, audit-web §12b); accept/reject/edit are real `<button>`s with visible text labels; tab order follows the workflow; the whole decision loop is keyboard-operable (`INTERACTION_PATTERNS.md` §1). Contrast: all text ≥4.5:1 per DESIGN_SYSTEM §4.

**Playbook rules applying.** Rule 2 (trust triad), Rule 3 (one loud thing — the frame), Rule 4 (warnings/status not color-only), Rule 5 (tabular timecodes), Rule 6 (UNKNOWN scores, verbatim reason), Rule 8 (keyboard), Rule 9 (no emoji), Rule 10 (real frames only).

## 2. TimelineStrip

**Purpose.** Horizontal strip showing the accepted moments laid out against the source duration — what is in the cut, in order, with drag handles for trim boundaries. It is orientation, not the review surface; it never carries decisions.

**Primary action.** None — the strip is navigational (playhead scrub / select a moment). Its quietness is the point (Rule 3).

**Anatomy.**
- **Track** — bg-level surface (elevation 0); accepted moments render as accent-tinted segments proportional to real durations (from probed media; Rule 10).
- **Time ruler** — mono labels, tabular numerals, tick spacing derived from real total duration; `--:--:--` placeholders while the source is unprobed.
- **Segment edges** — visible 2px handles with **44px invisible hit areas** (Rule 7).
- **Playhead** — 1px accent line + small mono timecode readout.

**States.** *Default* / *Hover* (segment edge highlights, handle enlarges to visible 44px-equivalent) / *Active* (dragging: segment shows origin and destination — motion must show what changed, Rule 12) / *Disabled* (no source loaded: strip renders an empty-state band "Import a video to build a timeline" — a door, not a dead end) / *Loading* (ruler and segments skeleton after source probe starts) / *Empty* (no accepted moments yet: teaches the next action "Review candidates to add moments") / *Error* (probe failure banner with retry — what/why/next action).

**A11y.** `role="toolbar"`/`role="slider"` semantics for the playhead (arrow keys step frames; Home/End jump); segments are focusable stops announcing "Moment 2, 00:04:12 to 00:04:47"; trim via keyboard (arrow keys move the focused boundary; shift+arrow = 1s). Zoom controls ≥44px.

**Playbook rules.** Rule 3 (quiet), Rule 5 (ruler numerals), Rule 7 (hit areas), Rule 8 (keyboard scrub), Rule 10 (real durations), Rule 12 (drag shows change).

## 3. TranscriptEditor

**Purpose.** Edit the clip's transcript/subtitles: original text and (when translation is enabled) translated text side-by-side, with word-level timestamps from `clipforge/transcribe.py` (faster-whisper, word-level per the README) and translations from `clipforge/translate.py` (Argos, local). Every edit is attributable: AI-suggested vs manually-edited is always visible.

**Primary action.** Commit the edited segment (applies the edit to the subtitle track and marks the line "Edited").

**Anatomy.**
- **Two-pane layout** — original (left) / translated (right); rows locked to the same segment so a pair scrolls together. Each row: mono timecode gutter (start–end, tabular) + editable text body.
- **Provenance badge per row** — `AI-suggested` (neutral/info chip) vs `Edited` (accent chip) vs `Unreviewed` — text + hue, never hue alone (Rule 4). A row the human touched keeps its `Edited` badge after undo? No — reverting restores the previous state and the badge reverts with it; the badge reflects current content provenance, not history.
- **Word-timing indicator** — for karaoke captions (`clipforge/captions.py`), rows show whether word-level timing exists for this segment; missing word timings render `UNKNOWN` in the timing column, not a fabricated spread.
- **Translation status column** — for the translated pane: `translated` / `translation failed` / `UNKNOWN` (no translation requested) — each with its own text label and a per-row retry action on failure.

**States.** *Default* (rows on surface-1; alternating rows may use bg for rhythm) / *Hover* (row surface-2) / *Active* (focused row: accent hairline; caret visible) / *Disabled* (read-only mode while a re-transcription is running; banner states why and when it clears) / *Loading* (skeleton rows matching final line rhythm — count from the real transcript length once known, generic pulse before that) / *Empty* (no transcript yet: "Run transcription to fill this pane" pointing at the exact control; distinct from "transcription failed" which offers Retry with the error reason) / *Error* (transcription/translation failure banner: what/why/next; per-row retry for single failed translations).

**A11y.** The editor is a standard editable text container (contenteditable or textarea-per-row) — full keyboard editing with undo/redo (`INTERACTION_PATTERNS.md` §2); row chips are text (screen-reader complete); side-by-side relationship announced via `aria-describedby` linking the translation to its original; timecode gutter is `aria-hidden` (duplicated in the row's accessible description). Contrast per DESIGN_SYSTEM §4.

**Playbook rules.** Rule 2 (triad), Rule 4 (provenance badges), Rule 5 (timecode gutter), Rule 6 (no invented word timings; edits attributable), Rule 8 (keyboard + undo), Rule 10 (real text only), Rule 13 (state what translation is: local Argos, per README).

## 4. CaptionStyleBrowser

**Purpose.** Choose caption styling (font, size, position, colors, karaoke mode) with a **live preview rendered from the real transcript text** — never "The quick brown fox" or "Sample caption".

**Primary action.** Apply style (writes the style preset used by `clipforge/captions.py`).

**Anatomy.**
- **Preview pane** — a real frame from the clip (same extraction path as CandidateMomentCard) with the styled caption composited on top; uses the actual current transcript segment at the preview timecode. Under reduced-motion, the preview is a static composite (no cycling animation) — the HeroVideo downgrade principle (audit-web §2).
- **Style controls** — size, position, color pairs (text/outline), karaoke highlight mode; every control ≥44px; values read from tokens where a token exists.
- **Preset list** — named presets; a preset that requires a capability not present (e.g. a font not shipped) renders disabled **with the reason on the row** (Rule 13: strikethrough/limit stated, not hidden).

**States.** *Default* / *Hover* / *Active* (preset selected: accent-container tint + `aria-selected`) / *Disabled* (no clip loaded: preview area shows "Import a video to preview caption styles") / *Loading* (preview frame extraction: skeleton at preview aspect ratio; controls remain usable) / *Empty* (no transcript text yet: preview shows the frame alone and a notice "Caption preview appears once a transcript exists" — the empty state teaches the next action) / *Error* (style-apply failure: what/why/next; preview render failure falls back to the bare frame + error line, never a fake caption).

**A11y.** Controls are labeled (`aria-label` where icon-only, visible text preferred); color controls present both the color swatch and its name ("Ink on paper", "Cyan on graphite") — color never alone (Rule 4); the preview pane is `role="img"` with an aria-label describing the style ("white text, black outline, bottom center, karaoke cyan highlight"); live region announces applied style changes politely.

**Playbook rules.** Rule 2, Rule 4, Rule 7, Rule 9 (icons not emoji), Rule 10 (real frame + real transcript text), Rule 12 (no decorative cycling under reduced motion).

## 5. RenderQueueRow

**Purpose.** One row per render/export job: what is rendering, its measurable progress or honest indeterminate state, cancel/retry actions, and its logs. A ledger, not a raw table (playbook Law 7: ledgers answer "what happened to my stuff").

**Primary action.** Contextual: cancel while running; retry after failure; open output when done.

**Anatomy.**
- **Identity** — job name (clip slug), source, started-at absolute timestamp (Rule 5: absolute timestamps in ledgers).
- **Progress** — shown **only** when the pipeline reports a measurable fraction (ffmpeg/whisper progress where available); otherwise an indeterminate pulse bar + label "working — progress not reportable". A fabricated percentage is a Rule 6 violation. The running state's pulse dot is ClipForge's single sanctioned ambient motion (DESIGN_SYSTEM §8).
- **Status chip** — queued / running / done / failed / canceled via the shared `StatusChip` (color + text + sr text).
- **Logs** — expandable per-row log region (playbook Law 7: expandable per-item reasons); last error line surfaced in the row when failed, with the full log one click away.

**States.** *Default* / *Hover* / *Active* (expanded row) / *Disabled* (cancel disabled in the last moments of a finishing job — with tooltip "finalizing, too late to cancel") / *Loading* (row skeleton when the queue index is refreshing) / *Empty* (queue empty states: "not started yet" vs "nothing matches this filter" vs "queue index failed to load" — Rule 2 zero-cause triad) / *Error* (failed row: what happened, why, next action = Retry + "Open logs"; a failed job never silently leaves the queue).

**A11y.** Row is a list item with an accessible name "Render job jellyfish-immortal, running, 62 percent" or "…running, progress not reportable"; progressbar role with `aria-valuenow` only when a real fraction exists (omitted otherwise); cancel/retry/open are ≥44px buttons with text labels; expanded log region is a labeled region with keyboard access.

**Playbook rules.** Rule 2, Rule 3 (the running/failed job is the loud thing), Rule 4, Rule 5 (absolute timestamps, tabular numbers), Rule 6 (measurable progress only), Rule 12 (pulse dot is sanctioned ambient motion).

## 6. ExportPanel

**Purpose.** Configure and launch the final export: resolution, caption variant (original / translated per the README's `clip_final.<lang>.mp4` outputs), bitrate, output naming — and state exactly what will be produced before it is produced.

**Primary action.** Start export.

**Anatomy.**
- **Manifest preview** — the exact list of outputs that will be produced (primary mp4, translated variant + srt, metadata.json, transcript.json — the artifact set the README documents), each with its real expected filename; unknown-at-config-time fields (e.g. final size) render "determined at render time", not estimates dressed as facts.
- **Options** — resolution (1080×1920 default per README), caption language toggle (only languages actually present from `clipforge/translate.py`), container/bitrate selects. An option not available in the current build is absent or disabled-with-reason (Rule 13).
- **Cost/time statement** — honest runtime expectation ("runs locally; a 60s clip typically renders in minutes on CPU") — stated in measured terms from real runs; until measured numbers exist, the panel says "duration varies — first runs are unmeasured", never a made-up average (Rule 6).

**States.** *Default* / *Hover* / *Active* (export running: primary button becomes "Open render queue"; the panel's loud thing moves to the queue) / *Disabled* (no accepted moments: button disabled with reason "review and accept at least one moment") / *Loading* (manifest computation skeleton) / *Empty* (nothing to export: same door copy as the review rail) / *Error* (export launch failure: what/why/next — e.g. "output directory not writable — choose another location").

**A11y.** Form semantics with labeled groups; the manifest list is a real list; the primary button carries its state in text ("Start export" → "Export running — open queue"); errors are `role="alert"`.

**Playbook rules.** Rule 2, Rule 3, Rule 4, Rule 5 (filenames/numbers mono, tabular), Rule 6 (no fake size/duration), Rule 13 (honest runtime copy).

## 7. SettingsProviderPanel

**Purpose.** Disclose every provider and data-flow decision in one place: what runs locally, what touches the network, which models are used, where files are written — and the controls to change them.

**Primary action.** Save settings — via optimistic save with rollback (`INTERACTION_PATTERNS.md` §5): the panel updates immediately, and a failed save restores values and shows a named-failure banner with Retry (the ahyeon-archive verified pattern, audit-web §12b).

**Anatomy.**
- **Data-flow disclosure block** — explicit, plain-language table of each stage: download (network: source video URL), transcription (local, faster-whisper), moment picking (local Ollama qwen2.5:3b by default; speech-density heuristic fallback), translation (local Argos, optional), rendering (local ffmpeg). "Network" vs "local" is a text column + icon — never color alone (Rule 4). This block is the panel's loud thing: the local-first promise is a design feature (Rule 13).
- **Model selection** — the Ollama model tag actually configured; a model that is not installed renders "not installed — pull required" with the command, per the README's `ollama serve` step.
- **Paths** — workspace/output directories rendered in mono (Rule 5); a missing/unwritable path is an inline error with the fix, not a silent fallback.
- **Version/provenance footer** — app version and, if applicable, the settings-file path.

**States.** *Default* / *Hover* / *Active* / *Disabled* (read-only while a render is running — banner explains why settings that affect rendering are locked) / *Loading* (skeleton rows for the provider table while config loads) / *Empty* (n/a — settings always exist; an unset value renders its honest default label, e.g. "target language: none") / *Error* (save failure: optimistic rollback + banner naming the setting that failed + Retry; disk errors state the path).

**A11y.** `role="radiogroup"`/`aria-checked` semantics for option sets (the ahyeon-archive pattern, audit-web §12b); the disclosure table is a real `<table>` with headers; every toggle has a visible label; `aria-live="polite"` announces save success/failure.

**Playbook rules.** Rule 2 (triad + optimistic rollback), Rule 4, Rule 5 (mono paths), Rule 6 (no invented install states), Rule 8 (keyboard), Rule 13 (explicit local/cloud disclosure — the defining requirement of this panel).

---

## Traceability summary

| Component | loudest element | audited pattern source |
|---|---|---|
| CandidateMomentCard | real preview frame | linuxify shared-state kit (audit-android §6); ahyeon-archive attribution UI (audit-web §12a); HeroVideo real-media discipline (audit-web §2) |
| TimelineStrip | playhead | signal-noise tuner/scroll-ruler concept (audit-web §4); Rule 7 hit-area requirements |
| TranscriptEditor | focused row | ahyeon-archive optimistic-save + radio semantics (audit-web §12b); linuxify mono runtime values (audit-android §6) |
| CaptionStyleBrowser | live preview | ahyeon-s-vision HeroVideo downgrade (audit-web §2); showcase preset/contract discipline (audit-web §3) |
| RenderQueueRow | running/failed job | playbook Law 7 ledger; linuxify StatusChip (audit-android §6); playbook candidate 17 (actionable-first ordering) |
| ExportPanel | manifest preview | bilal-s-grand-showcase "every number rendered is real" (audit-web §3) |
| SettingsProviderPanel | local/cloud disclosure | playbook Law 12; momostack "Telemetry-Zero" honesty (audit-web §5); ahyeon-archive radiogroup (audit-web §12b) |
