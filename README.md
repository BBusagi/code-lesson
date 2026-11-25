# code-lesson

把一个源代码文件变成**带语音讲解的网页**：左边是代码，右边逐段朗读讲解，同时高亮正在讲的代码行。
这是一个 [Claude Code](https://claude.com/claude-code) skill，也可以不经过 Claude，直接用 `build.py` 生成。

Turn a source file into a narrated, section-by-section walkthrough page (Claude Code skill).

## 讲解结构
每次讲解固定分成五部分：**总览 → 重点 → 脚本细节 → 开发中遇到的问题 → 总结**。

## 语音
| 情况 | 使用的语音 |
|---|---|
| 有 OpenAI API key | OpenAI TTS（`gpt-4o-mini-tts`），预先合成 mp3，自然人声；结果会缓存，不重复计费 |
| 没有 key，或 API 出错 | 自动退回浏览器自带的语音（Edge 的 "Natural" 声音、Chrome 的 "Google 普通话" 效果最好） |
| mp3 在页面里加载失败 | 页面自动切换到浏览器语音继续朗读 |

## 安装
```bash
git clone https://github.com/BBusagi/code-lesson ~/.claude/skills/code-lesson
```
在 Claude Code 里说"讲解一下 xxx.py"，或输入 `/code-lesson xxx.py`。

可选：OpenAI key（不要提交到仓库）
```bash
mkdir -p ~/.config/code-lesson
read -rsp "OpenAI API key: " k && printf '%s' "$k" > ~/.config/code-lesson/openai_key && chmod 600 ~/.config/code-lesson/openai_key && unset k
```

## 不经过 Claude 直接生成
```bash
python3 build.py examples/pendulum.py examples/pendulum.steps.json /tmp/pendulum_lesson.html --tts browser
```
`--tts auto`（默认）有 key 时合成语音，否则退回浏览器语音；`--tts openai` 失败时报错；`--tts browser` 不调用 API。
只需要 Python 3 标准库。

## 文件
| 文件 | 作用 |
|---|---|
| `SKILL.md` | Claude 的工作流程 |
| `template.html` | 页面模板（浅色 / 深色主题，中文 / 日语 / 英语界面） |
| `build.py` | 检查讲解词 → 选择语音 → 生成页面 |
| `tts_openai.py` | OpenAI TTS 合成，带缓存 |
| `examples/` | 示例脚本和讲解词 |
| `CHANGELOG.md` | 版本记录 |
