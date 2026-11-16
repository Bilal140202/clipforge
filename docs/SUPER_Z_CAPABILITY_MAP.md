# Super Z capability map → ClipForge (Phase 0 deliverable)

Verified 2026-11-16 in the actual runtime. "Verified" = the capability was
executed or its tool was invoked this session; "present" = tool/skill exists
but was not exercised; "absent" = checked and not available.

| Guide capability | Availability | Evidence | ClipForge use | Fallback | Limitations | Security/privacy |
| --- | --- | --- | --- | --- | --- | --- |
| GLM chat / LLM reasoning | verified | `z-ai chat` CLI present; not called this session | moment re-ranking, translation QC, agent ops | local Ollama adapter (upstream) | network + account bound; per-call cost | transcript text would leave the machine → provider setting must stay opt-in |
| ASR (speech-to-text) | verified (local) | faster-whisper 1.2.1 ran e2e on 50s audio; 110 words | core transcription with word timestamps | z-ai `asr` (cloud, untested) | base model download needs HF reachability | local model = audio never leaves device |
| Translation | present (untested here) | argostranslate in requirements; skipped locally (KI-002) | en-default caption translation | z-ai chat-based translation (opt-in) | pulls torch; heavy | Argos = local; cloud fallback must be explicit consent |
| VLM / image understanding | present | `z-ai vision` CLI listed | frame evidence for candidates, thumbnail review | OpenCV heuristics | untested | frames sent to cloud only with consent |
| TTS | verified | `z-ai tts` generated the 50s e2e narration wav | optional voiceover, fixture generation | edge-tts (upstream) | cloud service | synthetic fixtures only; no user data |
| Video understanding | present | `z-ai video` CLI listed | scene/shot analysis for discovery | ffmpeg scene detection | untested | cloud; opt-in |
| Image generation/edit | present | `z-ai image`/`image-edit` listed | optional thumbnails/backgrounds | none | never fabricate source-video evidence | label generated assets |
| Web search / page reading | present | harness skills listed | research, license audits | direct curl/API | — | respect robots/terms |
| Browser automation | present | agent-browser skill listed | UI visual QA screenshots | Playwright install | untested | least-privilege use |
| Document generation (docx/pdf/xlsx/pptx) | present | skills listed | release notes, QA reports | plain markdown | — | — |
| Charts/diagrams | present | charts skill listed | score-breakdown visuals, architecture diagrams | matplotlib | — | — |
| FFmpeg/FFprobe media processing | verified | ffmpeg 7.1.5 executed all cut/reframe/burn stages | core media engine | none needed | CPU-only sandbox | — |
| GitHub API/Actions | verified | fork + issues via REST; Actions workflows exist upstream | CI, releases, task ledger | manual owner runs | token is fork-scoped (no upstream push) | token stays outside repo; rotate after use |
| Scheduling (cron) | present in harness, **non-durable** | cron tool exists but dies with the session | watched-folder batch jobs | GitHub Actions cron (durable) | never claim schedules survive the sandbox | — |
| Persistent background processes | absent | sandbox recycles between turns | long renders | run locally / in Actions | — | — |

Rule (master prompt §3.10): none of these Super Z capabilities are available
to ClipForge end users by default. ClipForge ships its own local provider
adapters; cloud helpers are opt-in, documented in `docs/PROVIDERS.md` (future).
