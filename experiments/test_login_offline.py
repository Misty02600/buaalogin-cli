"""
离线测试脚本 - 断开校园网后运行此脚本测试登录功能
运行方式: uv run python test_login_offline.py
结果会保存到 test_result.log
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "test_result.log"


def log(msg):
    """打印并写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    # 清空旧日志
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== 离线登录测试 ===\n\n")

    log("开始测试...")

    # 读取凭据
    username = os.getenv("BUAA_USERNAME")
    password = os.getenv("BUAA_PASSWORD")

    if not username or not password:
        log("错误: 未找到 BUAA_USERNAME 或 BUAA_PASSWORD 环境变量")
        log("请检查 .env 文件")
        return

    log(f"使用账户: {username}")

    # 测试 Playwright 登录
    log("正在启动 Playwright...")

    from playwright.sync_api import sync_playwright

    url = "http://gw.buaa.edu.cn/srun_portal_pc?ac_id=1&theme=buaa"

    with sync_playwright() as p:
        log("启动浏览器 (有头模式)...")
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()

        try:
            log(f"访问: {url}")
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            current_url = page.url
            log(f"当前URL: {current_url}")
            log(f"页面标题: {page.title()}")

            # 检查是否已登录
            if "success" in current_url:
                log("检测到已登录状态，无需登录")
                page.screenshot(path="screenshot_already_logged.png")
                log("截图已保存: screenshot_already_logged.png")
            else:
                log("检测到未登录状态，开始填写表单...")
                page.screenshot(path="screenshot_before_login.png")
                log("截图已保存: screenshot_before_login.png")

                # 打印所有可见的 input
                log("=== 查找输入框 ===")
                inputs = page.query_selector_all("input")
                for inp in inputs:
                    name = inp.get_attribute("name") or ""
                    id_ = inp.get_attribute("id") or ""
                    type_ = inp.get_attribute("type") or ""
                    visible = inp.is_visible()
                    log(
                        f"  input: name={name}, id={id_}, type={type_}, visible={visible}"
                    )

                # 尝试填写用户名
                log("尝试填写用户名...")
                username_input = page.locator(
                    'input[name="username"]:visible, input#username:visible'
                ).first
                if username_input.count() > 0:
                    username_input.fill(username)
                    log("用户名已填写")
                else:
                    log("警告: 未找到可见的用户名输入框")

                # 尝试填写密码
                log("尝试填写密码...")
                password_input = page.locator(
                    'input[name="password"]:visible, input#password:visible, input[type="password"]:visible'
                ).first
                if password_input.count() > 0:
                    password_input.fill(password)
                    log("密码已填写")
                else:
                    log("警告: 未找到可见的密码输入框")

                page.screenshot(path="screenshot_after_fill.png")
                log("截图已保存: screenshot_after_fill.png")

                # 尝试点击登录按钮
                log("尝试点击登录按钮...")
                login_btn = page.locator(
                    'button:has-text("登录"), button:has-text("Login"), #login-account, input[type="submit"]'
                ).first
                if login_btn.count() > 0:
                    login_btn.click()
                    log("已点击登录按钮")
                else:
                    log("警告: 未找到登录按钮")

                # 等待结果
                page.wait_for_timeout(5000)
                page.screenshot(path="screenshot_after_login.png")
                log("截图已保存: screenshot_after_login.png")

                final_url = page.url
                log(f"登录后URL: {final_url}")

                if "success" in final_url:
                    log("✅ 登录成功！")
                else:
                    log("❌ 登录可能失败，请检查截图")

        except Exception as e:
            log(f"错误: {e}")
            page.screenshot(path="screenshot_error.png")
            log("错误截图已保存: screenshot_error.png")

        finally:
            log("测试完成，5秒后关闭浏览器...")
            page.wait_for_timeout(5000)
            browser.close()

    log(f"\n测试结束，详细日志请查看: {LOG_FILE}")
    log("截图文件请查看项目根目录下的 screenshot_*.png")


if __name__ == "__main__":
    main()
