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

### Next actions
1. GitHub Issues (native, enabled) — milestone + task set with evidence.
2. CI `tests.yml` first green run on the fresh repo.
3. Output-validation module (ffprobe artifact gate) — PLAN.md item 1.
