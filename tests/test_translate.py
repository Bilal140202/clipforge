"""Unit tests for translate: _fit_subtitle, write_translated, translate_hook."""
import pytest

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


class _FakeProvider:
    """Duck-typed provider: returns canned replies from .complete()."""

    def __init__(self, reply):
        self.reply = reply
        self.name = "fake"

    def complete(self, prompt, system=None):
        return self.reply


def test_translate_hook_empty_hook_returns_empty():
    assert translate.translate_hook("", "en", _FakeProvider("{}")) == ""


def test_translate_hook_translates_via_provider():
    p = _FakeProvider('{"translation": "  Why now?  "}')
    assert translate.translate_hook("왜 지금?", "en", p,
                                    source_lang="ko") == "Why now?"


def test_translate_hook_failure_is_loud():
    with pytest.raises(RuntimeError):
        translate.translate_hook("왜 지금?", "en",
                                 _FakeProvider("not json at all"))


def test_fit_hook_wraps_to_big_font_lines():
    out = translate.fit_hook("Why couldn't I think of filming this before?")
    for line in out.split("\n"):
        assert len(line) <= 18
    assert len(out.split("\n")) <= 3
