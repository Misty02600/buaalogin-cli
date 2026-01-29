"""调试脚本：检查登录页面 DOM 结构"""

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    url = "http://gw.buaa.edu.cn/srun_portal_pc?ac_id=1&theme=buaa"
    print(f"正在访问: {url}")

    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
        print(f"页面标题: {page.title()}")
        print(f"当前URL: {page.url}")

        # 保存页面截图
        page.screenshot(path="debug_screenshot.png")
        print("已保存截图: debug_screenshot.png")

        print("\n=== INPUT 元素 ===")
        inputs = page.query_selector_all("input")
        for inp in inputs:
            name = inp.get_attribute("name") or ""
            id_ = inp.get_attribute("id") or ""
            type_ = inp.get_attribute("type") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            visible = inp.is_visible()
            print(
                f"  name={name!r}, id={id_!r}, type={type_!r}, placeholder={placeholder!r}, visible={visible}"
            )

        print("\n=== BUTTON 元素 ===")
        buttons = page.query_selector_all("button")
        for btn in buttons:
            id_ = btn.get_attribute("id") or ""
            cls = btn.get_attribute("class") or ""
            text = (btn.text_content() or "").strip()
            visible = btn.is_visible()
            print(f"  id={id_!r}, class={cls!r}, text={text!r}, visible={visible}")

        print("\n=== A 链接（可能是登录按钮）===")
        links = page.query_selector_all("a")
        for link in links:
            id_ = link.get_attribute("id") or ""
            cls = link.get_attribute("class") or ""
            href = link.get_attribute("href") or ""
            text = (link.text_content() or "").strip()[:20]
            visible = link.is_visible()
            if id_ or "login" in cls.lower() or "登录" in text:
                print(f"  id={id_!r}, class={cls!r}, text={text!r}, visible={visible}")

    except Exception as e:
        print(f"错误: {e}")

    input("\n按回车关闭浏览器...")
    browser.close()
