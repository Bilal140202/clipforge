"""Unit tests for clipforge.captions pure logic (no ffmpeg burn)."""
from clipforge import captions


def test_group_lines_respects_word_limit():
    words = [{"start": i * 0.5, "end": i * 0.5 + 0.4, "text": f"w{i}"}
             for i in range(10)]
    lines = captions.group_lines(words)
    assert all(len(l) <= captions.MAX_WORDS_PER_LINE for l in lines)
    assert sum(len(l) for l in lines) == 10


def test_group_lines_respects_time_span():
    words = [{"start": i * 1.0, "end": i * 1.0 + 0.4, "text": "w"}
             for i in range(10)]
    lines = captions.group_lines(words)
    for line in lines:
        assert line[-1]["start"] - line[0]["start"] <= \
            captions.MAX_LINE_SECONDS + 1e-6


def test_karaoke_text_escapes_braces():
    words = [{"start": 0.0, "end": 0.5, "text": "{odd}"}]
    text = captions.karaoke_text(words)
    assert "{\\kf" in text
    assert "(odd)" in text and "{odd}" not in text


def test_ass_time_format():
    assert captions._ass_time(0) == "0:00:00.00"
    assert captions._ass_time(75.256) == "0:01:15.26"
    assert captions._ass_time(-3) == "0:00:00.00"


def test_build_ass_writes_dialogue_and_hook(tmp_path):
    words = [{"start": i * 0.4, "end": i * 0.4 + 0.3, "text": f"w{i}"}
             for i in range(8)]
    path = tmp_path / "cap.ass"
    lines = captions.build_ass(words, "WATCH THIS", 5.0, str(path))
    assert lines and path.exists()
    body = path.read_text()
    assert body.count("Dialogue:") == len(lines) + 1  # + hook event
    assert "WATCH THIS" in body
