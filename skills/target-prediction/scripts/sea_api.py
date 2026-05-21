import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HOME_URL = "https://sea.bkslab.org/"
SEARCH_URL = "https://sea.bkslab.org/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Referer": HOME_URL,
}


def create_session():
    return requests.Session()


def fetch_csrf_token(session):
    print("正在获取 CSRF Token...")
    home_response = session.get(HOME_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(home_response.text, "html.parser")

    token_input = soup.find("input", {"name": "csrf_token"})
    if token_input:
        csrf_token = token_input.get("value")
        print(f"✅ 成功获取 Token: {csrf_token[:20]}...")
        return csrf_token

    print("❌ 未能直接找到 csrf_token，尝试从源码匹配...")
    token_search = re.search(r'name="csrf_token" value="([^"]+)"', home_response.text)
    if token_search:
        csrf_token = token_search.group(1)
        print(f"✅ 成功获取 Token: {csrf_token[:20]}...")
        return csrf_token

    raise RuntimeError("无法获取 CSRF Token，请检查网页结构。")


def submit_search(session, csrf_token, smiles):
    data = {
        "csrf_token": csrf_token,
        "ref_type": "library",
        "ref_library_id": "default",
        "query_type": "custom",
        "query_custom_targets_paste": smiles,
    }

    print("正在提交搜索请求...")
    response = session.post(SEARCH_URL, headers=HEADERS, data=data, timeout=60)
    print(f"状态码: {response.status_code}")
    return response


def extract_job_url(resp):
    """优先从响应头 Location 获取任务 URL，兜底从 HTML 里提取。"""
    location = resp.headers.get("Location")
    if location:
        return urljoin(HOME_URL, location)

    match = re.search(r"/jobs/search_[0-9a-f-]+", resp.text)
    if match:
        return urljoin(HOME_URL, match.group(0))

    if "/jobs/search_" in resp.url:
        return resp.url

    return None


def wait_for_job_result(session, job_url, max_wait=300, interval=2):
    """轮询任务页，直到拿到最终结果页面。"""
    print(f"🔍 开始轮询任务页面: {job_url}")
    print("等待结果页面加载完成...")
    start = time.time()

    poll_headers = {
        **HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": HOME_URL,
    }

    while time.time() - start < max_wait:
        try:
            job_resp = session.get(job_url, headers=poll_headers, timeout=30)
        except requests.RequestException as e:
            print(f"⚠️ 轮询异常: {e}")
            time.sleep(interval)
            continue

        print(f"轮询状态码: {job_resp.status_code} | URL: {job_resp.url}")

        page_text = job_resp.text
        if "Proces" in page_text:
            print("   🔄 任务处理中，继续等待...")
            time.sleep(interval)
            continue

        if "Results" in page_text:
            print("   ✅ 任务成功，已跳转到结果页面。")
            return job_resp

        if job_resp.status_code == 202:
            time.sleep(interval)
            continue

        if job_resp.status_code in (301, 302, 303, 307, 308):
            next_url = job_resp.headers.get("Location")
            if next_url:
                job_url = urljoin(HOME_URL, next_url)
                print(f"↪️ 更新轮询地址: {job_url}")
            time.sleep(interval)
            continue

        if job_resp.status_code == 200:
            time.sleep(interval)
            continue

        print(f"❌ 任务异常，状态码: {job_resp.status_code}")
        return None

    print("⏰ 轮询超时，未拿到最终结果")
    return None


def parse_result_table(saved_html):
    """解析 SEA 结果页中的目标表格。"""
    soup = BeautifulSoup(saved_html, "html.parser")

    table = soup.find("table", class_="table table-bordered")
    if table is None:
        raise ValueError("未找到目标表格")

    tbody = table.find("tbody")
    if tbody is None:
        raise ValueError("目标表格缺少 tbody")

    rows = tbody.find_all("tr", recursive=False)
    data_rows = rows[1:]
    results = []

    for row in data_rows:
        tds = row.find_all("td")
        if len(tds) < 5:
            continue

        results.append(
            {
                "Target Key": tds[0].get_text(strip=True),
                "Target Name": tds[1].get_text(strip=True),
                "Description": tds[2].get_text(strip=True),
                "P-Value": tds[3].get_text(strip=True),
                "MaxTC": tds[4].get_text(strip=True),
            }
        )

    return results


def parse_and_print_result(html_text):
    parsed_results = parse_result_table(html_text)
    print(f"✅ 解析完成，共 {len(parsed_results)} 条结果")
    print(parsed_results[:5])
    return parsed_results


def run(smiles, max_wait=120, interval=2):
    session = create_session()

    try:
        csrf_token = fetch_csrf_token(session)
        response = submit_search(session, csrf_token, smiles)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

    if response.status_code == 200:
        if "Results" in response.text:
            print("请求同步完成，正在解析结果...")
            try:
                return parse_and_print_result(response.text)
            except Exception as e:
                print(f"⚠️ 结果解析失败: {e}")
                print(response.text[:1000])
                return None

        print("200 响应未包含结果页，尝试进入任务页轮询...")
        job_url = extract_job_url(response) or response.url
        final_response = wait_for_job_result(
            session, job_url, max_wait=max_wait, interval=interval
        )
        if final_response is None:
            print("❌ 等待超时，未检测到结果页面。")
            return None

        try:
            return parse_and_print_result(final_response.text)
        except Exception as e:
            print(f"⚠️ 结果解析失败: {e}")
            print(final_response.text[:1000])
            return None

    if response.status_code == 202:
        print("请求已接受，任务在后台执行中...")
        job_url = extract_job_url(response)
        if not job_url:
            print("❌ 未找到任务 URL，无法继续轮询。")
            return None

        final_response = wait_for_job_result(
            session, job_url, max_wait=max_wait, interval=interval
        )
        if final_response is None:
            return None

        try:
            return parse_and_print_result(final_response.text)
        except Exception as e:
            print(f"⚠️ 结果解析失败: {e}")
            print(final_response.text[:1000])
            return None

    print("❌ 提交失败，服务器未接受请求。")
    print(response.text[:500])
    return None


def main(smiles, max_wait=120, interval=2):
    return run(smiles, max_wait=max_wait, interval=interval)


if __name__ == "__main__":
    demo_smiles = "OC1=C2C=3[C@](CC=4C2=C(O)C(OC)=CC4)([N+](C)(C)CCC3C=C1OC)[H]"
    main(demo_smiles, max_wait=120, interval=2)
