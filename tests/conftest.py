"""Shared transcript fixtures for ClipForge tests (no models, no network)."""
import pytest


def make_words(spec, t0=0.0, wps=3.0):
    """Build a word list from [(text, word_count_or_None), ...].

    Each entry becomes `word_count` evenly spaced words at `wps` words/sec.
    """
    words = []
    t = t0
    for text, count in spec:
        count = count if count is not None else max(1, len(text.split()))
        dur_each = (1.0 / wps)
        for k in range(count):
            words.append({"start": round(t, 3),
                          "end": round(t + dur_each * 0.9, 3),
                          "text": text if k == 0 else "w"})
            t += dur_each
    return words


@pytest.fixture
def dense_then_silence_transcript():
    """60s synthetic transcript: sparse intro, dense middle, silent tail.

    The dense middle (20s-40s) should win the fallback density pick.
    """
    words = []
    words += make_words([("Okay so let me start with some slow.", 8),
                         ("background talk here.", 3)], t0=2.0)
    words += make_words(
        [("Why do octopuses have", 4), ("three hearts and blue blood?",
          5), ("Because their blood uses copper, not iron.", 7),
         ("That is the strangest fact you will hear today.", 9),
         ("Their hearts even stop when they swim.", 7)], t0=20.0)
    words += make_words([("And that is the end.", 5)], t0=50.0)
    segments = []
    cur = []
    for w in words:
        cur.append(w)
        if w["text"].endswith(("?", ".",)):
            segments.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                             "text": " ".join(x["text"] for x in cur)})
            cur = []
    return {"language": "en", "language_probability": 0.9,
            "duration": 60.0, "words": words, "segments": segments}
