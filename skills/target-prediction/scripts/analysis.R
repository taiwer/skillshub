#!/usr/bin/env Rscript
# target_prediction_analysis.R
# 中药复方靶点预测结果分析与可视化
# 运行: Rscript scripts/analysis.R
# 前提: 03_Output/merged_targets.csv 和 swiss_targets.csv 已存在

library(ggplot2)
library(dplyr)

# ── 1. 读取数据 ──────────────────────────────────────────────
merged   <- read.csv("03_Output/merged_targets.csv",   stringsAsFactors = FALSE)
swiss    <- read.csv("03_Output/swiss_targets.csv",    stringsAsFactors = FALSE)
compounds <- read.csv("01_Data/compounds.csv",          stringsAsFactors = FALSE)

cat("数据读取完成:\n")
cat("  Swiss 靶点总数:", nrow(swiss), "\n")
cat("  合并去重后:    ", nrow(merged), "\n")

# ── 2. 确定靶点名称列 ──────────────────────────────────────────
target_col <- intersect(c("Target.Name", "Target Name", "Common.name", "Target"), colnames(merged))
if(length(target_col) == 0) stop("未找到靶点名称列")
target_col <- target_col[1]

# ── 3. 靶点频次统计 ──────────────────────────────────────────
target_freq <- merged %>%
  group_by(!!sym(target_col)) %>%
  summarise(
    Compound_Count = n_distinct(Compound),
    Source = paste(unique(Source), collapse = " / "),
    .groups = "drop"
  ) %>%
  arrange(desc(Compound_Count))

cat("\n── 被最多化合物命中的靶点 (Top 20) ──\n")
top20 <- head(target_freq, 20)
for(i in seq_len(nrow(top20))) {
  cat(sprintf("  %2d. %-50s  %d compounds  [%s]\n", 
              i, substr(top20[[target_col]][i], 1, 50), 
              top20$Compound_Count[i], top20$Source[i]))
}

# ── 4. 各化合物靶点数量 ────────────────────────────────────────
compound_targets <- merged %>%
  group_by(No, Compound) %>%
  summarise(
    Total_Targets = n(),
    .groups = "drop"
  ) %>%
  arrange(desc(Total_Targets))

cat("\n── 各化合物靶点数量 (Top 10) ──\n")
for(i in seq_len(min(10, nrow(compound_targets)))) {
  row <- compound_targets[i, ]
  cat(sprintf("  %2d. %-40s Total: %3d\n",
              i, substr(row$Compound, 1, 40), row$Total_Targets))
}

# ── 5. 可视化 ──────────────────────────────────────────────────

# 5a. 靶点频次分布柱状图
p1 <- ggplot(target_freq, aes(x = Compound_Count)) +
  geom_histogram(binwidth = 1, fill = "steelblue", color = "white", alpha = 0.8) +
  labs(
    title = "Target Frequency Distribution",
    subtitle = "How many targets are hit by how many compounds",
    x = "Number of Compounds Targeting",
    y = "Number of Targets"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold", size = 14))
ggsave("03_Output/target_frequency_distribution.png", p1, width = 8, height = 6, dpi = 150)

# 5b. Top 20 靶点柱状图
top20_df <- top20 %>%
  mutate(Target_Short = substr(!!sym(target_col), 1, 40))
p2 <- ggplot(top20_df, aes(x = reorder(Target_Short, Compound_Count), y = Compound_Count)) +
  geom_col(fill = "coral", alpha = 0.85) +
  coord_flip() +
  labs(title = "Top 20 Targets by Number of Compounds", x = "", y = "Number of Compounds") +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(face = "bold", size = 13))
ggsave("03_Output/top20_targets.png", p2, width = 10, height = 7, dpi = 150)

# 5c. 各化合物靶点数量柱状图
compound_plot <- compound_targets %>%
  head(20) %>%
  mutate(Compound_Short = substr(Compound, 1, 30))
p3 <- ggplot(compound_plot, aes(x = reorder(Compound_Short, Total_Targets), y = Total_Targets)) +
  geom_col(fill = "#2196F3", alpha = 0.85) +
  coord_flip() +
  labs(title = "Top 20 Compounds: Swiss Target Count", x = "", y = "Number of Targets") +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(face = "bold", size = 13))
ggsave("03_Output/compound_target_comparison.png", p3, width = 10, height = 7, dpi = 150)

# ── 6. 输出汇总表 ──────────────────────────────────────────────
write.csv(target_freq, "03_Output/target_frequency.csv", row.names = FALSE)
write.csv(compound_targets, "03_Output/compound_target_summary.csv", row.names = FALSE)

# ── 7. 摘要 ────────────────────────────────────────────────────
cat("\n", paste(rep("=", 60), collapse = ""), "\n")
cat("分析完成!\n")
cat("  化合物总数:", nrow(compounds), "\n")
cat("  有靶点预测的化合物:", n_distinct(merged$Compound), "\n")
cat("  唯一靶点总数:", nrow(target_freq), "\n")
cat("  合并后靶点记录:", nrow(merged), "\n")
cat("  输出文件:\n")
cat("    03_Output/target_frequency.csv            - 靶点频次表\n")
cat("    03_Output/compound_target_summary.csv     - 化合物靶点汇总\n")
cat("    03_Output/target_frequency_distribution.png - 频次分布图\n")
cat("    03_Output/top20_targets.png               - Top20靶点图\n")
cat("    03_Output/compound_target_comparison.png  - 化合物靶点对比图\n")
cat(paste(rep("=", 60), collapse = ""), "\n")
