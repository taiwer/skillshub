# Target Prediction 详细使用指南

## 全流程概览

```
原始数据 → Step1 初始化 → Step2 数据标准化 → Step3 SMILES补全 → Step4 预测 → Step5 合并
```

## Step 1: 初始化项目目录

```bash
mkdir -p 项目名/01_Data 项目名/02_Script 项目名/03_Output/swiss_raw 项目名/03_Output/sea_raw
cp 原始数据.xlsx 项目名/01_Data/
```

## Step 2: 数据标准化

从 Excel 提取化合物数据，输出标准格式 CSV。

### 标准格式（compounds.csv）

最少必须列：`No`（序号）和 `Name`（英文名）。完整格式：

| No | Name | Formula | Source | SMILES | CAS | MW |
|----|------|---------|--------|--------|-----|----|

### 序号来源

- 优先从复方 sheet 的 Peak No./序号/No. 列获取
- 若无序号列，按顺序编号（1, 2, 3...）

### 关键注意事项

1. **CSV 写入必须用 csv.writer**：化合物名可能含逗号（如 "6,16α-Dihydroxydehydroeburiconic acid"），用 f-string 写 CSV 会破坏列对齐
2. **复方 sheet 数据质量**：Formula/Identification 列常错位，仅用其序号列，化合物数据从单味药 sheet 提取
3. **去重**：同名+同分子式视为同一化合物，归属列用 `\` 合并
4. **排除糖类**：Sucrose、Raffinose、Maltohexaose 等不适合靶点预测

## Step 3: SMILES 补全

### PubChem PUG-REST API

**关键注意**：PubChem 返回的 SMILES 字段名是 `SMILES`（不是 `CanonicalSMILES`）。

查询 URL 示例：
```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/Chlorogenic%20acid/property/SMILES,IUPACName,MolecularFormula/CSV
```

### 查询策略（按优先级）

1. 直接用英文名查询
2. CID fallback：先获取 CID，再查属性
3. 替代名称变体：去掉前缀数字、希腊字母等
4. 分子式辅助查询：列出候选供人工确认

### 手动补充

PubChem 查不到的化合物（常见于 TCM 三萜类），需从以下来源手动补充：
- TCMSP (http://tcmsp.cn)
- 中药化学数据库
- 文献报道

### 输出文件

- `compounds_with_smiles.csv`：在 compounds.csv 基础上增加 SMILES/IUPAC/CID/Method/FormulaMatch 列
- `target_prediction_input.csv`：仅包含有 SMILES 的化合物（列：No, Name, SMILES）

## Step 4: 靶点预测

### 运行命令

```bash
python scripts/batch_predict.py --input target_prediction_input.csv --output 03_Output/ --source both --delay 3
```

### 输入 CSV 格式

| No | Name | SMILES |
|----|------|--------|

No 列用于文件命名和结果追踪。

### 输出文件命名规则

- Swiss 单个结果：`03_Output/swiss_raw/{No}.csv`（如 `3.csv`、`11.csv`）
- SEA 单个结果：`03_Output/sea_raw/{No}.csv`
- 所有汇总 CSV 必须包含 No 列

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | str | 无 | 输入 CSV（含 No, Name, SMILES 列） |
| `--smiles` | str | 无 | 单个 SMILES 码 |
| `--name` | str | "unknown" | 化合物名称 |
| `--output` | str | "target_results" | 输出目录 |
| `--source` | str | "both" | 数据源: swiss/sea/both |
| `--organism` | str | "Homo_sapiens" | 物种（Swiss 用） |
| `--delay` | float | 3 | 批量请求间隔秒数 |
| `--sea-max-wait` | int | 120 | SEA 最大等待秒数 |

## Step 5: 合并结果

### 输出文件

| 文件 | 说明 |
|------|------|
| `merged_targets.csv` | 合并去重结果（含 No 列） |
| `swiss_targets.csv` | Swiss 全部结果（含 No 列） |
| `sea_targets.csv` | SEA 全部结果（含 No 列） |
| `errors.csv` | 失败记录（含 No 列） |
| `swiss_raw/{No}.csv` | Swiss 单个化合物原始结果 |
| `sea_raw/{No}.csv` | SEA 单个化合物原始结果 |

### 合并去重逻辑

以 (Compound, Target Name) 为去重键，同一化合物在同一靶点上只保留一条记录。

## API 说明

### SwissTargetPrediction API (`swiss_api.py`)

**核心函数**: `run(smiles, output_dir, file_prefix, return_details)`

- `smiles`: SMILES 码
- `output_dir`: 保存目录
- `file_prefix`: 输出文件前缀（用序号如 "3"，不用化合物名）
- `return_details`: 是否返回详细信息 dict

**返回值**:
- `return_details=False`: 状态字符串
- `return_details=True`: dict `{status, files, job_id}`

**工作流程**:
1. 访问首页建立会话
2. POST 提交 SMILES 和物种参数
3. 从响应 HTML 提取 Job ID
4. 轮询结果页面直到表格出现或超时
5. 用 pandas 解析 HTML 表格并保存为 CSV

### SEA API (`sea_api.py`)

**核心函数**: `run(smiles, max_wait, interval)`

- `smiles`: SMILES 码
- `max_wait`: 最大等待秒数（默认 120）
- `interval`: 轮询间隔秒数（默认 2）

**返回值**: list of dict 或 None

**工作流程**:
1. 访问首页获取 CSRF Token
2. POST 提交 SMILES 和 Token
3. 根据响应状态轮询或直接解析结果
4. 用 BeautifulSoup 解析 HTML 表格

## 常见问题

### Q1: CSV 列错位
化合物名含逗号（如 "6,16α-Dihydroxydehydroeburiconic acid"）时，必须用 `csv.writer(QUOTE_MINIMAL)` 写入，不能用 f-string。

### Q2: PubChem SMILES 字段名
PUG-REST 返回 `SMILES` 而非 `CanonicalSMILES`。请求 URL 属性参数用 `SMILES`。

### Q3: 复方 sheet 数据质量
复方 sheet 的 Formula/Identification 列常错位。仅用其序号列，化合物数据从单味药 sheet 提取。

### Q4: Swiss 提交失败
可能是 SMILES 格式问题或服务器临时限制。检查 SMILES 是否有效，稍后重试。

### Q5: SEA 获取 CSRF Token 失败
SEA 网站结构可能更新。检查 `sea_api.py` 中的 Token 提取逻辑。

### Q6: 批量请求被限流
增大 `--delay` 参数（如改为 5-10 秒），或在非高峰时段运行。

### Q7: SEA 覆盖率低
SEA 对复杂 TCM 三萜类结构支持有限，部分化合物可能无结果。这是正常现象。