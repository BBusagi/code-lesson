# code-lesson changelog

## v0.1 (2026-11-24)
First version.
- Page: code on the left with highlighted lines, narration panel on the right (play / pause / previous / next,
  speed, auto-advance, table of contents grouped by part, keyboard: Space / ← →). Light and dark theme.
- Lesson structure: 总览 → 重点 → 脚本细节 → 开发中遇到的问题 → 总结.
- Speech: OpenAI TTS (gpt-4o-mini-tts, voice coral, cached) when a key exists; otherwise automatic fallback to the
  browser's voices (Edge "Natural" > Chrome "Google" > OS voices). The page also falls back if an mp3 fails to load.
- Files: SKILL.md, template.html, build.py, tts_openai.py (standard library only), examples/pendulum.*, README.md
