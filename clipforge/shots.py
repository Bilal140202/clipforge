"""Shot-change detection and boundary snapping (stage 3.5 evidence).

The moment picker must respect the source's own camera cuts: a clip
whose window straddles many shot changes reads as "jump cuts every few
seconds" even though every content boundary is clean. This module adds
the visual half of boundary discipline:

- detect_shot_changes(): ffmpeg scene-change detection (scaled frames,
  cheap) -> sorted cut timestamps.
- shot_stability_score(): 1.0 for a window with no internal cuts,
  decaying with each cut - used as a discovery sub-score.
- snap_to_shots(): move a window's edges onto the nearest camera cut
  (within tolerance) so the clip opens on a fresh take and closes
  before the camera cuts away.

Design provenance: the snap mechanic generalizes PeakCut's (MIT)
sentence-boundary snap to visual boundaries; the stability sub-score
follows the clean-room signal-weight pattern documented in
docs/research/REFERENCE_PROJECT_AUDIT.md (SupoClip audit). No third-
party code is used.
"""
import math
import re
import subprocess

SCENE_THRESHOLD = 0.35
SNAP_TOLERANCE = 1.5
EPSILON = 0.05


def detect_shot_changes(path, threshold=SCENE_THRESHOLD):
    """Timestamps (seconds, ascending) where the source changes shot.

    showinfo logs at INFO level, so stderr must NOT be captured with
    `-v error` (that silences it - the bug that made every source look
    like it had zero cuts). Returns [] when ffmpeg fails (loud warning)
    or when the source genuinely has no cuts - callers treat shots as
    optional evidence, never a hard dependency.
    """
    cmd = [
        "ffmpeg", "-an", "-sn", "-i", str(path),
        "-vf", f"scale=192:-2,select=gt(scene\\,{threshold}),showinfo",
        "-f", "null", "-",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=1200)
    except (OSError, subprocess.TimeoutExpired):
        print("[shots] WARNING: scene detection failed to run - "
              "no shot evidence (treat as single-take or retry)")
        return []
    if proc.returncode != 0:
        print(f"[shots] WARNING: ffmpeg exited {proc.returncode} - "
              "no shot evidence")
        return []
    times = sorted(float(t) for t in
                   re.findall(r"pts_time:([0-9]+\.?[0-9]*)",
                              proc.stderr.decode("utf-8", "replace")))
    return times


def cuts_in_window(start, end, shots):
    """Number of camera cuts strictly inside (start, end)."""
    return sum(1 for t in shots if start < t < end)


def shot_stability_score(start, end, shots):
    """1.0 when the window never changes camera; halves per extra cut."""
    cuts = cuts_in_window(start, end, shots)
    if cuts == 0:
        return 1.0
    return 1.0 / (1.0 + 0.5 * cuts)


def _nearest_change(t, shots, tol):
    best, best_d = None, tol
    for s in shots:
        d = abs(s - t)
        if d < best_d:
            best, best_d = s, d
    return best


def snap_to_shots(start, end, shots, duration,
                  min_clip, max_clip, tol=SNAP_TOLERANCE):
    """Snap window edges onto camera cuts when one sits within tol.

    start moves to just after the cut (clip opens on a fresh take);
    end moves to just before the cut (clip closes before the camera
    leaves). Duration bounds are preserved; when a snap would break
    them, that edge stays put.
    """
    if not shots:
        return start, end
    dur = end - start

    t = _nearest_change(start, shots, tol)
    if t is not None:
        new_start = min(max(t + EPSILON, 0.0), duration)
        new_dur = end - new_start
        if min_clip * 0.6 <= new_dur <= max_clip * 1.05:
            start = new_start

    t = _nearest_change(end, shots, tol)
    if t is not None:
        new_end = min(max(t, start + min_clip * 0.6), duration)
        if min_clip * 0.6 <= new_end - start <= max_clip * 1.05:
            end = new_end

    if end - start > max_clip * 1.05:  # a snap extended us: trim to bound
        end = start + max_clip
    if end - start < min_clip * 0.6:  # a snap shrank us: widen to floor
        end = min(duration, start + min_clip * 0.6)
    return round(min(start, duration), 3), round(min(end, duration), 3)


def stability_note(cuts, dur):
    """One-line human summary for candidates.json evidence."""
    if cuts == 0:
        return "single camera take"
    cpm = cuts / max(dur, 0.1) * 60.0
    return (f"{cuts} camera cut(s) inside the window "
            f"({cpm:.1f}/min; "
            f"{'acceptable pacing' if cpm <= 2.0 else 'busy - review'})")


def expected_cuts(dur):
    """Cuts a comfortably-paced window may contain (~1 per 30s)."""
    return math.floor(max(dur, 0.0) / 30.0)
