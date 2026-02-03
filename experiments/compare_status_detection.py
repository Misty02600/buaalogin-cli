"""对比 requests 和 Playwright 访问校园网网关的结果"""

import asyncio
from playwright.async_api import async_playwright
import requests

GATEWAY_URL = "https://gw.buaa.edu.cn/"


def test_with_requests():
    print("=" * 60)
    print("【requests 检测】")
    print("=" * 60)

    try:
        r = requests.get(
            GATEWAY_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            allow_redirects=True,
        )
        print(f"状态码: {r.status_code}")
        print(f"最终 URL: {r.url}")
        print(f"包含 'success': {'success' in r.url.lower()}")

        if "<title>" in r.text:
            start = r.text.find("<title>") + 7
            end = r.text.find("</title>")
            print(f"页面标题: {r.text[start:end]}")

        keywords = ["success", "登录成功", "注销", "已登录", "在线"]
        for kw in keywords:
            found = kw in r.text.lower() or kw in r.url.lower()
            print(f"  '{kw}': {'✅' if found else '❌'}")

        return r.url
    except Exception as e:
        print(f"失败: {e}")
        return None


async def test_with_playwright():
    print("\n" + "=" * 60)
    print("【Playwright 检测】")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(GATEWAY_URL, wait_until="networkidle", timeout=15000)

            print(f"最终 URL: {page.url}")
            print(f"包含 'success': {'success' in page.url.lower()}")
            print(f"页面标题: {await page.title()}")

            content = await page.content()
            keywords = ["success", "登录成功", "注销", "已登录", "在线"]
            for kw in keywords:
                found = kw in content.lower() or kw in page.url.lower()
                print(f"  '{kw}': {'✅' if found else '❌'}")

            await page.screenshot(path=".sandbox/gateway_screenshot.png")
            print("\n截图: .sandbox/gateway_screenshot.png")

            return page.url
        except Exception as e:
            print(f"失败: {e}")
            return None
        finally:
            await browser.close()


def test_srun_api():
    """测试深澜 rad_user_info API"""
    print("\n" + "=" * 60)
    print("【深澜 API 检测】")
    print("=" * 60)

    api_url = "https://gw.buaa.edu.cn/cgi-bin/rad_user_info"

    try:
        r = requests.get(
            api_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        print(f"URL: {api_url}")
        print(f"状态码: {r.status_code}")
        print(f"响应内容: {r.text[:500]}")

        # 解析判断
        text = r.text.strip()
        if "error" in text.lower() or text == "" or "not_online" in text.lower():
            print("\n❌ API 显示：未登录")
            return False
        else:
            print("\n✅ API 显示：已登录")
            return True
    except Exception as e:
        print(f"失败: {e}")
        return None


async def main():
    req_url = test_with_requests()
    api_result = test_srun_api()
    pw_url = await test_with_playwright()

    print("\n" + "=" * 60)
    print("【对比】")
    print(f"requests:   {req_url}")
    print(f"API 检测:   {'已登录' if api_result else '未登录'}")
    print(f"Playwright: {pw_url}")


if __name__ == "__main__":
    asyncio.run(main())
