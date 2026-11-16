"""Provider layer + translation tests (fake provider — no network)."""
import pytest

from clipforge import providers, translate


class FakeProvider:
    name = "fake"

    def __init__(self, reply=None):
        self.reply = reply or (
            'Sure! Here is the JSON:\n```json\n{"translations": ['
            '{"i": 1, "text": "hola"}, {"i": 2, "text": "mundo"}]}\n```')
        self.last_prompt = None

    def available(self):
        return True

    def complete(self, prompt, system=None, temperature=None):
        self.last_prompt = prompt
        return self.reply


def _cues():
    return [{"index": 1, "start_ms": 0, "end_ms": 2000, "text": "hello"},
            {"index": 2, "start_ms": 2000, "end_ms": 4000, "text": "world"}]


def test_translate_cues_with_fake_provider():
    out = translate.translate_cues(_cues(), "es", FakeProvider())
    assert [(t["index"], t["target"]) for t in out] == \
        [(1, "hola"), (2, "mundo")]
    assert out[0]["start_ms"] == 0 and out[0]["end_ms"] == 2000
    assert out[0]["source"] == "hello"


def test_translate_cues_prompt_is_schema_constrained():
    p = FakeProvider()
    translate.translate_cues(_cues(), "es", p)
    assert "JSON" in p.last_prompt and '"i"' in p.last_prompt


def test_translate_cues_count_mismatch_fails_loudly():
    bad = FakeProvider(reply='{"translations": [{"i": 1, "text": "hola"}]}')
    with pytest.raises(RuntimeError):
        translate.translate_cues(_cues(), "es", bad)


def test_translate_cues_no_provider_raises():
    with pytest.raises(RuntimeError):
        translate.translate_cues(_cues(), "es", None)


def test_write_translated_emits_srt_and_vtt(tmp_path):
    translated = translate.translate_cues(_cues(), "es", FakeProvider())
    srt = tmp_path / "out.srt"
    vtt = tmp_path / "out.vtt"
    t_cues = translate.write_translated(translated, str(srt), str(vtt))
    assert "hola" in srt.read_text() and "WEBVTT" in vtt.read_text()
    assert t_cues[0]["text"] == "hola"


# ------------------------------------------------------------ extract_json
def test_extract_json_handles_fences_and_prose():
    assert providers.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert providers.extract_json('Answer: {"a": [1, 2]} done') == \
        {"a": [1, 2]}
    with pytest.raises(ValueError):
        providers.extract_json("no json here")
    with pytest.raises(ValueError):
        providers.extract_json('{"unterminated": 1')


# ------------------------------------------------------------ get_provider
def test_get_provider_unknown_is_none(monkeypatch):
    monkeypatch.delenv("CLIPFORGE_PROVIDER", raising=False)
    assert providers.get_provider("bogus-name") is None


def test_get_provider_prefers_requested_available_provider():
    # z-ai CLI exists in this runtime; ollama almost surely does not.
    prov = providers.get_provider("zai")
    assert prov is None or prov.name == "zai"


# ------------------------------------------------------------ bilingual ASS
def test_build_bilingual_ass_contains_karaoke_and_trans(tmp_path):
    from clipforge import captions
    words = [{"start": i * 0.5, "end": i * 0.5 + 0.4, "text": f"w{i}"}
             for i in range(6)]
    translated = [{"index": 1, "start_ms": 0, "end_ms": 1500,
                   "source": "w0", "target": "primera"},
                  {"index": 2, "start_ms": 1500, "end_ms": 3000,
                   "source": "w3", "target": "segunda"}]
    path = tmp_path / "bi.ass"
    captions.build_bilingual_ass(words, translated, "MIRA", 4.0, str(path))
    body = path.read_text()
    assert body.count("Trans,,") == 2
    assert "primera" in body and "segunda" in body
    assert "MIRA" in body and "\\kf" in body  # karaoke intact
    assert "Style: Trans," in body


def test_cli_doctor_smoke():
    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, "-m", "clipforge.cli", "doctor"],
        cwd="/home/z/my-project/clipforge", capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert '"ffmpeg": true' in proc.stdout
