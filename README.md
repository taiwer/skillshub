# SkillHub — Skill 管理中心

> 📦 **101 个 skill**：9 个外部导入 + 92 个 Hermes 内置

---

## 🏷️ 来源标记

| 标记 | 含义 |
|------|------|
| 🔵 nature | 从 Yuan1z0825/nature-skills 导入，需测试 |
| 🟢 Hermes | Hermes Agent 内置 skill |

---

## 📊 总览

| 类别 | 数量 | 来源 |
|------|------|------|
| 🧪 学术论文 | 9 | 🔵 nature |
| 💻 软件开发 | 12 | 🟢 Hermes |
| 🎨 创意制作 | 17 | 🟢 Hermes |
| 🤖 MLOps | 9 | 🟢 Hermes |
| 📈 生产力 | 9 | 🟢 Hermes |
| 🔧 GitHub 工作流 | 6 | 🟢 Hermes |
| 🍎 Apple 生态 | 5 | 🟢 Hermes |
| 🖥️ 部署运维 | 5 | 🟢 Hermes |
| 🎬 媒体 | 5 | 🟢 Hermes |
| 🤖 自主 AI 代理 | 4 | 🟢 Hermes |
| 🔬 研究 | 4 | 🟢 Hermes |
| 🐶 其他 | 4 | 🟢 Hermes |
| 📊 数据科学 | 3 | 🟢 Hermes |
| 🎮 游戏 | 2 | 🟢 Hermes |
| 📧 邮件 | 1 | 🟢 Hermes |
| 🌐 MCP | 1 | 🟢 Hermes |
| 📝 笔记 | 1 | 🟢 Hermes |
| 🔴 红队测试 | 1 | 🟢 Hermes |
| 🏠 智能家居 | 1 | 🟢 Hermes |
| 📱 社交媒体 | 1 | 🟢 Hermes |
| 💬 元宝 | 1 | 🟢 Hermes |

---

## 🔵 外部导入 — nature-skills（9 个，需测试）

| # | Skill | 功能 | 状态 |
|---|-------|------|------|
| 1 | `nature-writing` | 论文章节撰写（摘要/引言/方法/结果/讨论） | 🔄 |
| 2 | `nature-polishing` | 学术英文润色 / 中文翻译优化 | 🔄 |
| 3 | `nature-response` | 审稿意见逐点回复 / 修回信 | 🔄 |
| 4 | `nature-reader` | 论文中英对照全文精读 | 🔄 |
| 5 | `nature-figure` | Nature 级图表制作（Python/R） | 🔄 |
| 6 | `nature-academic-search` | 多源文献检索（arXiv/PubMed/Crossref） | 🔄 |
| 7 | `nature-citation` | Nature/CNS 引文格式管理 | 🔄 |
| 8 | `nature-data` | Data Availability 声明 / FAIR 合规 | 🔄 |
| 9 | `nature-paper2ppt` | 论文一键转中文 PPTX 演示 | 🔄 |

## 🟢 Hermes 内置 — skills 清单（92 个）

| 类别 | Skills |
|------|--------|
| 💻 软件开发 | `writing-plans` `plan` `spike` `test-driven-development` `systematic-debugging` `subagent-driven-development` `requesting-code-review` `python-debugpy` `node-inspect-debugger` `hermes-agent-skill-authoring` `debugging-hermes-tui-commands` `skillhub-management` |
| 🎨 创意 | `architecture-diagram` `ascii-art` `ascii-video` `baoyu-comic` `baoyu-infographic` `claude-design` `comfyui` `design-md` `excalidraw` `humanizer` `creative-ideation` `manim-video` `p5js` `pixel-art` `popular-web-designs` `pretext` `sketch` `songwriting-and-ai-music` `touchdesigner-mcp` |
| 🤖 MLOps | `dspy` `huggingface-hub` `audiocraft` `segment-anything` `vllm` `obliteratus` `llama-cpp` `lm-evaluation-harness` `weights-and-biases` |
| 📈 生产力 | `airtable` `google-workspace` `linear` `maps` `nano-pdf` `notion` `ocr-and-documents` `powerpoint` `teams-meeting-pipeline` |
| 🔧 GitHub | `github-auth` `github-repo-management` `github-pr-workflow` `github-code-review` `github-issues` `codebase-inspection` |
| 🍎 Apple | `apple-notes` `apple-reminders` `findmy` `imessage` `macos-computer-use` |
| 🖥️ 部署 | `vite-frontend-deployment` `deploy-java-webapp-macos` `kanban-orchestrator` `kanban-worker` `webhook-subscriptions` |
| 🎬 媒体 | `gif-search` `heartmula` `songsee` `spotify` `youtube-content` |
| 🤖 AI 代理 | `claude-code` `codex` `hermes-agent` `opencode` |
| 🔬 研究 | `arxiv` `blogwatcher` `llm-wiki` `polymarket` `research-paper-writing` |
| 📊 数据科学 | `target-prediction` `jupyter-live-kernel` `intern-pubchem-name-conversion` |
| 🎮 游戏 | `minecraft-modpack-server` `pokemon-player` |
| 🐶 其他 | `dogfood` `godmode` `native-mcp` `yuanbao` |
| 单类 | `himalaya` `openhue` `obsidian` `xurl` |

---

## 📂 目录结构

```
skillhub/
├── README.md        ← 管理面板
└── skills/          ← 101 个 skill
    ├── nature-*/    ← 🔵 外部导入 (9)
    └── */           ← 🟢 Hermes 内置 (92)
```

## 📝 使用方式

1. 告诉我「测试 xxx skill」
2. 我跑测试后更新状态：✅ / ⚠️ / 🔄 / ❌
3. 通过的直接推送到 GitHub
