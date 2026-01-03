from playwright.sync_api import sync_playwright
import pandas as pd
import json
import time


def crawl_dce_api():
    source_url = "http://www.dce.com.cn/dce/channel/list/180.html"
    target_api = "http://www.dce.com.cn/dcereport/publicweb/tradepara/contractInfo"

    request_data = {"varietyId": "all", "tradeType": "1", "lang": "zh"}

    custom_headers = {
        "accept": "application/json, text/plain, */*",
        "cache-control": "no-cache",
        "clientid": "web",
        "pragma": "no-cache",
        "referer": source_url,
        "origin": "https://www.dce.com.cn",
        "content-type": "application/json",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        page = context.new_page()

        try:
            print("正在加载来源页面，生成有效会话...")
            page.goto(source_url, wait_until="load", timeout=30000)

            page.wait_for_selector("html", state="attached", timeout=20000)

            time.sleep(3)

            page_content = page.content()
            if len(page_content.strip()) < 100:
                raise Exception("页面加载失败，内容为空")
            print("来源页面加载成功，无超时异常！")

            print("正在发送接口请求...")
            response = context.request.post(
                url=target_api,
                data=json.dumps(request_data),
                headers=custom_headers,
                timeout=30000,
            )

            if response.ok:
                result = response.json()
                print("接口请求成功！返回数据：")
                data_json = json.dumps(result, ensure_ascii=False, indent=2)

                df = pd.DataFrame(result["data"])
                print(df.head())
            else:
                print(f"接口请求失败，状态码：{response.status}")
                print(f"失败响应内容：{response.text()}")

        except Exception as e:
            page.screenshot(path="error_page.png")
            print(f"爬取异常：{str(e)}")
        finally:
            time.sleep(2)
            browser.close()


if __name__ == "__main__":
    crawl_dce_api()