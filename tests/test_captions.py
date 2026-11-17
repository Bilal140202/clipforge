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


def test_style_layout_keeps_trans_clear_of_captions():
    """Regression (KI-007 / issue #15): the Trans line must sit fully above
    the worst-case caption block, so a 2-3 line wrapped karaoke caption can
    never collide with the translation."""
    styles = {}
    for row in captions.HEADER.splitlines():
        if row.startswith("Style:"):
            parts = row.split(",")
            styles[parts[0].split()[1]] = {
                "fontsize": float(parts[2]), "margin_v": float(parts[20])}
    cap, tr = styles["Caption"], styles["Trans"]
    # PlayRes 1920-tall: caption block grows upward from its bottom margin;
    # allow up to 3 display lines to be safe (CJK tokens wrap wide).
    cap_top_worst = 1920 - cap["margin_v"] - 3 * cap["fontsize"] * 1.25
    trans_bottom = 1920 - tr["margin_v"]
    # require a real clearance gap — boundary-touching counts as a failure
    # (observed on owner footage: 2-line Trans + 3-line Caption met at
    # exactly the boundary and collided).
    assert trans_bottom >= cap_top_worst + 40, (
        f"Trans bottom {trans_bottom} within 40px of caption worst-case "
        f"top {cap_top_worst:.0f}")
    # and the caption must fit 2+ display lines inside the safe band.
    assert cap["margin_v"] + 2 * cap["fontsize"] * 1.25 < 1920 * 0.5


def test_build_translation_only_ass_has_no_source_karaoke(tmp_path):
    """Issue #16: translation-only mode must emit ONLY TransSolo + Hook
    events — no source-language karaoke Dialogue at all."""
    cues = [{"start_ms": 100, "end_ms": 2000, "text": "Hello there"},
            {"start_ms": 2500, "end_ms": 4000, "text": "Second line"}]
    path = tmp_path / "solo.ass"
    events = captions.build_translation_only_ass(cues, "HOOK TEXT", 6.0,
                                                 str(path))
    body = path.read_text()
    assert body.count("Dialogue:") == 3  # 2 cues + hook
    assert body.count(",TransSolo,,") == 2  # Dialogue rows only (header
    # declares the style too, so count the dialogue-form occurrences)
    assert "HOOK TEXT" in body
    # styles may be declared in the header; no Dialogue may USE the
    # source-language Caption style, and no karaoke timing may appear
    for row in body.splitlines():
        if row.startswith("Dialogue:"):
            assert ",Caption,," not in row, row
    assert "\\kf" not in body  # no karaoke timing anywhere
    assert all(e.startswith("Dialogue: 0,") or e.startswith("Dialogue: 2,")
               for e in events)


def test_transsolo_sits_in_caption_zone():
    """TransSolo (sole caption in translation mode) must occupy the normal
    caption zone — bottom margin like Caption, not the raised bilingual
    Trans position that would leave the caption area empty."""
    styles = {}
    for row in captions.HEADER.splitlines():
        if row.startswith("Style:"):
            parts = row.split(",")
            styles[parts[0].split()[1]] = {
                "fontsize": float(parts[2]), "margin_v": float(parts[20])}
    cap, solo = styles["Caption"], styles["TransSolo"]
    assert solo["margin_v"] == cap["margin_v"]
    assert solo["fontsize"] >= cap["fontsize"] - 4
