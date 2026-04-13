"""探测当前登录页的真实表单结构与提交流程。"""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    LOGIN_URL,
    attach_page_recorders,
    collect_page_inventory,
    create_run_dir,
    print_run_summary,
    redact_visible_form_values,
    resolve_credentials,
    wait_for_page_ready,
    write_json,
    write_text,
)
from playwright.sync_api import sync_playwright

USERNAME_SELECTORS = [
    "#username:visible",
    "input[name='username']:visible",
    "input[name='user']:visible",
    "input[type='text']:visible",
    "input[type='tel']:visible",
]

PASSWORD_SELECTORS = [
    "#password:visible",
    "input[name='password']:visible",
    "input[name='passwd']:visible",
    "input[name='pwd']:visible",
    "input[type='password']:visible",
]

SUBMIT_SELECTORS = [
    "#login:visible",
    "#login-account:visible",
    "#loginBtn:visible",
    "#login-btn:visible",
    "button[type='submit']:visible",
    "input[type='submit']:visible",
    "button:has-text('登录'):visible",
    "button:has-text('Login'):visible",
    "a:has-text('登录'):visible",
]

ERROR_SELECTORS = [
    ".layui-layer-content",
    ".error-message",
    ".alert-danger",
    ".alert-error",
    ".error",
    "#error-msg",
    "#errormsg",
    ".msg-error",
    ".login-error",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="探测当前登录页面的输入框、按钮、错误提示与提交后的跳转行为。"
    )
    parser.add_argument("--url", default=LOGIN_URL, help="登录页 URL。")
    parser.add_argument(
        "--submit-mode",
        choices=["none", "invalid", "real"],
        default="invalid",
        help="none=只采样不提交，invalid=提交错误凭据，real=提交真实凭据。",
    )
    parser.add_argument("--user", help="校园网用户名，仅在 real 模式下使用。")
    parser.add_argument("--password", help="校园网密码，仅在 real 模式下使用。")
    parser.add_argument(
        "--invalid-user",
        default="diagnostic_invalid_user",
        help="invalid 模式下使用的假用户名。",
    )
    parser.add_argument(
        "--invalid-password",
        default="diagnostic_invalid_password",
        help="invalid 模式下使用的假密码。",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="显示浏览器窗口，默认无头运行。",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=30000,
        help="页面加载超时时间（毫秒）。",
    )
    parser.add_argument(
        "--wait-after-submit-ms",
        type=int,
        default=5000,
        help="点击提交后额外等待的时间（毫秒）。",
    )
    parser.add_argument("--label", help="可选标签，用于区分不同采样目录。")
    return parser.parse_args()


def probe_selectors(
    page,
    selectors: list[str],
) -> tuple[list[dict[str, Any]], str | None]:
    results: list[dict[str, Any]] = []
    chosen: str | None = None

    for selector in selectors:
        locator = page.locator(selector)
        count = locator.count()
        visible = False
        sample: dict[str, Any] | None = None

        if count:
            first = locator.first
            try:
                visible = first.is_visible(timeout=500)
            except Exception:
                visible = False

            try:
                sample = first.evaluate(
                    """(element) => ({
                        tag: element.tagName.toLowerCase(),
                        id: element.id || "",
                        name: element.getAttribute("name") || "",
                        type: element.getAttribute("type") || "",
                        className: String(element.className || "").trim(),
                        text: (element.innerText || element.textContent || element.value || "").trim().slice(0, 160),
                    })"""
                )
            except Exception:
                sample = None

        if visible and chosen is None:
            chosen = selector

        results.append(
            {
                "selector": selector,
                "count": count,
                "visible": visible,
                "sample": sample,
            }
        )

    return results, chosen


def collect_error_details(page) -> dict[str, Any]:
    selector_results, chosen_selector = probe_selectors(page, ERROR_SELECTORS)
    text_hits = page.evaluate(
        """() => {
            const isVisible = (element) => Boolean(
                element &&
                (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
            );
            const keywords = ["错误", "失败", "认证", "invalid", "error", "incorrect", "wrong"];

            return Array.from(document.querySelectorAll("body *"))
                .map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    id: element.id || "",
                    className: String(element.className || "").trim(),
                    text: String(element.innerText || element.textContent || "").replace(/\\s+/g, " ").trim(),
                    visible: isVisible(element),
                }))
                .filter((item) => item.text && keywords.some((keyword) => item.text.toLowerCase().includes(keyword.toLowerCase())))
                .slice(0, 40);
        }"""
    )

    return {
        "selector_results": selector_results,
        "chosen_selector": chosen_selector,
        "text_hits": text_hits,
    }


def main() -> None:
    args = parse_args()
    run_dir = create_run_dir("probe-login-flow", args.label)

    credentials = resolve_credentials(args.user, args.password)
    if args.submit_mode == "real":
        if credentials["username"] is None or credentials["password"] is None:
            raise SystemExit(
                "real 模式缺少凭据，请提供 --user/--password、环境变量或已保存配置。"
            )
        submit_username = credentials["username"]
        submit_password = credentials["password"]
    elif args.submit_mode == "invalid":
        submit_username = args.invalid_user
        submit_password = args.invalid_password
    else:
        submit_username = None
        submit_password = None

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page()
        requests_log, responses_log, console_log = attach_page_recorders(page)

        try:
            page.goto(args.url, timeout=args.timeout_ms)
            wait_for_page_ready(page, args.timeout_ms)

            before_inventory = collect_page_inventory(page)
            username_results, chosen_username_selector = probe_selectors(
                page, USERNAME_SELECTORS
            )
            password_results, chosen_password_selector = probe_selectors(
                page, PASSWORD_SELECTORS
            )
            submit_results, chosen_submit_selector = probe_selectors(
                page, SUBMIT_SELECTORS
            )

            page.screenshot(path=str(run_dir / "before-submit.png"), full_page=True)
            write_text(run_dir / "before-submit.html", page.content())
            write_json(run_dir / "before-inventory.json", before_inventory)

            submit_action = "not_requested"
            if args.submit_mode != "none":
                if chosen_username_selector is None or chosen_password_selector is None:
                    submit_action = "missing-input-selector"
                else:
                    page.locator(chosen_username_selector).first.fill(
                        submit_username or ""
                    )
                    page.locator(chosen_password_selector).first.fill(
                        submit_password or ""
                    )

                    if args.submit_mode == "invalid":
                        page.screenshot(
                            path=str(run_dir / "after-fill.png"),
                            full_page=True,
                        )

                    if chosen_submit_selector is not None:
                        page.locator(chosen_submit_selector).first.click()
                        submit_action = f"click:{chosen_submit_selector}"
                    else:
                        page.locator(chosen_password_selector).first.press("Enter")
                        submit_action = "press:Enter-on-password"

                    page.wait_for_timeout(args.wait_after_submit_ms)
                    wait_for_page_ready(page, args.timeout_ms)

            after_inventory = collect_page_inventory(page)
            error_details = collect_error_details(page)

            if args.submit_mode == "real":
                redact_visible_form_values(page)

            page.screenshot(path=str(run_dir / "after-submit.png"), full_page=True)
            write_text(run_dir / "after-submit.html", page.content())
            write_json(run_dir / "after-inventory.json", after_inventory)
            write_json(
                run_dir / "selector-probe.json",
                {
                    "username": username_results,
                    "password": password_results,
                    "submit": submit_results,
                    "errors": error_details["selector_results"],
                },
            )
            write_json(run_dir / "error-details.json", error_details)
            write_json(run_dir / "network-requests.json", requests_log)
            write_json(run_dir / "network-responses.json", responses_log)
            write_json(run_dir / "console.json", console_log)

            summary = {
                "script": "probe_login_flow.py",
                "target_url": args.url,
                "submit_mode": args.submit_mode,
                "submit_action": submit_action,
                "initial_url": before_inventory["url"],
                "final_url": after_inventory["url"],
                "title_before": before_inventory["title"],
                "title_after": after_inventory["title"],
                "selected_locators": {
                    "username": chosen_username_selector,
                    "password": chosen_password_selector,
                    "submit": chosen_submit_selector,
                    "error": error_details["chosen_selector"],
                },
                "credential_sources": credentials["sources"],
                "heuristics": {
                    "final_url_contains_success": "success"
                    in after_inventory["url"].lower(),
                    "final_url_contains_srun": "srun" in after_inventory["url"].lower(),
                    "visible_password_inputs_after": [
                        item
                        for item in after_inventory["inputs"]
                        if item["visible"] and item["type"] == "password"
                    ],
                    "error_text_hit_count": len(error_details["text_hits"]),
                },
                "artifact_files": [
                    "before-submit.png",
                    "before-submit.html",
                    "before-inventory.json",
                    "after-submit.png",
                    "after-submit.html",
                    "after-inventory.json",
                    "selector-probe.json",
                    "error-details.json",
                    "network-requests.json",
                    "network-responses.json",
                    "console.json",
                ]
                + (["after-fill.png"] if args.submit_mode == "invalid" else []),
            }
            write_json(run_dir / "summary.json", summary)
        finally:
            browser.close()

    print_run_summary("probe_login_flow.py", run_dir)


if __name__ == "__main__":
    main()
