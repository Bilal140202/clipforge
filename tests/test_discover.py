"""Unit tests for clipforge.discover (pure logic + one ffmpeg smoke)."""
import json
import math
import pathlib
import shutil
import subprocess
import sys

import pytest

from clipforge import discover


# ------------------------------------------------------------- sentences
def test_sentences_split_on_punctuation_and_pause():
    words = [
        {"start": 0.0, "end": 0.5, "text": "Hello"},
        {"start": 0.5, "end": 1.0, "text": "world."},
        {"start": 3.0, "end": 3.5, "text": "New"},
        {"start": 3.5, "end": 4.0, "text": "sentence!"},
    ]
    s = discover.sentences_from_words(words)
    assert len(s) == 2
    assert s[0]["text"] == "Hello world."
    assert abs(s[1]["start"] - 3.0) < 1e-6


def test_sentences_split_on_long_pause_without_punctuation():
    words = [
        {"start": 0.0, "end": 0.5, "text": "One"},
        {"start": 0.5, "end": 1.0, "text": "two"},
        {"start": 4.0, "end": 4.5, "text": "three"},
    ]
    s = discover.sentences_from_words(words)
    assert len(s) == 2  # 3.0s pause splits, despite no punctuation


# ------------------------------------------------------------- candidates
def test_candidates_within_bounds(dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    sents = discover.sentences_from_words(tr["words"])
    cands = discover.generate_candidates(sents, tr["duration"], 15, 60)
    assert cands, "expected candidates for a 60s spoken transcript"
    for c in cands:
        assert 15 * 0.6 <= c["end"] - c["start"] <= 60 * 1.05 + 1e-6
        assert 0 <= c["start"] < c["end"] <= 60.0


def test_sentences_windows_start_at_sentence_edges(
        dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    sents = discover.sentences_from_words(tr["words"])
    starts = {round(s["start"], 2) for s in sents}
    for c in discover.generate_candidates(sents, tr["duration"], 15, 60):
        if c["origin"] == "sentence-window":
            assert round(c["start"], 2) in starts


# --------------------------------------------------------------- scoring
def test_scores_in_unit_range_and_deterministic(
        dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    out1 = discover.discover_moments(tr, top_n=5)
    out2 = discover.discover_moments(tr, top_n=5)
    for cand in out1["candidates"] + out2["candidates"]:
        assert all(0.0 <= v <= 1.0 for v in
                   cand["score_components"].values())
        assert 0.0 <= cand["overall_score"] <= 100.0
    a = [(c["start_ms"], c["end_ms"], c["overall_score"])
         for c in out1["candidates"]]
    b = [(c["start_ms"], c["end_ms"], c["overall_score"])
         for c in out2["candidates"]]
    assert a == b, "discovery must be deterministic"


def test_top_n_limits_and_ranks(dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    out = discover.discover_moments(tr, top_n=3)
    assert len(out["candidates"]) <= 3
    ranks = [c["rank"] for c in out["candidates"]]
    assert ranks == sorted(ranks) == list(range(1, len(ranks) + 1))
    scores = [c["overall_score"] for c in out["candidates"]]
    assert scores == sorted(scores, reverse=True)


def test_schema_fields_present(dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    out = discover.discover_moments(tr, top_n=2)
    for c in out["candidates"]:
        for key in ("candidate_id", "start_ms", "end_ms", "duration_ms",
                    "rank", "overall_score", "score_components",
                    "transcript_excerpt", "hook_summary", "why_it_works",
                    "boundary_confidence", "transcription_confidence",
                    "risk_flags", "review_status"):
            assert key in c, f"missing schema field {key}"
    assert out["candidates"][0]["transcription_confidence"] is None
    assert "not calibrated" in out["candidates"][0]["score_basis"]


def test_empty_transcript_returns_no_candidates():
    out = discover.discover_moments({"words": [], "segments": [],
                                     "duration": 30.0, "language": "en"})
    assert out["candidates"] == []


# ------------------------------------------------------------------ dedup
def test_dedup_suppresses_high_overlap():
    cands = [
        {"start": 10.0, "end": 40.0, "overall": 0.9},
        {"start": 12.0, "end": 42.0, "overall": 0.7},  # IoU ~0.83
        {"start": 60.0, "end": 90.0, "overall": 0.5},
    ]
    kept, suppressed = discover.dedup(cands)
    assert len(kept) == 2
    assert len(suppressed) == 1
    assert kept[0]["overall"] == 0.9


def test_discover_dedup_count_reported(dense_then_silence_transcript):
    tr = dense_then_silence_transcript
    out = discover.discover_moments(tr, top_n=10)
    assert isinstance(out["suppressed_as_overlapping"], int)
    assert out["suppressed_as_overlapping"] >= 0


# ------------------------------------------------------------------ audio
@pytest.mark.skipif(shutil.which("ffmpeg") is None,
                    reason="ffmpeg not installed")
def test_compute_rms_and_zscores(tmp_path):
    wav = tmp_path / "tone.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=440:duration=2",
         str(wav)], check=True)
    rms = discover.compute_rms(str(wav), hop_sec=0.5)
    assert rms is not None and len(rms) == 4
    assert (rms > 0).all()
    z = discover.energy_zscores(rms)
    assert abs(float(z.mean())) < 1e-6  # CI float noise is ~1e-9


def test_window_energy_neutral_without_audio():
    assert discover._window_energy(None, 0.5, 0, 10) == 0.5


# -------------------------------------------------------------------- CLI
def test_cli_writes_candidates_json(tmp_path, dense_then_silence_transcript):
    tr_path = tmp_path / "transcript.json"
    tr_path.write_text(json.dumps(dense_then_silence_transcript))
    out = tmp_path / "candidates.json"
    repo = str(pathlib.Path(__file__).resolve().parents[1])
    proc = subprocess.run(
        [sys.executable, "-m", "clipforge.discover", "--transcript",
         str(tr_path), "--top-n", "3", "--out", str(out)],
        cwd=repo, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["engine"] == "clipforge-discovery-v1"
    assert 1 <= len(data["candidates"]) <= 3
