"""ClipForge pipeline orchestrator.

Usage:
    python -m clipforge.pipeline --input <video-url-or-file> \
        [--whisper-model base] [--llm-model qwen2.5:3b] [--no-llm] \
        [--max-clip 60] [--min-clip 15] [--target-lang es] \
        [--workdir work] [--outdir out]

Stages: download -> transcribe -> pick moment -> cut -> reframe 9:16 ->
karaoke captions + hook -> (optional) Argos translation.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess

from . import captions, pick, reframe, transcribe


def download(source, workdir):
    if os.path.isfile(source):
        print(f"[download] local file: {source}")
        return source
    out_tpl = os.path.join(workdir, "source.%(ext)s")
    base = ["yt-dlp", "--no-playlist", "-f", "best[ext=mp4]/best",
            "-o", out_tpl]
    attempts = [[]]
    if "youtube.com" in source or "youtu.be" in source:
        # Cloud IPs are often bot-walled; some player clients get through.
        attempts += [["--extractor-args", f"youtube:player_client={c}"]
                     for c in ("android", "tv", "web_embedded")]
    last_err = ""
    for extra in attempts:
        for old in glob.glob(os.path.join(workdir, "source.*")):
            os.remove(old)
        proc = subprocess.run(base + extra + [source],
                              capture_output=True, text=True)
        if proc.returncode == 0 and glob.glob(
                os.path.join(workdir, "source.*")):
            break
        last_err = proc.stderr or proc.stdout
    else:
        raise RuntimeError(f"download failed:\n{last_err[-1500:]}")
    matches = sorted(glob.glob(os.path.join(workdir, "source.*")))
    if not matches:
        raise RuntimeError("yt-dlp produced no file")
    print(f"[download] {source} -> {matches[0]}")
    return matches[0]


def cut_segment(source, start, end, workdir):
    seg = os.path.join(workdir, "segment.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", source,
        "-t", f"{end - start:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", seg,
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[cut] {start:.1f}-{end:.1f}s -> segment.mp4")
    return seg


def clip_words(words, start, end):
    out = []
    for w in words:
        if w["end"] <= start or w["start"] >= end:
            continue
        out.append({"start": max(0.0, w["start"] - start),
                    "end": min(end, w["end"]) - start,
                    "text": w["text"]})
    return out


def main():
    ap = argparse.ArgumentParser(description="ClipForge pipeline")
    ap.add_argument("--input", required=True,
                    help="Direct video file URL (non-YouTube) or local path")
    ap.add_argument("--whisper-model", default="base")
    ap.add_argument("--llm-model", default="qwen2.5:3b")
    ap.add_argument("--ollama-url", default="http://localhost:11434")
    ap.add_argument("--no-llm", action="store_true",
                    help="Skip Ollama, use the heuristic moment picker")
    ap.add_argument("--max-clip", type=float, default=60.0)
    ap.add_argument("--min-clip", type=float, default=15.0)
    ap.add_argument("--target-lang", default="",
                    help="Translate captions into LANG via the configured "
                         "provider (e.g. es, hi)")
    ap.add_argument("--provider", default="",
                    help="LLM provider for translation: ollama | zai "
                         "(auto-detected when omitted)")
    ap.add_argument("--use-discover", action="store_true",
                    help="Use the multi-signal discovery engine instead of "
                         "the single-moment picker; writes candidates.json "
                         "with ranked, explainable candidates")
    ap.add_argument("--top-n", type=int, default=5,
                    help="Candidate count kept by --use-discover")
    ap.add_argument("--workdir", default="work")
    ap.add_argument("--outdir", default="out")
    args = ap.parse_args()

    os.makedirs(args.workdir, exist_ok=True)
    os.makedirs(args.outdir, exist_ok=True)
    args.outdir = os.path.abspath(args.outdir)

    source = download(args.input, args.workdir)
    transcript = transcribe.transcribe(source, args.whisper_model, args.workdir)
    if args.use_discover:
        from . import discover
        result = discover.discover_moments(
            transcript, audio_path=source, min_clip=args.min_clip,
            max_clip=args.max_clip, top_n=args.top_n)
        cpath = os.path.join(args.outdir, "candidates.json")
        with open(cpath, "w") as f:
            json.dump(result, f, indent=2)
        if not result["candidates"]:
            raise SystemExit("discovery found no candidates - check the "
                             "transcript or widen --min-clip/--max-clip")
        best = result["candidates"][0]
        moment = {"start": best["start_ms"] / 1000.0,
                  "end": best["end_ms"] / 1000.0,
                  "title": best["suggested_title"],
                  "hook": best["hook_summary"],
                  "reason": best["why_it_works"],
                  "source": "clipforge-discovery-v1",
                  "candidate_id": best["candidate_id"],
                  "overall_score": best["overall_score"]}
        print(f"[discover] {len(result['candidates'])} candidates -> "
              f"{cpath}; using rank 1 for the cut")
    else:
        moment = pick.pick_moment(
            transcript, args.ollama_url, args.llm_model,
            args.min_clip, args.max_clip, args.workdir, use_llm=not args.no_llm)
    start, end = moment["start"], moment["end"]

    segment = cut_segment(source, start, end, args.workdir)
    reframed = os.path.join(args.workdir, "reframed.mp4")
    reframe.reframe(segment, reframed)

    words = clip_words(transcript["words"], start, end)
    ass_path = os.path.join(args.workdir, "captions.ass")
    lines = captions.build_ass(words, moment.get("hook"), end - start, ass_path)
    final = os.path.join(args.outdir, "clip_final.mp4")
    captions.burn("reframed.mp4", "captions.ass", final, cwd=args.workdir)

    translated_ok = False
    translation_provider = None
    from . import subtitles as subs
    all_cues = subs.cues_from_transcript(transcript)
    window_cues = subs.clip_window_cues(all_cues, int(start * 1000),
                                        int(end * 1000))
    window_cues, _ = subs.auto_repair(window_cues)
    with open(os.path.join(args.outdir, "captions.srt"), "w") as f:
        f.write(subs.serialize_srt(window_cues))
    with open(os.path.join(args.outdir, "captions.vtt"), "w") as f:
        f.write(subs.serialize_vtt(window_cues))
    if args.target_lang:
        try:
            from . import providers
            from . import translate as xlate
            prov = providers.get_provider(args.provider or None)
            if prov is None:
                raise RuntimeError(
                    "no provider available (ollama/z-ai) - use --provider")
            translation_provider = prov.name
            translated = xlate.translate_cues(
                window_cues, args.target_lang, prov,
                source_lang=transcript["language"])
            t_cues = xlate.write_translated(
                translated,
                os.path.join(args.outdir,
                             f"captions.{args.target_lang}.srt"),
                os.path.join(args.outdir,
                             f"captions.{args.target_lang}.vtt"))
            bi_ass = os.path.join(args.workdir,
                                  f"captions.{args.target_lang}.ass")
            captions.build_bilingual_ass(words, t_cues, moment.get("hook"),
                                         end - start, bi_ass)
            t_out = os.path.join(args.outdir,
                                 f"clip_final.{args.target_lang}.mp4")
            captions.burn("reframed.mp4", os.path.basename(bi_ass), t_out,
                          cwd=args.workdir)
            translated_ok = True
        except Exception as exc:  # noqa: BLE001 - translation is optional
            print(f"[translate] skipped: {exc}")

    metadata = {
        "input": args.input,
        "language": transcript["language"],
        "whisper_model": args.whisper_model,
        "moment": moment,
        "target_lang": args.target_lang or None,
        "translated": translated_ok,
        "translation_provider": translation_provider,
        "subtitles_gates": subs.validate(window_cues)["gates"],
        "outputs": sorted(os.listdir(args.outdir)),
    }
    with open(os.path.join(args.outdir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    shutil.copy(os.path.join(args.workdir, "transcript.json"), args.outdir)
    shutil.copy(ass_path, args.outdir)
    print(f"[done] artifacts in {args.outdir}: {metadata['outputs']}")


if __name__ == "__main__":
    main()
