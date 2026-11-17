# WORKLOG.md — execution history

## Session 1 (2026-11-16, archived)
Recon, reference + UI research, first discovery engine, 21 tests, e2e smoke
on a fork of `superz1402/clipforge` (commits 4bee204..1f51a23). Archived at
`clipforge-arch/` (local only). Fork deleted 2026-11-17 — see session 2
D-001 in DECISIONS.md. Full session-1 log: `clipforge-arch/WORKLOG.md`.

## Session 2 — 2026-11-17 (UTC), from-scratch rebuild

### Objective
Replace the fork with a clean, from-scratch ClipForge repository and build +
RUN the system end-to-end in the sandbox.

### Work performed
1. Deleted `Bilal140202/clipforge` fork (HTTP 204; content preserved in
   `clipforge-arch/`), created fresh repo with Issues ENABLED
   (has_issues: true — resolves session-1 KI-008).
2. Re-homed session-1 assets: core modules (transcribe, pick, discover,
   captions, reframe), 21 tests, docs/research + ui-research + architecture
   + capability map, MIT LICENSE. Upstream-specific docs (HANDOFF, MUSIC,
   previews, licenses evidence) excluded — they belong to the legacy repo.
3. New modules built:
   - `clipforge/subtitles.py`: SRT/VTT parse+serialize, cue building from
     transcripts, 5 gates (G1 duration 0.8-7.5s, G2 <=2 lines x 42 chars,
     G3 timing/overlap, G4 non-empty, G5 order), mechanical auto-repair
     (merge-short, split-long on word boundaries, overlap clamp, renumber)
     — clean-room; text is never rewritten.
   - `clipforge/providers.py`: LLM adapter layer (zai CLI + Ollama HTTP +
     get_provider auto-detect + extract_json tolerant parser). z-ai output
     shape verified live before coding (choices[0].message.content, JSON in
     fences).
   - `clipforge/translate.py` (rewritten): batched, schema-constrained cue
     translation via the provider layer; timing preserved, per-chunk
     alignment with loud failure. Replaces the argostranslate-only module.
   - `clipforge/cli.py`: stable agent-facing contract (doctor/transcribe/
     discover/subtitles/translate/render/pipeline).
   - `captions.build_bilingual_ass`: karaoke + translated line (Trans
     style) + hook in one ASS.
   - `pipeline.py`: always exports SRT+VTT for the chosen window with
     gate report in metadata.json; translation now provider-based with
     bilingual variant burn.
4. Fresh identity: pyproject (console script `clipforge`), README with
   honest status table, AGENTS/PLAN/DECISIONS/KNOWN_ISSUES/RELEASE_CHECKLIST.

### Failures recorded
- cli.py cmd_transcribe initially contained a nonsense guard statement
  (open(os.devnull) no-op) — caught in review, removed before commit.
- providers.py: `import re` placed at bottom with noqa — works but ugly;
  kept for now, noted as cleanup.

### Verification (actual results, 2026-11-17)
- `python -m pytest tests/ -q` -> **44 passed** (0.74s), offline.
- Full system e2e (`scripts/e2e_clipforge.sh` in sandbox): 3-section
  2.7-minute TTS video built with ffmpeg -> `clipforge doctor` ok
  (provider auto-detected: zai) -> local faster-whisper transcription ->
  discovery: 5 candidates kept / 42 suppressed, audio energy used, spread
  across all 3 sections (rank-1 = octopus hook window, 80.3/100) ->
  render rank-1: 45.68s 1080x1920 h264+aac -> Spanish translation via
  provider (real LLM, batched cues) -> bilingual variant clip_final.es.mp4
  -> subtitle gates on exported SRT: 5/5 passed, 0 violations.
- Visual QA of bilingual frames: hook overlay (top), Spanish Trans line
  (above caption), karaoke word-highlight (bottom) all render correctly.
- Bug caught and fixed during e2e: `build_bilingual_ass` read key
  `"target"` while `write_translated` emits `"text"` -> ES variant burned
  without translation (byte-identical output caught by `cmp`). Fixed to
  accept both keys; e2e re-run clean.
- Bugs caught by the test suite before e2e: broken `parse_ts` regex group
  handling (rewritten); `auto_repair` could not repair leading short cues
  nor split beyond 2 pieces (rewritten with recursive word-boundary split).

- CI on the fresh repo: runs 1-3 failed (av 14.4 no py3.12 linux wheel ->
  source build missing ffmpeg dev headers; then 2 environment-dependent
  tests: hardcoded sandbox cwd, 1e-9 float epsilon). Root causes fixed
  (`av==14.2.0` pin everywhere, argostranslate dropped — translation is
  provider-based now, portable tests). **Run 4: `00e3155` — success**
  (https://github.com/Bilal140202/clipforge/actions/runs/43910002949).

### Next actions
1. Output-validation module (ffprobe artifact gate) — issue #6, Phase-2 exit.
2. LLM re-ranking adapter over candidates (issue #7).
3. Multilingual corpus validation + Ollama path verification (issue #8).

### Ledger status at session end
- Milestone `v0.2 - Foundation` (MS#1) on GitHub.
- Issues #1-4 CLOSED with evidence (discovery, subtitles, providers/
  translation, CLI). Issues #5-11 OPEN; #5 (CI) closed after green run
  `00e3155` — see its evidence comment.

## Session 3 — 2026-11-17 (UTC)

### Trigger and corrections
Owner corrected two failures from sessions 1-2: (1) ClipForge must be
demonstrated as a CLIPPING tool on real footage — synthetic test patterns
were a fixture, not the product; (2) session 1 worked "blindly": fork/push
attempts happened before token permissions were verified. Also supplied:
a fresh fine-grained PAT and the full Master Execution Prompt (1286 lines)
with a persistence/recovery/UI addendum that takes precedence for task
tracking, persistence, and UI quality.

### Work performed
1. **Verify-first discipline restored** (the owner's complaint #2):
   authenticated identity + `.permissions` (push/admin/maintain all true
   on `Bilal140202/clipforge`) verified BEFORE any task. Token stored only
   in sandbox secrets (never printed/committed). Owner advised to rotate:
   the PAT is exposed in chat history, and the master prompt itself says
   "Never ask the user to paste a token into chat".
2. **Full master prompt read** (upload/Pasted Content_1794840934216.txt,
   1286 lines) and persisted verbatim as `docs/GOVERNANCE.md` (issue #12).
   AGENTS.md now encodes verify-before-work, startup protocol (§10), and
   session ending checklist (§11).
3. **Issues #12/#13/#14 created BEFORE implementation** (addendum §2).
4. **Real-footage clipping e2e (issue #13)**: NASA `NHQ_2021_0222_VF`
   Perseverance landing narration, 9.5 min, public domain (24.8MB 320px
   preview). Local faster-whisper transcription: 368 words / 47 segments /
   569.6s. Discovery: 5 kept / 66 suppressed, rank-1 = 432.3-478.9s (live
   landing-commentary segment). Render: 46.63s 1080×1920 + Spanish
   bilingual variant (real LLM translation). Subtitle gates 5/5 passed.
   Three extracted frames visually verified: real Mars surface footage
   with hook + Spanish line + karaoke captions rendering correctly.
5. **Ground-truth honesty**: NASA's official SRT asset for this video is a
   placeholder ("captions pending"), so no objective accuracy comparison
   was possible — recorded, not papered over. ASR artifacts on compressed
   320px audio documented as KI-008.
6. **Recovery tooling (issue #12)**: `scripts/checkpoint.py` (measured
   health JSON + WORKLOG checkpoint notes) + `docs/RECOVERY.md` honest
   runtime inventory — no auto-resume exists in this runtime; GitHub is
   the only durable store; recovery = the documented startup protocol.
7. **UI audit extension (issue #14)**: `docs/ui-research/
   USER_PROJECT_UI_AUDIT.md` Part III — 153-repo inventory across
   Bilal140202/ansaribilal14/superz1402 + six new deep dives (OVE Android
   5/5, OVE Web 4/5, Your-Files-Redesign 5/5, AuraGallery 4/5,
   Choose-Your-Monster 2/5, nexpdf +motion tokens 4/5) with file-path
   citations and 15 engineering lessons (force-dark studio, token review
   rule, commit-once gestures, honest states, screen-state maps,
   tool-chip bar, semantic lane colors, tabular-nums).

### Failures and fixes this session
- NASA collection.json URL contains a smart quote + spaces → curl
  "Malformed input" → fixed via urllib path quoting (persisted
  `scripts/fetch_real_footage.py`).
- `USER_PROJECT_UI_AUDIT.md` Write initially failed (file exists from
  session 1) → resolved by APPENDING Part III, preserving session-1 work
  (addendum rule: never overwrite without understanding).
- KI-007 recorded: 2-line Spanish translations can graze the karaoke
  caption (Trans MarginV) — cosmetic, caption polish pass.

### Commits and verification
- (recorded in issue #12/#13/#14 closure comments; push verified via
  `git ls-remote` + API at commit time — see checkpoint entries below)

### Next actions
1. Issue #6 output-validation module (Phase-2 exit) — now more urgent
   since real-footage renders exist.
2. Issue #7 LLM re-ranking (rank-1 "hook" fragments on real footage show
   heuristic limits; KI-008).
3. Issue #8 multilingual corpus + Ollama path; issue #9 font packs;
   issue #10 agent guides/MCP + screen-state map (Part III lessons #7-#9);
   issue #11 docs set.

### Checkpoint 2026-11-16T17:10:26+00:00 — session 3: governance+recovery adopted, real-footage e2e (#13), UI audit Part III (#14); committing #12/#13/#14 work
- branch `main` head `d37a04a38d75` remote_head `d37a04a38d75` synced=True dirty=8

## Session 4 — 2026-11-17 (UTC): owner-provided footage e2e + recycle-recovery proof

### Recovery event (the addendum working as designed)
The sandbox recycle between turns wiped the ENTIRE `clipforge/` working
tree (including `.git`). Remote `552cf21` was untouched. Recovery
followed `docs/RECOVERY.md`: re-init git → fetch → `reset --mixed` →
verify drift (43 deletions, zero local-only changes) → `reset --hard
origin/main` → tests green. Lost runtime state: installed pip packages
(reinstalled from pinned requirements.txt) and the git remote +
credential config (re-added). Zero commits lost. First real recycle-wipe;
the GitHub-first persistence held exactly as designed.

### Owner footage run (issue #15)
Owner uploaded a Drive video (`new.mp4`, 43.2MB): 335.1s (5m35s),
1280x720 h264 30fps + AAC, **Korean speech** (auto-detected; 123
segments / 279 words) — ClipForge's first non-English source. Pipeline:
transcribe (faster-whisper base, lang=ko) → discover (5 kept / 66
suppressed; rank-1 = 25.89-71.86s, score 70.7, hook "왜 한동안 이걸 찍을
생각을 하지 못했을까요?") → render rank-1 45.97s 1080x1920,
**face-tracked** reframe (MediaPipe path), ko→en translation (first
non-es translation path, real LLM), karaoke + hook burn → subtitle
gates 5/5, 0 violations → frames QA'd at 2s/20s/40s + hook.

### Caption layout fix (KI-007 resolved)
Frame QA at t=2s exposed a real collision: a 3-display-line karaoke
caption touched the 2-line EN translation (Trans MarginV=440 landed
exactly on the caption worst-case boundary). Fixed: Caption 78→64px +
side margins 60→110, Trans MarginV→520, plus regression test
`test_style_layout_keeps_trans_clear_of_captions` enforcing a 40px
clearance (45/45 tests). Re-render verified clean at 2s/40s. Hangul
renders correctly via libass font fallback (style declares DejaVu Sans;
fontconfig supplies CJK glyphs).

### Honest limitations recorded
- Whisper `base` on casual Korean produces fragment/garbage tokens
  (KI-008 non-English case; e.g. rank-5 hook); `--whisper-model small`
  is the mitigation.
- The source video carries its own burned-in Korean subtitles — they
  coexist with ours in frames (inherent to the input, not a bug).
- Keyword-heuristic discovery is English-biased; on Korean it ranked by
  energy/flow (plausible top score 70.7) — issues #7/#8 remain the fix.

### Next actions
1. Issue #6 output-validation module (Phase-2 exit).
2. Issue #7 LLM re-ranking; #8 multilingual corpus + Ollama; #9 fonts.
3. Issue #10 agent guides/MCP + screen-state maps; #11 docs set.

### Checkpoint 2026-11-17T09:25:17+00:00 — session 4 complete: owner Korean footage clipped e2e (#15), KI-007 caption collision fixed (40108c8), recycle-wipe recovered from GitHub with zero loss
- branch `main` head `3b35a6193e12` remote_head `3b35a6193e12` synced=True dirty=0

## Session 5 — 2026-11-17 (UTC): translation-only caption mode (#16)

Owner request: when a clip is translated, showcase ONLY the translated
caption — no source-language karaoke. Implemented `render
--caption-mode bilingual|translation` (default preserves prior behavior):

- `captions.build_translation_only_ass`: TransSolo + Hook events only;
  regression tests assert zero Caption-style dialogues and zero \kf.
- New `TransSolo` style: Caption-zone geometry (MarginV 220, 64px) so a
  solo translation does not float at the raised bilingual position.
- In translation mode the MAIN output is the solo render (no karaoke
  base burn); requires a working provider, else hard-exits rather than
  silently shipping the wrong captions.
- Found + fixed while gating the output: translated SRT was never gated
  before and one LLM cue was 44 chars vs G2's 42 limit. New
  `translate._fit_subtitle` (word-wrap 42, hard-slice for spaceless CJK,
  2-line cap with ellipsis) enforces G2 deterministically; tests added.

Verified: owner rank-1 re-rendered translation-only (45.97s, 1080x1920,
face-tracked), gates 5/5 0 violations, frames QA'd (EN-only captions in
zone; remaining Korean text in one frame is the source's own burn-in).
52/52 tests.

### Checkpoint 2026-11-17T09:55:46+00:00 — session 5: translation-only caption mode (#16) with G2 fit enforcement; owner clip re-rendered EN-only
- branch `main` head `f0143b488f0d` remote_head `f0143b488f0d` synced=True dirty=0

## Session 6 — 2026-11-17 (UTC): the permanent caption-language rule (#17)

Owner made it permanent: a clip's captions speak the video's own language
OR full English — never both, never mixed. English choice also means the
HOOK is translated (no source-language hook anywhere).

- `langrule.py`: pure decision function + `CaptionPlan`; decision table
  fully unit-tested (13 tests). ASK path: TTY prompt, else exit 2 with
  the exact question for agents to relay.
- Wired into `cli.py render` AND legacy `pipeline.py` (decision before
  heavy work; pipeline metadata records `caption_rule`).
- `--caption-mode` demoted to legacy knob: the rule overrides it when
  English is chosen, with a loud printed note.
- English-only: hook translated via `translate.translate_hook` +
  `fit_hook` (18-char/3-line fit for the 104px style); provider failure
  = hard error, never silent fallback.
- Verified e2e on owner footage with `--caption-lang en --caption-mode
  bilingual`: rule overrode the mode, burned English hook + English
  captions, gates 5/5; frames QA'd; compliant clip re-uploaded to the
  owner's Drive slot (replacing the Korean-hook version).
- 69/69 tests. README rewritten (rule table, CLI reference, gates, FAQ);
  CHANGELOG started; versions synced to 0.4.0.
