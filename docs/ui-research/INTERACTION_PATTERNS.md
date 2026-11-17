# ClipForge Interaction Patterns — v0.1

Status: **PROPOSAL** distilled from the merged audit (`USER_PROJECT_UI_AUDIT.md`) plus media-tool needs. Where a pattern is directly verified in an audited repo, the citation is given; where ClipForge extends a verified pattern into new territory (notably the letter-key review bindings), it is marked **[proposal]** — a decision to make, not an observed fact. Rules cited are from `UI_ENGINEERING_PLAYBOOK.md`.

---

## 1. Keyboard-first review flow

**Verified grounding.** The playbook requires "a keyboard path through every flow" (Law 10, PLAYBOOK.md:137). The audited corpus shows the mechanics: ahyeon-s-vision makes gallery tiles keyboard-operable with `role="button" tabIndex={0}` + Enter (`src/pages/Index.tsx:390-404`), drives a lightbox with Escape / ArrowLeft / ArrowRight and a "1 / N" counter (`Index.tsx:107-144`), and ships a MediaRail with arrow buttons, `role="region"` semantics and a unit test asserting all 35 items stay reachable (`src/components/MediaRail.tsx`, `src/test/media-rail.test.tsx`) — audit-web §2. signal-noise's overlay cycle traps Tab and returns focus on Escape (`src/components/StationOverlay.tsx:77-91`) — audit-web §4.

**ClipForge pattern [proposal].** The review workspace is operable end-to-end without a mouse. Bindings:

| Key | Action |
|---|---|
| `J` | accept current candidate (add to clip plan) |
| `K` | reject current candidate |
| `E` | open trim/edit for current candidate |
| `←` / `→` | previous / next candidate (with a "3 / 12" counter, the ahyeon-s-vision pattern) |
| `Space` | play/pause preview of the current candidate |
| `,` / `.` | step preview back/forward one frame **[proposal]** |
| `Enter` | trigger the focused control (standard) |
| `Escape` | close dialog / cancel trim (standard) |
| `?` | show the shortcut overlay |

`J/K` deliberately mirrors the vim-inherited review idiom common in review tools; it is **not** present in the audited repos — it is an extension of their verified keyboard-first mechanics to ClipForge's decision loop, and the first visual review must confirm it does not collide with text-entry focus (bindings are suppressed while the transcript editor holds focus). A visible shortcut legend ships on the review screen (answer-first: the keys are the interface, not easter eggs). The counter and rail semantics follow the MediaRail pattern: `role="listbox"`/`option`, `aria-selected`, counter in the accessible name.

**Why.** Candidate review is a high-volume decision loop; pointer-only review makes the queue a treadmill. Keyboard-first is also the cheapest accessibility win (Rule 8).

## 2. Undo/redo for text edits

**Verified grounding.** None in the audited repos — the closest verified analog is ahyeon-archive's optimistic save with rollback (`pages/verify-the-unverified/client/src/App.tsx:38-82, 200-224`), which is per-write rollback rather than an edit-history stack. **[proposal]** below is a derived requirement for the TranscriptEditor, stated as one.

**ClipForge pattern [proposal].** The transcript editor (original and translated panes) keeps a per-segment undo/redo stack: every accepted edit is one undo step; word-timing-preserving transforms (re-timing) are separate steps from text edits. `Ctrl/Cmd+Z` / `Ctrl/Cmd+Shift+Z` are bound editor-wide; toolbar buttons exist and are ≥44px. Provenance badges track the *current* content: undoing an edit restores the row's `AI-suggested` badge; a redo re-marks `Edited`. Saving is optimistic (§5) — undo does not fight the network layer because rollback already restored the last persisted state on failure. Redo histories are cleared only when the underlying data changes from outside the editor (re-transcription), and the editor announces that reset rather than silently dropping the stack.

**Why.** Transcript editing is fear-heavy work — users who cannot undo will not edit. The rollback pattern (§5) covers persistence failures; the undo stack covers *user regret*, and both are required for the editor to be trusted.

## 3. Dialog and focus-trap pattern

**Verified grounding.** signal-noise `StationOverlay.tsx` is the copyable reference (audit-web §4): `role="dialog" aria-modal="true" aria-label`, a real focus trap cycling focusables on Tab (77-91), Escape returning focus to the trigger, scroll lock cooperating with the page's smooth-scroll engine, and hash routing so dialogs are deep-linkable (`#station/{id}`, 29-49). Corroborating patterns: bilal-s-grand-showcase's full-screen overlay menu with `role="dialog"`, `aria-modal`, focus moved in, Escape closes, focus returns (`DESIGN.md` §5/§8 — audit-web §3); ahyeon-s-vision's TalentThread modal handles Escape/arrows + scroll lock (`TalentThread.tsx:178-191`) and its Feedback dialog is a native `<dialog>` with `role="status" aria-live="polite"` (`Feedback.tsx`) — audit-web §2.

**ClipForge pattern.** One dialog component; every modal (trim editor, shortcut legend, destructive confirms, export confirm) uses it. Requirements: `role="dialog"` + `aria-modal="true"` + accessible name; focus moves to the first interactive element on open and returns to the trigger on close; Tab/Shift+Tab cycle inside; Escape closes (except while a render is being configured — then Escape asks, it does not discard); scroll locks the workspace behind; the scrim uses `--scrim`. Destructive confirms (cancel a render, discard edits) state the consequence plainly and never confirm-shame (Rule 13). Deep-linkable dialogs (hash routing) are **not adopted** for v0.1 — workspace state is session-local; the mechanism is noted for when review states become shareable.

## 4. Navigation structure — the project workspace

**Verified grounding.** linuxify drives a compact bottom bar and an expanded rail from **one** `Destination(route, label, icon)` list with `calculateWindowSizeClass` (`MainActivity.kt:85-170`), and documents the tab-state bug it fixed: `popUpTo(home){saveState=true} + restoreState=true` restored a whole saved stack; the fix pops without save so a tab tap always lands on the tab's root while ViewModels keep process-scoped state (`MainActivity.kt:172-198`) — audit-android §6. bilal-s-grand-showcase contributes the skip link as first focusable element, e2e-tested (`src/index.css:519-537`, `e2e/smoke.spec.ts` — audit-web §3). nexpdf shows string-route switching with argument-bearing routes (`"viewer:uri"`, `ui/AppRoot.kt` — audit-android §5) as a deliberately simple pattern that would not scale past a 5-screen app.

**ClipForge pattern [proposal].** The project workspace has six sections, driven from one destination list (the linuxify mechanism), rendered as a left rail on wide viewports and a top/tab strip on narrow ones:

1. **Review** — candidate rail + preview (the default landing section)
2. **Timeline** — strip + accepted plan
3. **Transcript** — editor (original/translated)
4. **Captions** — style browser
5. **Render** — queue + logs
6. **Export** — manifest + launch

Plus persistent access to **Settings** (panel, not a destination) and the project switcher. Section selection follows the linuxify lesson: activating a section shows that section's root; per-section state (scroll position, filters, expanded rows) survives in the section's own state holder, not in navigation history. A skip link ("Skip to review rail") is the first focusable element. Each section has one loud thing (Rule 3); the destination list never carries badges that fake urgency (Rule 13) — a render-failure indicator on the Render destination is allowed only while actionable (playbook candidate 17: the top slot goes to the worst thing you can still do something about).

## 5. Optimistic save with rollback

**Verified grounding.** ahyeon-archive's decision app (`pages/verify-the-unverified/client/src/App.tsx`, 543 lines — audit-web §12b): `onMutate` snapshots the cache, `onError` restores it and sets `failedOptionId`, rendering a **persistent banner that names the lost choice and offers a one-tap "Retry save"** (38-82, 200-224). Radio semantics ride along (`role="radiogroup"` / `role="radio"` / `aria-checked`, 139-153). The playbook's trust triad and "surfaces must agree" laws (Laws 3-4) are the standard this pattern satisfies.

**ClipForge pattern.** Applies to every write that persists project state: transcript edits, style-preset changes, settings changes (SettingsProviderPanel), review decisions. Sequence: (1) apply to the UI immediately; (2) write to the project store; (3) on failure, restore the prior state, mark the affected control, and render a persistent banner — "Save failed: your edit to segment 12 was not written (disk error). [Retry save]" — naming the lost change (the ahyeon-archive wording discipline). The banner persists until resolved; toasts are for non-blocking confirmations only (playbook Law 3: blocking errors get a banner, not a toast). While a write is in flight, the affected control shows its pending state but stays legible (no disabling the whole panel).

## 6. Skeleton loading

**Verified grounding.** nexpdf `ui/common/Skeleton.kt` (audit-android §5): a reusable pulse skeleton — `rememberInfiniteTransition` alpha 0.5→1, 700ms `RepeatMode.Reverse` tween, background `colorScheme.surfaceContainerHighest.copy(alpha = pulse)`, parameterized corner radius; theme-aware, zero hex. The playbook mandates "skeletons matching final layout. Spinners only for sub-second waits" (Law 3, PLAYBOOK.md:54) and the critique-round budget allows "skeleton pulse only" as ambient motion (`CONTRIBUTING.md`).

**ClipForge pattern.** One `Skeleton` primitive implements the nexpdf pulse (alpha 0.5→1, 700ms reverse, on `--surface-3`, radius parameterized). Every async surface composes skeletons that **match the final layout**: candidate rail → card-shaped skeletons with frame block + timecode lines + bar rows; transcript → line-rhythm rows; queue → row skeletons. Spinners are reserved for sub-second waits (nothing in ClipForge's pipeline qualifies, so effectively none). Skeleton counts reflect known real cardinality when known (e.g. transcript rows after parse) and a bounded generic count before that — skeletons never fabricate content (Rule 6). Skeletons respect reduced motion (pulse removed; static tint remains — the information "loading" must survive without animation, playbook Rule 12).

## 7. Error surfaces with recovery actions

**Verified grounding.** The playbook defines the shape: errors state (a) what happened, (b) why, (c) the next action; dead-end errors are bugs; blocking errors get a banner, not a toast (Law 3, PLAYBOOK.md:47-58; `AGENTS.md` rule 2). Verified exemplars: bilal-s-grand-showcase `ErrorBoundary.tsx` — human message, never a stack trace, two recovery links + Reload (audit-web §3); its themed 404 "SIGNAL LOST" with three escape-hatch buttons (`NotFoundPage.tsx:23-30`); ahyeon-s-vision's Feedback dialog with an HTTP 429-specific message and retry wording (`Feedback.tsx` — audit-web §2); ahyeon-archive's `role="alert"` + "Try again" refetch (`App.tsx:454-468`); linuxify's shared `ErrorState` (title/body + optional retry) routed everywhere (`Common.kt` — audit-android §6).

**ClipForge pattern.** Shared `ErrorState` component (the linuxify mechanism): banner, not toast; icon + text; what/why/next-action; a primary recovery button wired to the actual fix (Retry, Re-import, Open logs, Choose another location) and at most one escape-hatch link. Errors name the real cause from the pipeline (e.g. which ffmpeg exit, which download failure) — a generic "something went wrong" is a dead end and fails the checklist. Transient failures on non-blocking operations may toast, but every blocking failure renders inline. Verification UI (e.g. "model installed?") distinguishes authorized / missing / wrong-record / lookup-error — or says "unverified — check incomplete" (playbook Law 5); concretely: model checks report "installed", "not installed", or "could not reach Ollama" — never a checkmark that only means "answered something".

## 8. Motion rules

**Verified grounding.** Playbook candidate 16: motion earns its place only by showing *what changed*; reduced-motion is a hard baseline (PLAYBOOK.md:246-255). bilal-s-grand-showcase's `motion.tsx` header contracts: "Reduced motion is a hard off-switch… fine-pointer-only effects never touch touch devices… every scroll-triggered primitive fires exactly once per mount and disconnects its observer" (audit-web §3); ambient motion whitelisted to "marquee tickers, live-dot pulse, caret blink, clock ticks" (`DESIGN.md` §7); global reduced-motion clamp (`index.css:805-820`). signal-noise documents the upstream gap — Lenis "does NOT respect `prefers-reduced-motion`" — and gates it (`research/contradictions.md` C-01). ahyeon-s-vision's `HeroVideo` downgrades real media to a static poster under reduced-motion / Save-Data / 2G (`HeroVideo.tsx:22-36`). nexpdf's written rule: nothing decorative blocks input; ≤450ms (`docs/DESIGN_TOKENS.md`).

**ClipForge pattern.**
- **Animates:** candidate accept/reject (card exits the rail showing destination — the queue reflows); panel enter/exit (220ms fade + 0.96→1 scale, nexpdf's screen-enter); dialog/sheet entry (320ms); segment drag (segment shows origin→destination); skeleton pulse; the render-queue running dot (the one sanctioned ambient motion); caption-style preview refresh (crossfade between composites).
- **Never animates:** preview playback itself; scrubbing (playhead tracks the pointer exactly); transcript text while typing; timecode readouts (they tick with media, they do not tween); focus ring appearance; error banners (they appear).
- **Reduced motion:** the global clamp removes entry/exit transitions and the skeleton pulse and the running dot's animation (the dot becomes static); playback, scrubbing, and all functional behavior are unaffected — nothing essential is lost (playbook Rule 12 verify). All durations from `DESIGN_SYSTEM.md` §8 (120/220/320ms, `--ease-standard`); nothing decorative blocks input.

## 9. Touch targets and mouse precision

**Verified grounding.** Playbook Law 10: ≥24×24 CSS px minimum, 44px held on mobile web; visible focus rings; contrast floors (PLAYBOOK.md:137). Verified practice: signal-noise buttons `min-height: 44px` (`globals.css:183-186`); jarvis-agent's 44dp icon targets and `minHeight 44dp` input (`activity_main.xml:33, 80, 114, 138, 456`); nexpdf's ≥48dp acceptance line (`docs/UI_ACCEPTANCE_CHECKLIST.md`); linuxify nav icons with `contentDescription = label`. The failure case: momostack's `outline: none` input styling that stripped keyboard affordances (`main.css:1289`).

**ClipForge pattern [proposal].** All controls 44px minimum — desktop included — because an editor's pointers are doing precision work, and the same floor removes a whole class of regression. Precision-specific rules:
- **Trim handles:** visible handle may be 2px; its hit area is 44px wide (invisible extension), so a mouse can grab a frame boundary and a finger can too.
- **Scrubbing:** the timeline playhead and any scrub target support pointer-capture while dragging (no dead zones); arrow keys step frames for exactness (§1); shift+arrow steps 1s **[proposal]**.
- **Magnify-on-drag:** while dragging a trim boundary, a zoomed timecode readout renders above the handle **[proposal]** — precision feedback in the mono voice; the timeline's ruler spacing must be computable from real duration (Rule 10).
- **Touch:** the review rail's swipe actions mirror the keyboard bindings (swipe = accept/reject) with the same 44px floors; fine-pointer-only effects (hover reveals) never carry information available exclusively to mouse users (the showcase's fine-pointer contract, audit-web §3).
- **Cursor:** no custom cursor replaces native affordances — the momostack lesson (audit-web §5, Avoid #5). The default cursor plus token-styled hover states is the whole story.
