# ClipForge

**Local-first, agent-operable short-form video clipping studio.** Turn a
long-form video into ranked vertical clips with karaoke captions, a hook
overlay, gated subtitle exports, and provider-translated captions —
**fully runnable on a CPU laptop, no API keys required** for the core
loop. Cloud LLM providers are optional adapters, never requirements.

```
input video ──► local transcription (faster-whisper, word timestamps)
            ──► multi-signal moment discovery (ranked, explainable candidates)
            ──► cut ──► 9:16 reframe (MediaPipe face-tracked / center fallback)
            ──► captions decided by the permanent language rule (#17)
            ──► karaoke captions + hook (ASS burn)
            ──► subtitle gates (validate/repair, SRT + VTT export)
            ──► provider translation when the rule says so (Ollama | z-ai)
            ──► validated artifacts
```

## ⚖️ The permanent caption-language rule (#17)

This rule is **permanent and has no exceptions**. It lives in
`clipforge/langrule.py` as one pure function, is wired into BOTH the
`render` command and the legacy `pipeline`, and cannot be bypassed by
any flag combination.

> If the video's speech is in a different language than the captions
> being made, the user is ASKED: **same-language captions, or English?**
> If the user chooses English, the output is **FULL ENGLISH ONLY** —
> no source-language karaoke, no bilingual stack, not even a
> source-language hook. One caption, one language.

| Video's language | Requested captions | What happens |
| --- | --- | --- |
| Korean | *(none given)* | Korean karaoke captions (same-language default) |
| Korean | Korean | Korean karaoke captions |
| Korean | **English** | **English-only enforced**: translated cues + English hook; `--caption-mode bilingual` is overridden with a loud note |
| Korean | Spanish | the tool ASKS: Korean or English? (TTY prompt; agents get exit code 2 + the exact question to relay) |
| unknown | English | English-only enforced (noted) |
| unknown | Spanish | the tool ASKS |
| English | Korean | English captions (video is already English; no ask needed) |

Plain words for a kid: *the video talks in one language. You can keep
that language on screen, or switch everything to English — but you can
never show both, and you can never mix them.*

## Status (honest)

| Capability | State |
| --- | --- |
| Transcription (local, word-level) | works, verified |
| Multi-signal discovery + dedup + schema | works (heuristic v1), verified |
| 9:16 reframe (face-tracked / center fallback) | works, verified |
| Karaoke + hook burn | works, verified |
| Subtitle gates + repair (SRT/VTT) | works, unit-tested |
| Permanent language rule (#17) incl. hook translation | works, unit-tested + verified e2e on owner footage |
| English-only caption mode (#16) + G2 fit enforcement | works, verified e2e |
| Provider translation (Ollama/z-ai) | works, verified e2e |
| MCP server, editor UI, font packs | not built (tracked in Issues) |

## Quickstart

```bash
pip install -r requirements.txt
clipforge doctor                                   # environment check
python -m clipforge.cli transcribe --input talk.mp4 --out transcript.json
python -m clipforge.cli discover --transcript transcript.json --audio talk.mp4 --top-n 5

# same-language captions (the video's own language):
python -m clipforge.cli render --source talk.mp4 --transcript transcript.json \
    --start-ms 0 --end-ms 46000 --hook "Why three hearts?" --out clip_final.mp4

# FULL English only (rule #17 decides; --caption-mode is overridden):
python -m clipforge.cli render --source talk.mp4 --transcript transcript.json \
    --start-ms 0 --end-ms 46000 --hook "Por qué tres corazones?" \
    --caption-lang en --out clip_final.mp4

# or the whole flow at once:
python -m clipforge.pipeline --input talk.mp4 --use-discover --top-n 5 --target-lang en
```

When the rule needs a human decision and no human is attached (scripts,
CI, agents), the command **exits with code 2** and prints the exact
question plus both choices, so any agent can relay it to the user and
re-run with `--caption-lang` set.

## CLI reference (render)

| Flag | Meaning |
| --- | --- |
| `--source` | input video file |
| `--transcript` | transcript JSON from `transcribe` |
| `--start-ms` / `--end-ms` | the window to cut |
| `--hook` | the hook overlay line (translated automatically when English-only) |
| `--caption-lang` | rule #17: omit = video's language; `en` = full English only; anything else asks |
| `--caption-mode` | legacy knob; the rule overrides it whenever English is chosen |
| `--translate-lang` | old spelling of `--caption-lang` (still accepted) |
| `--provider` | `ollama` (local, default) or `zai` |
| `--out` / `--workdir` | output clip + scratch dir |

## The caption gates

Every exported subtitle file must pass three gates before ClipForge
calls it done — `clipforge subtitles validate` re-checks any file:

- **G1 duration** — no cue flashes by faster than a readable minimum or
  lingers absurdly long.
- **G2 layout** — at most 2 lines, each ≤ 42 characters. Translations
  are force-fitted (`translate._fit_subtitle`: word-wrap, hard-slice for
  spaceless scripts, ellipsis cap) so the gate can never be violated.
- **G3 timing** — no overlaps, cues ordered, inside the clip window.

## Providers

Set `CLIPFORGE_PROVIDER=ollama` (local, default) or `zai` (the z-ai
CLI), or pass `--provider`. Translation is optional and skipped with a
clear message when no provider exists — **except** on an English-only
clip, where a missing or failing provider is a hard error: the permanent
rule forbids silently falling back to source-language captions. Cloud
providers receive transcript text — that is an explicit choice,
documented in `docs/SUPER_Z_CAPABILITY_MAP.md`.

## Tests

```bash
python -m pytest tests/ -q     # no network, no models, < 2s
```

69 tests cover the rule decision table, gate math, caption builders,
translation fitting, discovery schema, and repair logic. The rule's
tests live in `tests/test_langrule.py` — change `langrule.py` and that
file in the same commit.

## Repository docs

- `docs/research/` — reference-project audits, feature matrix, license rules
- `docs/ui-research/` — UI playbook, design system, component catalog, QA checklist
- `docs/SUPER_Z_CAPABILITY_MAP.md` — what the host runtime provides vs. what ClipForge ships
- `PLAN.md` / `WORKLOG.md` / `DECISIONS.md` / `KNOWN_ISSUES.md` / `RELEASE_CHECKLIST.md`
- `CHANGELOG.md` — what shipped, when, and why

## FAQ

**Why can't I get bilingual captions anymore?**
The owner made it a permanent rule (#17): one caption, one language.
Bilingual stacks are exactly what the rule forbids. The `--caption-mode`
flag still exists so old scripts don't break, but the rule overrides it
and says so loudly in the output.

**Why did my render exit with code 2?**
The rule needed a human choice (the video's language and your requested
caption language didn't match, and it wasn't English). Re-run with
`--caption-lang <video-language>` or `--caption-lang en`.

**Why is the hook also translated?**
Because "full English only" means nothing in the source language is on
screen — including the hook. If the hook translation fails, the render
fails; it never falls back to the original hook.

**Does transcription or the rule need the network?**
No. faster-whisper runs locally; the rule is a pure function. Only the
optional translation step talks to a provider.

## License

MIT. See `docs/research/LICENSE_AND_ATTRIBUTION_AUDIT.md` before importing
third-party ideas: AGPL and unlicensed sources require clean-room
reimplementation.
