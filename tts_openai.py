#!/usr/bin/env python3
"""Synthesize each lesson step to an mp3 with the OpenAI TTS API (standard library only).

usage: python3 tts_openai.py STEPS_JSON OUT_DIR [--voice coral] [--model gpt-4o-mini-tts] [--lang zh-CN]
(normally called by build.py --tts auto)

API key: environment variable OPENAI_API_KEY, or the file ~/.config/code-lesson/openai_key (chmod 600).
Results are cached in ~/.cache/code-lesson/ by (model, voice, instructions, text): rebuilding does not pay twice.
Writes OUT_DIR/step_01.mp3, step_02.mp3, ...
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

KEY_FILE = Path.home() / ".config/code-lesson/openai_key"
CACHE = Path.home() / ".cache/code-lesson"
INSTRUCTIONS = {
    "zh": "用自然、亲切的普通话讲解，像一位耐心的老师在给学生讲代码。语速适中，句子之间有自然停顿，英文术语按英文读。",
    "ja": "自然で親しみやすい日本語で、落ち着いた先生がコードを説明するように話してください。英語の用語は英語で読んでください。",
    "en": "Speak naturally and warmly, like a patient teacher walking a student through code.",
}


class TTSError(Exception):
    pass


def find_key():
    """API key from the environment or the key file; None if there is none."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
    return key or None


def synthesize(steps, out_dir, lang="zh-CN", voice="coral", model="gpt-4o-mini-tts", log=print):
    """One mp3 per step into out_dir. Raises TTSError (no key, HTTP error, network error)."""
    key = find_key()
    if not key:
        raise TTSError(f"no API key (OPENAI_API_KEY or {KEY_FILE})")
    instructions = INSTRUCTIONS.get(lang[:2].lower(), INSTRUCTIONS["en"])
    out = Path(out_dir)
    CACHE.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    for i, s in enumerate(steps, 1):
        text = s["say"]
        h = hashlib.sha256(json.dumps([model, voice, instructions, text], ensure_ascii=False).encode()).hexdigest()[:20]
        cached = CACHE / f"{h}.mp3"
        if cached.exists():
            log(f"  step {i:2d}: cached")
        else:
            body = {"model": model, "voice": voice, "input": text, "response_format": "mp3"}
            if "tts-1" not in model:  # the older tts-1 models do not take instructions
                body["instructions"] = instructions
            req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=json.dumps(body).encode(),
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    audio = r.read()
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace").replace(key, "***")[:300]
                raise TTSError(f"step {i}: HTTP {e.code}: {msg}") from None
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                raise TTSError(f"step {i}: network error: {e}") from None
            tmp = cached.with_suffix(".part")
            tmp.write_bytes(audio)
            tmp.replace(cached)  # only complete files enter the cache
            log(f"  step {i:2d}: synthesized ({len(text)} chars)")
        shutil.copyfile(cached, out / f"step_{i:02d}.mp3")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("steps")
    p.add_argument("out_dir")
    p.add_argument("--voice", default="coral")
    p.add_argument("--model", default="gpt-4o-mini-tts")
    p.add_argument("--lang", default="zh-CN")
    a = p.parse_args()
    try:
        synthesize(json.loads(Path(a.steps).read_text(encoding="utf-8")), a.out_dir, a.lang, a.voice, a.model)
    except TTSError as e:
        sys.exit(str(e))
    print(f"wrote mp3 files to {a.out_dir}")
