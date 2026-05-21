import os
import re
import time
from io import StringIO
from urllib.parse import quote

import pandas as pd
import requests

URL_HOME = "https://www.swisstargetprediction.ch/"
URL_PREDICT = "https://www.swisstargetprediction.ch/predict.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.swisstargetprediction.ch",
    "Referer": "https://www.swisstargetprediction.ch/",
}


def classify_response_status(page_url, page_text):
    """根据返回页面内容和 URL 判断当前状态。"""
    text_lower = page_text.lower()
    url_lower = page_url.lower()

    if "alert(xxxx" in text_lower or "your job will not submitted" in text_lower:
        return "noTarget", "检测到提交失败/无结果的 alert 信息"

    if "error_page.php" in url_lower:
        if "invalid smiles" in text_lower:
            return "invalid_smiles", "检测到 Invalid SMILES"
        if "error" in text_lower:
            return "error_page", "检测到错误页面并包含 Error"
        return "error_page", "进入错误页面"

    if (
        "invalid smiles" in text_lower
        or "too large" in text_lower
        or "smiles too large" in text_lower
    ):
        return "invalid_smiles", "检测到 SMILES 无效或过大"

    if "internal server error" in text_lower:
        return "error_page", "检测到服务器内部错误"

    if "error" in text_lower and "result.php" not in url_lower:
        return "error_page", "检测到页面错误信息"

    return None, None


def init_session():
    session = requests.Session()
    print("步骤 1: 访问首页以建立会话并获取 Cookie...")
    session.get(URL_HOME, headers=HEADERS, timeout=30)
    return session


def submit_prediction(session, smiles, organism="Homo_sapiens"):
    encoded_organism = quote(organism, safe="")
    encoded_smiles = quote(smiles, safe="")
    # 手工构造 x-www-form-urlencoded，避免 smiles 特殊字符被错误处理。
    payload = f"organism={encoded_organism}&smiles={encoded_smiles}&Example=&ioi=2"
    request_headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    print("步骤 2: 提交预测任务...")
    response = session.post(
        URL_PREDICT, headers=request_headers, data=payload, timeout=60
    )

    if 'alert("Your job will not submitted' in response.text:
        print(
            "❌ 提交失败：服务器仍然拒绝了请求。可能需要处理更复杂的验证（如隐藏的 Token）。"
        )
    else:
        print("✅ 提交可能成功！")
        print(f"响应内容前500字: {response.text[:500]}")

    return response


def extract_job_info(html_content, organism="Homo_sapiens"):
    job_match = re.search(r"job=(\d+)", html_content)
    if not job_match:
        print("❌ 未在 HTML 中直接发现 Job ID，可能隐藏在其他地方。")
        return None, None

    job_id = job_match.group(1)
    result_url = f"https://www.swisstargetprediction.ch/result.php?job={job_id}&organism={organism}"
    print(f"🎯 成功提取到 Job ID: {job_id}")
    print(f"🔗 最终结果链接: {result_url}")
    return job_id, result_url


def save_tables(job_id, page_text, output_dir="swiss_xlsx_results", file_prefix=None):
    tables = pd.read_html(StringIO(page_text))
    if not tables:
        print("⚠️ 页面中未解析到表格。")
        return []

    os.makedirs(output_dir, exist_ok=True)
    print(f"📊 共提取到 {len(tables)} 个表格。")
    saved_files = []

    prefix = file_prefix if file_prefix else f"job_{job_id}"

    for idx, table_df in enumerate(tables, start=1):
        output_path = os.path.join(output_dir, f"{prefix}_table_{idx}.csv")
        table_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ 表格 {idx} 已保存: {output_path}")
        print(table_df.head(5).to_string(index=False))
        saved_files.append(output_path)

    return saved_files


def poll_result_and_export(
    session,
    job_id,
    result_url,
    wait_interval_short=0.5,
    wait_interval_long=3,
    wait_max_time=300,
    output_dir="swiss_xlsx_results",
    file_prefix=None,
):
    print("🔍 提交完成，开始高频监听页面变化...")
    start_time = time.time()
    poll_count = 0
    final_status = None
    saved_files = []

    while time.time() - start_time < wait_max_time:
        poll_count += 1
        try:
            result_response = session.get(result_url, headers=HEADERS, timeout=30)
        except requests.RequestException as req_err:
            print(f"⚠️ 轮询请求异常: {req_err}")
            time.sleep(wait_interval_long)
            continue

        current_url = result_response.url
        print(f"🔍 当前URL: {current_url}")

        if result_response.status_code != 200:
            print(f"⚠️ 结果页状态码异常: {result_response.status_code}")
            time.sleep(wait_interval_long)
            continue

        current_status, reason = classify_response_status(
            current_url, result_response.text
        )

        if current_status:
            print(f"❌ 状态判定: {current_status} ({reason})")
            final_status = current_status
            break

        try:
            saved_files = save_tables(
                job_id,
                result_response.text,
                output_dir=output_dir,
                file_prefix=file_prefix,
            )
            if saved_files:
                final_status = "success"
                break
        except ValueError:
            # 尚未出表格，继续等待
            pass
        except Exception as parse_error:
            print(f"⚠️ 解析表格时出现异常: {parse_error}")

        sleep_time = wait_interval_short if poll_count <= 20 else wait_interval_long
        time.sleep(sleep_time)

    return final_status or "timeout", saved_files


def run(
    smiles,
    output_dir="swiss_xlsx_results",
    file_prefix=None,
    return_details=False,
):
    session = init_session()
    response = submit_prediction(session, smiles)
    job_id, result_url = extract_job_info(response.text)

    if not job_id or not result_url:
        return "job_not_found"

    final_status, saved_files = poll_result_and_export(
        session,
        job_id,
        result_url,
        output_dir=output_dir,
        file_prefix=file_prefix,
    )

    if final_status == "success":
        print("🎉 任务完成并已导出表格。")
    elif final_status == "noTarget":
        print("✅ 确认为无靶点结果 (noTarget)。")
    elif final_status == "invalid_smiles":
        print("❌ SMILES 无效或过大 (invalid_smiles)。")
    elif final_status == "error_page":
        print("❌ 页面/服务错误 (error_page)。")
    elif final_status == "job_not_found":
        print("❌ 未能提取任务 ID (job_not_found)。")
    else:
        print("⏰ 超时：在设定时间内未获取到可用结果。")

    if return_details:
        return {
            "status": final_status,
            "files": saved_files,
            "job_id": job_id,
        }

    return final_status


def main():
    smiles = "O[C@H]1[C@H](N2C=3C(N=C2)=C(N)N=CN3)O[C@H](CO)[C@H]1O"  # 这里直接使用一个示例 SMILES
    run(smiles)


if __name__ == "__main__":
    main()
