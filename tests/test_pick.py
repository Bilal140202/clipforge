"""Unit tests for clipforge.pick fallback logic (no Ollama, no network)."""
import json

from clipforge import pick


def test_clamp_moment_respects_duration_and_bounds():
    # 200s window clamped into a 120s video -> end at duration, still valid
    m = pick._clamp_moment({"start": 100.0, "end": 200.0}, 120.0, 15, 60)
    assert m["start"] == 100.0 and m["end"] == 120.0
    # over-long window is shrunk to max_clip
    m3 = pick._clamp_moment({"start": 0.0, "end": 100.0}, 120.0, 15, 60)
    assert m3["start"] == 0.0 and m3["end"] == 60.0
    # too-short window is extended to min_clip
    m2 = pick._clamp_moment({"start": 0.0, "end": 2.0}, 120.0, 15, 60)
    assert m2["end"] - m2["start"] >= 15.0


def test_fallback_picks_densest_window(dense_then_silence_transcript):
    moment = pick._fallback_moment(dense_then_silence_transcript, 15, 60)
    start, end = moment["start"], moment["end"]
    assert end - start <= 60.0 + 1e-6
    # dense region is 20-40s: the chosen window must overlap it
    assert start < 40.0 and end > 20.0
    assert moment["source"] == "fallback"


def test_pick_moment_without_llm_writes_json(
        tmp_path, dense_then_silence_transcript):
    moment = pick.pick_moment(dense_then_silence_transcript,
                              "http://127.0.0.1:9", "unused", 15, 60,
                              str(tmp_path), use_llm=False)
    saved = json.loads((tmp_path / "moment.json").read_text())
    assert saved == moment
    assert moment["start"] < moment["end"]
