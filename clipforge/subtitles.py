"""Subtitle I/O and repair gates (clean-room, stdlib only).

Formats: SRT and WebVTT parse/serialize. Gates validate cue lists; the
mechanical repair pass fixes what gates reject (merging, splitting on word
boundaries, overlap clamping) and never invents or rewrites text.

Gates (a cue list passes only when all hold):
  G1 duration:      0.8s <= end-start <= 7.5s
  G2 layout:        <= 2 lines, each <= 42 chars
  G3 timing sanity: start < end, no overlap with the previous cue
  G4 content:       non-empty text after strip
  G5 order:         sorted by start time
"""
import re

MAX_CHARS = 42
MAX_LINES = 2
MIN_DUR_MS = 800
MAX_DUR_MS = 7500

_TS_SRT = re.compile(r"^(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})$")
_TS_VTT = re.compile(r"^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\.(\d{1,3})$")


def parse_ts(ts):
    """Parse SRT or VTT timestamp -> milliseconds."""
    ts = ts.strip()
    m = _TS_SRT.match(ts)
    if m:
        hh, mm, ss, ms = m.groups()
        return ((int(hh) * 60 + int(mm)) * 60 + int(ss)) * 1000 + \
            int(ms.ljust(3, "0"))
    m = _TS_VTT.match(ts)
    if m:
        hh = int(m.group(1)) if m.group(1) else 0
        mm, ss, ms = int(m.group(2)), int(m.group(3)), m.group(4)
        return ((hh * 60 + mm) * 60 + ss) * 1000 + int(ms.ljust(3, "0"))
    raise ValueError(f"bad timestamp {ts!r}")


def fmt_ts(ms, vtt=False):
    ms = max(0, int(ms))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    sep = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _block_ts(line):
    for token in line.replace("-->", " -> ").split("->"):
        pass
    parts = line.split("-->")
    return [p.strip() for p in parts]


def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        if "-->" not in lines[0]:
            lines = lines[1:]  # numeric index line
        if not lines or "-->" not in lines[0]:
            raise ValueError(f"unparseable SRT block: {block[:80]!r}")
        start_s, end_s = _block_ts(lines[0])
        cues.append({"start_ms": parse_ts(start_s),
                     "end_ms": parse_ts(end_s),
                     "text": "\n".join(lines[1:]).strip()})
    return cues


def parse_vtt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        if not lines or lines[0].startswith(("WEBVTT", "NOTE", "STYLE")):
            continue
        idx = 1 if ("-->" not in lines[0] and len(lines) > 1) else 0
        if "-->" not in lines[idx]:
            continue
        start_s, end_s = _block_ts(lines[idx])
        cues.append({"start_ms": parse_ts(start_s),
                     "end_ms": parse_ts(end_s),
                     "text": "\n".join(lines[idx + 1:]).strip()})
    return cues


def serialize_srt(cues):
    out = []
    for i, c in enumerate(cues, 1):
        out.append(f"{i}\n{fmt_ts(c['start_ms'])} --> "
                   f"{fmt_ts(c['end_ms'])}\n{c['text'].strip()}\n")
    return "\n".join(out)


def serialize_vtt(cues):
    out = ["WEBVTT\n"]
    for c in cues:
        out.append(f"{fmt_ts(c['start_ms'], vtt=True)} --> "
                   f"{fmt_ts(c['end_ms'], vtt=True)}\n{c['text'].strip()}\n")
    return "\n".join(out)


def wrap_text(text, max_chars=MAX_CHARS, max_lines=MAX_LINES):
    """Greedy word wrap; None when the text cannot fit the layout gate."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w if len(w) <= max_chars else None
            if cur is None:
                return None
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        return None
    return "\n".join(lines)


def cues_from_transcript(transcript, max_chars=MAX_CHARS,
                         max_dur_ms=MAX_DUR_MS):
    """Build repair-ready cues from a clipforge transcript (words+segments)."""
    segs = transcript.get("segments") or []
    if not segs and transcript.get("words"):
        cur = []
        for w in transcript["words"]:
            cur.append(w)
            if w["text"].rstrip("\"'“”’").endswith((".", "!", "?")):
                segs.append({"start": cur[0]["start"],
                             "end": cur[-1]["end"],
                             "text": " ".join(x["text"] for x in cur)})
                cur = []
        if cur:
            segs.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                         "text": " ".join(x["text"] for x in cur)})
    cues, idx = [], 1
    for s in segs:
        text = (s.get("text") or "").strip()
        if not text:
            continue
        cues.append({"index": idx,
                     "start_ms": int(round(s["start"] * 1000)),
                     "end_ms": int(round(s["end"] * 1000)),
                     "text": text})
        idx += 1
    return cues


def validate(cues):
    """Return {passed, gates, violations} — pure check, no mutation."""
    gates = {"G1_duration": True, "G2_layout": True, "G3_timing": True,
             "G4_content": True, "G5_order": True}
    violations = []
    prev = None
    for c in cues:
        dur = c["end_ms"] - c["start_ms"]
        if not (MIN_DUR_MS <= dur <= MAX_DUR_MS):
            gates["G1_duration"] = False
            violations.append({"index": c.get("index"), "gate": "G1",
                               "detail": f"duration {dur}ms"})
        if c["start_ms"] >= c["end_ms"]:
            gates["G3_timing"] = False
            violations.append({"index": c.get("index"), "gate": "G3",
                               "detail": "start >= end"})
        if prev is not None and c["start_ms"] < prev["end_ms"]:
            gates["G3_timing"] = False
            violations.append({"index": c.get("index"), "gate": "G3",
                               "detail": "overlaps previous cue"})
        if not (c.get("text") or "").strip():
            gates["G4_content"] = False
            violations.append({"index": c.get("index"), "gate": "G4",
                               "detail": "empty text"})
        lines = (c.get("text") or "").split("\n")
        if len(lines) > MAX_LINES or any(
                len(l) > MAX_CHARS for l in lines):
            gates["G2_layout"] = False
            violations.append({"index": c.get("index"), "gate": "G2",
                               "detail": f"{len(lines)} lines, "
                                         f"max {max(map(len, lines))} chars"})
        if prev is not None and c["start_ms"] < prev["start_ms"]:
            gates["G5_order"] = False
            violations.append({"index": c.get("index"), "gate": "G5",
                               "detail": "out of order"})
        prev = c
    return {"passed": all(gates.values()), "gates": gates,
            "violations": violations}


def auto_repair(cues):
    """Mechanical repair. Returns (cues, actions). Text is never rewritten."""
    actions = []
    cues = [dict(c) for c in sorted(cues, key=lambda c: c["start_ms"])]
    # merge too-short cues into the previous neighbour when one exists
    merged = []
    for c in cues:
        if c["end_ms"] - c["start_ms"] < MIN_DUR_MS and merged:
            merged[-1]["text"] = (merged[-1]["text"] + " " + c["text"]).strip()
            merged[-1]["end_ms"] = max(merged[-1]["end_ms"], c["end_ms"])
            actions.append({"action": "merge_short", "at_ms": c["start_ms"]})
        else:
            merged.append(c)
    # a leading short cue has no previous neighbour: merge into the next
    while len(merged) > 1 and \
            merged[0]["end_ms"] - merged[0]["start_ms"] < MIN_DUR_MS:
        merged[1]["start_ms"] = merged[0]["start_ms"]
        merged[1]["text"] = (merged[0]["text"] + " "
                             + merged[1]["text"]).strip()
        actions.append({"action": "merge_short",
                        "at_ms": merged[0]["start_ms"]})
        merged.pop(0)
    # a lone short cue: extend to the minimum duration
    for c in merged:
        if c["end_ms"] - c["start_ms"] < MIN_DUR_MS:
            c["end_ms"] = c["start_ms"] + MIN_DUR_MS
            actions.append({"action": "extend_short", "at_ms": c["start_ms"]})
    # split over-long cues on word boundaries
    split = []
    for c in merged:
        dur = c["end_ms"] - c["start_ms"]
        wrapped = wrap_text(c["text"])
        if dur <= MAX_DUR_MS and wrapped:
            c["text"] = wrapped
            split.append(c)
            continue
        pieces = _split_piece(c, max_dur_ms=MAX_DUR_MS)
        split.extend(pieces)
        if len(pieces) > 1:
            actions.append({"action": "split_long",
                            "at_ms": c["start_ms"],
                            "pieces": len(pieces)})
    # clamp overlaps
    out = []
    for c in split:
        if out and c["start_ms"] < out[-1]["end_ms"]:
            out[-1]["end_ms"] = max(out[-1]["start_ms"] + 1,
                                    c["start_ms"] - 1)
            actions.append({"action": "clamp_overlap",
                            "at_ms": c["start_ms"]})
        out.append(c)
    for i, c in enumerate(out, 1):
        c["index"] = i
    return out, actions


def _split_piece(cue, max_dur_ms=MAX_DUR_MS):
    """Recursively split a cue at word boundaries until every piece fits
    the layout gate (and duration, best effort). Words are never altered."""
    def rec(words, s_ms, e_ms):
        text = " ".join(words)
        wrapped = wrap_text(text)
        if wrapped and (e_ms - s_ms) <= max_dur_ms:
            return [dict(cue, start_ms=s_ms, end_ms=e_ms, text=wrapped)]
        if len(words) == 1:
            return [dict(cue, start_ms=s_ms, end_ms=e_ms, text=wrapped or
                         text)]
        mid = len(words) // 2
        split_ms = s_ms + int((e_ms - s_ms) * mid / len(words))
        return (rec(words[:mid], s_ms, split_ms - 1)
                + rec(words[mid:], split_ms, e_ms))
    return rec(cue["text"].split(), cue["start_ms"], cue["end_ms"])


def clip_window_cues(cues, start_ms, end_ms):
    """Slice cues into [start_ms, end_ms) and shift to clip-local time."""
    out = []
    for c in cues:
        if c["end_ms"] <= start_ms or c["start_ms"] >= end_ms:
            continue
        out.append({"index": 0,
                    "start_ms": max(0, c["start_ms"] - start_ms),
                    "end_ms": min(end_ms, c["end_ms"]) - start_ms,
                    "text": c["text"]})
    for i, c in enumerate(out, 1):
        c["index"] = i
    return out
