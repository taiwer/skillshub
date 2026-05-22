# SkillHub — Skill 管理中心

> 📦 **10 个 skill**：9 个外部导入 + 1 个管理工具

---

## 🏷️ 来源标记

| 标记 | 含义 |
|------|------|
| 🔵 nature | 从 Yuan1z0825/nature-skills 导入 |
| ⚙️ 自有 | 自建 skill |

---

## 📊 总览

| 类别 | 数量 | 来源 |
|------|------|------|
| 🧪 学术论文 | 9 | 🔵 nature |
| ⚙️ 管理工具 | 1 | ⚙️ 自有 |

---

## 🔵 nature-skills（9 个）

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

## ⚙️ 自有 skill

| # | Skill | 功能 | 状态 |
|---|-------|------|------|
| 1 | `skillhub-management` | SkillHub 管理面板维护 | ✅ |

---

## 📂 目录结构

```
skillhub/
├── README.md        ← 管理面板
└── skills/          ← 10 个 skill
    ├── nature-*/    ← 🔵 外部导入 (9)
    └── skillhub-management/ ← ⚙️ 自建 (1)
```

## 📝 使用方式

1. 告诉我「测试 xxx skill」
2. 我跑测试后更新状态：✅ / ⚠️ / 🔄 / ❌
3. 通过的直接推送到 GitHub
