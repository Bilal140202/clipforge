# License and Attribution Audit

**Date:** 2026-11-16
**Scope:** the six reference repositories reviewed for ClipForge (see [REFERENCE_PROJECT_AUDIT.md](REFERENCE_PROJECT_AUDIT.md) for HEAD SHAs, file paths, and feature detail).
**Method:** each license was read from the cloned repository at its pinned HEAD commit. The "verification status" below states whether the actual license file or notice was read — it is a source-level check, not a legal review. Legal questions about a specific port should go to a lawyer, not to this document.

**Standing rule:** licenses can change at any time; re-verify before each ClipForge release (re-read the LICENSE/NOTICE files at the then-current HEAD of any repository ClipForge borrows from, and re-run the checks in this document).

## Summary

| Repository | License name | Verified by reading the actual license file? | Compatible with MIT ClipForge? | Engineer rule (one line) |
|---|---|---|---|---|
| supoclip | AGPL-3.0 | Yes — LICENSE file read in full; README badge agrees | **No** (strong copyleft; network-use clause) | No code, no prompt text, no doc prose; ideas only, reimplemented independently, with an attribution note |
| PeakCut | MIT | Yes — LICENSE read ("MIT License / Copyright (c) 2026 PeakCut contributors") | Yes | Code and ideas directly adoptable; retain the MIT copyright notice and license text in any ported material |
| perfect-srt | None — all rights reserved | Yes — absence verified: no LICENSE file, no license mention in README, AGENTS.md, or code comments | **No** (nothing granted) | Clean-room only: no code, no doc text, no names-pack content, no prompt wording; do not redistribute the committed example SRT |
| lemo-opuscar | Multi-license REUSE scheme (NOASSERTION on GitHub): code MIT, docs CC BY-NC 4.0, demo films CC BY 4.0 | Yes — `LICENSE` + `LICENSES/` + `REUSE.toml` read | Code: yes. Docs/text: **no** (NC forbids commercial reuse in an MIT repo) | Practices transfer; every sentence of agent-facing prose is rewritten, never copied |
| Openclip | MIT | Yes — plain MIT text read ("Copyright (c) 2026 AIONIX") | Yes (moot) | No adoption decided on quality/dormancy grounds; nothing taken; keep as a footnote |
| OpenShorts | MIT core + OpenShorts Commercial License for `cloud/` | Yes — MIT LICENSE read ("Copyright (c) 2024 OpenShorts") and the `cloud/` NOTICE read | Core: yes. `cloud/`: **no** (redistribution and hosting-as-a-service prohibited) | Reuse confined to MIT paths; `cloud/` never copied, vendored, or linked as a dependency |

## Per-project detail

### 1. supoclip — AGPL-3.0

- **License name:** AGPL-3.0.
- **Verification status:** the actual `LICENSE` file was read in full at HEAD `c9f5ac4bf8a1eac596cc9ce5758134a0442c8ed6`; the README badge agrees.
- **Compatibility with MIT ClipForge:** incompatible for code reuse. AGPL is strong copyleft: incorporating its code would force those components (and derivative work) to AGPL, conflicting with ClipForge's MIT licensing. The network-use clause also applies if ClipForge exposes similar functionality as a service. The prompt texts in the repo are part of the copyrighted work and are treated like code.
- **Rule for ClipForge engineers:** no code, no prompt text, no doc prose from supoclip enters this repository — not pasted, not paraphrased line-by-line, not vendored. Ideas (windowing, virality subscores, rerank, dedup, karaoke captions, emoji injection, and the rest) are reimplemented independently from the behavioral descriptions in REFERENCE_PROJECT_AUDIT.md §1, with an attribution note (see "Attribution practice" below).
- **Fork separation:** the SupoClip fork runs in a separate repository under AGPL. No AGPL code from that fork (or from upstream supoclip) enters this repository. Keep the fork out of ClipForge's build paths, dependency trees, and CI.

### 2. PeakCut — MIT

- **License name:** MIT.
- **Verification status:** the actual `LICENSE` file was read at HEAD `b3e403e27444b620a50a4ec1cf44b3afff9e9e45` ("MIT License / Copyright (c) 2026 PeakCut contributors", full ISC/MIT text).
- **Compatibility with MIT ClipForge:** fully compatible.
- **Rule for ClipForge engineers:** code and ideas may be adopted directly. Any ported or adapted file retains the PeakCut MIT copyright notice and license text (in the file header or in a NOTICE/CREDITS file covering the ported set). Attribution is a license condition of good practice here even where the bare MIT text would permit less.

### 3. perfect-srt — no license (all rights reserved)

- **License name:** none. No LICENSE file; no license mention in README, AGENTS.md, or code comments. Default copyright applies: all rights reserved.
- **Verification status:** verified as an absence — the audit checked for a LICENSE file and for license mentions in README, AGENTS.md, and code comments at HEAD `9861ccdc58d17e0d1b2134d8e92dc4a116c7ed9b` and found none.
- **Compatibility with MIT ClipForge:** incompatible. With no license grant, nothing may be copied, redistributed, or derived.
- **Rule for ClipForge engineers:** clean-room only. No code, no doc text, no names-pack content, no prompt wording from perfect-srt enters this repository. Architectural ideas (timing skeleton, index-range addressing, coverage checklist, mechanical-only repair, output gates, glossary-with-banned-substrings, ♪ policy) are reimplemented independently for vertical-video defaults, from the behavioral description in REFERENCE_PROJECT_AUDIT.md §3, with an attribution note. Additionally: the committed example SRT in that repo is third-party broadcast content (copyrighted) — do not redistribute it or copy from it.

### 4. lemo-opuscar — multi-license REUSE scheme

- **License name:** NOASSERTION on GitHub; the repository uses a REUSE scheme (`LICENSE` + `LICENSES/` + `REUSE.toml`): code (`core/`, `tools/`, `styleboard/`, `plugin/`, demo code) MIT; **every `.md` document — including AGENTS.md, DIRECTOR.md, TECHNIQUE.md, STYLE.md and the image-gen prompts — CC BY-NC 4.0**; demo films/stills CC BY 4.0; third-party assets keep their own licenses; the "Clawd" character is Anthropic's and explicitly unlicensed; six TTS narration tracks are excluded from reuse. `plugin.json` declares `MIT AND CC-BY-NC-4.0`.
- **Verification status:** yes — the actual `LICENSE`, `LICENSES/`, and `REUSE.toml` were read at HEAD `3a7132b996be0241c1ea0ab180d519f06e6f10b6`.
- **Compatibility with MIT ClipForge:** the MIT-licensed code is compatible, but the code is not the useful part for ClipForge. The valuable part — the agent-facing documentation prose — is CC BY-NC 4.0, which forbids commercial reuse and therefore cannot be copied into an MIT-licensed repository if any commercial use is possible.
- **Rule for ClipForge engineers:** rewrite, don't copy. The practices in AGENTS.md/DIRECTOR.md/TECHNIQUE.md/STYLE.md (router table, setup contract, machine gates, folder discipline, provenance) transfer; not one sentence of that prose does. Anything ClipForge writes in those patterns must be original wording. Also: do not copy demo-film content or the excluded assets.

### 5. Openclip — MIT

- **License name:** MIT, "Copyright (c) 2026 AIONIX", plain MIT text.
- **Verification status:** yes — the actual `LICENSE` file was read at HEAD `80c3d8b0cd994fd996473f2495d93e0f1d9a0494`.
- **Compatibility with MIT ClipForge:** compatible. Reuse would be legal.
- **Rule for ClipForge engineers:** no adoption — the decision against Openclip is on quality and maintenance grounds (hardcoded Windows ffmpeg paths, keyframe-inaccurate `-c copy` cutting, no tests/CI, effectively dormant), not license grounds. Nothing is taken from it; it is retained as a footnote. If that ever changes, re-read the license at the then-current HEAD first.

### 6. OpenShorts — MIT core + commercial `cloud/`

- **License name:** MIT for the core ("Copyright (c) 2024 OpenShorts"); `cloud/` is under the **OpenShorts Commercial License** per a NOTICE in the repository (view/modify/self-host for personal-internal use permitted; redistribution and hosting-as-a-service prohibited).
- **Verification status:** yes — the MIT `LICENSE` and the `cloud/` NOTICE were both read at HEAD `77340dfe176a3b23080655056b42f7395eefe30b`.
- **Compatibility with MIT ClipForge:** MIT core is compatible; `cloud/` is incompatible with ClipForge redistribution.
- **Rule for ClipForge engineers:** reuse is confined to MIT paths. Everything under `cloud/` (billing, auth, autopilot, GDPR, metering) must not be copied, vendored, derived from, or linked as a dependency — including transitive links. Because `cloud/` and MIT code share one repository, any engineer porting OpenShorts code must check the specific file paths against the NOTICE before porting; if ClipForge ever vendors OpenShorts code, add a lint/path check that fails the build on any `cloud/` path.
- **README credit:** the existing ClipForge README credit to OpenShorts ("architecture inspiration") is accurate per the audit, warranted, and is retained unchanged.

## Attribution practice for ClipForge

- **Direct code reuse (MIT sources, e.g. PeakCut):** retain the upstream copyright notice and MIT license text with the ported code (file header or a NOTICE/CREDITS entry), and note the upstream repository and commit the port came from.
- **Clean-room reimplementation (supoclip, perfect-srt):** where a module reimplements an idea first seen in one of these repositories, add a brief attribution note stating the source repository, its license, and the idea reimplemented — e.g. "moment deduplication by shorter-span overlap ratio: concept from FujiwaraChoki/supoclip (AGPL-3.0), independently implemented; no code or text reused." The note credits the idea; it does not import the license.
- **Pattern adoption with rewritten text (lemo-opuscar):** no attribution note is legally required for practices, but adding one keeps the provenance discipline (a practice adopted from lemo-opuscar's agent-operability model) visible and auditable.
- **Standing credits:** the OpenShorts architecture-inspiration credit in the README stays. Any new standing credits follow the same placement (README) and the same factual style.

## Re-verification before each release

- Licenses are checked as of 2026-11-16 at the HEAD SHAs listed in REFERENCE_PROJECT_AUDIT.md. They can change: a project can relicense, add a NOTICE (as OpenShorts did for `cloud/`), or move files between license scopes.
- Before each ClipForge release that includes borrowed code or newly reimplemented ideas: re-read the LICENSE/NOTICE of each source repository at its current HEAD, confirm the SHAs this document cites still match what was audited, and confirm no borrowed file path has moved under a different license scope (the OpenShorts `cloud/` boundary is the case to watch).
- GitHub metadata (stars, forks, activity) cited in the audit is point-in-time and drifts; it carries no license weight.
