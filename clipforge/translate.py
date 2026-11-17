"""Provider-based caption translation.

Translates subtitle cues through the selected LLM provider (z-ai or Ollama)
in batched, schema-constrained calls. The provider never changes cue timing;
only text is translated. When no provider is available, translation is
honestly skipped (the pipeline stays fully local and key-free otherwise).
"""
from . import providers

SYSTEM = (
    "You are a professional subtitle translator. You translate numbered "
    "subtitle cues into the requested language. You keep the same number of "
    "cues, preserve meaning and tone, keep each translation short enough to "
    "fit two lines of 42 characters, and you answer with JSON only."
)


def _chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size], i


def translate_cues(cues, target_lang, provider, chunk_size=30,
                   source_lang=None):
    """Translate cues -> [{index, start_ms, end_ms, source, target}].

    Raises RuntimeError on provider failure (caller decides whether
    translation is optional). On a per-chunk count mismatch the chunk is
    aligned by index when possible, else the chunk fails loudly.
    """
    if provider is None:
        raise RuntimeError("no LLM provider available for translation")
    results = []
    for chunk, offset in _chunks(cues, chunk_size):
        payload = [{"i": c["index"], "text": c["text"]} for c in chunk]
        src = f" (source language: {source_lang})" if source_lang else ""
        prompt = (
            f"Translate these subtitle cues into {target_lang}{src}.\n"
            f"Return JSON only: {{\"translations\": [{{\"i\": <cue index>, "
            f"\"text\": \"<translation>\"}}]}} with exactly {len(chunk)} "
            f"entries, same order, same i values.\n\n"
            + "\n".join(f"{c['index']}: {c['text'].replace(chr(10), ' ')}"
                        for c in chunk)
        )
        reply = provider.complete(prompt, system=SYSTEM)
        data = providers.extract_json(reply)
        items = data.get("translations") if isinstance(data, dict) else data
        if not isinstance(items, list) or len(items) != len(chunk):
            raise RuntimeError(
                f"provider returned {len(items) if isinstance(items, list) else '?'}"
                f" translations for {len(chunk)} cues")
        by_i = {it.get("i"): (it.get("text") or "") for it in items
                if isinstance(it, dict)}
        for c in chunk:
            t = by_i.get(c["index"])
            if not isinstance(t, str):
                raise RuntimeError(f"missing translation for cue "
                                   f"{c['index']} (keys: {list(by_i)})")
            results.append({"index": c["index"],
                            "start_ms": c["start_ms"],
                            "end_ms": c["end_ms"],
                            "source": c["text"],
                            "target": t.strip()})
    return results


def _fit_subtitle(text, width=42, max_lines=2):
    """Fit a translated cue to the layout gate: <=max_lines lines of
    <=width chars. Word-wraps for spaced scripts; hard-slices for
    spaceless ones (CJK); overlong text is truncated with an ellipsis
    rather than violating the caption layout (G2)."""
    t = " ".join((text or "").split()).strip()
    if len(t) <= width:
        return t
    if " " in t:
        lines, cur = [], ""
        for w in t.split():
            cand = f"{cur} {w}".strip()
            if len(cand) <= width:
                cur = cand
            else:
                lines.append(cur)
                cur = w if len(w) <= width else w[:width]
            if len(lines) == max_lines:
                break
        if cur:
            if len(lines) < max_lines:
                lines.append(cur)
            elif not lines[max_lines - 1].endswith("…"):
                lines[max_lines - 1] = \
                    lines[max_lines - 1][:width - 1].rstrip() + "…"
        return "\n".join(lines[:max_lines])
    return "\n".join(t[i * width:(i + 1) * width][:width - 1]
                     if (i + 1) * width <= len(t) and i + 1 < max_lines
                     else t[i * width:(i + 1) * width]
                     for i in range(max_lines))[:2 * width]


def write_translated(cues_translated, srt_path, vtt_path=None):
    from . import subtitles
    t_cues = [{"index": t["index"], "start_ms": t["start_ms"],
               "end_ms": t["end_ms"], "text": _fit_subtitle(t["target"])}
              for t in cues_translated]
    with open(srt_path, "w") as f:
        f.write(subtitles.serialize_srt(t_cues))
    if vtt_path:
        with open(vtt_path, "w") as f:
            f.write(subtitles.serialize_vtt(t_cues))
    return t_cues
