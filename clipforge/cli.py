"""ClipForge CLI: one stable entrypoint for agents and humans.

Subcommands:
  doctor      environment + dependency health check (machine-readable)
  transcribe  local faster-whisper transcription (word timestamps)
  discover    multi-signal moment discovery (ranked candidates)
  subtitles   build / validate / repair / convert subtitle cues
  translate   translate cues via the configured provider
  pipeline    full flow: input -> transcribe -> discover -> render -> export

Every subcommand writes JSON or media to --out; nothing prints fake progress.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from . import discover as discover_mod
from . import subtitles as subs
from . import transcribe as transcribe_mod


def cmd_doctor(args):
    checks = {}
    checks["ffmpeg"] = bool(shutil.which("ffmpeg"))
    checks["ffprobe"] = bool(shutil.which("ffprobe"))
    try:
        import faster_whisper  # noqa: F401
        checks["faster_whisper"] = True
    except ImportError:
        checks["faster_whisper"] = False
    from . import providers
    prov = providers.get_provider(args.provider or None)
    checks["provider"] = prov.name if prov else None
    checks["translation_possible"] = prov is not None
    result = {"ok": all([checks["ffmpeg"], checks["ffprobe"],
                         checks["faster_whisper"]]), "checks": checks}
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def cmd_transcribe(args):
    transcript = transcribe_mod.transcribe(args.input, args.model,
                                           os.path.dirname(
                                               os.path.abspath(args.out))
                                           or ".")
    dest = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "w") as f:
        json.dump(transcript, f)
    print(f"[transcribe] wrote {dest}")
    return 0


def cmd_discover(args):
    with open(args.transcript) as f:
        transcript = json.load(f)
    result = discover_mod.discover_moments(
        transcript, audio_path=args.audio or None,
        min_clip=args.min_clip, max_clip=args.max_clip, top_n=args.top_n)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".",
                exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    for c in result["candidates"]:
        print(f"[discover] #{c['rank']} {c['overall_score']:5.1f} "
              f"{c['start_ms'] / 1000:7.2f}-{c['end_ms'] / 1000:7.2f}s "
              f"{c['hook_summary'][:48]!r}")
    return 0


def cmd_subtitles(args):
    if args.op == "from-transcript":
        with open(args.transcript) as f:
            cues = subs.cues_from_transcript(json.load(f))
    elif args.op == "validate" or args.op == "repair":
        cues = _load_cues(args)
    else:
        cues = _load_cues(args)
    if args.op == "validate":
        report = subs.validate(cues)
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 2
    if args.op == "repair":
        cues, actions = subs.auto_repair(cues)
        report = subs.validate(cues)
        out = {"actions": actions, "post_repair": report, "cues": cues}
        _write_out(args.out, out)
        print(f"[subtitles] {len(actions)} repairs; "
              f"post_repair passed={report['passed']}")
        return 0 if report["passed"] else 2
    # from-transcript / convert: validate, repair, then serialize
    fixed, _ = subs.auto_repair(cues)
    report = subs.validate(fixed)
    text = (subs.serialize_vtt(fixed) if args.op == "to-vtt"
            else subs.serialize_srt(fixed))
    if args.out:
        _write_out(args.out, text)
    else:
        print(text, end="")
    print(f"[subtitles] wrote {len(fixed)} cues; gates passed="
          f"{report['passed']}", file=sys.stderr)
    return 0


def _load_cues(args):
    if args.subs_file.endswith(".vtt"):
        return subs.parse_vtt(open(args.subs_file).read())
    return subs.parse_srt(open(args.subs_file).read())


def _write_out(path, data):
    with open(path, "w") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2)


def cmd_translate(args):
    from . import providers, translate
    prov = providers.get_provider(args.provider or None)
    if prov is None:
        print(json.dumps({"translated": False,
                          "reason": "no provider available"}))
        return 1
    with open(args.cues) as f:
        data = json.load(f)
    cues = data["cues"] if isinstance(data, dict) else data
    translated = translate.translate_cues(cues, args.lang, prov)
    out = {"lang": args.lang, "provider": prov.name,
           "translated": translated}
    _write_out(args.out, out)
    print(f"[translate] {len(translated)} cues -> {args.lang} "
          f"via {prov.name}")
    return 0


def cmd_render(args):
    from . import captions, reframe
    start_ms, end_ms = int(args.start_ms), int(args.end_ms)
    segment = _cut(args.source, start_ms, end_ms, args.workdir)
    reframed = os.path.join(args.workdir, "reframed.mp4")
    reframe.reframe(segment, reframed)
    with open(args.transcript) as f:
        transcript = json.load(f)
    all_cues = subs.cues_from_transcript(transcript)
    window = subs.clip_window_cues(all_cues, start_ms, end_ms)
    window, _ = subs.auto_repair(window)
    words = _clip_words(transcript["words"], start_ms, end_ms)
    dur_s = (end_ms - start_ms) / 1000
    final = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(final) or ".", exist_ok=True)
    solo = bool(args.translate_lang) and args.caption_mode == "translation"
    if not solo:
        ass_path = os.path.join(args.workdir, "captions.ass")
        captions.build_ass(words, args.hook, dur_s, ass_path)
        captions.burn("reframed.mp4", "captions.ass", final,
                      cwd=os.path.abspath(args.workdir))
    with open(os.path.splitext(final)[0] + ".srt", "w") as f:
        f.write(subs.serialize_srt(window))
    with open(os.path.splitext(final)[0] + ".vtt", "w") as f:
        f.write(subs.serialize_vtt(window))
    if args.translate_lang:
        _translate_burn(args, window, words, reframed, final, dur_s,
                        transcript.get("language"), primary=solo)
    print(f"[render] wrote {final}")
    return 0


def _translate_burn(args, window, words, reframed, final, dur_s,
                    source_lang, primary=False):
    from . import captions, providers, translate
    prov = providers.get_provider(args.provider or None)
    if prov is None:
        print("[render] translation skipped: no provider")
        if primary:
            raise SystemExit("[render] --caption-mode translation requires "
                             "a working provider (no fallback captions)")
        return
    try:
        translated = translate.translate_cues(window, args.translate_lang,
                                              prov,
                                              source_lang=source_lang)
        t_cues = translate.write_translated(
            translated, os.path.splitext(final)[0]
            + f".{args.translate_lang}.srt")
        tl_path = os.path.join(os.path.abspath(args.workdir),
                               f"captions.{args.translate_lang}.ass")
        if primary:
            captions.build_translation_only_ass(t_cues, args.hook, dur_s,
                                                tl_path)
            captions.burn(os.path.basename(reframed),
                          os.path.basename(tl_path), final,
                          cwd=os.path.abspath(args.workdir))
            print(f"[render] translation-only captions -> {final}")
            return
        captions.build_bilingual_ass(words, t_cues, args.hook, dur_s,
                                     tl_path)
        t_out = os.path.splitext(final)[0] + f".{args.translate_lang}.mp4"
        captions.burn(os.path.basename(reframed), os.path.basename(tl_path),
                      t_out, cwd=os.path.abspath(args.workdir))
        print(f"[render] bilingual variant -> {t_out}")
    except Exception as exc:  # noqa: BLE001 - translation stays optional
        print(f"[render] translation failed (non-fatal): {exc}")
        if primary:
            raise SystemExit("[render] translation-only render failed; "
                             "no output written") from exc


def _cut(source, start_ms, end_ms, workdir):
    os.makedirs(workdir, exist_ok=True)
    seg = os.path.join(workdir, "segment.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{start_ms / 1000:.3f}", "-i", source,
         "-t", f"{(end_ms - start_ms) / 1000:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
         seg], check=True, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    return seg


def _clip_words(words, start_ms, end_ms):
    s, e = start_ms / 1000, end_ms / 1000
    out = []
    for w in words:
        if w["end"] <= s or w["start"] >= e:
            continue
        out.append({"start": max(0.0, w["start"] - s),
                    "end": min(e, w["end"]) - s, "text": w["text"]})
    return out


def cmd_pipeline(args):
    sys.argv = [sys.argv[0]] + args.forward
    from . import pipeline
    pipeline.main()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="clipforge",
                                 description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("doctor", help="environment health check")
    p.add_argument("--provider", default="")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("transcribe", help="local transcription")
    p.add_argument("--input", required=True)
    p.add_argument("--model", default="base")
    p.add_argument("--out", default="transcript.json")
    p.set_defaults(fn=cmd_transcribe)

    p = sub.add_parser("discover", help="moment discovery")
    p.add_argument("--transcript", required=True)
    p.add_argument("--audio", default="")
    p.add_argument("--top-n", type=int, default=5)
    p.add_argument("--min-clip", type=float, default=15)
    p.add_argument("--max-clip", type=float, default=60)
    p.add_argument("--out", default="candidates.json")
    p.set_defaults(fn=cmd_discover)

    p = sub.add_parser("subtitles", help="subtitle I/O and gates")
    p.add_argument("op", choices=["from-transcript", "validate", "repair",
                                  "to-srt", "to-vtt"])
    p.add_argument("--transcript")
    p.add_argument("--subs-file")
    p.add_argument("--out", default="")
    p.set_defaults(fn=cmd_subtitles)

    p = sub.add_parser("translate", help="translate cues via provider")
    p.add_argument("--cues", required=True)
    p.add_argument("--lang", required=True)
    p.add_argument("--provider", default="")
    p.add_argument("--out", default="translated.json")
    p.set_defaults(fn=cmd_translate)

    p = sub.add_parser("render", help="cut+reframe+caption a window")
    p.add_argument("--source", required=True)
    p.add_argument("--transcript", required=True)
    p.add_argument("--start-ms", type=int, required=True)
    p.add_argument("--end-ms", type=int, required=True)
    p.add_argument("--hook", default="")
    p.add_argument("--workdir", default="work")
    p.add_argument("--out", default="clip_final.mp4")
    p.add_argument("--translate-lang", default="")
    p.add_argument("--caption-mode", default="bilingual",
                   choices=["bilingual", "translation"],
                   help="translation mode: the main output carries ONLY the "
                        "translated line + hook (no source-language "
                        "karaoke); bilingual: karaoke + raised translation "
                        "variant as before")
    p.add_argument("--provider", default="")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("pipeline", help="full flow (legacy flags apply)")
    p.add_argument("forward", nargs=argparse.REMAINDER)
    p.set_defaults(fn=cmd_pipeline)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
