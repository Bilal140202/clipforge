# PLAN.md — ClipForge from-scratch roadmap

Repo: `Bilal140202/clipforge` (fresh, no fork lineage). Updated 2026-11-17.

## Phase status

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Recon + reference research | complete (docs/research/, capability map; carried from session 1, re-homed) |
| 1 | Architecture + contracts | complete for v0.2 (modules, CLI contract, candidate schema) |
| 2 | Media foundation (import/probe/cut/reframe/render/validate) | partial — cut/reframe/burn verified; standalone output-validation module pending |
| 3 | Transcription + subtitles | partial — transcription verified; subtitle gates + SRT/VTT built and unit-tested; editor-ready revision model pending |
| 4 | Moment discovery | heuristic v1 verified e2e; LLM re-ranking adapter pending |
| 5 | Translation/multilingual | provider path verified e2e (en→es via z-ai); corpus validation + local Ollama path pending |
| 6 | Caption/font engine | partial — karaoke + hook + bilingual styles; font packs pending |
| 7 | Smart reframing + polish | center-crop + MediaPipe path present; batch/thumbnails pending |
| 8 | Agent interfaces | CLI contract shipped (`python -m clipforge.cli --help`, `doctor`); MCP/skill files pending |
| 9 | Docs + showcase | README honest-status shipped; guides + screenshots pending |

## Next highest-value

1. Output-validation module (ffprobe-based artifact gate) — Phase 2 exit.
2. LLM re-ranking adapter over discovery candidates (provider layer ready).
3. GitHub Issues: create milestone + task set (issues are enabled here).
4. CI workflow (tests.yml) on the fresh repo, verified green.
5. Agent guides + real screenshots (docs/ui-research/ is the spec).
