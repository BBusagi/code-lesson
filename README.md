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

## 定位
最有价值的是"开发中遇到的问题"这一部分：把开发时踩过的坑（现象 → 原因 → 解决）整理进讲解，交接时不再丢失经验。
与同类工具的区别：

| 同类 | 区别 |
|---|---|
| CodeTour（VS Code，按步骤跳到代码行 + 文字说明） | 加了语音和固定的五部分结构 |
| IDE 的 "Explain this code" | 只能看到当前代码；这里讲为什么这样写、试过什么、失败过什么 |
| 录屏讲解（Loom 等） | 不用录制，代码改了重新生成即可 |

适合：新人入职与项目交接、自学、给不擅长读代码的同事或客户讲解。

## 路线图
### 功能改进
- [ ] **随手记录开发问题**：开发时把"现象 → 原因 → 解决"写进日志文件，生成讲解时读取，不依赖对话记录（v0.2 优先）
- [ ] **按函数名定位 + 记录 commit**：代码修改后行号不再错位，并能提示讲解已过期
- [ ] **真实浏览器测试**：mp3 加载失败时切换浏览器语音、语速调节等
- [ ] 支持多个文件（跟随调用关系讲解）
- [ ] 每段配图或运行结果（截图、曲线）
- [ ] 在页面上直接向 Claude 提问
- [ ] 逐字同步高亮（使用能返回逐字时间的 TTS）
- [ ] 日语讲解
- [ ] 导出为视频或音频

### 推广准备
- [ ] 添加 LICENSE
- [ ] 英文 README（保留中文版，另加日文版）
- [ ] 公开的演示页（用单摆示例），README 顶部放动图或短视频
- [ ] GitHub Topics（`claude-code`、`claude-skill`、`code-walkthrough`、`tts`、`education`）和 v0.1 Release
- [ ] 打包为 Claude Code 插件，一条命令安装
- [ ] 提交到 Claude Code 的 awesome 列表和社区

### 推广渠道
| 渠道 | 内容 |
|---|---|
| Zenn / Qiita | 实践文章 |
| 掘金 / 知乎 / B站 | 文章或演示视频 |
| X（Twitter） | 30 秒演示：代码逐行高亮 + 语音 |
| Reddit（r/ClaudeAI 等） | 演示 + 突出"开发问题沉淀"的卖点 |
| Hacker News "Show HN" | 功能更完整后再发 |
