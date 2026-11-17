"""Unit tests for translate._fit_subtitle + write_translated wrapping."""
from clipforge import translate


def test_fit_short_unchanged():
    assert translate._fit_subtitle("Short line") == "Short line"


def test_fit_wraps_long_to_two_lines():
    t = ("Why couldn't I think of filming this before and showing it "
         "to everyone right now")
    out = translate._fit_subtitle(t)
    lines = out.split("\n")
    assert len(lines) <= 2
    assert all(len(l) <= 42 for l in lines)


def test_fit_truncates_huge_text_with_ellipsis():
    t = "word " * 60
    out = translate._fit_subtitle(t.strip())
    lines = out.split("\n")
    assert len(lines) == 2
    assert lines[-1].endswith("…")


def test_fit_hard_slices_spaceless_cjk():
    t = "한동안이걸찍을생각을하지못했을까요" * 3  # no spaces, long
    out = translate._fit_subtitle(t)
    lines = out.split("\n")
    assert len(lines) == 2
    assert all(0 < len(l) <= 42 for l in lines)


def test_write_translated_wraps_cues(tmp_path):
    cues = [{"index": 1, "start_ms": 0, "end_ms": 2000,
             "target": "x" * 60 + " tail words here to wrap nicely"}]
    srt = tmp_path / "out.en.srt"
    t_cues = translate.write_translated(cues, str(srt))
    body = srt.read_text()
    assert len(t_cues) == 1
    for line in t_cues[0]["text"].split("\n"):
        assert len(line) <= 42
    assert " --> " in body
