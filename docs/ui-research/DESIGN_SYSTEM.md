# ClipForge Design System — proposed tokens v0.1

Status: **PROPOSAL**. Nothing in this file is implemented yet; `ui/src/tokens.css` does not exist (the ClipForge repo currently ships the Python pipeline only — `clipforge/pipeline.py` and siblings). These tokens are grounded entirely in the owner's own audited systems: the merged audit `USER_PROJECT_UI_AUDIT.md` (this directory) and the owner's playbook (`/home/z/my-project/staging/repos/agent-ui-playbook/`). **Every token value states its provenance** — the audited repo file (via the audit section) it derives from. Values marked "not verified" are gaps, not guesses.

Identity statement: ClipForge is a **dark-first, graphite-and-terminal-cyan media tool** — the verified identity of linuxify, the most disciplined dark-first technical UI in the audit (audit-android §6). An optional light alternative follows bilal-s-grand-showcase's porcelain/Klein-blue system (audit-web §3). The system deliberately avoids the "training-corpus palette" (purple/indigo gradients, glass cards) named in the playbook's anti-pattern catalog (`PLAYBOOK.md` §VI).

Provenance keys used below:
- **[lin]** linuxify `app/src/main/java/com/linuxify/app/ui/theme/Color.kt`, `ui/theme/Type.kt` (audit-android §6)
- **[show]** bilal-s-grand-showcase `src/index.css`, `DESIGN.md` (audit-web §3)
- **[nex]** nexpdf `ui/theme/Motion.kt`, `ui/theme/Type.kt`, `ui/common/Skeleton.kt`, `docs/DESIGN_TOKENS.md` (audit-android §5)
- **[yfa]** Your-Files-Android `uim3/theme/Color.kt`, `Theme.kt`, `Type.kt`, `Spacing.kt` (audit-android §3)
- **[sn]** signal-noise `src/app/globals.css`, `README.md` ADR-001 (audit-web §4)
- **[momo]** momotts `assets/css/main.css` (audit-android §2)
- **[momostk]** momostack `README.md`, `assets/css/main.css` (audit-web §5)
- **[arch]** ahyeon-archive `pages/full-story/index.html` (audit-web §12a)
- **[pb]** agent-ui-playbook `PLAYBOOK.md` / `CHECKLIST.md` (re-verified)

---

## 1. Surface & ink (dark-first column)

The primary column. Graphite surfaces rise in lightness for elevation; one cyan accent carries all interaction.

| Token | Dark value | Provenance |
|---|---|---|
| `--bg` | `#0E1116` | [lin] linuxify background, "restrained technical" dark-first neutrals |
| `--surface-1` | `#151A21` | [lin] linuxify surface step 1 |
| `--surface-2` | `#1C232C` | [lin] linuxify surface step 2 |
| `--surface-3` | `#242D38` | [lin] linuxify surface step 3 |
| `--ink` | `#E3E7EC` | [lin] linuxify text primary |
| `--ink-secondary` | `#D6DCE3` | [lin] linuxify text secondary |
| `--ink-dim` | `#8A93A6` | [lin] linuxify text dim |
| `--outline` | `#303945` | [lin] linuxify outline/hairline |
| `--accent` | `#5CC8D7` | [lin] linuxify terminal cyan, dark mode |
| `--accent-strong` | `#0E7C8C` | [lin] linuxify terminal cyan, light mode (usable as the pressed/active step on dark too) |
| `--accent-container` | `#10393F` | [lin] linuxify cyan container (dark) — tint fills for selected rows/active tools |
| `--accent-on-container` | `#B8ECF4` | [lin] linuxify on-cyan-container (dark) |
| `--scrim` | `rgba(0,0,0,0.667)` (≈`#AA000000`) | [audit-android §1] jarvis-agent drawer scrims (`activity_main.xml`) — the observed precedent for overlay scrims; expressed as alpha, not hex |

Tint fills at 8-12% alpha are the sanctioned way to color-wash a surface instead of raw color blocks — the momotts practice ([momo], `main.css:10-50`). "One deliberate accent color beats three decorative ones" ([pb] Law 1): cyan is the only accent; media-category coding (Rule: semantic category map, [yfa] `CategoryColors.kt`) may add per-genre hues later via one map + resolver, never per-screen hex.

## 2. Surface & ink (light alternative column)

Informed by bilal-s-grand-showcase's "Porcelain Day" — the most mature tokenized light system in the audit ([show], `src/index.css:40-190`). ClipForge keeps its cyan accent in light mode (not Klein blue) so the identity survives the theme switch; the porcelain neutrals and the "no gradients, flat fields only" law are what carry over ([show] `DESIGN.md` §2.4).

| Token | Light value | Provenance |
|---|---|---|
| `--bg` | `#F5F5F1` | [show] porcelain background |
| `--surface-1` | `#FCFCFB` | [show] card surface |
| `--surface-2` | `#EFEFEB` | derived: mid-step between [show] `#F5F5F1` and card `#FCFCFB` — **not verified** against an audited repo; compute contrast before adoption |
| `--ink` | `#131318` | [show] porcelain foreground |
| `--ink-secondary` | `#3F3F46` | **not verified** — interpolated between [show] foreground and muted |
| `--ink-dim` | `#5B5B66` | [show] muted-foreground (audit records 7.8:1; recomputed here as 6.13:1 — see §4) |
| `--outline` | `#D2D2D0` | [show] border |
| `--accent` | `#0E7C8C` | [lin] linuxify light-mode cyan |
| `--accent-container` | `#B8ECF4` | [lin] linuxify light cyan container |
| `--accent-on-container` | `#10393F` | [lin] linuxify light on-cyan-container |

## 3. Status colors — color is never the only signal

Fixed hues per theme mode, with the linuxify rule stated in its source: *"never color-only: always paired with label"* ([lin] `Color.kt:32-42`, audit-android §6). Every status renders as **color + text label (+ icon)** through one shared status component (playbook Rule 4; [lin] `Common.kt:24-63` `StatusChip` = dot + mono label + `contentDescription`).

| Status | Dark | Light | Provenance |
|---|---|---|---|
| `--status-success` | `#4ADE80` | `#15803D` | [lin] `Color.kt:32-42` |
| `--status-warning` | `#FBBF24` | `#B45309` | [lin] `Color.kt:32-42` |
| `--status-error` | `#F87171` | `#B91C1C` | [lin] `Color.kt:32-42` |
| `--status-info` | `#60A5FA` | `#1D4ED8` | [lin] `Color.kt:32-42` |
| `--status-neutral` | `#8A93A6` | `#5C6672` | [lin] `Color.kt:32-42` |

ClipForge status vocabulary maps onto these: queued/neutral, running/info, done/success, failed/error, canceled/warning, unverified (AI-suggested content)/neutral. Badge vocabulary for asset provenance (generated / sourced / licensed / unverified) follows the ahyeon-archive tier-badge pattern ([arch], audit-web §12a).

## 4. Contrast verification

Three contrast claims appear in the audits. They are recomputed here with the standard WCAG relative-luminance formula so the proposal carries its own numbers.

| Pair | Audit records | Recomputed (this doc) | Verdict |
|---|---|---|---|
| `#8A93A6` on `#151A21` (linuxify dim on surface-1) | ≈4.6:1 (`linuxify/docs/UI_REVIEW.md`, audit-android §6) | **5.66:1** | passes AA 4.5:1 either way; discrepancy flagged, audit's method not on file |
| `#0B2BC2` on `#F5F5F1` (Klein blue on porcelain) | 9.2:1 (`DESIGN.md` §2, audit-web §3) | **8.98:1** | passes AA; rounding difference only |
| `#5B5B66` on `#F5F5F1` (muted on porcelain) | 7.8:1 (`DESIGN.md` §2, audit-web §3) | **6.13:1** | passes AA; discrepancy flagged |
| `#5CC8D7` on `#0E1116` (accent dark on bg) | not recorded | **9.63:1** (own computation) | passes AA |
| `#E3E7EC` on `#0E1116` (ink on bg) | not recorded | **15.23:1** (own computation) | passes AAA |
| `#0E7C8C` on `#F5F5F1` (accent light on porcelain) | not recorded | **4.49:1** (own computation) | **marginal** — use for large text/icons (3:1) or darken before use on body text |

All dark-mode status hues pass ≥4.5:1 on `--bg` (recomputed: success 10.85, warning 11.33, error 6.84, info 7.44). The enforceable bar remains the playbook's: contrast ≥ 4.5:1 body / 3:1 large text ([pb] Law 10).

## 5. Typography

**Reference stacks actually found in the audits** (named as the evidence base):

| Repo | Stack (as audited) | Audit |
|---|---|---|
| momotts | Fraunces variable serif display (`'opsz' 72`) + Archivo body + Space Mono labels; `.mono-label` 0.72rem/700/uppercase/0.14em | audit-android §2 |
| bilal-s-grand-showcase | Bricolage Grotesque 700-800 display + Inter Tight body + IBM Plex Mono data; `.data-mono` = `tabular-nums` | audit-web §3 |
| signal-noise | Space Grotesk + JetBrains Mono, self-hosted, "96KB total" (ADR-001) | audit-web §4 |
| ahyeon-archive (full-story) | Fraunces 900 display + Archivo body + IBM Plex Mono meta | audit-web §12a |
| Your-Files-Android | Arimo (downloadable Google Font, 4 weights) | audit-android §3 |
| nexpdf | `FontFamily.Default` only — 5 styles, avoiding font-license burden in v0.1 | audit-android §5 |
| linuxify | platform sans for prose + `FontFamily.Monospace` for **all runtime values** (paths, sizes, PIDs, ports) | audit-android §6 |

**ClipForge proposal: a two-file, two-voice stack.** `--font-ui: "Space Grotesk", system-ui, sans-serif` and `--font-mono-data: "JetBrains Mono", ui-monospace, monospace`, self-hosted (provenance: [sn] ADR-001 — the owner's own verified lean pairing, ~96KB total). Rationale: an editor is a data instrument first; the linuxify precedent ([lin]) shows the mono-runtime-values voice is what makes a technical tool coherent, and JetBrains Mono is already the mono face in two audited owner repos ([sn], [momostack]). The serif-display voices (Fraunces, Bricolage) are available for a future marketing site, **not** for editor chrome — a UI where numbers dominate should not set display serif against mono data.

**Scale — 5 UI roles (nexpdf's deliberate minimalism, [nex] `Type.kt`), each annotated with its intended usage (the Your-Files-Android practice, [yfa] `Type.kt`):**

| Token | Size/line | Usage (annotation) |
|---|---|---|
| `--text-headline` | 28/34 · 600 | Screen titles ("Review candidates", "Export") — nexpdf headlineMedium 28 |
| `--text-title` | 22/28 · 600 | Panel titles — nexpdf titleLarge 22 |
| `--text-body-strong` | 16/24 · 500 | Section headers inside panels, primary buttons — nexpdf titleMedium 16 @ +0.15 tracking |
| `--text-body` | 14/20 · 400 | Default UI text, transcript prose — nexpdf bodyMedium 14 |
| `--text-label` | 11/16 · 500, uppercase +0.14em tracking | Chip labels, eyebrows — nexpdf labelSmall 11; `.mono-label`/`.sn-meta` practice ([momo]/[sn]) |

**Mono data roles (linuxify's three mono styles verbatim, [lin] `Type.kt`):**

| Token | Size/line | Usage |
|---|---|---|
| `--text-mono-label` | 11/14 · 500 | Status chip labels |
| `--text-mono-small` | 12/16 | Timecodes in lists, file sizes, queue counts |
| `--text-mono-body` | 13/18 | Timecode readouts under the preview, transcript timestamps gutter |

All countable/timecode surfaces get `font-variant-numeric: tabular-nums` — playbook Law 6 ([pb] PLAYBOOK.md:90) and the showcase's `.data-mono` precedent ([show]). Rule: `tabular-nums` on anything countable; monospace for IDs/paths/hashes (LAW 6), matching linuxify's runtime-values rule.

## 6. Spacing — 4px-based scale

Base-4 values with named steps and context aliases (the Your-Files-Android named-object pattern, [yfa] `Spacing.kt`; the 8pt-multiple discipline is documented in [momostk] `README.md` rule 4 — ClipForge uses the 4px half-step because editor panels pack denser than marketing pages).

| Token | px | Provenance |
|---|---|---|
| `--space-1` | 4 | [yfa] `Spacing.kt` `sm 4` |
| `--space-2` | 8 | [yfa] `md 8` |
| `--space-3` | 12 | [yfa] `lg 12` |
| `--space-4` | 16 | [yfa] `xl 16` |
| `--space-6` | 24 | [yfa] `xxl 24` |
| `--space-8` | 32 | [yfa] `xxxl 32` |

Context aliases (same naming practice as [yfa]): `--space-panel-inner` = 16, `--space-list-item-y` = 8 (candidate rows), `--space-screen-x` = 24, `--space-panel-gap` = 8 (gaps between docked panels). Rule: no arbitrary padding in components — grep-able (§8). The yfa 2px step (`xs 2`) is **dropped** so every step is a multiple of 4; hairline separations use `--outline` borders, not 2px gaps.

## 7. Radius scale

Derived from the single-seed formula verified in Your-Files-Android `Theme.kt:12-25` ([yfa]): `xsmall = r*0.3, small = r*0.6, medium = r, large = r*1.4, xlarge = r*2.0`. Seed **12** (the formula's documented default). Derived values snap to the nearest 4px multiple (own computation: 3.6→4, 7.2→8, 12.0→12, 16.8→16, 24.0→24).

| Token | px | Component assignment (nexpdf's written shape scale, [nex] `docs/DESIGN_TOKENS.md`) |
|---|---|---|
| `--radius-xs` | 4 | timecode chips, inline tags |
| `--radius-sm` | 8 | inputs, small buttons, transcript rows |
| `--radius-md` | 12 | cards, panels, CandidateMomentCard frame |
| `--radius-lg` | 16 | modals/dialogs, style preview cards (nexpdf: cards 16dp) |
| `--radius-xl` | 24 | sheets/oversized panels, tool chips (nexpdf: tool chips 24dp) |
| `--radius-pill` | 999px | the sanctioned exception — accept/reject stamps and status pills, "buttons stadium" per nexpdf; pill-as-stamp precedent in [show] (chips 999px "they are *stamps*") and [momo] (`--radius-pill: 999px`) |

Honest note: nexpdf's own sheets use 28dp; ClipForge's derived scale lands dialogs at 16 and sheets at 24 — the divergence from nexpdf's 28 is a choice, recorded here. The zero-radius instrument systems ([show], [sn] `--radius: 0rem`) were considered and rejected: ClipForge is a media viewer, not a print poster; frames read better with soft corners.

## 8. Motion tokens

Durations and easing from nexpdf's verified motion system ([nex] `ui/theme/Motion.kt`, audit-android §5): "Motion as named constants, not magic numbers."

| Token | Value | Provenance |
|---|---|---|
| `--motion-quick` | 120ms | [nex] `NexMotion.QUICK` — hovers, focus, chip toggles |
| `--motion-standard` | 220ms | [nex] `NexMotion.STANDARD` — panel enter/exit, card state changes; also the nexpdf screen-enter fade (fade 220ms + scale 0.96→1, `docs/DESIGN_TOKENS.md`) |
| `--motion-emphasized` | 320ms | [nex] `NexMotion.EMPHASIZED` — dialog/sheet entry, review-rail add/remove |
| `--ease-standard` | `cubic-bezier(0.05, 0.7, 0.1, 1.0)` | [nex] EmphasizedDecelerate constant, the one easing value quoted in the audit |
| `--ease-snap` (alt) | `cubic-bezier(0.22, 1, 0.36, 1)` | [momo] `--ease-out`, verified alternate for micro-interactions |
| `--motion-spring` | spring, low-bounce/medium-low-stiffness | [nex] `expressiveSpring()` = `DampingRatioLowBouncy` + `StiffnessMediumLow` — native re-ordering in lists; on the web stack use `--motion-emphasized` + `--ease-standard` as the fallback (spring is not a CSS primitive) |

Written motion spec carried over from nexpdf's `docs/DESIGN_TOKENS.md` (audit-android §5): motion 200-450ms range — **nothing decorative blocks input**; screen-enter = fade 220ms + scale 0.96→1; page/section crossfade 250ms. Budget corroboration: the playbook's own critique-round list allows "150-200ms ease-out + skeleton pulse only" ([pb] `CONTRIBUTING.md`). Skeleton pulse: alpha 0.5→1, 700ms reverse tween on `surfaceContainerHighest.copy(alpha = pulse)` — the verified nexpdf `Skeleton.kt` pattern ([nex], audit-android §5). Ambient motion whitelist mechanism from [show] `DESIGN.md` §7 ("marquee tickers, live-dot pulse, caret blink, clock ticks"): ClipForge's only sanctioned ambient motion is the **running-job pulse dot** in the render queue and the **live level meter** during playback capture. Everything else animates only to show *what changed* (playbook Rule 12). A global `prefers-reduced-motion` clamp is mandatory ([show] `motion.tsx` contract 1; [sn] `globals.css:288-303`; [pb] candidate 16).

## 9. Elevation — tonal, not shadowed

nexpdf's written rule: elevation tiers 0/1/3/6dp **from tonal roles**, "no raw shadows" ([nex] `docs/DESIGN_TOKENS.md`, audit-android §5). ClipForge maps the tiers onto the surface ladder:

| Elevation | Surface | Usage |
|---|---|---|
| 0 | `--bg` | workspace canvas, timeline track area |
| 1 | `--surface-1` | docked panels, candidate cards, queue rows |
| 2 | `--surface-2` | hover state of a card, active panel |
| 3 | `--surface-3` | dialogs, command palette, dropdowns |
| overlay | `--scrim` + `--surface-3` | modal layers (scrim precedent: jarvis-agent drawers, audit-android §1) |

Definition comes from `--outline` hairlines (the [lin] outline token; hairline discipline also in [momo] and [momostack]), not drop shadows. Forbidden: glow shadows and glassmorphism — playbook forbid-list ([pb] Law 11) and the momostack cautionary example ([momo] glass cards, audit-web §5 verdict). Tinted shadow tokens (momotts `--shadow-warm`, [momo]) exist in the corpus but are **not adopted** for v0.1.

## 10. How tokens are enforced

Single source file: **`ui/src/tokens.css`** holds every value above under `:root` (dark-first) plus a light column — the playbook Law 1 structure ([pb] PLAYBOOK.md:14, :27) and the showcase's "every value tokenized" practice ([show] `src/index.css:40-190`). Enforcement is mechanical, not aspirational — the failure mode to avoid is jarvis-agent's decorative `colors.xml` (audit-android §1) and momostack's README-prose tokens (audit-web §5):

1. **Grep gate (CI):** `grep -rEn '#[0-9a-fA-F]{3,8}|rgba?\([0-9]' ui/src --include='*.css' --include='*.tsx' | grep -v 'ui/src/tokens.css'` must return nothing (playbook Law 1 Verify, verbatim pattern).
2. **Spacing/radius/motion greps:** no `padding|margin|gap` with arbitrary px outside tokens; all `transition|animation` durations reference `var(--motion-*)`; commands as in `UI_ENGINEERING_PLAYBOOK.md` Rules 1, 7, 12.
3. **Checklist traceability:** every `CHECKLIST.md`-style item traces to a rule ([pb] `CHECKLIST.md`: "Every item traces to a law") — see `UI_QA_CHECKLIST.md`.
4. **Docs-code parity rule:** a doc may not claim a token that grep cannot find in `ui/src/tokens.css` — the linuxify Spacing-drift lesson (audit-android §6, anti-pattern #4).
5. **Divergence contract:** if a sibling product ever shares this repo family, write the three-property divergence contract down and re-check it on every visual change, per the showcase's practice ([show] `DESIGN.md:41-53`, `AGENTS.md` §3).
