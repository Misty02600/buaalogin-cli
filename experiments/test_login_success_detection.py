"""
测试登录成功后页面状态的调试脚本

运行方式：
1. 确保 .env 中配置了正确的账号密码
2. 断开校园网（未登录状态）
3. 运行: uv run python scripts/test_login_success_detection.py

此脚本会执行登录，然后检测三种方法的可靠性
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

LOGIN_URL = "https://gw.buaa.edu.cn/srun_portal_pc?ac_id=1&theme=buaa"


def test_detection_methods(page):
    """测试三种检测登录成功的方法"""
    print("\n" + "=" * 60)
    print("检测登录成功方法测试")
    print("=" * 60)

    # 方法1：检查注销按钮
    print("\n=== 方法1: 检查注销按钮 ===")
    try:
        logout_locator = page.locator("text=注销, text=logout, text=下线").first
        is_visible = logout_locator.is_visible(timeout=2000)
        print(f"注销按钮可见: {is_visible}")
        if is_visible:
            text = logout_locator.text_content()
            print(f"按钮文字: {text!r}")
    except Exception as e:
        print(f"检测失败: {e}")

    # 方法2：检查 URL
    print("\n=== 方法2: 检查 URL ===")
    current_url = page.url
    print(f"当前 URL: {current_url}")
    print(f"包含 'success': {'success' in current_url.lower()}")
    print(f"包含 'online': {'online' in current_url.lower()}")

    # 方法3：检查成功提示文字
    print("\n=== 方法3: 检查成功提示文字 ===")
    try:
        success_locator = page.locator("text=登录成功, text=success, text=已连接").first
        is_visible = success_locator.is_visible(timeout=1000)
        print(f"成功提示可见: {is_visible}")
        if is_visible:
            text = success_locator.text_content()
            print(f"提示文字: {text!r}")
    except Exception as e:
        print(f"检测失败: {e}")

    # 额外检测：页面内容分析
    print("\n=== 额外: 页面内容分析 ===")
    print(f"页面标题: {page.title()}")

    # 查找所有可能的状态指示元素
    print("\n查找包含关键词的元素:")
    keywords = [
        "注销",
        "logout",
        "下线",
        "在线",
        "online",
        "成功",
        "success",
        "已连接",
        "用户",
    ]
    for kw in keywords:
        try:
            elements = page.locator(f"text={kw}").all()
            if elements:
                print(f"  '{kw}': 找到 {len(elements)} 个元素")
                for i, el in enumerate(elements[:3]):  # 最多显示3个
                    try:
                        if el.is_visible():
                            text = el.text_content()[:50] if el.text_content() else ""
                            print(f"    [{i}] visible=True, text={text!r}")
                    except:
                        pass
        except:
            pass


def main():
    username = os.getenv("BUAA_USERNAME")
    password = os.getenv("BUAA_PASSWORD")

    if not username or not password:
        print("错误: 请在 .env 文件中配置 BUAA_USERNAME 和 BUAA_PASSWORD")
        return

    print(f"使用账户: {username}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        try:
            print(f"\n访问: {LOGIN_URL}")
            page.goto(LOGIN_URL, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            print(f"当前 URL: {page.url}")
            page.screenshot(path="screenshot_initial.png")
            print("截图已保存: screenshot_initial.png")

            # 检查是否已登录
            test_detection_methods(page)

            # 如果看起来是登录页面，尝试登录
            if "username" in page.content() or "password" in page.content():
                print("\n" + "=" * 60)
                print("检测到登录表单，尝试登录...")
                print("=" * 60)

                username_input = page.locator("#username:visible").first
                password_input = page.locator("#password:visible").first

                if username_input.count() > 0 and password_input.count() > 0:
                    username_input.fill(username)
                    password_input.fill(password)

                    login_button = page.locator(
                        '#login-account, button:has-text("登录"), button:has-text("Login")'
                    ).first
                    login_button.click()

                    print("等待登录结果...")
                    page.wait_for_timeout(5000)

                    page.screenshot(path="screenshot_after_login.png")
                    print("截图已保存: screenshot_after_login.png")

                    # 再次测试检测方法
                    print("\n\n【登录后再次检测】")
                    test_detection_methods(page)
                else:
                    print("未找到用户名/密码输入框")
            else:
                print("\n看起来已经登录了")

        except Exception as e:
            print(f"错误: {e}")
            import traceback

            traceback.print_exc()

        input("\n按回车关闭浏览器...")
        browser.close()


if __name__ == "__main__":
    main()
