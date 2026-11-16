# CLIPFORGE — MASTER EXECUTION PROMPT FOR SUPER Z
## Build the complete, agent-first, open-source short-form video clipping studio

**Project repository:** `superz1402/clipforge`  
**Publishing owner/account:** `bilal140202`  
**Primary objective:** Turn ClipForge into a dependable end-to-end clipping production system that can discover high-value moments, create polished Shorts/Reels/TikToks, repair and translate subtitles, render deliverables, and operate through both a human-facing application and AI-agent interfaces.

---

# 0. EXECUTION DIRECTIVE — READ THIS FIRST

You are not being asked to write a proposal, create a mockup, or produce a superficial prototype. You are being asked to inspect the existing ClipForge repository, research the supplied reference projects, design the implementation, build the software, test it, document it, and publish a verifiable result.

Work autonomously using the tools and capabilities actually available in your environment. Use your planning, multi-agent orchestration, web research, browser automation, filesystem, shell, Python/Node execution, code editing, media understanding, ASR, image generation/editing, document generation, spreadsheet generation, charting, scheduling, and quality-assurance capabilities where they genuinely help.

**Do not pretend a capability exists merely because this prompt mentions it.** Your first job is to establish which tools, models, APIs, runtimes, skills, credentials, and system permissions are actually available. Distinguish:
1. Native Super Z capabilities available now.
2. Capabilities available through installed tools or configured credentials.
3. Capabilities that can be implemented locally with open-source software.
4. Capabilities that require optional third-party services, credentials, hardware, or user action.
5. Capabilities that are not currently possible.

Never claim that a task, test, deployment, upload, or integration succeeded unless you observed the success result. If blocked, record the exact blocker and continue with independent work.

## Non-negotiable operating rules

- Preserve the existing repository, history, working features, and user data. Inspect before modifying.
- Never overwrite or delete existing work without understanding it and creating a recoverable path.
- Do not expose, print, commit, log, or place credentials in source files. Use environment variables or a documented local secrets mechanism. Never ask the user to paste a token into chat.
- The GitHub publishing identity requested by the owner is `bilal140202`. Verify the authenticated account and repository permissions before publishing. Do not assume the account or token is configured.
- Keep the project open-source. Audit licenses before reusing code, assets, models, fonts, or reference implementations. Prefer clean-room implementations and compatible dependencies where necessary.
- Prefer free, local, CPU-capable defaults and no recurring paid service. GPU, cloud, commercial APIs, and hosted models may be optional accelerators, never hidden requirements for core local workflows.
- Do not require Docker or WSL. Provide native setup paths. If containers are offered, they must be optional.
- Do not make the product dependent on one LLM vendor. Keep model/provider integrations behind adapters.
- Build working software, not a landing-page-only shell. UI controls must connect to real functionality.
- Do not use fake progress, fake preview data, fabricated AI scores, simulated exports, or placeholder buttons in a release.
- Maintain a persistent project worklog and update it after every meaningful task or phase. Your execution environment may be ephemeral; the repository must preserve state.
- Make reasonable decisions independently. Ask the user only when a decision is genuinely blocking, destructive, financially consequential, or requires their private credentials/approval.
- Keep the user informed with concise milestone updates, but prioritize implementation over status narration.

---

# 1. PRODUCT DEFINITION

ClipForge is an **agent-first, local-first video clipping and short-form production studio**. Its purpose is to turn long-form source videos into a set of compelling, properly timed, visually polished, captioned, translated, export-ready vertical clips with minimal manual effort.

It should serve two audiences:

### A. Human creator / operator
A creator can open the application, import a video, inspect suggested moments, choose clips, edit captions and framing, select a style, render, review, and export.

### B. AI agent / automation operator
An AI agent can install or inspect ClipForge, understand its capabilities from machine-readable documentation, submit a source, request moment discovery, review evidence, correct subtitles, translate, render, inspect outputs, and retrieve deliverables through stable interfaces.

The agent interface is a first-class product surface, not an afterthought.

## Definition of done

A user can install ClipForge on a supported desktop operating system, import a local video, run analysis, receive ranked candidate moments with evidence and timestamps, select or adjust clips, generate or correct captions, translate captions to English by default when appropriate, style captions with built-in fonts, reframe to vertical, render valid video files, inspect the results, and export a clean deliverables package.

The same workflow must be callable through a CLI and a documented agent interface. A feature is not complete merely because a screen or endpoint exists; it must work end-to-end and be tested.

---

# 2. SOURCE-OF-TRUTH INPUTS AND REFERENCE PROJECTS

Inspect these sources directly. Read their READMEs, source trees, dependency manifests, licenses, tests, release history, and relevant implementation files. Do not infer functionality from project names or screenshots.

## Required references

1. **SupoClip** — https://github.com/FujiwaraChoki/supoclip  
   Research its clipping workflow, animated captions, visual presentation, and implementation details.

2. **PeakCut** — https://github.com/haziqahmedqasmi/PeakCut  
   Research its moment-selection and clipping logic. The owner explicitly wants PeakCut's approach combined with SupoClip's approach to improve the selection of vital moments.

3. **Perfect SRT** — https://github.com/superz1402/perfect-srt  
   Research its subtitle correction workflow, line/section handling, terminology, and reusable logic. Integrate or adapt its capabilities where technically and legally appropriate.

4. **Lemo Opuscar** — https://github.com/lemomo-ai/lemo-opuscar  
   Research its agent-first installation, workflow, documentation, maintenance model, and the way it makes software understandable and operable by agents. Use it as a reference for the operational experience, not as a reason to copy unrelated code.

5. **Openclip** — https://github.com/aionixOS/Openclip  
   Evaluate it as a research candidate. Record what is useful, what is not, and why.

6. **OpenShorts** — https://github.com/mutonby/openshorts  
   Evaluate it as a research candidate. Record what is useful, what is not, and why.

7. **Existing ClipForge** — https://github.com/superz1402/clipforge  
   This repository is the project to improve. Inspect it first and preserve working behavior.

## Research requirements

Create and maintain:
- `docs/research/REFERENCE_PROJECT_AUDIT.md`
- `docs/research/FEATURE_COMPARISON_MATRIX.md`
- `docs/research/LICENSE_AND_ATTRIBUTION_AUDIT.md`
- `docs/architecture/ARCHITECTURE_DECISIONS.md`

For every reference, document:
- Repository URL and inspected commit/release.
- License and compatibility assessment.
- Actual features verified in code.
- Useful algorithms, UX patterns, data structures, or workflows.
- Dependencies and operational constraints.
- What can be reused, what must be independently implemented, and what should not be adopted.
- Tests or evidence supporting the assessment.

**Do not blindly combine repositories.** Avoid dependency conflicts, duplicate engines, unmaintained packages, incompatible licenses, and code copied without attribution. Prefer modular adapters and clean interfaces.

## Explicit product requirements from the owner

- Combine the strongest moment-selection ideas from **both SupoClip and PeakCut**. This is a central product requirement.
- Integrate the subtitle correction and line/section repair capabilities represented by **Perfect SRT**.
- Provide a broad built-in font library that is available automatically after installation. Users must not need to manually download ordinary built-in fonts.
- Also support importing custom fonts, subject to validation and licensing/user responsibility.
- Support translation, with English as the default target language for non-English speech.
- Particularly handle Korean, Thai, Japanese, Chinese, and mixed-language speech. Do not assume one language per entire video.
- Deliver a complete workflow, not a disconnected set of utilities.
- Build an attractive, professional, useful application and a public-facing project showcase.
- Make the project installable and understandable by different AI agents and coding environments through documented, stable interfaces. Do not claim universal compatibility without testing each adapter.

---

# 3. FIRST PHASE: INSPECT SUPER Z'S ACTUAL POWERS

Before implementation, use the attached **Super Z: The Complete Capabilities Guide (Version 2026)** as the source for the Super Z capability inventory. Preserve its terminology and map its capabilities to this project.

The guide describes the following capability areas. Treat these as documented capabilities, then verify which are enabled in the current runtime before relying on them.

## 3.1 Intelligence and orchestration
- GLM foundation model.
- Task classification and routing engine.
- Multi-agent orchestration with specialist agents.
- Shared worklog for coordination.
- Planning, exploration, frontend styling, full-stack development, and synthesis.

Use parallel agents for independent research or implementation tasks when available. The main agent remains accountable for architecture, integration, decisions, and final verification. Define interfaces before delegating to avoid incompatible parallel changes.

## 3.2 Document and report production
The guide describes:
- Word documents using `docx-js`, including structured layouts, cover pages, tables of contents, typography, headers/footers, and post-processing checks.
- PDF production using ReportLab, design blueprints, LaTeX/Tectonic, and PDF manipulation workflows.
- PowerPoint generation using `python-pptx`.
- Excel workbooks with formulas, validation, charts, and multiple sheets.

Use these abilities to generate professional project documentation, comparison matrices, QA reports, release notes, and (where useful) business-facing reports. Do not create documents merely to appear productive.

## 3.3 Web development
The guide describes full-stack web application work with:
- Next.js 16
- TypeScript
- Tailwind CSS 4
- shadcn/ui
- Prisma
- API routes, server logic, database operations, WebSockets, and integrated test/fix cycles.

Inspect the current ClipForge stack before choosing whether to retain it or migrate. Do not force Next.js into a desktop/media application if the existing architecture is better. If using this stack for the web interface, keep media processing in a robust local backend/service.

## 3.4 Data visualization
The guide describes:
- matplotlib and seaborn for statistical charts.
- ECharts and D3.js for interactive visualizations.
- Mermaid and Playwright/CSS for structural diagrams and rendered visuals.

Use these tools for explainable analytics, project diagrams, selection evidence, and operational dashboards when appropriate.

## 3.5 AI and media
The guide describes:
- LLM chat and context management.
- Image generation and editing.
- Vision-language model image understanding.
- Speech-to-text (ASR).
- Text-to-speech (TTS).
- Video understanding and temporal scene analysis.

Map these to ClipForge:
- LLM: semantic moment ranking, explanations, script/context analysis, and agent interactions.
- VLM: scene/frame understanding, subject/context analysis, and visual evidence.
- ASR: source transcription and word/segment timestamps.
- TTS: optional voiceover/dubbing workflow, not a mandatory part of core clipping.
- Video understanding: scene changes, visual context, motion, speaker/subject continuity, and shot analysis.
- Image generation/editing: optional thumbnails and design assets; never fabricate source-video evidence.

Use actual provider SDK/API documentation and validate model limits, formats, latency, and pricing. The guide mentions `z-ai-web-dev-sdk`; inspect the installed SDK and its actual supported endpoints rather than assuming it provides every operation required.

## 3.6 Web intelligence and browser automation
The guide describes:
- Real-time web search.
- Web-page extraction.
- Browser automation through a Rust-based headless CLI with a Node.js fallback.
- Image search with hosted image URLs.

Use these for research, repository audits, documentation, and optional online-source ingestion. Do not use browser automation to bypass authentication, DRM, paywalls, access restrictions, or platform protections. Respect source-site terms and copyright.

## 3.7 Software engineering and filesystem
The guide describes:
- Multi-language code reading, writing, editing, debugging, optimization, and testing.
- Python, JavaScript/TypeScript, Bash, Git, and other languages.
- Shell execution, package installation, filesystem access, glob and regex search.
- Persisting scripts to disk before execution.

Use reproducible scripts and checked-in configuration. Avoid destructive commands. Keep temporary media, caches, generated output, and user source files in clearly separated directories.

## 3.8 Quality assurance and workflow management
The guide describes:
- Structured task plans and live todo tracking.
- Multi-layer verification.
- Automated post-generation checks.
- Iterative self-review and correction.
- Mandatory read/outline/generate/verify workflows for documents.

Apply the same discipline to software and media:
1. Inspect.
2. Plan.
3. Implement.
4. Run tests.
5. Inspect actual rendered outputs.
6. Fix.
7. Re-run.
8. Record evidence.

## 3.9 Scheduling and automation
The guide describes cron-style scheduling, fixed-rate intervals, timezone handling, and a minimum five-minute interval. Treat this as an optional capability for scheduled batch jobs, watched folders, and recurring reports. Confirm current runtime support, persistence, and execution guarantees before enabling. Never imply that schedules survive shutdown unless they do.

## 3.10 Capability-to-task mapping deliverable

Create `docs/SUPER_Z_CAPABILITY_MAP.md` with columns:
- Guide capability.
- Runtime availability verified? (yes/no/partial/not tested).
- Evidence/tool/API.
- ClipForge use.
- Fallback.
- Limitations.
- Security/privacy notes.

Do not claim that Super Z's own capabilities are automatically available to end users of ClipForge. ClipForge needs its own provider adapters and local implementations.

---

# 4. REPOSITORY AUDIT AND SAFE BASELINE

1. Verify the authenticated GitHub identity and access to `superz1402/clipforge`.
2. Inspect repository tree, branches, tags, open issues/PRs, latest commits, README, license, package manifests, build scripts, tests, CI, and current release.
3. Run the existing project exactly as documented.
4. Record baseline build/test results before changing code.
5. Identify existing architecture, completed features, unfinished work, technical debt, and known bugs.
6. Preserve existing working workflows and public interfaces unless a migration is justified.
7. Create a feature inventory and implementation plan.

Create or update these persistent files:
- `AGENTS.md` — instructions for coding agents working in this repository.
- `PLAN.md` — current roadmap with status and dependencies.
- `WORKLOG.md` — chronological execution record.
- `DECISIONS.md` — architecture and product decisions with rationale.
- `KNOWN_ISSUES.md` — verified issues, reproduction steps, workarounds.
- `RELEASE_CHECKLIST.md` — release gates.
- `docs/` — user, developer, architecture, and agent documentation.

Do not create duplicate files if equivalent files already exist; update the existing source of truth.

---

# 5. TARGET ARCHITECTURE

Choose architecture based on the current repository and actual constraints. The following is a target capability map, not a mandate to rewrite a working codebase.

## 5.1 Recommended separation of concerns

1. **Desktop/local application layer** — project management, media library, timeline, review, settings, render queue.
2. **Application/API layer** — typed operations for projects, assets, analysis, clips, subtitles, render jobs, and exports.
3. **Media engine** — FFmpeg/FFprobe-based probing, trimming, crop/reframe, compositing, subtitle burn-in, audio handling, encoding, validation.
4. **Intelligence layer** — ASR, language identification, translation, semantic analysis, visual analysis, moment ranking, optional LLM reasoning.
5. **Agent interface layer** — CLI, MCP server if feasible, OpenAPI/REST if useful, agent skill files, machine-readable schemas.
6. **Persistence layer** — project metadata, jobs, candidate evidence, transcripts, subtitle revisions, render settings, and output manifests.
7. **Provider adapters** — local and remote ASR, translation, LLM, VLM, and optional TTS providers.

Use stable internal data models so providers can be swapped without rewriting the product.

## 5.2 Local-first principles
- Core import, probing, trimming, rendering, subtitle editing, and export must work locally.
- Do not upload user videos by default.
- Explain exactly what data leaves the device when an optional cloud provider is enabled.
- Provide explicit local/cloud provider settings.
- Support cancellation and cleanup.
- Use CPU-friendly defaults; expose hardware acceleration only when detected and verified.
- Avoid requiring a GPU, Docker, WSL, or paid API for the basic workflow.
- Provide Windows-first setup if repository context indicates Windows as the primary user environment, while keeping macOS/Linux support in the architecture.

## 5.3 Suggested stack (validate before adoption)
- FFmpeg and FFprobe for media processing.
- Python for media/AI orchestration where it fits existing code.
- TypeScript for frontend and agent-facing client libraries where appropriate.
- SQLite for local metadata if a database is needed.
- A typed schema layer for all API contracts.
- Optional FastAPI for a local service.
- Optional MCP server for agent tools.
- Optional Next.js web interface if the existing project is already web-first.

Do not add technology simply because it appears in this prompt. Minimize dependencies and document why each important dependency exists.

---

# 6. CORE WORKFLOW: SOURCE VIDEO TO FINISHED SHORTS

Implement a cohesive workflow with explicit state and recoverability.

## Stage 1 — Import and inspect
Support:
- Local video files.
- Batch local files.
- Common formats including MP4, MOV, MKV, and WebM where supported by FFmpeg.
- Audio-only files where useful for transcription and analysis.
- Authorized URLs only, subject to source terms and platform restrictions.

On import:
- Probe duration, resolution, frame rate, codecs, audio streams, rotation, aspect ratio, and file size.
- Generate a stable asset ID and metadata record.
- Detect corrupt or unsupported inputs and explain the issue.
- Create lightweight proxies/thumbnails when useful.
- Never modify the original source file.

## Stage 2 — Analyze the source
Run independent analysis passes that can be enabled/disabled:
- Audio extraction and normalization.
- Speech recognition with timestamps.
- Language identification at segment level.
- Speaker diarization where available and useful.
- Scene/shot boundary detection.
- Visual frame sampling and scene understanding.
- Audio event and energy analysis.
- Silence and pause detection.
- Transcript segmentation and semantic analysis.
- Topic, entity, and narrative-context extraction.

Persist intermediate artifacts so a failed later stage does not require repeating all analysis.

## Stage 3 — Discover vital moments
This is one of the most important differentiators. Do not simply divide a video into equal chunks, select loud sections, or choose the first few transcript paragraphs.

Build a **multi-signal moment discovery engine** combining the verified and legally usable approaches learned from SupoClip and PeakCut.

### Candidate evidence signals
- Semantic completeness: does the excerpt communicate a coherent idea?
- Hook strength: does the opening create curiosity or immediate relevance?
- Emotional intensity: excitement, surprise, humor, tension, sincerity, or other meaningful emotion.
- Audio dynamics: emphasis, vocal energy, meaningful pauses, laughter, audience response, music transitions.
- Visual dynamics: scene changes, motion, gestures, subject visibility, relevant visual events.
- Narrative value: setup/payoff, reveal, punchline, strong opinion, useful explanation, surprising fact.
- Standalone comprehensibility: can a viewer understand the clip without the entire source?
- Ending quality: does it land cleanly, resolve, or invite a response?
- Duration suitability for selected platform and user settings.
- Transcript confidence and timestamp confidence.
- Redundancy relative to other candidate clips.
- Context risk: does the excerpt become misleading when removed from its original context?

### Candidate-generation and ranking process
1. Generate multiple overlapping candidate windows from transcript segments, sentence/section boundaries, scene boundaries, and audio/visual events.
2. Preserve enough pre-context and post-context to evaluate the excerpt.
3. Use more than one discovery strategy where possible, reflecting both reference projects' strengths.
4. Normalize evidence scores so one signal does not dominate merely due to scale.
5. Rank candidates with explainable sub-scores and evidence.
6. Detect duplicate or highly overlapping candidates.
7. Merge or adjust boundaries where the combined moment is stronger.
8. Penalize clips that start mid-sentence, cut a key noun/name, lose necessary context, or end before the payoff.
9. Generate multiple duration variants when sensible.
10. Allow the user/agent to set target count, duration range, content tone, and platform.
11. Return a ranked list with start/end timestamps, title suggestion, transcript excerpt, score breakdown, reason for selection, and warnings.
12. Keep human/agent override possible at every step.

### Selection output schema
Each candidate should include:
- `candidate_id`
- `source_asset_id`
- `start_ms`, `end_ms`, `duration_ms`
- `rank`
- `overall_score`
- `score_components`
- `transcript_excerpt`
- `detected_language_segments`
- `hook_summary`
- `why_it_works`
- `context_summary`
- `boundary_confidence`
- `transcription_confidence`
- `visual_evidence_refs`
- `audio_evidence_refs`
- `risk_flags`
- `suggested_title`
- `suggested_caption`
- `review_status`

Do not invent numerical confidence. If a model does not return calibrated confidence, label the score as a heuristic ranking score and explain its basis.

### Moment-selection acceptance criteria
- Candidates are grounded in real source timestamps.
- The user can inspect why each clip was selected.
- Multiple strong moments can be found in long videos.
- The system does not repeatedly return near-identical moments.
- The chosen boundaries preserve meaning.
- A low-confidence result is marked for review rather than presented as certain.
- A test corpus includes varied speech styles, silence, music, dialogue, interviews, podcasts, and non-English content.

---

# 7. MULTILINGUAL ASR, LANGUAGE DETECTION, AND TRANSLATION

The owner's explicit requirement is that non-English content should be automatically detected and translated into English captions by default.

## Required languages and conditions
At minimum, design and test for:
- Korean
- Thai
- Japanese
- Chinese (identify script/locale when possible)
- English
- Mixed-language speech and code-switching
- Additional languages supported by the chosen providers

Do not assume the entire video uses one language. Detect language per segment or smaller meaningful region where supported.

## Required behavior
1. Transcribe the original speech in its original language.
2. Preserve the original transcript and its timestamps.
3. Identify language per segment and preserve code-switching.
4. Translate into English by default when the source is not English.
5. Allow the user to select another target language or turn translation off.
6. Provide side-by-side original and translated text in the editor.
7. Preserve meaning, names, honorifics, slang, idioms, humor, and technical terms.
8. Avoid literal translations that sound unnatural.
9. Use neighboring transcript context to resolve ambiguity.
10. Maintain a project glossary for people, brands, places, fandom terms, product names, and recurring vocabulary.
11. Mark uncertain names or ambiguous phrases for review.
12. Never silently replace the original transcript with translated text.
13. Support subtitle export in original language, translated language, or bilingual layout.
14. Keep timestamps aligned to speech, not merely translated sentence length.

## Translation quality controls
- Preserve meaning and tone.
- Avoid hallucinating words not present in source audio.
- Keep proper nouns consistent.
- Respect line length and reading speed after translation.
- Re-segment translated text where necessary without corrupting original timing.
- Record provider/model and translation revision metadata.
- Provide a correction path for human edits and glossary updates.

## Provider strategy
Implement provider adapters rather than hard-coding a single ASR or translation service. Evaluate:
- Available Super Z ASR capability through the documented SDK/runtime.
- Open-source local ASR options with multilingual coverage.
- Optional hosted ASR/translation providers.
- Offline language identification where practical.

For each provider, document:
- Supported languages.
- Word-level or segment-level timestamp quality.
- Model size and hardware requirements.
- Local/cloud behavior.
- License.
- Pricing/usage limitations if applicable.
- Known weaknesses.

A cloud provider must be optional. Do not claim local offline translation works unless the actual model and language packs are installed and tested.

---

# 8. PERFECT-SRT-STYLE SUBTITLE REPAIR AND EDITING

Integrate the capabilities researched in `superz1402/perfect-srt` where permitted. The product must have a proper subtitle-repair pipeline, not just raw ASR output.

## Repair operations
- Fix punctuation and capitalization.
- Correct sentence boundaries.
- Repair broken lines and awkward line breaks.
- Merge fragments that belong together.
- Split overlong captions into readable units.
- Correct obvious ASR errors using audio/context evidence.
- Preserve names, terminology, and glossary entries.
- Detect repeated or duplicated words.
- Detect missing or overlapping timestamps.
- Detect implausibly short or long caption durations.
- Detect reading-speed problems.
- Align captions to speech.
- Preserve speaker labels when available.
- Preserve original and translated versions separately.
- Allow undo/redo and revision history.

## Subtitle formats
At minimum:
- SRT
- VTT
- ASS/SSA for advanced styling where supported

## Caption data model
Use a stable representation containing:
- Segment ID.
- Start/end time in milliseconds.
- Original text.
- Translated text(s).
- Speaker ID/label if available.
- Language.
- Confidence/evidence metadata where available.
- Style reference.
- Revision/version.
- Manual-lock flag.

## Subtitle editor
Provide:
- Timeline-linked caption list.
- Video preview.
- Direct text editing.
- Split/merge controls.
- Timing adjustment.
- Search/replace.
- Glossary-aware corrections.
- Original/translated view.
- Readability warnings.
- Undo/redo.
- Import/export.
- Clear indication of AI-suggested versus manually edited text.

Never alter user-approved text without an explicit action or a clearly reversible operation.

---

# 9. CAPTION ANIMATION AND TYPOGRAPHY ENGINE

Combine the useful caption presentation and animation patterns discovered in SupoClip with a flexible, reusable styling engine.

## Built-in font library
The application must ship with or automatically provision a broad, curated font library. A normal user must not have to hunt for and manually download fonts to use the built-in styles.

Requirements:
- Bundle or automatically install fonts only when their licenses permit redistribution.
- Include appropriate Latin and multilingual script coverage.
- Ensure Korean, Thai, Japanese, and Chinese glyphs render correctly.
- Provide script-aware fallback stacks.
- Avoid missing-glyph boxes.
- Document each font's source, license, and redistribution terms.
- Make font packs versioned and updateable.
- Provide a font browser with live preview.
- Allow custom TTF/OTF import.
- Validate custom font files and handle invalid fonts safely.
- Do not silently substitute a font without telling the user.

## Caption styling
Provide presets such as:
- Clean minimal
- Bold creator
- Podcast emphasis
- Karaoke/word highlight
- Editorial
- Documentary
- Gaming
- Educational
- Soft subtitle
- High-contrast accessibility

The names are examples; build a coherent, non-generic design system.

## Animation capabilities
Where technically appropriate:
- Word or phrase highlighting.
- Karaoke progression.
- Pop-in/pop-out.
- Scale emphasis.
- Color emphasis.
- Position and entrance transitions.
- Speaker-specific styling.
- Emphasis on selected keywords.
- Controlled motion that does not distract from the video.

Animations must remain readable and not cause clipping, flicker, or timing drift.

## Style editor
Allow adjustment of:
- Font family and weight.
- Font size.
- Fill and highlight colors.
- Stroke/outline.
- Shadow.
- Background plate.
- Alignment and position.
- Safe margins.
- Line spacing.
- Maximum line count.
- Word/phrase emphasis.
- Animation preset and intensity.

Provide a live preview using actual transcript content and real output rendering.

---

# 10. VERTICAL REFRAMING AND VISUAL COMPOSITION

Support common outputs:
- 9:16 vertical (primary).
- 1:1 square.
- 4:5 portrait.
- 16:9 landscape.

For vertical conversion:
- Detect faces/people/primary subjects where possible.
- Track subject position across frames.
- Keep important faces and objects inside the crop.
- Smooth camera movement; avoid jitter.
- Handle multiple speakers and speaker handoffs.
- Use safe margins for platform UI overlays.
- Offer manual crop adjustment and keyframes.
- Provide static center crop as a reliable fallback.
- Detect when the source cannot be reframed cleanly and warn the user.

Do not claim intelligent tracking unless it is implemented and tested on moving subjects.

Optional layout modes:
- Full-frame crop.
- Fit with blurred background.
- Fit with solid/brand background.
- Split-screen or speaker layout only if source analysis can support it.

---

# 11. RENDERING AND EXPORT ENGINE

Use FFmpeg/FFprobe or another justified, reliable media pipeline.

## Render controls
- Output resolution and frame rate.
- Aspect ratio.
- Video codec and quality preset.
- Audio codec/bitrate.
- Caption burn-in or sidecar subtitle.
- Crop/reframe mode.
- Caption preset.
- Start/end adjustment.
- Optional intro/outro or watermark controlled by the user.
- Output naming and destination.
- Batch render.

## Output requirements
- MP4 with broadly compatible H.264/AAC defaults.
- Optional higher-efficiency codecs where supported.
- Correct rotation/orientation.
- Correct duration and audio sync.
- No black frames introduced by processing.
- No accidental source overwrite.
- Deterministic output names.
- Render logs and failure diagnostics.

## Post-render validation
For every output:
1. Confirm file exists and is non-empty.
2. Probe codec, duration, resolution, frame rate, and audio streams.
3. Confirm expected aspect ratio.
4. Check subtitle visibility and safe margins.
5. Inspect representative frames from beginning, middle, and end.
6. Detect black/frozen frames where feasible.
7. Check audio/video duration mismatch.
8. Record validation status in an output manifest.

Do not mark a render complete if validation fails.

---

# 12. THUMBNAILS, TITLES, AND PUBLISHING ASSETS

Generate optional:
- Thumbnail candidates from actual source frames.
- Title suggestions grounded in the clip.
- Description/caption text.
- Hashtag suggestions where relevant.
- Chapter/context notes.
- Platform-specific metadata templates.

Use image generation only for optional graphic elements or backgrounds. Do not fabricate a person, scene, quote, or event and present it as a frame from the source video.

Publishing integrations must respect official APIs and terms. Do not automate platform uploads through brittle browser workarounds or bypass restrictions. If a platform's API is unavailable or restricted, provide a user-controlled export package and clear manual upload instructions.

---

# 13. AGENT-FIRST INTERFACE

ClipForge must be operable by AI agents without requiring them to understand internal source code.

## Required interfaces
Implement and document:
1. **CLI** — stable commands for installation checks, project creation, asset import, analysis, moment discovery, subtitle repair, translation, rendering, validation, and export.
2. **Machine-readable API** — REST/OpenAPI or another suitable typed interface if justified by architecture.
3. **MCP server** — implement if the runtime and dependency ecosystem support it reliably.
4. **Agent skill/instructions** — concise, actionable files that tell agents how to inspect, install, operate, troubleshoot, and verify ClipForge.
5. **Examples** — copy-pasteable workflows and structured request/response samples.

## Suggested agent operations
Names can change to fit existing architecture, but semantics must be clear:
- `clipforge.health_check`
- `clipforge.get_capabilities`
- `clipforge.create_project`
- `clipforge.import_media`
- `clipforge.probe_media`
- `clipforge.analyze_media`
- `clipforge.transcribe`
- `clipforge.detect_languages`
- `clipforge.discover_moments`
- `clipforge.get_candidates`
- `clipforge.review_candidate`
- `clipforge.create_clip`
- `clipforge.reframe_clip`
- `clipforge.repair_subtitles`
- `clipforge.translate_subtitles`
- `clipforge.update_glossary`
- `clipforge.apply_caption_style`
- `clipforge.render_clip`
- `clipforge.validate_output`
- `clipforge.export_project`
- `clipforge.get_job_status`
- `clipforge.cancel_job`

Every operation needs:
- Typed input schema.
- Typed output schema.
- Validation.
- Clear errors.
- Idempotency or safe retry behavior where applicable.
- Job IDs for long-running work.
- Cancellation behavior.
- Progress/state reporting.
- Permission and path safety.

## Agent compatibility
Provide separate setup/integration guides for:
- OpenAI Codex.
- Google Antigravity / Gemini-based coding agents.
- Claude Code, if compatible with the implemented interfaces.
- GLM/Z.ai and Super Z workflows.
- Generic MCP-capable agents.
- Generic CLI-capable agents.

Do not claim that an integration has been tested just because the protocol is theoretically compatible. Label each as:
- Tested.
- Expected compatible, not yet tested.
- Partial.
- Unsupported.

## Agent installation and discovery
An agent should be able to:
1. Detect the operating system and prerequisites.
2. Inspect current installation state.
3. Install or guide installation without destructive assumptions.
4. Run a health check.
5. Read the capability manifest.
6. Execute a sample workflow.
7. Verify outputs.
8. Find troubleshooting guidance.

Create:
- `AGENTS.md`
- `skills/clipforge/SKILL.md` or an equivalent standard agent skill location.
- `docs/agents/README.md`
- `docs/agents/CODEX.md`
- `docs/agents/ANTIGRAVITY.md`
- `docs/agents/CLAUDE_CODE.md`
- `docs/agents/SUPER_Z.md`
- `docs/agents/MCP.md`
- `schemas/capabilities.json`
- `schemas/` for request/response definitions.

Do not invent proprietary integration support. Build around open protocols and documented commands.

---

# 14. HUMAN-FACING APPLICATION EXPERIENCE

Design a professional media workstation, not a generic AI dashboard.

## Main workspaces
- Home / recent projects.
- Project workspace.
- Media bin.
- Analysis status.
- Moment discovery / candidate review.
- Clip editor and preview.
- Subtitle editor.
- Caption/font style library.
- Render queue.
- Export/deliverables.
- Settings / providers / privacy.
- Logs and diagnostics.

## Candidate review experience
Each candidate card should show:
- A real preview frame or clip preview.
- Start/end/duration.
- Transcript excerpt.
- Selection rationale.
- Score breakdown.
- Language/translation status.
- Warnings.
- Accept, reject, edit boundaries, and preview actions.

## Render queue
Show:
- Job state.
- Progress only when measurable.
- Current stage.
- Elapsed time.
- Cancel/retry where safe.
- Logs and error details.
- Output location when complete.

## UI quality bar
- Responsive layouts.
- Clear hierarchy and typography.
- Keyboard accessibility.
- Useful empty/loading/error states.
- No fake buttons.
- No fake metrics.
- No excessive decoration.
- Consistent design tokens.
- Real previews from actual media.
- No unexplained technical jargon in creator-facing flows.

Use Super Z's documented design system as a design resource: mood-driven color choices based on temperature, weight, and energy; its described library of 50+ design styles; and consistent styling across app, docs, and showcase. Choose one coherent visual direction rather than mixing styles.

---

# 15. PROJECT / CLIENT / BUSINESS WORKFLOWS

The product should be capable of supporting a small clipping service or content agency, not just one-off personal editing.

Where appropriate, support:
- Multiple projects.
- Client/workspace labels.
- Batch source processing.
- Reusable brand/caption presets.
- Project glossary.
- Approval states.
- Versioned outputs.
- Deliverables checklist.
- Export folders per client/project.
- A metadata sheet for each batch.
- CSV/XLSX reporting for source, candidate, render, and delivery status.

Keep this practical and local-first. Do not build unnecessary CRM, billing, or user-account systems before the core clipping workflow is reliable.

---

# 16. DATA MODEL, STORAGE, AND RECOVERY

Define and document entities for:
- Project
- SourceAsset
- AnalysisRun
- Transcript
- TranscriptSegment
- GlossaryEntry
- CandidateMoment
- Clip
- SubtitleTrack
- SubtitleRevision
- CaptionStyle
- RenderJob
- RenderOutput
- ExportPackage
- ProviderConfiguration (without storing raw secrets in ordinary records)

Requirements:
- Stable IDs.
- Timestamps in a consistent format, preferably integer milliseconds internally.
- Schema migrations.
- Safe recovery after interruption.
- Atomic writes where possible.
- Clear separation of source, cache, project metadata, and output.
- Ability to rerun failed stages without destroying successful intermediate work.
- Project export/import or backup strategy.
- No secrets in project exports by default.

---

# 17. SECURITY, PRIVACY, AND RESPONSIBLE USE

- Treat all source media, subtitles, metadata, and URLs as untrusted input.
- Validate file paths and prevent path traversal.
- Avoid shell injection; use safe process APIs and argument arrays.
- Limit resource use for untrusted media.
- Do not execute code embedded in media or metadata.
- Keep secrets out of logs, screenshots, and generated docs.
- Provide explicit consent before external upload or publishing.
- Do not bypass DRM, access controls, paywalls, or platform restrictions.
- Document copyright and source-content responsibility.
- Respect font, model, and code licenses.
- Use least privilege for browser and filesystem operations.
- Provide clear data retention and cache deletion controls.
- Do not transmit private source content to cloud models without user choice.

---

# 18. PERFORMANCE AND RELIABILITY

Measure rather than guess.

- Probe media without loading entire files into memory.
- Use streaming/chunked processing where practical.
- Cache intermediate analysis.
- Allow analysis and render jobs to resume or fail safely.
- Bound concurrency based on CPU/RAM.
- Offer low-resource mode.
- Detect available hardware acceleration and verify actual use.
- Avoid spawning too many heavyweight model processes.
- Make model downloads optional and explicit.
- Show expected storage requirements before large downloads.
- Ensure UI remains responsive during long-running tasks.
- Provide cancellation and cleanup.
- Capture actionable diagnostics.

Create a performance test report with representative media sizes and hardware profiles. Do not publish fabricated speed claims.

---

# 19. TESTING AND ACCEPTANCE GATES

Build tests at multiple levels.

## Unit tests
- Timestamp conversion and clipping boundaries.
- Candidate scoring and deduplication.
- Subtitle split/merge and line wrapping.
- Translation data preservation.
- Font discovery and fallback.
- Crop/reframe math.
- File naming and path validation.
- API schema validation.
- Job state transitions.

## Integration tests
- FFmpeg probe and trim.
- ASR adapter.
- Language detection.
- Translation adapter.
- Subtitle export.
- Caption rendering.
- Vertical reframing.
- Output validation.
- CLI/API/MCP operations.

## End-to-end tests
Use legally usable sample media or generated test fixtures. Include:
- English interview/podcast.
- Korean speech.
- Thai speech.
- Japanese speech.
- Chinese speech.
- Mixed-language/code-switching sample.
- Multiple speakers.
- Music and noisy audio.
- Rapid dialogue.
- Long pauses.
- Vertical and landscape source videos.
- Face/subject moving across frame.
- Video with no clear face.
- Video with poor audio.

For each test, preserve expected transcripts or manually reviewed ground truth where feasible. Record known limitations honestly.

## Visual QA
Inspect actual rendered output frames and play the generated files. Check:
- Captions are legible.
- Correct glyphs render for each script.
- No text is cut off.
- No face/subject is cropped incorrectly.
- Timing is synchronized.
- No audio is missing.
- No blank or corrupt output.
- The clip begins and ends naturally.

## Release gates
Do not declare a release until:
- Clean installation works on at least one supported OS.
- Existing tests pass or regressions are documented.
- Core import-to-export workflow works.
- Candidate selection is grounded in source timestamps.
- Subtitle repair works.
- Translation behavior is verified for the languages claimed.
- Font fallback and custom font import are tested.
- CLI workflow works.
- Agent interface works for at least one real agent/client.
- Output validation passes.
- Documentation matches the actual implementation.
- License and security audits are complete.

---

# 20. DOCUMENTATION AND SHOWCASE WEBSITE

Produce documentation that allows both a person and an AI agent to succeed without asking the author basic setup questions.

## Required docs
- `README.md` — product overview, screenshots, quick start, supported platforms, feature status.
- `docs/INSTALLATION.md` — prerequisites and installation per OS.
- `docs/QUICK_START.md` — first source-to-Short workflow.
- `docs/USER_GUIDE.md` — complete application guide.
- `docs/AGENT_GUIDE.md` — agent-first usage.
- `docs/CLI_REFERENCE.md`
- `docs/API_REFERENCE.md`
- `docs/MCP_REFERENCE.md` if implemented.
- `docs/PROVIDERS.md` — local/cloud provider setup, limitations, privacy.
- `docs/FONTS_AND_LICENSES.md`
- `docs/TROUBLESHOOTING.md`
- `docs/FAQ.md`
- `docs/ARCHITECTURE.md`
- `docs/CONTRIBUTING.md`
- `CHANGELOG.md`
- `LICENSE` (choose a suitable OSI-approved license only after checking existing project license and owner intent).

## Public showcase
Build a polished landing page for ClipForge, preferably in the existing project's deployment approach.

It must include:
- Clear value proposition.
- Real feature explanations.
- Workflow overview.
- Real application screenshots or genuine rendered demonstrations.
- Moment discovery explanation.
- Multilingual subtitle and translation workflow.
- Caption/font engine.
- Agent-first integration.
- Privacy/local-first positioning, accurately qualified.
- Installation instructions and GitHub link.
- Documentation link.
- Roadmap and current status.
- Contribution information.

Do not invent testimonials, user counts, performance statistics, model accuracy claims, or platform partnerships. Do not use fake UI screenshots. If a feature is not yet implemented, label it as planned rather than showing it as completed.

---

# 21. GITHUB, VERSIONING, AND RELEASE PROCESS

Use `superz1402/clipforge` as the working repository unless inspection shows the project has already been intentionally moved. Publish under the requested owner/account `bilal140202` only after verifying authenticated identity and permissions.

- Preserve Git history.
- Use feature branches for substantial work.
- Make focused commits with descriptive messages.
- Never commit secrets, source videos, private user media, large model files, or build caches.
- Add `.gitignore` rules.
- Use GitHub Issues for substantial unresolved work if access permits.
- Add CI for linting, type checking, tests, and builds.
- Add release tags only when release gates pass.
- Use semantic versioning consistently.
- Attach checksums and release notes to downloadable builds where supported.
- Keep a changelog.
- Verify published release assets and links after publishing.

If permissions or credentials are unavailable, complete local work and provide exact commands/steps for the owner. Never claim that GitHub publishing happened when it did not.

---

# 22. IMPLEMENTATION PHASES — EXECUTE IN ORDER, ADAPT TO REPOSITORY

## Phase 0 — Capability and repository reconnaissance
- Read this prompt and the attached Super Z capability guide completely.
- Verify actual Super Z runtime tools.
- Audit ClipForge and all reference projects.
- Record baseline tests.
- Create research and capability maps.
- Produce an implementation plan with dependencies and risk levels.

**Gate:** No implementation assumptions remain undocumented.

## Phase 1 — Architecture and core contracts
- Define data models.
- Define job lifecycle and error model.
- Define provider interfaces.
- Define CLI/API/agent contracts.
- Decide how media processing runs.
- Document migration strategy.

**Gate:** Contracts are stable enough for parallel work.

## Phase 2 — Reliable media foundation
- Import/probe.
- Project persistence.
- FFmpeg trimming and export.
- Job queue and cancellation.
- Output validation.
- Basic UI workflow.

**Gate:** A source can be imported, trimmed, rendered, and validated without AI.

## Phase 3 — Transcription and subtitle foundation
- ASR adapter(s).
- Segment timestamps.
- Language detection.
- Subtitle data model.
- Perfect-SRT-style correction pipeline.
- SRT/VTT/ASS import/export.
- Subtitle editor.

**Gate:** A real speech sample can be transcribed, corrected, edited, and exported.

## Phase 4 — Moment discovery engines
- Implement candidate generation.
- Implement independent evidence signals.
- Incorporate the researched SupoClip and PeakCut ideas.
- Add explainable ranking.
- Add deduplication and boundary refinement.
- Add candidate review UI and agent operations.

**Gate:** On a varied test corpus, the engine returns useful, non-duplicative, contextually coherent candidates with real timestamps and evidence.

## Phase 5 — Translation and multilingual quality
- Segment-level language detection.
- Korean, Thai, Japanese, Chinese and mixed-language tests.
- English-default translation.
- Glossary and terminology.
- Bilingual editing and exports.
- Uncertainty handling.

**Gate:** Language-specific behavior is verified; unsupported cases are clearly disclosed.

## Phase 6 — Caption and font engine
- Built-in licensed font packs.
- Multilingual font fallback.
- Custom font import.
- Style presets.
- Animated captions.
- Actual preview and render integration.

**Gate:** Fonts and captions render correctly in real output files, not just in UI mockups.

## Phase 7 — Smart reframing and creator polish
- Subject detection/tracking.
- Smooth crop.
- Manual correction.
- Aspect ratio presets.
- Thumbnail/title helpers.
- Batch workflows.

**Gate:** Reframing and exports pass visual QA on multiple source types.

## Phase 8 — Agent integrations
- CLI.
- API/OpenAPI if selected.
- MCP if supported.
- Agent skill and guides.
- Capability manifest.
- Test with at least one actual external agent client.

**Gate:** An agent can execute a complete source-to-export workflow and inspect the resulting files.

## Phase 9 — Documentation, showcase, release
- Complete docs.
- Generate genuine screenshots.
- Build showcase.
- CI.
- Security/license review.
- Release package.
- Verify public artifacts.

**Gate:** Release checklist passes with evidence.

Do not wait for every optional feature before making a useful internal milestone. But do not label incomplete work as a finished product.

---

# 23. MULTI-AGENT DELEGATION PLAN

If sub-agents are available, delegate independent work with explicit deliverables and boundaries.

Suggested roles:
1. **Repository auditor** — ClipForge baseline, architecture, tests, risks.
2. **Reference researcher** — SupoClip, PeakCut, Perfect SRT, Lemo Opuscar, Openclip, OpenShorts, licenses.
3. **Media pipeline engineer** — FFmpeg, probing, clipping, rendering, validation.
4. **Moment intelligence engineer** — candidate discovery, scoring, boundaries, deduplication.
5. **Multilingual engineer** — ASR, language detection, translation, glossary.
6. **Subtitle/typography engineer** — repair, line breaking, font packs, animation.
7. **Frontend engineer** — creator workflow UI and visual QA.
8. **Agent integration engineer** — CLI, MCP/API, skill files.
9. **QA/security engineer** — tests, threat model, output inspection, release gates.

Each sub-agent must:
- Read `AGENTS.md`.
- Read relevant architecture contracts.
- Work in a defined area/branch or submit a patch.
- Record findings in the shared worklog.
- Cite code paths and test evidence.
- Avoid editing shared contracts without coordination.

The main agent must integrate and test all contributions. Parallel work does not excuse incompatible code or missing verification.

---

# 24. CONTINUOUS WORKLOG AND RECOVERY

Update `WORKLOG.md` after every meaningful action. Each entry should include:
- Date/time.
- Phase.
- Task performed.
- Files changed.
- Commands/tests run.
- Results.
- Failures and blockers.
- Decisions.
- Next concrete action.

Also maintain:
- `PLAN.md` with status: not started / in progress / blocked / complete.
- `DECISIONS.md` with rationale.
- `KNOWN_ISSUES.md` with reproduction details.
- `docs/research/` with source findings.

At the end of each session:
1. Save all useful work.
2. Commit coherent changes when appropriate.
3. Record the exact next action.
4. Ensure another agent can resume from repository files alone.

Never rely exclusively on conversational memory.

---

# 25. FINAL DELIVERABLES

The final result should include, as applicable to the actual implementation:

### Software
- Working ClipForge application.
- Local media engine.
- Moment discovery engine combining verified SupoClip and PeakCut ideas.
- Multilingual transcription and translation.
- Subtitle repair/editor.
- Built-in font library and custom font support.
- Caption animation and styling.
- Vertical reframing.
- Render queue and validated export.
- CLI.
- API and/or MCP agent interface.
- Agent skill and compatibility guides.
- Tests and CI.

### Documentation and assets
- Full setup and user documentation.
- Architecture and research audits.
- License and attribution report.
- Super Z capability map.
- Agent instructions.
- Genuine screenshots/demos.
- Public showcase website.
- Changelog and release notes.
- Test and QA report.
- XLSX/CSV feature and release matrix if useful.

### Final report to owner
Provide a concise but complete report with:
1. What was already present in ClipForge.
2. What you built.
3. What works end-to-end.
4. What was tested, with exact test commands and results.
5. Which languages were actually tested.
6. Which agent integrations were actually tested.
7. Which features require optional models, credentials, or hardware.
8. Known limitations and unresolved bugs.
9. GitHub branch/commit/PR/release links, only if actually created.
10. Showcase and documentation links, only if deployed and verified.
11. Exact local installation/run instructions.
12. The next highest-value work item.

Never hide incomplete features behind broad claims such as “fully AI-powered” or “supports all languages.”

---

# 26. START NOW — FIRST ACTIONS

Do these actions in order, without asking the owner to repeat the brief:

1. Read the existing ClipForge repository and its current state.
2. Read the attached Super Z capability guide and create the capability-to-task map described above.
3. Verify the actual Super Z runtime tools and credentials available to this session.
4. Audit all six reference repositories and licenses.
5. Record the baseline build and tests.
6. Create/update the persistent project worklog and plan.
7. Present a short evidence-based findings summary and then proceed into implementation. Do not stop after the summary.
8. Implement the smallest complete vertical slice first: import → analyze/transcribe → discover candidate → edit/repair captions → translate when needed → style → render → validate → export.
9. Expand the system in phases, maintaining working software and tests at each gate.
10. Publish only after the release gates pass and permissions are verified.

**The required outcome is a real, usable, maintainable, open-source ClipForge product that turns long-form media into polished short-form deliverables and can be operated by humans or AI agents. Execute the work; do not merely describe how it could be done.**
