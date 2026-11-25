#!/usr/bin/env python3
"""Build a narrated code-lesson page: source file + steps JSON -> one HTML page (+ an mp3 folder if TTS works).

usage: python3 build.py SOURCE STEPS_JSON OUT_HTML [--title T] [--lang zh-CN|ja-JP|en-US]
                        [--tts auto|openai|browser] [--voice coral] [--audio DIR]

STEPS_JSON = [{"part": "总览", "from": 1, "to": 4, "title": "...", "say": "..."}, ...]   (lines 1-based, inclusive)

Speech:
  --tts auto     (default) OpenAI TTS -> OUT_HTML's stem + "_audio/"; no key or any error -> browser speech
  --tts openai   OpenAI TTS, stop with an error if it fails
  --tts browser  browser speech only (no API call)
  --audio DIR    use existing step_01.mp3 ... instead of synthesizing
The page itself also falls back to browser speech if an mp3 cannot be loaded.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from tts_openai import TTSError, synthesize  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("source")
p.add_argument("steps")
p.add_argument("out")
p.add_argument("--title")
p.add_argument("--lang", default="zh-CN")
p.add_argument("--tts", choices=["auto", "openai", "browser"], default="auto")
p.add_argument("--voice", default="coral")
p.add_argument("--audio")
a = p.parse_args()

src, out = Path(a.source), Path(a.out)
code = src.read_text(encoding="utf-8")
n_lines = len(code.rstrip("\n").split("\n"))
steps = json.loads(Path(a.steps).read_text(encoding="utf-8"))

# ---- check the steps ----
assert isinstance(steps, list) and steps, "steps must be a non-empty list"
for i, s in enumerate(steps, 1):
    missing = {"from", "to", "title", "say"} - set(s)
    assert not missing, f"step {i}: missing {missing}"
    assert 1 <= s["from"] <= s["to"] <= n_lines, f"step {i}: lines {s['from']}-{s['to']} outside 1-{n_lines}"

# ---- speech: existing mp3s, OpenAI TTS, or browser speech ----
audio_dir, speech = None, "browser speech"
if a.audio:
    audio_dir, speech = Path(a.audio), "existing audio"
elif a.tts != "browser":
    target = out.with_name(out.stem + "_audio")
    print(f"OpenAI TTS -> {target}/")
    try:
        synthesize(steps, target, a.lang, a.voice)
        audio_dir, speech = target, "OpenAI TTS"
    except TTSError as e:
        if a.tts == "openai":
            sys.exit(f"TTS failed: {e}")
        print(f"  fallback to browser speech: {e}")  # auto: no key / error -> the page uses the browser's voices

lesson = {"title": a.title or f"{src.name} 讲解", "file": src.name, "lang": a.lang, "code": code, "steps": steps}
if audio_dir:
    files = [audio_dir / f"step_{i:02d}.mp3" for i in range(1, len(steps) + 1)]
    lost = [str(f) for f in files if not f.exists()]
    assert not lost, f"missing audio: {lost}"
    lesson["audio"] = [os.path.relpath(f.resolve(), out.resolve().parent).replace(os.sep, "/") for f in files]

# ---- page ----
blob = json.dumps(lesson, ensure_ascii=False).replace("</", "<\\/")  # never close the <script> early
html = (HERE / "template.html").read_text(encoding="utf-8")
html = html.replace("{{TITLE}}", lesson["title"].replace("<", "&lt;")).replace("{{LESSON_JSON}}", blob)
out.write_text(html, encoding="utf-8")
print(f"wrote {out}: {len(steps)} steps, {n_lines} lines, speech = {speech}")
if audio_dir:  # what to pass to the Artifact tool as `files`
    print("AUDIO_FILES " + json.dumps({rel: str(out.resolve().parent / rel) for rel in lesson["audio"]}, ensure_ascii=False))
