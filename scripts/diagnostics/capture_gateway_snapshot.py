"""抓取当前网关页面的静态快照。"""

from __future__ import annotations

import argparse

from common import (
    LOGIN_URL,
    attach_page_recorders,
    collect_page_inventory,
    create_run_dir,
    print_run_summary,
    wait_for_page_ready,
    write_json,
    write_text,
)
from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="抓取当前校园网网关页面的截图、HTML 和 DOM 摘要。"
    )
    parser.add_argument("--url", default=LOGIN_URL, help="要访问的网关 URL。")
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
        "--label",
        help="可选标签，用于区分不同采样目录。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = create_run_dir("capture-gateway-snapshot", args.label)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page()
        requests_log, responses_log, console_log = attach_page_recorders(page)

        try:
            page.goto(args.url, timeout=args.timeout_ms)
            wait_for_page_ready(page, args.timeout_ms)

            inventory = collect_page_inventory(page)

            page.screenshot(path=str(run_dir / "page.png"), full_page=True)
            write_text(run_dir / "page.html", page.content())
            write_json(run_dir / "inventory.json", inventory)
            write_json(run_dir / "network-requests.json", requests_log)
            write_json(run_dir / "network-responses.json", responses_log)
            write_json(run_dir / "console.json", console_log)

            summary = {
                "script": "capture_gateway_snapshot.py",
                "target_url": args.url,
                "final_url": page.url,
                "title": page.title(),
                "input_count": len(inventory["inputs"]),
                "button_count": len(inventory["buttons"]),
                "form_count": len(inventory["forms"]),
                "request_count": len(requests_log),
                "response_count": len(responses_log),
                "console_count": len(console_log),
                "artifacts": {
                    "screenshot": "page.png",
                    "html": "page.html",
                    "inventory": "inventory.json",
                    "requests": "network-requests.json",
                    "responses": "network-responses.json",
                    "console": "console.json",
                },
            }
            write_json(run_dir / "summary.json", summary)
        finally:
            browser.close()

    print_run_summary("capture_gateway_snapshot.py", run_dir)


if __name__ == "__main__":
    main()
