# ClipForge UI QA Checklist — pre-merge gate

Status: **binding** for any change under `ui/src/`. Combines the owner's playbook verify style (every item traces to a rule; grep-able checks — `/home/z/my-project/staging/repos/agent-ui-playbook/CHECKLIST.md`, re-verified) with nexpdf's per-push checklist process (`nexpdf/docs/UI_ACCEPTANCE_CHECKLIST.md`, audit-android §5) and the showcase's push checklist ("Browser pass: desktop 1440 + mobile 390, light **and** dark, zero console errors" — audit-web §3).

**Process (nexpdf's discipline):** run this gate on every UI push, before claiming done — alongside typecheck + lint + tests + build green, then exercising the real flow (playbook agent rule 1, PLAYBOOK.md:200). Record the run: date, change set, checked-by, and the honest limits of the run (the linuxify `docs/UI_REVIEW.md` method: label each row's verification method; "screenshot evidence: none produced — none may be fabricated", audit-android §6).

---

## 1. Automated checks (copy-paste; each must pass)

Run from the repo root. Commands target the planned `ui/src/` tree with token file `ui/src/tokens.css` (`DESIGN_SYSTEM.md` §10). A command "passing" means: the listed result holds.

### 1.1 No inline hex or rgb() outside the token file (Rule 1)
```bash
grep -rEn '#[0-9a-fA-F]{3,8}|rgba?\([0-9]' ui/src \
  --include='*.css' --include='*.tsx' --include='*.ts' --include='*.html' \
  | grep -v 'ui/src/tokens.css'
```
**Pass = no output.** (Playbook Law 1 Verify pattern. The failure it prevents: jarvis-agent's decorative `colors.xml` and Liteshare's 37 hardcoded seeds — audit-android §1, §4.)

### 1.2 No silently dropped focus (Rule 8)
```bash
grep -rEn 'outline:\s*(none|0)' ui/src --include='*.css' --include='*.tsx' | grep -v 'focus-visible'
grep -rEn 'tabIndex=\{"?[1-9]' ui/src --include='*.tsx'
```
**Pass = no output.** (The failure it prevents: momostack's `outline: none` that stripped keyboard affordances — audit-web §5.)

### 1.3 No emoji in UI source (Rule 9)
```bash
# emoji/symbol codepoints in UI source; requires GNU grep with PCRE (-P)
grep -rPn '[\x{1F000}-\x{1FAFF}\x{2190}-\x{27BF}\x{FE0F}\x{2B00}-\x{2BFF}]' ui/src \
  --include='*.tsx' --include='*.ts' --include='*.css' | grep -v test
```
**Pass = no output.** Emoji are legal only inside *user content* data (e.g. a transcript's original text), never in chrome. (The failure it prevents: ahyeon-s-vision's emoji-as-icons — audit-web §2.)

### 1.4 No TODO / placeholder / fake-content text (Rules 6, 10)
```bash
grep -rEn 'TODO|FIXME|XXX|HACK|lorem|Lorem|placeholder|sample text|Sample caption|coming soon' ui/src \
  --include='*.tsx' --include='*.ts' --include='*.css' --include='*.html' | grep -v test
grep -rEnE 'duration=\{"?[0-9]+:[0-9]{2}|progress[^,;]{0,20}(=[[:space:]]*0?\.[0-9]+|=[[:space:]]*[0-9]{1,3}[[:space:]]*%)' ui/src --include='*.tsx' | grep -v test
grep -rEn 'Math\.random|mock-data|fake-|dummy-frame|sample-frame|PosterStub|placeholder\.(png|jpg|webp)' ui/src | grep -v test
```
**Pass = no output.** The `UNKNOWN` literal and `--:--:--` timecode placeholder are the *allowed* honesty conventions (`COMPONENT_CATALOG.md` §0) — grep may find those; it must not find invented values. (The failure it prevents: fake completeness, playbook Laws 4/8/12.)

### 1.5 Timecodes live in one component, tabular (Rule 5)
```bash
grep -rEn '[0-9]{1,2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?' ui/src --include='*.tsx' | grep -v 'Timecode' | grep -v test
grep -rn 'tabular-nums' ui/src/tokens.css
```
**Pass = first command no output (outside the Timecode component and tests); second finds the data token.** (linuxify's mono-for-runtime-values rule and the showcase's `.data-mono` — audit-android §6, audit-web §3.)

### 1.6 Motion references tokens and honors reduced motion (Rule 12)
```bash
grep -rEn 'animation|transition' ui/src --include='*.css' --include='*.tsx' | grep -v 'var(--motion' | grep -v 'reduced-motion'
grep -rn 'prefers-reduced-motion' ui/src --include='*.css'
```
**Pass = first command no output (every transition references a motion token or a reduced-motion guard); second finds the clamp.** (Showcase `motion.tsx` contracts; nexpdf ≤450ms rule — audit-web §3, audit-android §5.)

### 1.7 Async surfaces declare their three states (Rule 2)
```bash
files=$(grep -rl 'await ' ui/src --include='*.tsx')
grep -L 'Loading\|Skeleton' $files   # files with async work and no loading state
grep -L 'Empty\|empty'      $files   # ... no empty state
grep -L 'Error\|error'      $files   # ... no error state
```
**Pass = no files listed** (every file containing async work mentions loading, empty, and error handling — a coarse gate; §2.4 exercises them for real). (linuxify's shared-state kit enforcement — audit-android §6.)

### 1.8 Builds and the flow are green (Rule 11)
```bash
# project-standard checks; exact commands to be fixed when the UI toolchain lands
# expected: typecheck + lint + tests + build all exit 0
```
A green build alone is **not** a pass — §2 and §3 are the gate. (Playbook agent rule 1: "a passing build is not done; a working journey is", PLAYBOOK.md:200.)

## 2. Manual review list (each item traces to a rule)

Exercise the **real flow** — import a real source, review real candidates, edit the real transcript, style real captions, render a real clip — not a fixture. Check both themes and both pointer modes.

**Hierarchy & structure**
- [ ] Squint (or blur) each workspace section: exactly one loud element (Rule 3; playbook "Does exactly one thing stand out?", PLAYBOOK.md:133)
- [ ] The primary action of each section is obvious without reading a tooltip (nexpdf: "single primary action", audit-android §5)
- [ ] Spacing uses the 4px scale steps only; no arbitrary px in diffs (DESIGN_SYSTEM §6; grep in §1.1's spirit)
- [ ] No cards inside cards, no glassmorphism, no gradients — the forbid-list (Rule 9 / playbook Law 11)

**Wiring & honesty**
- [ ] Every visible control is wired to real behavior — click each one; no dead buttons, no controls that log but do nothing (nexpdf's real-flow gate)
- [ ] Every number on screen traces to an attributable operation, or reads UNKNOWN (Rule 6; playbook Law 8 Verify: "what operation produced this?")
- [ ] Zero counts state their cause: not yet / filtered out / failed to load (Rule 2; playbook Law 4)
- [ ] Marketing-flavored copy check: no fake urgency, no confirm-shaming; real limits stated (Rule 13; playbook Law 12 Verify)

**States exercised (not just designed)**
- [ ] Loading state observed on a real slow operation (skeleton matches final layout; no spinner > sub-second) (Rule 2; nexpdf Skeleton pattern)
- [ ] Empty state observed per async surface, each teaching the next action (Rule 2)
- [ ] Error state observed with what/why/next-action and a wired recovery action; blocking errors use banners (Rule 2; audit-web §3 ErrorBoundary pattern)
- [ ] Reduced motion on: nothing essential lost; skeleton pulse and running dot go static (Rule 12)

**Keyboard-only pass (Rule 8)**
- [ ] Complete import → review (`J`/`K`/`E`) → transcript edit → captions → render → export with **no mouse**
- [ ] Focus rings visible on every stop, **both themes**; skip link is the first focusable element
- [ ] Dialogs trap focus and return it on Escape (signal-noise `StationOverlay.tsx` pattern)
- [ ] Tab order follows the workflow; no focus traps outside dialogs

**Window-size pass (showcase push checklist, audit-web §3)**
- [ ] Desktop 1440 and mobile-class 390 (or the narrow editor layout): no clipped labels, no overflow, panels collapse sanely
- [ ] Light **and** dark: zero unstyled seams in borders, scrims, hover states (playbook Law 1: dark mode is a second column, never overrides)
- [ ] Zero console errors on both sizes (showcase push checklist)
- [ ] Grayscale pass on every status surface: pass/fail/running distinguishable without color (Rule 4; playbook Law 2 Verify)

**Real-content pass (Rule 10)**
- [ ] Preview frames are from the actual media; captions preview shows real transcript text; no placeholder imagery anywhere
- [ ] Timecodes/durations from the probed file; `--:--:--` only before probe completes
- [ ] Icon set consistent (lucide family only); no stock fallback icons (the jarvis-agent identity failure, audit-android §1)

## 3. Screenshot evidence requirements

Playbook agent rule 4: "Screenshot before and after every UI change. A UI change without a before/after didn't happen" (PLAYBOOK.md:203; `AGENTS.md` rule 12). For ClipForge:

1. **Before/after pair for every changed surface**, attached to the PR description, named by workspace section and state (e.g. `review-after-accept-dark.png`).
2. **Multiple viewport sizes**: desktop 1440 and the narrow editor width 390, per the showcase push checklist (audit-web §3). A change touching a responsive surface needs both.
3. **Both themes** (dark-first default + light column) whenever the change touches color, surface, or chrome.
4. **State evidence, not just happy path**: the loading/empty/error screenshot of any state this change introduced or touched.
5. **Grayscale variant** for any status/verdict surface touched (playbook Law 2 Verify).
6. Evidence lives in `ui/review/` alongside the change; the linuxify rule applies verbatim — "screenshot evidence: none produced — none may be fabricated" (audit-android §6): an empty evidence folder is reported as empty, never backfilled with actors or mockups presented as the real build.

## 4. The closure rule

**A UI issue closes only with visual evidence.** A fix is "done" when: (a) the automated checks in §1 pass, (b) the relevant manual items in §2 are re-checked on the real flow, and (c) a new screenshot pair shows the fixed surface — the same before/after standard as any change (playbook agent rule 4). "It compiles", "it should look right now", and "the grep is clean" do not close UI issues. Conversely, reporting an issue requires evidence too — a reported visual defect without a screenshot gets investigated, not auto-adopted (playbook process rule: single-reporter caution, PLAYBOOK.md:204). The sign-off record follows linuxify's honesty format (audit-android §6): per-item method labels (grep / manual / screenshot), defects found and fixed during the run, and explicit verification limits.

**Sign-off block (fill on every UI merge):**

```
Date:            ______    Change set: ______
Automated §1:    [ ] pass  (exceptions: ______, justified by rule ______)
Manual §2:       [ ] pass  (items not exercised: ______, reason: ______)
Evidence §3:     [ ] attached (surfaces: ______; viewports: 1440/390; themes: dark/light)
Verified by:     ______
Honest limits:   ______ (e.g. "no touch device available; keyboard pass only")
```
