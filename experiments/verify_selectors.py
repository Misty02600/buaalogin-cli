"""验证登录页面选择器的脚本。

离线运行此脚本，它会：
1. 打开登录页面，截图并保存 HTML
2. 尝试用错误密码登录，截图并保存错误信息
3. 所有结果保存到 .sandbox/ 目录

运行方式（在校园网未登录状态下）：
    uv run python experiments/verify_selectors.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / ".sandbox"
OUTPUT_DIR.mkdir(exist_ok=True)

# 登录页面 URL
LOGIN_URL = "https://gw.buaa.edu.cn/"


def main():
    print("=" * 60)
    print("BUAA 登录页面选择器验证脚本")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式方便观察
        page = browser.new_page()

        # region 步骤 1: 打开登录页面
        print("\n[1/4] 正在打开登录页面...")
        page.goto(LOGIN_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        # 截图
        page.screenshot(path=OUTPUT_DIR / "01_login_page.png", full_page=True)
        print("  ✓ 截图已保存: 01_login_page.png")

        # 保存 HTML
        html_content = page.content()
        (OUTPUT_DIR / "01_login_page.html").write_text(html_content, encoding="utf-8")
        print("  ✓ HTML 已保存: 01_login_page.html")
        # endregion

        # region 步骤 2: 分析登录表单元素
        print("\n[2/4] 正在分析登录表单元素...")

        report_lines = ["# 登录页面元素分析报告", "", f"URL: {page.url}", ""]

        # 查找用户名输入框
        report_lines.append("## 用户名输入框")
        username_selectors = [
            "#username",
            "input[name='username']",
            "input[type='text']",
        ]
        for sel in username_selectors:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=500):
                    report_lines.append(f"- `{sel}` ✓ 可见")
                    # 获取更多属性
                    attrs = page.evaluate(f"""() => {{
                        const el = document.querySelector("{sel}");
                        if (!el) return null;
                        return {{
                            id: el.id,
                            name: el.name,
                            className: el.className,
                            type: el.type,
                            placeholder: el.placeholder
                        }};
                    }}""")
                    if attrs:
                        report_lines.append(f"  - 属性: {attrs}")
                else:
                    report_lines.append(f"- `{sel}` ✗ 不可见")
            except Exception as e:
                report_lines.append(f"- `{sel}` ✗ 错误: {e}")

        # 查找密码输入框
        report_lines.append("")
        report_lines.append("## 密码输入框")
        password_selectors = [
            "#password",
            "input[name='password']",
            "input[type='password']",
        ]
        for sel in password_selectors:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=500):
                    report_lines.append(f"- `{sel}` ✓ 可见")
                    attrs = page.evaluate(f"""() => {{
                        const el = document.querySelector("{sel}");
                        if (!el) return null;
                        return {{
                            id: el.id,
                            name: el.name,
                            className: el.className,
                            type: el.type
                        }};
                    }}""")
                    if attrs:
                        report_lines.append(f"  - 属性: {attrs}")
                else:
                    report_lines.append(f"- `{sel}` ✗ 不可见")
            except Exception as e:
                report_lines.append(f"- `{sel}` ✗ 错误: {e}")

        # 查找登录按钮
        report_lines.append("")
        report_lines.append("## 登录按钮")
        button_selectors = [
            "#login-account",
            "button[type='submit']",
            "input[type='submit']",
            'button:has-text("登录")',
            'button:has-text("Login")',
            ".btn-submit",
            "#login-btn",
            "#loginBtn",
        ]
        for sel in button_selectors:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=500):
                    text = elem.text_content() or "(无文本)"
                    report_lines.append(f"- `{sel}` ✓ 可见, 文本: {text!r}")
                else:
                    report_lines.append(f"- `{sel}` ✗ 不可见")
            except Exception as e:
                report_lines.append(f"- `{sel}` ✗ 错误: {e}")

        # 列出所有按钮
        report_lines.append("")
        report_lines.append("## 页面上所有按钮")
        all_buttons = page.evaluate("""() => {
            const buttons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
            return Array.from(buttons).map(b => ({
                tag: b.tagName,
                id: b.id,
                className: b.className,
                type: b.type,
                text: b.textContent?.trim() || b.value || ''
            }));
        }""")
        for btn in all_buttons:
            report_lines.append(f"- {btn}")
        # endregion

        # region 步骤 3: 尝试登录并捕获错误
        print("\n[3/4] 正在尝试登录（使用错误密码）...")

        # 填写错误凭据
        try:
            page.locator("#username").first.fill("test_invalid_user")
            page.locator("#password").first.fill("test_invalid_pass")
            print("  ✓ 已填写测试凭据")
        except Exception as e:
            print(f"  ✗ 填写凭据失败: {e}")
            report_lines.append("")
            report_lines.append("## 填写凭据失败")
            report_lines.append(f"错误: {e}")

        # 截图（填写后）
        page.screenshot(path=OUTPUT_DIR / "02_filled_form.png")
        print("  ✓ 截图已保存: 02_filled_form.png")

        # 点击登录按钮
        login_clicked = False
        for sel in button_selectors:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=500):
                    elem.click()
                    login_clicked = True
                    print(f"  ✓ 点击了登录按钮: {sel}")
                    break
            except Exception:
                continue

        if not login_clicked:
            print("  ✗ 未能找到可点击的登录按钮")

        # 等待响应
        page.wait_for_timeout(3000)

        # 截图（登录后）
        page.screenshot(path=OUTPUT_DIR / "03_after_login.png", full_page=True)
        print("  ✓ 截图已保存: 03_after_login.png")

        # 保存登录后的 HTML
        html_after = page.content()
        (OUTPUT_DIR / "03_after_login.html").write_text(html_after, encoding="utf-8")
        print("  ✓ HTML 已保存: 03_after_login.html")
        # endregion

        # region 步骤 4: 分析错误信息元素
        print("\n[4/4] 正在分析错误信息元素...")

        report_lines.append("")
        report_lines.append("## 错误信息元素")
        report_lines.append(f"登录后 URL: {page.url}")

        error_selectors = [
            ".error-message",
            ".alert-danger",
            ".alert-error",
            ".error",
            "#error-msg",
            "#errormsg",
            ".msg-error",
            ".login-error",
            '[class*="error"]',
            '[class*="alert"]',
            '[id*="error"]',
        ]

        for sel in error_selectors:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=500):
                    text = elem.text_content() or "(无文本)"
                    report_lines.append(f"- `{sel}` ✓ 可见, 内容: {text!r}")
                else:
                    report_lines.append(f"- `{sel}` ✗ 不可见")
            except Exception as e:
                report_lines.append(f"- `{sel}` ✗ 错误: {e}")

        # 搜索包含特定文本的元素
        report_lines.append("")
        report_lines.append("## 包含错误关键词的元素")
        error_keywords = ["错误", "失败", "error", "invalid", "incorrect", "wrong"]
        found_texts = page.evaluate(
            """(keywords) => {
            const results = [];
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
                const text = walker.currentNode.textContent.trim();
                if (text && keywords.some(k => text.toLowerCase().includes(k.toLowerCase()))) {
                    const parent = walker.currentNode.parentElement;
                    results.push({
                        text: text.substring(0, 100),
                        tag: parent?.tagName,
                        id: parent?.id,
                        className: parent?.className
                    });
                }
            }
            return results;
        }""",
            error_keywords,
        )

        for item in found_texts:
            report_lines.append(f"- {item}")
        # endregion

        # 保存报告
        report_content = "\n".join(report_lines)
        (OUTPUT_DIR / "report.md").write_text(report_content, encoding="utf-8")
        print("\n✓ 分析报告已保存: report.md")

        browser.close()

    print("\n" + "=" * 60)
    print("验证完成！请查看以下文件：")
    print(f"  {OUTPUT_DIR}")
    print("  - 01_login_page.png/html  (登录页面)")
    print("  - 02_filled_form.png      (填写表单后)")
    print("  - 03_after_login.png/html (点击登录后)")
    print("  - report.md               (元素分析报告)")
    print("=" * 60)


if __name__ == "__main__":
    main()
