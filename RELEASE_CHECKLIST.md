# RELEASE_CHECKLIST.md — release gates

A release is declared only when every gate passes with recorded evidence.

- [ ] Clean install from requirements.txt on 2+ OS environments (av pin verified on one).
- [ ] `python -m pytest tests/ -q` green with output recorded.
- [ ] End-to-end run on real footage: transcribe → discover → cut → reframe → burn → export (verified on synthetic media session 1-2; repeat on real footage before release).
- [ ] Output-validation module gates artifacts (pending).
- [ ] Subtitle gates pass on all exported SRT/VTT (implemented; verify per release).
- [ ] Translation verified for every language claimed (en→es verified; others pending).
- [ ] Font packs render in real output (pending).
- [ ] CLI + agent interface documented and executed by a real external agent (pending).
- [ ] Documentation matches implementation.
- [ ] License/security audit re-verified (docs/research/LICENSE_AND_ATTRIBUTION_AUDIT.md).
- [ ] GitHub release tagged with notes + checksums after all gates pass.
