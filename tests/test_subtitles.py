"""Unit tests for clipforge.subtitles (clean-room gates) — offline."""
import pytest

from clipforge import subtitles as subs


# ------------------------------------------------------------- timestamps
def test_srt_timestamp_roundtrip():
    assert subs.parse_ts("00:01:05,250") == 65250
    assert subs.fmt_ts(65250) == "00:01:05,250"


def test_vtt_timestamp_roundtrip():
    assert subs.parse_ts("01:05.250") == 65250
    assert subs.parse_ts("00:01:05.250") == 65250
    assert subs.fmt_ts(65250, vtt=True) == "00:01:05.250"


# ------------------------------------------------------------ srt/vtt i/o
SRT = """1
00:00:01,000 --> 00:00:03,500
Hello world.

2
00:00:04,000 --> 00:00:06,000
Second cue.
"""
VTT = """WEBVTT

00:00:01.000 --> 00:00:03.500
Hello world.

00:00:04.000 --> 00:00:06.000
Second cue.
"""


def test_srt_parse_serialize_roundtrip():
    cues = subs.parse_srt(SRT)
    assert len(cues) == 2
    assert cues[0]["text"] == "Hello world."
    assert cues[1]["start_ms"] == 4000
    again = subs.parse_srt(subs.serialize_srt(cues))
    assert [(c["start_ms"], c["end_ms"], c["text"]) for c in again] == \
        [(c["start_ms"], c["end_ms"], c["text"]) for c in cues]


def test_vtt_parse_serialize_roundtrip():
    cues = subs.parse_vtt(VTT)
    assert len(cues) == 2
    assert subs.parse_vtt(subs.serialize_vtt(cues))[1]["text"] == \
        "Second cue."


# ---------------------------------------------------------------- wrapping
def test_wrap_text_fits_two_lines():
    wrapped = subs.wrap_text(
        "one two three four five six seven eight nine ten eleven twelve")
    assert wrapped is not None
    assert all(len(l) <= subs.MAX_CHARS for l in wrapped.split("\n"))
    assert len(wrapped.split("\n")) <= 2


def test_wrap_text_returns_none_when_unfittable():
    assert subs.wrap_text("x" * 100) is None


# ------------------------------------------------------------------ gates
def _cue(s, e, text, i=1):
    return {"index": i, "start_ms": s, "end_ms": e, "text": text}


def test_validate_passes_clean_cues():
    cues = [_cue(0, 3000, "Hello"), _cue(3000, 6000, "World", 2)]
    report = subs.validate(cues)
    assert report["passed"], report


def test_validate_catches_each_gate():
    long_dur = _cue(0, 9000, "too long")            # G1
    bad_layout = _cue(0, 3000, "a" * 50)            # G2
    overlap = [_cue(0, 3000, "a"), _cue(2000, 4000, "b", 2)]  # G3
    empty = _cue(0, 3000, "   ")                    # G4
    unordered = [_cue(5000, 6000, "a"), _cue(0, 1000, "b", 2)]  # G5
    assert any(v["gate"] == "G1" for v in subs.validate([long_dur])
               ["violations"])
    assert any(v["gate"] == "G2" for v in subs.validate([bad_layout])
               ["violations"])
    assert any(v["gate"] == "G3" for v in subs.validate(overlap)
               ["violations"])
    assert any(v["gate"] == "G4" for v in subs.validate([empty])
               ["violations"])
    assert not subs.validate(unordered)["gates"]["G5_order"]


# ------------------------------------------------------------ auto repair
def test_auto_repair_merges_short_and_passes():
    cues = [_cue(0, 400, "short"), _cue(500, 3500, "next cue", 2)]
    fixed, actions = subs.auto_repair(cues)
    report = subs.validate(fixed)
    assert report["passed"], report["violations"]
    assert actions and actions[0]["action"].startswith(("merge", "extend"))


def test_auto_repair_splits_long_cue_preserving_words():
    text = " ".join(f"word{i}" for i in range(30))
    cues = [_cue(0, 10000, text)]  # 10s, one line -> must split
    fixed, actions = subs.auto_repair(cues)
    assert len(fixed) >= 2
    assert any(a["action"] == "split_long" for a in actions)
    joined = " ".join(c["text"] for c in fixed)
    assert sorted(joined.split()) == sorted(text.split()), \
        "repair must never rewrite text"
    assert subs.validate(fixed)["passed"]


def test_auto_repair_clamps_overlap():
    cues = [_cue(0, 3000, "first"), _cue(2000, 4000, "second", 2)]
    fixed, actions = subs.auto_repair(cues)
    assert fixed[0]["end_ms"] <= fixed[1]["start_ms"] + 1
    assert any(a["action"] == "clamp_overlap" for a in actions)


# ------------------------------------------------------------- transcript
def test_cues_from_transcript_segments(dense_then_silence_transcript):
    cues = subs.cues_from_transcript(dense_then_silence_transcript)
    assert cues and cues[0]["start_ms"] >= 0
    assert [c["index"] for c in cues] == list(range(1, len(cues) + 1))


def test_clip_window_cues_slices_and_offsets():
    cues = [_cue(1000, 3000, "a"), _cue(20000, 24000, "b", 2),
            _cue(60000, 64000, "c", 3)]
    window = subs.clip_window_cues(cues, 19000, 50000)
    assert len(window) == 1
    assert window[0]["start_ms"] == 1000 and window[0]["text"] == "b"
    assert [c["index"] for c in window] == [1]
