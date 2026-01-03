#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/31 16:00
Desc: 大连商品交易所-业务数据-交易参数-日交易参数
http://www.dce.com.cn/dce/channel/list/180.html
"""

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import time


def contract_info_dec(instrument: str = "Future") -> pd.DataFrame:
    """
    大连商品交易所-业务数据-交易参数-日交易参数
    http://www.dce.com.cn/dce/channel/list/180.html
    :param instrument: 合约类型
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    # 映射合约类型到trade_type编码
    instrument_mapping = {"Future": "0", "Option": "1"}
    # 校验参数合法性
    if instrument not in instrument_mapping:
        raise ValueError(f"instrument参数仅支持：{list(instrument_mapping.keys())}")
    source_url = "http://www.dce.com.cn/dce/channel/list/180.html"
    target_api = "http://www.dce.com.cn/dcereport/publicweb/tradepara/contractInfo"

    request_data = {
        "varietyId": "all",
        "tradeType": instrument_mapping[instrument],
        "lang": "zh",
    }

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
            # 正在加载来源页面，生成有效会话...
            page.goto(source_url, wait_until="load", timeout=30000)

            page.wait_for_selector("html", state="attached", timeout=20000)

            time.sleep(3)

            page_content = page.content()
            if len(page_content.strip()) < 100:
                raise Exception("页面加载失败，内容为空")
            # 来源页面加载成功，无超时异常！

            # 正在发送接口请求...
            response = context.request.post(
                url=target_api,
                data=json.dumps(request_data),
                headers=custom_headers,
                timeout=30000,
            )

            if response.ok:
                result = response.json()
                # 接口请求成功！返回数据：
                df = pd.DataFrame(result["data"])
                return df
        except Exception as e:
            raise e
        finally:
            time.sleep(2)
            browser.close()


if __name__ == "__main__":
    contract_info_dec_df = contract_info_dec()
    print(contract_info_dec_df)
