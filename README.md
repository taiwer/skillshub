# SkillHub — Skill 管理中心

> 管理所有自定义 skill，记录功能、输入、输出、状态。

---

## 📋 Skill 清单

| # | Skill 名称 | 功能描述 | 状态 |
|---|-----------|---------|------|
| 1 | `nature-writing` | 论文写作：摘要、引言、方法、结果、讨论、结论等章节撰写 | 🔄 |
| 2 | `nature-polishing` | 论文润色：学术英文润色、中文翻译、句式优化 | 🔄 |
| 3 | `nature-response` | 审稿回复：逐点回复 reviewer，生成审稿回信 | 🔄 |
| 4 | `nature-reader` | 论文精读：中英对照全文解读，图文并排，原文锚点 | 🔄 |
| 5 | `nature-figure` | 论文图表：Nature 级图表制作（Python/R），提交级质量 | 🔄 |
| 6 | `nature-academic-search` | 文献检索：多源文献搜索、引文验证、MeSH 策略 | 🔄 |
| 7 | `nature-citation` | 引文管理：Nature/CNS 期刊引文格式，分句标注 | 🔄 |
| 8 | `nature-data` | 数据声明：Data Availability 声明、FAIR 合规审核 | 🔄 |
| 9 | `nature-paper2ppt` | 论文转 PPT：从论文生成 Nature 风格中文 PPTX 演示 | 🔄 |

---

## 📂 目录结构

```
skillhub/
├── README.md      ← 你在这里（管理面板）
├── skills/        ← 放原始 skill 文件
│   └── <skill名>/
│       └── SKILL.md
```

---

## 📝 使用方式

1. 把测试的 skill 放到 `skills/` 目录下
2. 在上方表格中记录：
   - **名称**：skill 名称
   - **功能**：这个 skill 做什么
   - **输入**：需要什么参数/文件
   - **输出**：返回什么结果
   - **状态**：✅ 可用 / ⚠️ 有问题 / 🔄 测试中
   - **备注**：注意事项、bug、改进方向
3. 测试通过后，将完整目录推送到 GitHub

---

## 🔍 状态说明

| 状态 | 含义 |
|------|------|
| ✅ | 测试通过，可以使用 |
| ⚠️ | 有问题，需修复 |
| 🔄 | 正在测试中 |
| ❌ | 已废弃 |
