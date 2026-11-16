# ClipForge

Local-first, agent-operable short-form video clipping studio. Turn a
long-form video into ranked vertical clips with karaoke captions, a hook
overlay, gated subtitle exports, and optional LLM-translated bilingual
variants — **fully runnable on a CPU laptop, no API keys required** for the
core loop. Cloud LLM providers are optional adapters, never requirements.

```
input video ──► local transcription (faster-whisper, word timestamps)
            ──► multi-signal moment discovery (ranked, explainable candidates)
            ──► cut ──► 9:16 reframe (MediaPipe face-tracked / center fallback)
            ──► karaoke captions + hook (ASS burn)
            ──► subtitle gates (validate/repair, SRT + VTT export)
            ──► optional translation via provider adapter (Ollama local | z-ai)
            ──► bilingual variant render ──► validated artifacts
```

## Status (honest)

| Capability | State |
| --- | --- |
| Transcription (local, word-level) | works, verified |
| Multi-signal discovery + dedup + schema | works (heuristic v1), verified |
| 9:16 reframe (face-tracked / center fallback) | works, verified |
| Karaoke + hook burn | works, verified |
| Subtitle gates + repair (SRT/VTT) | works, unit-tested |
| Provider translation (Ollama/z-ai) + bilingual render | works, verified e2e |
| MCP server, editor UI, font packs | not built (tracked in Issues) |

## Quickstart

```bash
pip install -r requirements.txt
clipforge doctor                                   # environment check
python -m clipforge.cli transcribe --input talk.mp4 --out transcript.json
python -m clipforge.cli discover --transcript transcript.json --audio talk.mp4 --top-n 5
python -m clipforge.cli render --source talk.mp4 --transcript transcript.json \
    --start-ms 0 --end-ms 46000 --hook "Why three hearts?" \
    --translate-lang es --out clip_final.mp4
# or the whole flow at once:
python -m clipforge.pipeline --input talk.mp4 --use-discover --top-n 5 --target-lang es
```

Providers: set `CLIPFORGE_PROVIDER=ollama` (local, default) or `zai`
(the z-ai CLI), or pass `--provider`. Translation is optional and skipped
with a clear message when no provider exists. Cloud providers receive
transcript text — that is an explicit choice, documented in
`docs/SUPER_Z_CAPABILITY_MAP.md`.

## Tests

```bash
python -m pytest tests/ -q     # no network, no models, < 2s
```

## Repository docs

- `docs/research/` — reference-project audits, feature matrix, license rules
- `docs/ui-research/` — UI playbook, design system, component catalog, QA checklist
- `docs/SUPER_Z_CAPABILITY_MAP.md` — what the host runtime provides vs. what ClipForge ships
- `PLAN.md` / `WORKLOG.md` / `DECISIONS.md` / `KNOWN_ISSUES.md` / `RELEASE_CHECKLIST.md`

## License

MIT. See `docs/research/LICENSE_AND_ATTRIBUTION_AUDIT.md` before importing
third-party ideas: AGPL and unlicensed sources require clean-room
reimplementation.
