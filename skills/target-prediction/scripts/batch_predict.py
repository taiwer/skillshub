#!/usr/bin/env python3
"""
批量靶点预测入口脚本。

支持两种模式：
1. 单个 SMILES 预测：--smiles "SMILES码" --name "化合物名"
2. 批量 CSV 预测：--input compounds.csv

CSV 格式要求：至少包含 Name 和 SMILES 两列。
"""

import argparse
import os
import sys
import time

import pandas as pd

# 将脚本所在目录加入路径，确保能导入同目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swiss_api import run as swiss_run
from sea_api import run as sea_run


def predict_single_swiss(name, smiles, output_dir, no="", organism="Homo_sapiens"):
    """使用 SwissTargetPrediction 预测单个化合物的靶点。"""
    print(f"\n{'=' * 60}")
    no_str = f"No.{no}" if no else ""
    print(f"🧬 SwissTargetPrediction 预测: {no_str} {name}")
    print(f"   SMILES: {smiles[:50]}...")
    print(f"{'=' * 60}")

    swiss_output_dir = os.path.join(output_dir, "swiss_raw")
    # 使用 No. 作为文件名前缀（如果有），否则用化合物名
    if no:
        file_prefix = str(no)
    else:
        file_prefix = name.replace(" ", "_").replace("/", "_")
    result = swiss_run(
        smiles,
        output_dir=swiss_output_dir,
        file_prefix=file_prefix,
        return_details=True,
    )

    if isinstance(result, dict) and result.get("status") == "success":
        files = result.get("files", [])
        if files:
            # 读取保存的 CSV 文件并返回 DataFrame
            df = pd.read_csv(files[0])
            df["No"] = no
            df["Compound"] = name
            df["SMILES"] = smiles
            df["Source"] = "SwissTargetPrediction"
            return df
    elif isinstance(result, dict):
        print(f"⚠️ Swiss 预测状态: {result.get('status', 'unknown')}")

    return pd.DataFrame()


def predict_single_sea(name, smiles, output_dir, no="", max_wait=120):
    """使用 SEA 预测单个化合物的靶点。"""
    print(f"\n{'=' * 60}")
    no_str = f"No.{no}" if no else ""
    print(f"🧬 SEA 预测: {no_str} {name}")
    print(f"   SMILES: {smiles[:50]}...")
    print(f"{'=' * 60}")

    results = sea_run(smiles, max_wait=max_wait)

    if results:
        df = pd.DataFrame(results)
        df["No"] = no
        df["Compound"] = name
        df["SMILES"] = smiles
        df["Source"] = "SEA"
        # 保存单个 SEA 结果到 sea_raw 目录
        sea_output_dir = os.path.join(output_dir, "sea_raw")
        os.makedirs(sea_output_dir, exist_ok=True)
        if no:
            sea_file = os.path.join(sea_output_dir, f"{no}.csv")
        else:
            sea_file = os.path.join(
                sea_output_dir, f"{name.replace(' ', '_').replace('/', '_')}.csv"
            )
        df.to_csv(sea_file, index=False, encoding="utf-8-sig")
        print(f"  ✅ SEA 单个结果已保存: {sea_file}")
        return df

    return pd.DataFrame()


def merge_results(swiss_df, sea_df):
    """合并两个数据库的靶点预测结果，去重。"""
    frames = []
    if not swiss_df.empty:
        frames.append(swiss_df)
    if not sea_df.empty:
        frames.append(sea_df)

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, ignore_index=True)

    # 尝试统一靶点名称列
    target_col = None
    for col in ["Target", "Target Name", "Common name", "Target Name (Uniport)"]:
        if col in merged.columns:
            target_col = col
            break

    if target_col:
        # 去重：同一化合物 + 同一靶点名称只保留一条
        merged = merged.drop_duplicates(subset=["Compound", target_col], keep="first")

    return merged


def main():
    parser = argparse.ArgumentParser(
        description="批量靶点预测：通过 SwissTargetPrediction 和 SEA 预测化合物靶点"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="输入 CSV 文件路径（包含 Name 和 SMILES 列）",
    )
    parser.add_argument(
        "--smiles",
        type=str,
        help="单个 SMILES 码（无需 CSV 文件时使用）",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="unknown",
        help="化合物名称（单个模式时使用）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="target_results",
        help="输出目录（默认: target_results）",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="both",
        choices=["swiss", "sea", "both"],
        help="数据源选择：swiss / sea / both（默认: both）",
    )
    parser.add_argument(
        "--organism",
        type=str,
        default="Homo_sapiens",
        help="物种选择（Swiss 用，默认: Homo_sapiens）",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3,
        help="批量请求间隔秒数（默认: 3）",
    )
    parser.add_argument(
        "--sea-max-wait",
        type=int,
        default=120,
        help="SEA 最大等待秒数（默认: 120）",
    )

    args = parser.parse_args()

    # 检查输入
    if not args.input and not args.smiles:
        parser.error("必须提供 --input CSV 文件或 --smiles 参数")

    os.makedirs(args.output, exist_ok=True)

    # 构建化合物列表
    compounds = []
    if args.smiles:
        compounds = [{"No": "", "Name": args.name, "SMILES": args.smiles}]
    elif args.input:
        input_df = pd.read_csv(args.input)
        if "SMILES" not in input_df.columns:
            print("❌ 输入 CSV 必须包含 SMILES 列")
            sys.exit(1)
        if "Name" not in input_df.columns:
            input_df["Name"] = [f"compound_{i}" for i in range(len(input_df))]
        if "No" not in input_df.columns:
            input_df["No"] = [""] * len(input_df)
        compounds = input_df[["No", "Name", "SMILES"]].to_dict("records")

    print(f"\n📋 共 {len(compounds)} 个化合物待预测")
    print(f"   数据源: {args.source}")
    print(f"   输出目录: {args.output}")

    all_swiss = []
    all_sea = []
    errors = []

    for i, comp in enumerate(compounds, 1):
        no = comp.get("No", "")
        name = comp["Name"]
        smiles = comp["SMILES"]
        no_str = f"No.{no}" if no else ""
        print(f"\n{'#' * 60}")
        print(f"# 处理第 {i}/{len(compounds)} 个化合物: {no_str} {name}")
        print(f"{'#' * 60}")

        try:
            if args.source in ("swiss", "both"):
                swiss_df = predict_single_swiss(
                    name, smiles, args.output, no=no, organism=args.organism
                )
                if not swiss_df.empty:
                    all_swiss.append(swiss_df)

            if args.source in ("sea", "both"):
                sea_df = predict_single_sea(
                    name, smiles, args.output, no=no, max_wait=args.sea_max_wait
                )
                if not sea_df.empty:
                    all_sea.append(sea_df)

        except Exception as e:
            print(f"❌ 处理 {no_str} {name} 时出错: {e}")
            errors.append({"No": no, "Name": name, "SMILES": smiles, "Error": str(e)})

        # 批量请求间添加延迟
        if i < len(compounds) and args.delay > 0:
            print(f"\n⏳ 等待 {args.delay} 秒后继续...")
            time.sleep(args.delay)

    # 合并并保存结果
    swiss_combined = (
        pd.concat(all_swiss, ignore_index=True) if all_swiss else pd.DataFrame()
    )
    sea_combined = pd.concat(all_sea, ignore_index=True) if all_sea else pd.DataFrame()
    merged = merge_results(swiss_combined, sea_combined)

    # 保存
    if not swiss_combined.empty:
        swiss_path = os.path.join(args.output, "swiss_targets.csv")
        swiss_combined.to_csv(swiss_path, index=False, encoding="utf-8-sig")
        print(f"\n✅ Swiss 结果已保存: {swiss_path} ({len(swiss_combined)} 条)")

    if not sea_combined.empty:
        sea_path = os.path.join(args.output, "sea_targets.csv")
        sea_combined.to_csv(sea_path, index=False, encoding="utf-8-sig")
        print(f"\n✅ SEA 结果已保存: {sea_path} ({len(sea_combined)} 条)")

    if not merged.empty:
        merged_path = os.path.join(args.output, "merged_targets.csv")
        merged.to_csv(merged_path, index=False, encoding="utf-8-sig")
        print(f"\n✅ 合并结果已保存: {merged_path} ({len(merged)} 条)")

    if errors:
        error_path = os.path.join(args.output, "errors.csv")
        pd.DataFrame(errors).to_csv(error_path, index=False, encoding="utf-8-sig")
        print(f"\n⚠️ 错误记录已保存: {error_path} ({len(errors)} 条)")

    # 打印汇总
    print(f"\n{'=' * 60}")
    print(f"📊 预测汇总")
    print(f"   化合物总数: {len(compounds)}")
    print(f"   成功预测: {len(compounds) - len(errors)}")
    print(f"   失败: {len(errors)}")
    print(f"   Swiss 靶点数: {len(swiss_combined)}")
    print(f"   SEA 靶点数: {len(sea_combined)}")
    print(f"   合并去重靶点数: {len(merged)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
