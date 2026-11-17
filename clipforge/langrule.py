"""The permanent caption-language rule — one decision table, no exceptions.

Owner rule (permanent since 2026-11-17, issue #17): a clip's captions
either speak the video's own language, or are FULL English. When they are
English, NOTHING else appears on screen: no source-language karaoke, no
bilingual stack, no other language. One caption, one language.

How to read this module (plain words):
- "source language"  = the language the person in the video is speaking
                       (whisper detects it, transcript["language"]).
- "caption language" = the language you want the captions written in.
- Same language      -> captions in that language (karaoke style).
- English requested  -> FULL English only: every caption AND the hook are
                        translated; the original language never appears.
- Anything else      -> the tool ASKS: same-language or English? A
                        human in a terminal gets a prompt; an agent
                        (non-TTY) gets exit code 2 with the exact
                        question to relay to the user.
"""
from dataclasses import dataclass

ANSWERS = ("same", "en", "other")


class CaptionChoiceRequired(Exception):
    """The rule needs a human decision: same-language or English.

    Carries `question` (single line) and `choices` (list) so any caller
    — CLI prompt, chat relay, web UI — can present it verbatim."""

    def __init__(self, question, choices):
        self.question = question
        self.choices = [str(c) for c in choices]
        super().__init__(f"{question} choices: {'; '.join(self.choices)}")


@dataclass(frozen=True)
class CaptionPlan:
    """What the renderer must do, decided once, by the rule."""

    caption_lang: str   # "" = the video's own language (karaoke captions)
    english_only: bool  # True = full English; no source-language captions
    translate: bool     # True = run the translation provider
    note: str           # one-line human explanation of the decision


def normalize_lang(code):
    """'ko-KR' -> 'ko', 'EN_US' -> 'en', '  ' -> ''. Never raises."""
    if not code:
        return ""
    head = str(code).strip().lower().replace("_", "-").split("-")[0]
    return head.strip()


def resolve_caption_plan(source_lang, caption_lang=None, mode="bilingual",
                         *, answer=None):
    """Decide the caption plan for a clip. Pure function: same inputs,
    same plan. Raises CaptionChoiceRequired when the rule says a human
    must choose (call again with `answer` in ANSWERS to proceed)."""
    src = normalize_lang(source_lang)
    cap = normalize_lang(caption_lang)

    if not cap:
        return CaptionPlan("", False, False,
                           "no caption language requested -> same-language "
                           "captions in the video's own language"
                           + (f" ({src})" if src else ""))

    if src and cap == src:
        return CaptionPlan(src, False, False,
                           f"captions requested in the video's own language "
                           f"({src}) -> same-language captions, no "
                           f"translation")

    if cap == "en":
        note = ("English requested -> English-only captions: translated "
                "cues + English hook, no source-language captions "
                "(permanent rule #17)")
        if normalize_lang(mode) == "bilingual":
            note += ("; --caption-mode bilingual was OVERRIDDEN by the "
                     "permanent rule (one caption, one language)")
        return CaptionPlan("en", True, True, note)

    if not src:
        question = (f"video speech language unknown and captions were "
                    f"requested in {cap.upper()}: full English, or "
                    f"proceed with {cap.upper()} anyway?")
        ans = _checked_answer(answer)
        if ans == "en":
            return CaptionPlan("en", True, True,
                               "source language unknown; user chose English "
                               "-> English-only captions (rule #17)")
        if ans == "other":
            return CaptionPlan(cap, False, True,
                               f"source language unknown; user chose to "
                               f"proceed with {cap} captions anyway")
        raise CaptionChoiceRequired(
            question,
            ["full English only (recommended; permanent rule #17)",
             f"proceed with {cap} captions anyway"])

    if src == "en":
        return CaptionPlan(
            "en", False, False,
            f"captions in {cap.upper()} were requested but the video is "
            f"already English -> English captions (same-language, no "
            f"translation)")

    # foreign video, foreign non-English caption request -> the rule's ask
    question = (f"video speech is {src.upper()} but captions were requested "
                f"in {cap.upper()}: captions in the video's own language, "
                f"or English?")
    ans = _checked_answer(answer)
    if ans == "same":
        return CaptionPlan(src, False, False,
                           f"user chose same-language ({src}) captions")
    if ans == "en":
        return CaptionPlan("en", True, True,
                           "user chose English -> English-only captions "
                           "(permanent rule #17)")
    raise CaptionChoiceRequired(
        question,
        [f"same-language ({src}) karaoke captions",
         "full English only (permanent rule: no source-language captions)"])


def _checked_answer(answer):
    if answer is None:
        return None
    a = normalize_lang(answer)  # harmless for "same"/"other"
    if a == "same":
        return "same"
    if a == "en":
        return "en"
    if a == "other":
        return "other"
    raise ValueError(f"answer must be one of {ANSWERS}, got {answer!r}")
