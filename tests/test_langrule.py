"""Decision-table tests for the permanent caption-language rule (#17).

Every row of the rule table gets a test, plus both exception paths.
If you change langrule.py, change this file in the same commit.
"""
import pytest

from clipforge import langrule
from clipforge.langrule import CaptionChoiceRequired, resolve_caption_plan


def test_no_caption_lang_means_same_language():
    plan = resolve_caption_plan("ko", None)
    assert plan.caption_lang == "" and not plan.translate
    assert not plan.english_only


def test_same_language_karaoke():
    plan = resolve_caption_plan("ko", "ko")
    assert plan.caption_lang == "ko" and not plan.translate
    assert not plan.english_only


def test_same_language_normalizes_region_codes():
    assert resolve_caption_plan("ko-KR", "ko_KR").caption_lang == "ko"


def test_english_choice_is_full_english_only():
    plan = resolve_caption_plan("ko", "en", "translation")
    assert plan.caption_lang == "en"
    assert plan.english_only and plan.translate
    assert "OVERRIDDEN" not in plan.note


def test_bilingual_mode_is_overridden_by_the_rule():
    plan = resolve_caption_plan("ko", "en", "bilingual")
    assert plan.english_only
    assert "OVERRIDDEN" in plan.note


def test_foreign_caption_request_asks_the_user():
    with pytest.raises(CaptionChoiceRequired) as ask:
        resolve_caption_plan("ko", "es")
    assert "KO" in ask.value.question and "ES" in ask.value.question
    assert len(ask.value.choices) == 2


def test_ask_resolved_with_same_language():
    plan = resolve_caption_plan("ko", "es", answer="same")
    assert plan.caption_lang == "ko" and not plan.translate


def test_ask_resolved_with_english():
    plan = resolve_caption_plan("ko", "es", answer="en")
    assert plan.english_only and plan.translate


def test_unknown_source_english_is_still_english_only():
    plan = resolve_caption_plan(None, "en")
    assert plan.english_only and plan.translate


def test_unknown_source_other_language_asks():
    with pytest.raises(CaptionChoiceRequired):
        resolve_caption_plan(None, "es")
    plan = resolve_caption_plan(None, "es", answer="other")
    assert plan.caption_lang == "es" and plan.translate
    assert not plan.english_only


def test_english_video_stays_english_no_ask():
    plan = resolve_caption_plan("en", "ko")
    assert plan.caption_lang == "en" and not plan.translate
    assert not plan.english_only


def test_bad_answer_is_rejected():
    with pytest.raises(ValueError):
        resolve_caption_plan("ko", "es", answer="maybe")


def test_normalize_lang_basics():
    assert langrule.normalize_lang("ko-KR") == "ko"
    assert langrule.normalize_lang("EN_us") == "en"
    assert langrule.normalize_lang("") == ""
    assert langrule.normalize_lang(None) == ""
