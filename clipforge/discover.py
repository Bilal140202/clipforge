"""Multi-signal moment discovery engine.

Generates overlapping candidate windows from transcript sentence
boundaries and (optionally) audio-energy peaks, scores them with
explainable heuristic sub-scores, deduplicates overlapping candidates,
and returns a ranked list.

Design provenance (see docs/research/REFERENCE_PROJECT_AUDIT.md):
- Sentence-boundary candidate windows, mechanical boundary snapping and
  overlap dedup follow the general approach verified in PeakCut (MIT).
- Multi-signal scoring with hook/completeness-style sub-scores is a
  clean-room reimplementation of ideas studied in SupoClip (AGPL). No
  SupoClip code or prompt text is used.
- Every score is a heuristic. These are NOT calibrated model
  confidences; candidates below the review threshold are flagged for
  human/agent review rather than presented as certain.

Usage:
    python -m clipforge.discover --transcript work/transcript.json \
        [--audio work/source.mp4] [--top-n 5] [--out work/candidates.json]
"""
import argparse
import json
import math
import os
import subprocess
from datetime import datetime, timezone

import numpy as np

# Sub-score weights (sum to 1.0). Kept explicit so results stay explainable.
WEIGHTS = {
    "hook_strength": 0.25,
    "completeness": 0.20,
    "speech_density": 0.20,
    "audio_energy": 0.15,
    "ending_quality": 0.10,
    "duration_fit": 0.10,
}
SENTENCE_ENDERS = {".", "!", "?"}
HOOK_SUPERLATIVES = ("best", "worst", "never", "always", "secret",
                     "why", "how", "most", "only")
DEDUP_IOU = 0.30


# ---------------------------------------------------------------- sentences
def sentences_from_words(words, pause_s=0.8):
    """Group a word stream into sentences on punctuation and pauses."""
    sentences, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else pause_s
        ends = w["text"].rstrip("\"'“”’)")
        if (ends and ends[-1] in SENTENCE_ENDERS) or (gap or 0) > pause_s:
            sentences.append({
                "start": cur[0]["start"],
                "end": cur[-1]["end"],
                "text": " ".join(x["text"] for x in cur),
                "word_count": len(cur),
            })
            cur = []
    if cur:
        sentences.append({
            "start": cur[0]["start"], "end": cur[-1]["end"],
            "text": " ".join(x["text"] for x in cur),
            "word_count": len(cur),
        })
    return sentences


# ------------------------------------------------------------------- audio
def compute_rms(path, hop_sec=0.5, rate=16000):
    """Per-hop RMS of the first audio stream, or None when unavailable."""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "a:0",
           "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    samples = np.frombuffer(proc.stdout, dtype=np.float32)
    hop = max(1, int(rate * hop_sec))
    n = len(samples) // hop
    if n == 0:
        return None
    frames = samples[: n * hop].reshape(n, hop)
    return np.sqrt((frames.astype(np.float64) ** 2).mean(axis=1))


def energy_zscores(rms):
    rms = np.asarray(rms, dtype=np.float64)
    sd = rms.std()
    if sd == 0:
        return np.zeros_like(rms)
    return (rms - rms.mean()) / sd


def _window_energy(z, hop_sec, start, end):
    if z is None or len(z) == 0:
        return 0.5  # neutral: no audio evidence available
    i0 = max(0, int(start / hop_sec))
    i1 = min(len(z), max(i0 + 1, int(end / hop_sec)))
    seg = z[i0:i1]
    return float(1.0 / (1.0 + math.exp(-float(seg.mean()))))


# -------------------------------------------------------------- candidates
def generate_candidates(sentences, duration, min_clip, max_clip, z=None,
                        hop_sec=0.5):
    """Sentence-boundary windows plus energy-peak-anchored windows."""
    if not sentences:
        return []
    cands = []
    # 1. sentence-boundary windows in two duration variants per start:
    #    the shortest window above the loose floor, and one sized close to
    #    the target duration (both clamped later; PeakCut-style mechanics)
    target = min(max_clip, 45.0)
    for i in range(len(sentences)):
        base = sentences[i]["start"]
        j_short = j_target = None
        for j in range(i, len(sentences)):
            dur = sentences[j]["end"] - base
            if j_short is None and dur >= min_clip * 0.7:
                j_short = j
            if dur >= target:
                j_target = j
                break
        for j in (j_short, j_target):
            if j is None:
                continue
            start, end = base, sentences[j]["end"]
            if end - start > max_clip * 1.05:
                continue
            cands.append({"start": start, "end": min(end, duration),
                          "origin": "sentence-window"})
    # 2. energy-peak anchors: start at a local energy maximum, snap the
    #    start to a sentence edge, cut at target duration snapped to the
    #    nearest sentence end (may land mid-sentence -> completeness < 1)
    if z is not None and len(z) > 4:
        k = max(1, len(z) // 40)
        peaks = np.argsort(z)[-k:] * hop_sec
        for p in sorted(peaks):
            si = min(range(len(sentences)),
                     key=lambda s: abs(sentences[s]["start"] - p))
            start = sentences[si]["start"]
            target = min(max_clip, max(min_clip, 0.75 * max_clip))
            raw_end = start + target
            se = min(range(len(sentences)),
                     key=lambda s: abs(sentences[s]["end"] - raw_end))
            end = min(max(sentences[se]["end"], start + min_clip * 0.6),
                      duration)
            if end - start < min_clip * 0.6 or end - start > max_clip * 1.05:
                continue
            cands.append({"start": start, "end": end,
                          "origin": "energy-peak"})
    # clamp + keep inside duration
    out = []
    for c in cands:
        start = max(0.0, c["start"])
        end = min(float(duration), max(start + 1.0, c["end"]))
        if min_clip * 0.6 <= end - start <= max_clip * 1.05:
            out.append({"start": round(start, 2), "end": round(end, 2),
                        "origin": c["origin"]})
    return out


# ---------------------------------------------------------------- scoring
def _hook_strength(first_sentence_text):
    t = (first_sentence_text or "").strip().lower()
    if not t:
        return 0.0
    score = 0.0
    if t.endswith("?"):
        score += 0.35
    if t and t[0].isdigit():
        score += 0.25
    if "you" in t.split() or "your" in t.split():
        score += 0.20
    if any(s in t for s in HOOK_SUPERLATIVES):
        score += 0.20
    if len(t.split()) <= 10:
        score += 0.15
    return min(1.0, score)


def _completeness(start, end, sentences):
    starts_ok = any(abs(s["start"] - start) < 0.25 for s in sentences)
    ends_ok = any(abs(s["end"] - end) < 0.25 for s in sentences)
    return (1.0 if starts_ok else 0.3) * 0.5 + (1.0 if ends_ok else 0.4) * 0.5


def _ending_quality(end, sentences, z, hop_sec):
    prev = [s for s in sentences if s["end"] <= end + 0.3]
    if not prev:
        return 0.5
    last = prev[-1]
    if abs(last["end"] - end) > 0.3:
        return 0.4  # cuts before the sentence lands
    if last["text"].rstrip("\"'“”’)")[-1:] in SENTENCE_ENDERS:
        return 1.0
    return 0.6


def _duration_fit(dur, min_clip, max_clip):
    target = min(max_clip, 45.0)
    sigma = max(1.0, 0.35 * target)
    return math.exp(-0.5 * ((dur - target) / sigma) ** 2)


def _density(words_in_window, dur):
    wps = words_in_window / max(dur, 0.1)
    if wps <= 0:
        return 0.0
    if 2.2 <= wps <= 3.8:
        return 1.0
    return float(min(1.0, (wps / 2.2) if wps < 2.2 else 3.8 / wps))


def score_candidate(cand, sentences, words, z, hop_sec, min_clip, max_clip):
    start, end = cand["start"], cand["end"]
    dur = end - start
    win_words = [w for w in words if w["end"] > start and w["start"] < end]
    inner = [s for s in sentences if s["start"] >= start - 0.05
             and s["end"] <= end + 0.05]
    first_text = inner[0]["text"] if inner else ""
    components = {
        "hook_strength": round(_hook_strength(first_text), 3),
        "completeness": round(_completeness(start, end, sentences), 3),
        "speech_density": round(_density(len(win_words), dur), 3),
        "audio_energy": round(_window_energy(z, hop_sec, start, end), 3),
        "ending_quality": round(_ending_quality(end, sentences, z, hop_sec),
                                3),
        "duration_fit": round(_duration_fit(dur, min_clip, max_clip), 3),
    }
    overall = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    return components, overall


# ------------------------------------------------------------------ dedup
def _iou(a, b):
    inter = max(0.0, min(a["end"], b["end"]) - max(a["start"], b["start"]))
    union = max(a["end"], b["end"]) - min(a["start"], b["start"])
    return inter / union if union > 0 else 0.0


def dedup(cands, iou=DEDUP_IOU):
    cands = sorted(cands, key=lambda c: c["overall"], reverse=True)
    kept, suppressed = [], []
    for c in cands:
        if any(_iou(c, k) > iou for k in kept):
            suppressed.append(c)
        else:
            kept.append(c)
    return kept, suppressed


# ------------------------------------------------------------- entry point
def discover_moments(transcript, duration=None, audio_path=None,
                     min_clip=15.0, max_clip=60.0, top_n=5,
                     source_asset_id=None):
    """Return the ranked candidate list with explainable evidence."""
    words = transcript.get("words") or []
    duration = float(duration or transcript.get("duration")
                     or (words[-1]["end"] if words else 0.0))
    sentences = sentences_from_words(words)
    z, hop_sec = None, 0.5
    if audio_path:
        rms = compute_rms(audio_path, hop_sec=hop_sec)
        if rms is not None:
            z = energy_zscores(rms)

    raw = generate_candidates(sentences, duration, min_clip, max_clip,
                              z=z, hop_sec=hop_sec)
    scored = []
    for c in raw:
        comps, overall = score_candidate(c, sentences, words, z, hop_sec,
                                         min_clip, max_clip)
        scored.append({**c, "components": comps, "overall": overall})
    kept, suppressed = dedup(scored)
    kept = kept[: max(1, int(top_n))]

    candidates = []
    for rank, c in enumerate(kept, 1):
        start, end = c["start"], c["end"]
        win_words = [w for w in words
                     if w["end"] > start and w["start"] < end]
        inner = [s for s in sentences
                 if s["start"] >= start - 0.05 and s["end"] <= end + 0.05]
        text = " ".join(s["text"] for s in inner)
        excerpt = (text[:180] + ("…" if len(text) > 180 else ""))
        before = [s for s in sentences if s["end"] <= start]
        flags = []
        if c["components"]["completeness"] < 0.9:
            flags.append("boundary_cut_may_split_sentence")
        if c["components"]["speech_density"] < 0.4:
            flags.append("low_speech_density")
        if c["components"]["audio_energy"] >= 0.8 and z is not None:
            flags.append("loud_section_check_audio")
        comps = c["components"]
        reasons = sorted(comps.items(), key=lambda kv: -kv[1])[:2]
        human = {
            "hook_strength": "strong opening line",
            "completeness": "clean start/end boundaries",
            "speech_density": "dense, steady speech",
            "audio_energy": "energetic audio section",
            "ending_quality": "lands on a sentence ending",
            "duration_fit": "duration fits the target",
        }
        candidates.append({
            "candidate_id": f"cand-{rank:02d}",
            "source_asset_id": source_asset_id,
            "start_ms": int(start * 1000),
            "end_ms": int(end * 1000),
            "duration_ms": int((end - start) * 1000),
            "rank": rank,
            "overall_score": round(100 * c["overall"], 1),
            "score_components": comps,
            "score_basis": "heuristic multi-signal v1 (not calibrated)",
            "transcript_excerpt": excerpt,
            "detected_language_segments": [{
                "language": transcript.get("language"),
                "start_ms": 0,
                "end_ms": int((end - start) * 1000),
                "note": "single language for whole transcript "
                        "(per-segment detection not implemented)",
            }],
            "hook_summary": (inner[0]["text"][:100] if inner else ""),
            "why_it_works": "; ".join(f"{human[k]} ({v})"
                                      for k, v in reasons),
            "context_summary": (before[-1]["text"][:120]
                                if before else "(start of video)"),
            "boundary_confidence": comps["completeness"],
            "transcription_confidence": None,
            "visual_evidence_refs": [],
            "audio_evidence_refs": (["rms-energy-hop"]
                                    if z is not None else []),
            "risk_flags": flags,
            "suggested_title": (" ".join(text.split()[:6])
                                or "Clip"),
            "suggested_caption": excerpt,
            "review_status": "pending_review",
            "window_origin": c["origin"],
        })

    return {
        "engine": "clipforge-discovery-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score_weights": WEIGHTS,
        "params": {"min_clip": min_clip, "max_clip": max_clip,
                   "top_n": top_n,
                   "audio_energy_used": z is not None},
        "candidates": candidates,
        "suppressed_as_overlapping": len(suppressed),
        "notes": ["All scores are heuristic ranking signals, not "
                  "calibrated confidences. review_status stays "
                  "pending_review until a human or agent accepts."],
    }


def main():
    ap = argparse.ArgumentParser(
        description="ClipForge multi-signal moment discovery")
    ap.add_argument("--transcript", required=True,
                    help="transcript.json from clipforge.transcribe")
    ap.add_argument("--audio", default="",
                    help="media file for RMS energy evidence (optional)")
    ap.add_argument("--top-n", type=int, default=5)
    ap.add_argument("--min-clip", type=float, default=15.0)
    ap.add_argument("--max-clip", type=float, default=60.0)
    ap.add_argument("--source-asset-id", default=None)
    ap.add_argument("--out", default="candidates.json")
    args = ap.parse_args()

    with open(args.transcript) as f:
        transcript = json.load(f)
    result = discover_moments(transcript, audio_path=args.audio or None,
                              min_clip=args.min_clip,
                              max_clip=args.max_clip,
                              top_n=args.top_n,
                              source_asset_id=args.source_asset_id)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    for c in result["candidates"]:
        print(f"[discover] #{c['rank']} {c['overall_score']:5.1f} "
              f"{c['start_ms'] / 1000:7.2f}-{c['end_ms'] / 1000:7.2f}s "
              f"{c['window_origin']:<13} {c['hook_summary'][:48]!r}")
    print(f"[discover] wrote {args.out} "
          f"({len(result['candidates'])} candidates, "
          f"{result['suppressed_as_overlapping']} suppressed)")


if __name__ == "__main__":
    main()
