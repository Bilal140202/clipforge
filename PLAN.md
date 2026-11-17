# PLAN.md — ClipForge from-scratch roadmap

Repo: `Bilal140202/clipforge` (fresh, no fork lineage). Updated 2026-11-17.

## Phase status

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Recon + reference research | complete (docs/research/, capability map; re-homed) |
| 1 | Architecture + contracts | complete for v0.2 (modules, CLI contract, candidate schema) |
| 2 | Media foundation | **real-footage validated** (NASA 9.5-min e2e, issue #13); standalone output-validation module still pending (issue #6) |
| 3 | Transcription + subtitles | transcription + gates verified on real footage; revision model pending |
| 4 | Moment discovery | heuristic v1 verified on real + synthetic; LLM re-ranking pending (issue #7) |
| 5 | Translation/multilingual | en→es verified e2e twice (synthetic + real); corpus + Ollama path pending (issue #8) |
| 6 | Caption/font engine | karaoke + hook + bilingual verified; KI-007 spacing graze; font packs pending (issue #9) |
| 7 | Smart reframing + polish | center-crop verified (320px source upscaled); batch/thumbnails pending |
| 8 | Agent interfaces | CLI contract shipped; governance + recovery tooling adopted (issue #12); MCP/skill files pending (issue #10) |
| 9 | Docs + showcase | GOVERNANCE/RECOVERY/audit docs shipped; guides + screenshots pending (issue #11) |

## Next highest-value

1. Issue #6: output-validation module (ffprobe artifact gate) — Phase-2 exit.
2. Issue #7: LLM re-ranking adapter (provider layer ready; real-footage
   rank-1 hooks show heuristic limits).
3. Issue #8: multilingual corpus (ko/th/ja/zh + code-switching) + Ollama
   path verification.
4. Issue #10: agent guides + screen-state maps (audit Part III lessons
   #7-#9 are the spec source).
5. Issue #11: user docs (INSTALLATION/QUICK_START/USER_GUIDE/CLI_REFERENCE).
