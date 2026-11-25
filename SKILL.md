---
name: code-lesson
description: Turn a source file into a narrated, section-by-section code walkthrough page (OpenAI TTS voice when a key exists, otherwise the browser's own speech; the matching lines are highlighted while each part is read). Use when the user asks to explain / teach / walk through a script with voice, 语音教学, 讲解脚本, コード解説を読み上げ, or invokes /code-lesson <file>.
---

# Code lesson (narrated walkthrough) · v0.1

Input: a source file path (ask only if none is given or obvious from context).
Output: one HTML page = code on the left with highlighted lines + narration panel with play / pause / previous / next, speed, voice choice, table of contents.

## Steps

1. **Read the whole file with line numbers** (`cat -n`). Understand it before writing; if it belongs to a project, read what it imports from the project too.
2. **Plan the lesson in five parts, always in this order** (field `part`, named in the user's language: 总览 / 重点 / 脚本细节 / 开发中遇到的问题 / 总结, or 概要 / 重要ポイント / 詳細 / 開発中の問題 / まとめ):
   1. **总览 Overview** (1–2 steps): what the file does and its result; the overall flow (timeline / data flow) and how the file is divided. Use the docstring range, then the whole file.
   2. **重点 Key points** (3–6 steps): the design ideas that matter most — ★-marked lines, non-obvious choices, things reused later. One idea per step, a tight line range each, explained in depth (why, what it enables). Keep bug stories for part 4.
   3. **脚本细节 Details** (4–8 steps): walk the rest of the file top to bottom by its own sections. Do not repeat the key points; refer back to them in one sentence.
   4. **开发中遇到的问题 Problems met during development** (2–6 steps): from this conversation's history (and comments in the file), each problem as symptom → cause → fix → lesson, with the line range where the fix lives. Include dead ends that were tried (e.g. shapes or settings that failed). If there is no known history, say so in one step or skip the part.
   5. **总结 Summary** (1 step, whole file): the 2–3 lessons to remember + 2–3 concrete changes to try, each with what to watch for.
3. **Write the narration (`say`) for speaking, not reading:**
   - The user's interaction language (zh → `zh-CN`, ja → `ja-JP`), plain spoken sentences ending in 。/．, 3–10 sentences per part.
   - Explain *why*, not just what: design choices, pitfalls, units, what would break if changed. Reuse facts established in the conversation (bugs found, measured numbers).
   - No symbols TTS reads badly: write numbers as words where they matter ("零点五秒"), avoid brackets, arrows, markdown, long identifiers in a row. Short identifiers (`mj_step`) are fine.
   - Name terms with the original word once (e.g. 法向力, normal force) for a learner.
4. **Write the steps JSON** into the scratchpad:
   `[{"part": "总览", "from": 1, "to": 4, "title": "short heading", "say": "narration"}, ...]`
5. **Build (speech is decided automatically):**
   `python3 ~/.claude/skills/code-lesson/build.py <source> <steps.json> <scratchpad>/<name>_lesson.html --title "<file> 讲解" --lang zh-CN`
   - `--tts auto` (default): OpenAI TTS into `<name>_lesson_audio/` when a key exists (`OPENAI_API_KEY` or `~/.config/code-lesson/openai_key`); no key or any API/network error → prints `fallback to browser speech` and builds a page that uses the browser's voices. Never ask the user to paste a key into the chat.
   - `--tts browser`: no API call. `--tts openai`: fail instead of falling back. `--voice <name>`: other OpenAI voice.
   - mp3s are cached in `~/.cache/code-lesson/`: unchanged steps are not paid for again.
   - It checks line ranges; fix and rebuild if it complains.
6. **Publish** the HTML with the Artifact tool (icon `code`). If the build printed `AUDIO_FILES {...}`, pass that JSON map as `files` (published path → local mp3). For a local/offline copy, copy the HTML together with its `_audio` folder.
7. The page itself also falls back to browser speech if an mp3 cannot be loaded, so a page never ends up silent.
8. **Reply briefly:** link, which speech was used (OpenAI TTS or browser fallback, and why), how to use (Space / ← →), the part list as a short table. For browser speech: Chrome → "Google 普通话", Edge → "Natural" voices are the most natural.

## Notes
- `template.html` holds the page; `build.py` checks the steps, picks the speech and injects the data; `tts_openai.py` makes the mp3s. Version history: `CHANGELOG.md`. Change the look there, once, for all lessons.
- `examples/pendulum.py` + `examples/pendulum.steps.json`: a complete small lesson (five parts, spoken style) to match in tone; try it with `python3 build.py examples/pendulum.py examples/pendulum.steps.json /tmp/pendulum_lesson.html --tts browser`.
- Highlighting is light: Python-style `#` comments by default, `//` for C/JS-like extensions.
- When the source file changes later, rebuild with the same steps file after adjusting any shifted line ranges, and republish to the same artifact path so the link stays.
