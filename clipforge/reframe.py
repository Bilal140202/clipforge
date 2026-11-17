"""Stage 5: face-tracked 9:16 reframe (OpenCV Haar -> ffmpeg).

Detects the main face on sampled frames, glides a 9:16 crop window
toward it and encodes 1080x1920 through an ffmpeg pipe. The crop never
teleports: a dead-zone swallows small drift and a velocity clamp limits
how fast the window may move, so the reframe reads as a slow pan - not
as camera-angle cuts (the failure this module was rewritten for: an
EMA that chased every detection made the vertical cut feel like it
switched cameras every few seconds).

Falls back to a center crop when no face is ever found.
"""
import subprocess

import cv2
import numpy as np

OUT_W, OUT_H = 1080, 1920
ASPECT = OUT_W / OUT_H  # 9/16
DETECT_EVERY = 6        # run the detector every Nth frame
DEAD_ZONE_FRAC = 0.06   # ignore target drift below this (fraction of w)
MAX_GLIDE_FRAC = 0.10   # crop center speed cap (fraction of w per s)
PERSIST_SEC = 2.0       # keep gliding toward the last face this long


def _crop_geometry(w, h):
    """Crop box size for a 9:16 window inside a w x h frame."""
    if w / h >= ASPECT:  # landscape-ish: full height, narrower width
        crop_h = h
        crop_w = int(h * ASPECT) & ~1
    else:  # already narrow: full width, shorter height
        crop_w = w & ~1
        crop_h = int(w / ASPECT) & ~1
    return crop_w, crop_h


def _detect_faces(cascade, frame_bgr, w, h):
    """(cx, cy, area) of faces in full-frame coords (Haar cascade)."""
    scale = 320.0 / w
    small = cv2.resize(frame_bgr, (320, max(1, int(h * scale))))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5,
                                     minSize=(int(320 * 0.08),) * 2)
    out = []
    for (x, y, rw, rh) in rects or []:
        out.append(((x + rw / 2) / 320 * w, (y + rh / 2) / 320 * h,
                    rw * rh))
    return out


def reframe(segment_path, out_path):
    cap = cv2.VideoCapture(segment_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {segment_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    crop_w, crop_h = _crop_geometry(w, h)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if cascade.empty():
        cascade = None  # graceful: center crop, never crash the render

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{OUT_W}x{OUT_H}", "-r", f"{fps:.6f}", "-i", "-",
        "-i", segment_path,
        "-map", "0:v", "-map", "1:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", out_path,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    target_cx = target_cy = None   # where the tracked face was last seen
    cx = cy = w / 2.0              # where the crop center actually is
    faces_seen = 0
    max_step = MAX_GLIDE_FRAC * w / max(fps, 1.0)  # px per frame
    dead_zone = DEAD_ZONE_FRAC * w
    frames_since_face = 0
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if cascade is not None and idx % DETECT_EVERY == 0:
            faces = _detect_faces(cascade, frame, w, h)
            if faces:
                faces_seen += 1
                frames_since_face = 0
                # stick to the face nearest the current crop center -
                # never bounce to a different panelist across the frame
                if target_cx is None:
                    pick = max(faces, key=lambda f: f[2])
                else:
                    pick = min(faces,
                               key=lambda f: (f[0] - cx) ** 2
                               + (f[1] - cy) ** 2)
                if (target_cx is None
                        or abs(pick[0] - target_cx) > dead_zone
                        or abs(pick[1] - target_cy) > dead_zone):
                    target_cx, target_cy = pick[0], pick[1]
            else:
                frames_since_face += DETECT_EVERY
                if frames_since_face > PERSIST_SEC * fps:
                    target_cx = target_cy = None  # give up: ease to center
        if target_cx is None:
            target_cx, target_cy = cx, cy  # glide back to center, slowly
        # glide: at most max_step px per frame toward the target
        dx = min(max(target_cx - cx, -max_step), max_step)
        dy = min(max(target_cy - cy, -max_step), max_step)
        cx += dx
        cy += dy
        x0 = int(min(max(cx - crop_w / 2, 0), w - crop_w))
        y0 = int(min(max(cy - crop_h / 2, 0), h - crop_h))
        crop = frame[y0:y0 + crop_h, x0:x0 + crop_w]
        resized = cv2.resize(crop, (OUT_W, OUT_H), interpolation=cv2.INTER_AREA)
        proc.stdin.write(resized.astype(np.uint8).tobytes())
        idx += 1

    cap.release()
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg reframe exited {rc}")
    mode = ("face-tracked glide" if faces_seen
            else "center crop (no face found)" if cascade
            else "center crop (no cascade)")
    print(f"[reframe] {idx} frames -> {OUT_W}x{OUT_H} ({mode})")
