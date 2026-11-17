# ClipForge UI Engineering Playbook — binding rules

Status: **binding** for every ClipForge UI change. Version: v0.1 (2026-11-16).
Adapted from the owner's `agent-ui-playbook` (13 laws + candidates, `/home/z/my-project/staging/repos/agent-ui-playbook/PLAYBOOK.md`, re-verified for this document) and the strongest findings of the merged user-project audit (`USER_PROJECT_UI_AUDIT.md` in this directory). Each rule carries: **Statement** · **Why** · **Implement in ClipForge** · **Verify** (grep-able, in the owner's playbook format).

**Scope note.** ClipForge's studio UI (candidate moment review, transcript/subtitle editing, caption styling, render queue, export) is planned but not yet implemented; the pipeline (`clipforge/pipeline.py`, `clipforge/pick.py`, `clipforge/transcribe.py`, `clipforge/translate.py`, `clipforge/captions.py`) is the backend these surfaces will drive. All verify commands below are written against the planned UI source tree `ui/src/` with the single token file `ui/src/tokens.css`. Until that tree exists, the commands are the definition of the gate the first UI commit must pass; they are not evidence of existing code.

---

## Rule 1 — Token-only styling; no inline hex

**Statement.** Every color, spacing, radius, duration and easing value used by a component comes from the token file (`ui/src/tokens.css`, see `DESIGN_SYSTEM.md`). Components reference `var(--…)` only. One deliberate accent color beats three decorative ones (playbook Law 1, PLAYBOOK.md:14).

**Why.** Components that hardcode colors drift the moment a second session touches them; bolt-on dark mode then shows broken seams in borders, shadows and hover states (PLAYBOOK.md:16). Verified failure cases: jarvis-agent declares `colors.xml` but hardcodes hex in every layout (`jarvis-agent/app/src/main/res/layout/activity_main.xml:6, 24, 52, 126, 160, 448` — audit-android §1); Liteshare carries 37 literal `Color(0xFF2196F3)` occurrences and a 0-byte theme file (`lib/src/core/theme/ui_enhancements.dart` — audit-android §4); ahyeon-s-vision leaks `style={{ color: "#e84040" }}` inline (`src/pages/Index.tsx:687` — audit-web §2).

**Implement in ClipForge.** `ui/src/tokens.css` is the only file allowed to contain raw color literals; it carries `:root` (dark-first values) and a light column. Any component needing a color the set lacks is a token-set bug — add the token, do not inline the value. Editor-specific consequence: preview-safe and light themes are second columns of the same data, never per-component overrides.

**Verify.**
```bash
# must return nothing (raw hex or rgb() outside the token file)
grep -rEn '#[0-9a-fA-F]{3,8}|rgba?\([0-9]' ui/src --include='*.css' --include='*.tsx' --include='*.ts' --include='*.html' | grep -v 'ui/src/tokens.css'
```

## Rule 2 — The trust triad: loading, empty, and error are designed before the happy path counts

**Statement.** Every async surface — import, transcription, moment picking, translation, render, export — ships designed loading, empty and error states before its happy path counts as done. Errors always state (a) what happened, (b) why, (c) the next action; dead-end errors are bugs (playbook Law 3, PLAYBOOK.md:47; `AGENTS.md` rule 2).

**Why.** The happy path is the only path an agent naturally generates; everything else is where trust dies (PLAYBOOK.md:49). Verified good implementations to copy: linuxify routes every list surface through shared `EmptyState` / `LoadingState` / `ErrorState` composables (`linuxify/app/src/main/java/com/linuxify/app/ui/components/Common.kt` — audit-android §6); ahyeon-archive's decision app renders loading, `role="alert"` error with "Try again", and filter-aware empties that explain themselves (`ahyeon-archive/pages/verify-the-unverified/client/src/App.tsx:449-475` — audit-web §12b); bilal-s-grand-showcase's `ErrorBoundary` gives recovery links and never a stack trace (`bilal-s-grand-showcase/src/components/site/ErrorBoundary.tsx` — audit-web §3).

**Implement in ClipForge.** Shared components first (the linuxify pattern): `LoadingState` = skeleton matching final layout (nexpdf `ui/common/Skeleton.kt` pulse pattern); `EmptyState` names the next action ("Import a video to begin — pick a source file" is a door; "No moments yet" is a dead end); `ErrorState` = banner (not toast) with reason + retry + escape hatch. A zero count on any filtered surface must say why it's zero — never stored / outside window / filtered out / failed to load (playbook Law 4); an empty candidate list during analysis is *not* the same state as "no candidates passed the threshold".

**Verify.**
```bash
# every async surface file must mention all three states; list files that fail
files=$(grep -rl 'await ' ui/src --include='*.tsx')
grep -L 'Loading\|Skeleton' $files   # async files with no loading state
grep -L 'Empty\|empty'      $files   # async files with no empty state
grep -L 'Error\|error'      $files   # async files with no error state
```
(Manual companion: for each async surface answer — what renders on timeout, on empty result, on a failed download? "Framework default" means not done.)

## Rule 3 — One loud thing per screen

**Statement.** Every screen has exactly one primary element — the answer to "should I worry? what do I do next?" — rendered at full weight; everything else steps down (playbook Law 9, PLAYBOOK.md:127).

**Why.** Uniform element weight forces users to diff the page themselves; the AI-generated variant is every card at the same elevation (PLAYBOOK.md:129). A dense editor without hierarchy is "a wall of equal cards" (audit-web §8, Avoid #9).

**Implement in ClipForge.** One loud thing per workspace section: Review → the candidate preview under decision; Timeline → the playhead/active clip; Render queue → the one running (or one failed) job; Settings → the local/cloud disclosure. Everything else steps down a token level (surface, text-dim). Never two simultaneous primary buttons in a view.

**Verify.**
```bash
# enumerate the views to squint-test (one primary per view); each hit is a screen to blur-check
grep -rEn 'primary-action|PrimaryButton' ui/src --include='*.tsx' | sort
```
(Manual companion, from the playbook: squint or blur the screen. Does exactly one thing stand out?)

## Rule 4 — Color never carries meaning alone

**Statement.** Status = color + text label (and/or icon). Color-coded dots get screen-reader text. Grounded in WCAG 2.2 SC 1.4.1 (playbook Law 2, PLAYBOOK.md:31).

**Why.** ~8% of men have some color-vision deficiency, and screenshots of status surfaces travel to contexts (print, grayscale, foreign tools) where the palette is not guaranteed (PLAYBOOK.md:33). Verified pattern: linuxify's `StatusChip` renders an 8dp dot **plus mono label** plus `contentDescription = "Status: ${status.label}"`, and its `Color.kt:32-42` carries the comment "never color-only: always paired with label" (`linuxify/.../ui/theme/Color.kt`, `ui/components/Common.kt:24-63` — audit-android §6).

**Implement in ClipForge.** Every render/queue/import state (queued / running / done / failed / canceled) renders through one `StatusChip`-style component: color token + text label + `aria` description. Candidate accept/reject states pair the tint with a visible word, never a green/red border alone. Provenance/aI-suggestion badges in the transcript pair hue with a word ("AI-suggested", "Edited").

**Verify.**
```bash
# every color-tinted status element must carry a label prop or label child — list suspects for manual grayscale check
grep -rEn 'tone="(success|warning|error|info|neutral)"' ui/src --include='*.tsx' | grep -v 'label'
```
(Manual companion, from the playbook: screenshot every status surface in grayscale — if pass/fail is indistinguishable, it fails.)

## Rule 5 — Tabular numerals for timecodes and counts

**Statement.** `font-variant-numeric: tabular-nums` on anything countable; numbers right-aligned in tables; monospace for IDs, paths, hashes; relative dates in dense lists, absolute timestamps in ledgers (playbook Law 6, PLAYBOOK.md:90).

**Why.** Proportional digits make columns shimmer so users cannot compare rows (PLAYBOOK.md:92). In a video editor every surface is numeric — timecodes, durations, bitrates, queue counts — and shimmering timecodes make scrubbing unreadable. Verified pattern: linuxify sets `FontFamily.Monospace` for **all runtime values** (paths, sizes, PIDs, ports, statuses) as a deliberate developer-tool voice (`linuxify/.../ui/theme/Type.kt` — audit-android §6); bilal-s-grand-showcase ships `.data-mono { tabular-nums }` (`bilal-s-grand-showcase/src/index.css:249-297` — audit-web §3); nexpdf keeps exactly 5 type roles to prevent drift (`nexpdf/.../ui/theme/Type.kt` — audit-android §5).

**Implement in ClipForge.** One `Timecode` component renders every time value, in the mono/data voice with `tabular-nums`; the token scale defines `--font-mono-data`. Durations, file sizes, and queue counts use the same voice. No component formats a timecode inline.

**Verify.**
```bash
# no timecode-like string should exist outside the Timecode component / token file
grep -rEn '[0-9]{1,2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?' ui/src --include='*.tsx' | grep -v 'Timecode' | grep -v 'test'
# data surfaces must set tabular-nums
grep -rEn 'tabular-nums' ui/src/tokens.css   # must return the data token
```

## Rule 6 — Honest data: no fake metrics, no invented progress; UNKNOWN over inferred numbers

**Statement.** When the system cannot attribute an outcome to a specific operation, display UNKNOWN. Never render a number inferred from counts (playbook Law 8, PLAYBOOK.md:113). Real limits in the UI; no fake urgency; no fake completeness (playbook Law 12, PLAYBOOK.md:161).

**Why.** Inferred numbers propagate and their provenance is gone — "An explicit UNKNOWN can clear on the next read; a wrong number never does" (PLAYBOOK.md:115). Verified patterns: ahyeon-archive renders a "Could not verify — kept open, on purpose" section and a footer stating "Every number on this page is fixed at that date — a published snapshot, not a live feed" (`ahyeon-archive/pages/full-story/index.html:196-201, 243` — audit-web §12a); bilal-s-grand-showcase hard-bans hardcoded counts — "Every number rendered is real… never hardcode counts" (`bilal-s-grand-showcase/AGENTS.md` §2 — audit-web §3); linuxify's UI review states "screenshot evidence: none produced — none may be fabricated" (`linuxify/docs/UI_REVIEW.md` — audit-android §6).

**Implement in ClipForge.** Render progress is only shown when ffmpeg/whisper reports a measurable fraction; indeterminate work shows an indeterminate state, never a fake percentage. A score the moment-picker did not produce renders as UNKNOWN, not as a guess. Export size/duration estimates are labeled as estimates with their provenance. Real limits stated in copy (e.g. local-only processing, proxy quality) rather than hidden.

**Verify.**
```bash
# no hardcoded progress, random values, or mock data outside tests
grep -rEnE 'progress[^,;]{0,20}(=[[:space:]]*0?\.[0-9]+|=[[:space:]]*[0-9]{1,3}[[:space:]]*%)' ui/src --include='*.tsx' | grep -v test
grep -rEn 'Math\.random|lorem|Lorem|placeholder-data|mock-data|fake-' ui/src --include='*.tsx' --include='*.ts' | grep -v test
# UNKNOWN is an allowed literal — enumerate where honesty labels are used
grep -rn 'UNKNOWN' ui/src --include='*.tsx' | wc -l
```

## Rule 7 — Targets are at least 44px on every pointer-precise surface

**Statement.** Interactive targets ≥ 24×24 CSS px minimum (WCAG 2.2 SC 2.5.8); ClipForge holds **all** controls to 44px — desktop and touch — because timeline handles, waveform scrubbers and caption chips are precision work (playbook Law 10, PLAYBOOK.md:137).

**Why.** These checks cost nothing at design time and are expensive to retrofit; agents skip them because they are invisible in screenshots (PLAYBOOK.md:139). Verified examples: linuxify uses 44dp icon targets and `minHeight 44dp` input (`jarvis-agent/.../activity_main.xml:33, 80, 114, 138, 456` — audit-android §1); signal-noise sets buttons `min-height: 44px` (`signal-noise/src/app/globals.css:183-186` — audit-web §4); nexpdf writes ≥48dp into its acceptance checklist (`nexpdf/docs/UI_ACCEPTANCE_CHECKLIST.md` — audit-android §5).

**Implement in ClipForge.** Token `--target-min: 44px` (see `DESIGN_SYSTEM.md`) with derived hit-area rules: timeline clip edges get invisible 44px drag affordances even when the visible handle is thinner; caption-style chips and queue row buttons are ≥44px tall. Visible handles may be small; the hit target may not.

**Verify.**
```bash
# any height/width under 44px is a suspect — must be a non-interactive glyph size or removed
grep -rEnE '(min-height|min-width|height|width):[[:space:]]*([0-9]|[1-3][0-9]|4[0-3])px' ui/src --include='*.css' --include='*.tsx' | grep -v tokens.css | grep -v test
```

## Rule 8 — Keyboard operability is a path, not an afterthought

**Statement.** A keyboard path exists through every flow — review, edit, caption, export — with visible focus rings everywhere; contrast ≥ 4.5:1 body / 3:1 large text (playbook Law 10, PLAYBOOK.md:137).

**Why.** Keyboard support is the cheapest a11y win and the first thing custom chrome breaks: momostack set input `outline: none` to make room for a custom cursor, so keyboard users lost affordances (`momostack/assets/css/main.css:1289` — audit-web §5, Avoid #5). Verified discipline: bilal-s-grand-showcase's `:focus-visible` ring is "Never removed, only restyled" (`bilal-s-grand-showcase/src/index.css:216-221` — audit-web §3); ahyeon-s-vision makes gallery tiles `role="button" tabIndex={0}` with Enter handling (`ahyeon-s-vision/src/pages/Index.tsx:390-404` — audit-web §2).

**Implement in ClipForge.** Global `:focus-visible` ring from tokens, never removed. The review flow is keyboard-first (`INTERACTION_PATTERNS.md`): tab order follows the workflow, dialogs trap focus and return it (the signal-noise `StationOverlay.tsx` pattern), and every button is a real focusable control. The transcript editor supports full keyboard editing with undo/redo.

**Verify.**
```bash
# focus must never be dropped silently
grep -rEn 'outline:\s*(none|0)' ui/src --include='*.css' --include='*.tsx' | grep -v 'focus-visible'
grep -rEn 'tabIndex=\{"?[1-9]' ui/src --include='*.tsx'   # positive tab indices are forbidden
```
(Manual companion: complete the review-to-export flow with no mouse; on both themes.)

## Rule 9 — No emoji as icons; a real icon set only

**Statement.** Iconography comes from a real icon set (lucide on web, per playbook Law 11, PLAYBOOK.md:147). Emoji in chrome, logos, or status indicators is forbidden — an accessibility and rendering-consistency hazard.

**Why.** Emoji render differently on every platform and cannot be consistently labeled or recolored; forbid-by-name beats adjective guidance "because names are checkable" (PLAYBOOK.md:149). Verified failure: ahyeon-s-vision uses emoji as icons throughout (`pc-icon`, tour flags, milestone chips — `ahyeon-s-vision/src/pages/Index.tsx` — audit-web §2, Avoid #2).

**Implement in ClipForge.** One icon set (lucide) for transport controls, panel headers, status accents, and settings rows. Emoji remain legal only inside *user content* (e.g. a transcript's original text), never in chrome the app renders.

**Verify.**
```bash
# emoji/symbol codepoints in UI source must return nothing outside test fixtures (requires GNU grep with PCRE, -P)
grep -rPn '[\x{1F000}-\x{1FAFF}\x{2190}-\x{27BF}\x{FE0F}\x{2B00}-\x{2BFF}]' ui/src --include='*.tsx' --include='*.ts' --include='*.css' | grep -v test
```

## Rule 10 — Real previews only: frames come from the actual media

**Statement.** Every visual that stands for media — candidate cards, timeline thumbnails, caption previews, export estimates — is computed from the real file. No stock placeholders, no fabricated poster frames, no invented durations.

**Why.** A preview that lies teaches users to distrust the one surface whose whole job is truth. This is playbook Law 8 (attribution) applied to media: a frame either came from the source file or it is UNKNOWN. Verified discipline: ahyeon-s-vision's `HeroVideo` renders real prebuffered layers and downgrades to a static poster under reduced-motion / Save-Data / 2G (`ahyeon-s-vision/src/components/HeroVideo.tsx:22-36` — audit-web §2) — real media, adaptively loaded; signal-noise attaches a `source` to every metric and renders it (`signal-noise/src/lib/content.ts:1-4,18` — audit-web §4).

**Implement in ClipForge.** Candidate cards extract their preview frame from the actual video (ffmpeg thumbnail at the moment's timestamp) before the card renders; until extraction completes the card shows the skeleton state, not a gray fake. Duration, resolution, and fps come from the probed file; before probe completes they render as UNKNOWN (`--:--` timecode placeholder, see `COMPONENT_CATALOG.md`). Caption previews render the real transcript text, never "Sample caption text".

**Verify.**
```bash
# placeholder/stub imagery and invented media values must return nothing
grep -rEn 'placeholder\.(png|jpg|webp)|dummy-frame|sample-frame|PosterStub' ui/src --include='*.tsx' --include='*.ts' | grep -v test
grep -rEn 'duration=\{"?[0-9]+:[0-9]{2}' ui/src --include='*.tsx' | grep -v test   # no hardcoded durations in components
```

## Rule 11 — UI is not done because it compiles

**Statement.** A passing build is not done; a working, *visually reviewed* journey is done. Typecheck + lint + tests + build green, then exercise the real flow; screenshot before and after every UI change (playbook agent rules 1 and 4, PLAYBOOK.md:200-203, `AGENTS.md` rules 1 and 12).

**Why.** Bugs that matter in editors are visual: misaligned timecode columns, clipped labels at 390px, focus rings invisible on dark. None of these fail a build. Verified process: nexpdf gates every UI push with `docs/UI_ACCEPTANCE_CHECKLIST.md` and admits honestly "no device here… manual on-device testing is on the user" (audit-android §5); linuxify's `docs/UI_REVIEW.md` records verification method per row and refuses to fabricate screenshot evidence (audit-android §6); bilal-s-grand-showcase's push checklist includes "Browser pass: desktop 1440 + mobile 390, light **and** dark, zero console errors" (audit-web §3).

**Implement in ClipForge.** The merge gate is `UI_QA_CHECKLIST.md` (this directory): automated greps, a manual review list, and screenshot evidence at multiple viewports in both themes. A UI change without a before/after pair did not happen. A UI issue closes only with visual evidence of the fix.

**Verify.**
```bash
# enumerate changed UI files; every one needs before/after evidence in the PR description
git diff --name-only "$(git merge-base HEAD main)"..HEAD -- ui/src | sort
# evidence directory must exist and be non-empty for the change set
ls ui/review/ 2>/dev/null
```

## Rule 12 — Motion pays rent, and reduced motion is honored

**Statement.** A transition earns its place only if it shows *what changed*; decoration is deleted. Every animation respects `prefers-reduced-motion` (playbook candidate 16, PLAYBOOK.md:246-255).

**Why.** Decorative motion taxes attention on every revisit; meaning-carrying motion is information (PLAYBOOK.md:250). Verified contracts: bilal-s-grand-showcase's `motion.tsx` header states "Reduced motion is a hard off-switch… fine-pointer-only effects never touch touch devices… every scroll-triggered primitive fires exactly once" (`bilal-s-grand-showcase/src/components/site/motion.tsx` — audit-web §3); signal-noise documents that Lenis does not honor reduced motion upstream and gates it accordingly (`signal-noise/research/contradictions.md` C-01 — audit-web §4).

**Implement in ClipForge.** Motion tokens (120/220/320ms, `DESIGN_SYSTEM.md`) applied only where change is communicated: clip accepted → card leaves the review rail showing destination; render started → row enters running state; transcript edit applied → the changed line flashes once. Transport controls, scrubbing, and preview playback are functional behavior, never animation. A global reduced-motion clamp removes entry/exit transitions entirely; media playback is unaffected.

**Verify.**
```bash
# every animation must carry a comment naming what changed; transitions must reference motion tokens
grep -rEn 'animation|transition' ui/src --include='*.css' --include='*.tsx' | grep -v 'var(--motion' | grep -v 'reduced-motion'
grep -rn 'prefers-reduced-motion' ui/src/tokens.css ui/src/styles.css   # clamp must exist
```

## Rule 13 — Honest copy and real limits

**Statement.** Real limits stated in the UI ("runs locally; nothing is uploaded"), features that do not exist are absent, not stubbed; no fake urgency, no confirm-shaming (playbook Law 12, PLAYBOOK.md:161).

**Why.** Trust is a design feature with an ROI (PLAYBOOK.md:162). Verified practice: momostack publishes its SHA-256 and "Telemetry-Zero" positioning (`momostack/README.md` — audit-web §5); ahyeon-archive keeps conflicts "shown, not smoothed over" (`ahyeon-archive/pages/full-story/index.html:243` — audit-web §12a).

**Implement in ClipForge.** Settings state explicitly what stays local (transcription, LLM picking, translation, rendering) and what leaves the machine (the source video download, if any) — see `SettingsProviderPanel` in `COMPONENT_CATALOG.md`. Missing capabilities (e.g. no GPU acceleration yet) are stated, not hidden.

**Verify.**
```bash
# no marketing-urgency or confirm-shaming copy patterns in UI strings
grep -rEn 'limited time|only today|are you *sure\?|we *hate to ask|don'?t *miss' ui/src --include='*.tsx' --include='*.ts' -i
```

---

## Traceability

| Rule | Source law / evidence |
|---|---|
| 1 Token-only | PLAYBOOK.md Law 1 (:14-27); audit-android §1, §4; audit-web §2 |
| 2 Trust triad | PLAYBOOK.md Laws 3-4 (:47-70); audit-android §5, §6; audit-web §12b, §3 |
| 3 One loud thing | PLAYBOOK.md Law 9 (:127-133); audit-web §8 (Avoid #9) |
| 4 Color + label | PLAYBOOK.md Law 2 (:31-39); audit-android §6 (`Color.kt:32-42`, `Common.kt:24-63`) |
| 5 Tabular numerals | PLAYBOOK.md Law 6 (:90-101); audit-android §6 (`Type.kt`); audit-web §3 (`.data-mono`) |
| 6 Honest data | PLAYBOOK.md Laws 8, 12 (:113-119, :161-165); audit-web §12a, §3; audit-android §6 |
| 7 44px targets | PLAYBOOK.md Law 10 (:137-143); audit-android §1, §5; audit-web §4 |
| 8 Keyboard | PLAYBOOK.md Law 10; audit-web §3 (`:focus-visible`), §5 (outline:none failure), §2 |
| 9 No emoji icons | PLAYBOOK.md Law 11 (:147-153); audit-web §2 |
| 10 Real previews | PLAYBOOK.md Laws 5, 8; audit-web §2 (`HeroVideo.tsx`), §4 (`content.ts`) |
| 11 Not-done-until-reviewed | PLAYBOOK.md §VII (:200-205), `AGENTS.md` rules 1/12; audit-android §5 (`UI_ACCEPTANCE_CHECKLIST.md`), §6 (`UI_REVIEW.md`); audit-web §3 |
| 12 Motion pays rent | PLAYBOOK.md candidate 16 (:246-255); audit-web §3 (`motion.tsx`), §4 (C-01) |
| 13 Honest copy | PLAYBOOK.md Law 12; audit-web §5, §12a |
