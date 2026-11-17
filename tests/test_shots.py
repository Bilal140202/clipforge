"""Unit tests for shot-change boundary discipline (no ffmpeg needed)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from clipforge import shots  # noqa: E402


SHOTS = [10.0, 25.0, 40.0, 60.0]


def test_cuts_in_window_counts_strictly_inside():
    assert shots.cuts_in_window(0, 100, SHOTS) == 4
    assert shots.cuts_in_window(0, 10, SHOTS) == 0      # boundary excluded
    assert shots.cuts_in_window(10, 40, SHOTS) == 1     # 25 only
    assert shots.cuts_in_window(0, 100, []) == 0


def test_stability_score_is_1_without_cuts_and_decays():
    assert shots.shot_stability_score(0, 9.9, SHOTS) == 1.0
    assert shots.shot_stability_score(0, 30, SHOTS) == pytest.approx(0.5)
    assert shots.shot_stability_score(0, 100, SHOTS) == pytest.approx(
        1.0 / 3.0)
    # monotonic decay with cut count
    a = shots.shot_stability_score(0, 30, SHOTS)
    b = shots.shot_stability_score(0, 100, SHOTS)
    assert a > b


def test_snap_moves_edges_onto_nearby_cuts():
    # start 1s after a cut at 25 -> snaps to just after the cut
    s, e = shots.snap_to_shots(26.0, 60.0, SHOTS, 120.0, 15.0, 60.0)
    assert s == pytest.approx(25.05, abs=0.01)
    # end 1.2s before a cut at 60 -> closes exactly on the cut
    assert e == pytest.approx(60.0, abs=0.01)


def test_snap_leaves_window_without_nearby_cuts():
    s, e = shots.snap_to_shots(100.0, 120.0, SHOTS, 200.0, 15.0, 60.0)
    assert (s, e) == (100.0, 120.0)


def test_snap_respects_duration_bounds():
    s, e = shots.snap_to_shots(55.0, 61.0, SHOTS, 70.0, 15.0, 60.0)
    assert s <= e and e <= 70.0
    # cannot exceed max_clip after a widening snap
    s, e = shots.snap_to_shots(38.0, 41.0, SHOTS, 500.0, 15.0, 60.0)
    assert e - s <= 60.0 * 1.05
    # cannot fall below the min floor after a shrink
    s, e = shots.snap_to_shots(58.5, 61.5, SHOTS, 500.0, 15.0, 60.0)
    assert e - s >= 15.0 * 0.6


def test_snap_no_shots_is_identity():
    assert shots.snap_to_shots(5.0, 40.0, [], 100.0, 15.0, 60.0) == (5.0, 40.0)


def test_expected_cuts_and_note():
    assert shots.expected_cuts(90) == 3
    assert shots.expected_cuts(29) == 0
    assert "single camera take" in shots.stability_note(0, 40.0)
    assert "camera cut" in shots.stability_note(2, 40.0)
    assert "busy - review" in shots.stability_note(10, 30.0)
