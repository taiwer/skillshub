---
name: target-prediction
description: 中药复方靶点预测全流程技能。从复方化学成分数据出发，经过数据标准化、SMILES查询、靶点预测、结果合并，输出完整靶点列表。当用户有复方成分数据需要预测靶点、进行网络药理学研究时使用此技能。
---

# Target Prediction Skill（中药复方靶点预测）

从中药复方化学成分数据出发，完成数据标准化 → SMILES补全 → 靶点预测 → 结果合并的全流程。

## 触发条件

当用户提到以下关键词时使用本技能：
- "预测靶点"、"找靶点"、"靶点预测"
- "SwissTargetPrediction"、"SEA"
- "网络药理学靶点"
- "复方成分靶点"、"化合物靶点"

## 完整工作流程（6步）

### Step 1: 初始化项目目录

创建项目文件夹，将原始数据文件复制到 `01_Data/`：

```
项目名/
  01_Data/          ← 原始数据 + 中间数据（复制原始文件到此）
  02_Script/        ← 脚本文件
  03_Output/        ← 预测结果
    swiss_raw/      ← Swiss 单个化合物原始结果（按序号命名）
    sea_raw/        ← SEA 单个化合物原始结果（按序号命名）
```

**操作**：
1. 创建上述目录结构
2. 将用户的原始数据文件（Excel/CSV）复制到 `01_Data/`
3. 在 `02_Script/` 中准备脚本

### Step 2: 数据标准化

检查原始数据文件，提取化合物信息，整理为标准格式 CSV。

**标准格式**（`01_Data/compounds.csv`）：

| 序号 | 中文名 | 英文名 | CAS号 | SMILES | 分子式 | 分子量 | 归属 |
|------|--------|--------|-------|--------|--------|--------|------|
| 1 | 腺嘌呤 | Adenine | 73-24-5 | N1=CN=C(N)C=2NC=NC12 | C5H5N5 | 135.05 | All |
| 2 | 水苏碱 | Stachydrine | 471-87-4 | C([O-])(=O)[C@H]1[N+](C)(C)CCC1 | C7H13NO2 | 143.09 | 甘草 |

**最少必须列**：`序号`（No）和 `英文名`（Name）。其他列按数据可用性逐步补全。

**关键规则**：
- **序号来源**：优先从复方 sheet 的 Peak No./序号/No. 列获取；若无，则按顺序编号
- **去重**：同名+同分子式的化合物合并，归属列用 `\` 合并（如 `BZ\GZ`）
- **排除糖类**：Sucrose、Raffinose、Maltohexaose 等大分子糖类不适合靶点预测，应排除
- **CSV写入**：必须使用 `csv.writer`（QUOTE_MINIMAL），不能用 f-string 写 CSV，否则含逗号的化合物名会破坏列对齐
- **复方sheet数据质量**：复方 sheet 常有 Formula/Identification 列错位问题，应优先使用单味药 sheet 提取数据，仅从复方 sheet 读取序号

**操作**：
1. 读取 Excel 各 sheet，识别化合物名、分子式、来源、序号列
2. 从复方 sheet 构建 序号→化合物名 映射
3. 从单味药 sheet 提取化合物数据
4. 去重、排除糖类、附加序号
5. 输出 `01_Data/compounds.csv`

### Step 3: 补全缺失数据（SMILES/CAS）

对缺少 SMILES 的化合物，通过 PubChem PUG-REST API 查询补全。

**查询策略**（按优先级）：
1. 直接用英文名查询 PubChem
2. CID fallback：先获取 CID，再查属性
3. 替代名称变体：去掉前缀数字、希腊字母等
4. 分子式辅助查询：列出候选供人工确认

**PubChem PUG-REST 关键注意**：
- 返回的 SMILES 字段名是 `SMILES`（不是 `CanonicalSMILES`）
- 请求 URL 属性参数用 `SMILES` 而非 `CanonicalSMILES`
- 化合物名含逗号/希腊字母时 PubChem 可能查不到，需尝试替代名称

**操作**：
1. 运行 `query_smiles.py` 批量查询
2. 输出 `01_Data/compounds_with_smiles.csv`（在 compounds.csv 基础上增加 SMILES/IUPAC/CID/Method/FormulaMatch 列）
3. 对查询失败的化合物，尝试手动替代名称（如 Catechin → "Catechin"，Quercetin-3β-D-glucoside → "Quercetin-3-glucoside"）
4. 仍失败的化合物需从 TCMSP/文献手动补充
5. 生成 `01_Data/target_prediction_input.csv`：仅包含有 SMILES 的化合物（列：No, Name, SMILES）

### Step 4: 靶点预测

使用 SwissTargetPrediction 和 SEA 进行靶点预测。

**运行命令**：
```bash
python scripts/batch_predict.py --input compounds.csv --output 03_Output/ --source both
```

**输入 CSV 格式**（`target_prediction_input.csv`）：

| No | Name | SMILES |
|----|------|--------|
| 3 | Protocatechuic acid-O-glucoside | C1=CC(=C(C=C1C(=O)O)O)OC2C... |
| 4 | schaftoside | C1[C@@H]([C@@H]... |

**关键规则**：
- **文件命名**：Swiss 和 SEA 的单个化合物原始结果文件用序号命名（如 `3.csv`、`11.csv`），不用化合物名
- **No 列传播**：所有输出 CSV 必须包含 No 列，与输入的序号对应
- **SEA 单个结果**：保存到 `03_Output/sea_raw/{No}.csv`
- **Swiss 单个结果**：保存到 `03_Output/swiss_raw/{No}.csv`
- **延迟**：批量请求间至少 3 秒延迟，避免限流
- **超时**：Swiss 和 SEA 均可能超时，失败记录到 `errors.csv`

### Step 5: 合并结果

合并两个数据库的预测结果，去重。

**输出文件**：

| 文件 | 说明 |
|------|------|
| `03_Output/merged_targets.csv` | 合并去重结果（含 No 列） |
| `03_Output/swiss_targets.csv` | Swiss 全部结果（含 No 列） |
| `03_Output/sea_targets.csv` | SEA 全部结果（含 No 列） |
| `03_Output/errors.csv` | 失败记录（含 No 列） |
| `03_Output/swiss_raw/{No}.csv` | Swiss 单个化合物原始结果 |
| `03_Output/sea_raw/{No}.csv` | SEA 单个化合物原始结果 |

**合并去重逻辑**：以 (Compound, Target Name) 为去重键，同一化合物在同一靶点上只保留一条记录。

### Step 6: R 语言后处理与可视化（可选）

靶点预测完成后，使用 `scripts/analysis.R` 生成统计和图表：

```bash
Rscript scripts/analysis.R
```

**输出**：
| 文件 | 说明 |
|------|------|
| `03_Output/target_frequency.csv` | 靶点频次表（被多少化合物命中） |
| `03_Output/compound_target_summary.csv` | 化合物靶点数量汇总 |
| `03_Output/target_frequency_distribution.png` | 靶点频次分布直方图 |
| `03_Output/top20_targets.png` | Top20 高频靶点柱状图 |
| `03_Output/compound_target_comparison.png` | Top20 化合物靶点数量图 |

**依赖**：R + ggplot2 + dplyr。

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `scripts/query_smiles.py` | PubChem 批量 SMILES 查询（名称→SMILES/IUPAC/CID/分子式） |
| `scripts/swiss_api.py` | SwissTargetPrediction API 调用 |
| `scripts/sea_api.py` | SEA API 调用 |
| `scripts/batch_predict.py` | 批量预测入口（支持 No 列、序号文件命名） |
| `scripts/analysis.R` | 靶点预测结果后处理与可视化（频次统计、Top20 靶点图、化合物靶点对比图） |

## 常见问题

- **CSV 列错位**：化合物名含逗号时必须用 csv.writer 写入，不能用 f-string
- **PubChem SMILES 字段名**：PUG-REST 返回 `SMILES` 而非 `CanonicalSMILES`
- **复方 sheet 数据质量**：Formula/Identification 列常错位，仅用其序号列
- **Swiss 超时**：复杂 TCM 三萜类化合物可能超时，可增大等待时间重试
- **SEA 服务器不可靠**：SEA (sea.bkslab.org) 经常完全不可用 — SSL 错误、连接断开、无响应。不要依赖 SEA，优先只跑 Swiss。若 SEA 必须，建议多次尝试且预期大部分会失败
- **TCM 三萜类异构体 SMILES**：Aliol C isomer、Pachymic acid isomer 等立体异构体在 PubChem 中常查不到。网络药理学中 SwissTargetPrediction 基于 2D 指纹相似度，可使用母体化合物的 PubChem SMILES 代替（如 Alisol C isomer → 用 Alisol C 的 SMILES）。在 compounds_with_smiles.csv 中标注 Method=isomer_parent
- **R 后处理**：靶点预测完成后可用 R 脚本做频次统计和可视化，见 `scripts/analysis.R`

## 详细指南

API 详情和脚本参数见 `references/usage-guide.md`。