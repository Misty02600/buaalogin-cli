"""检查状态 API 与 requests 侧网关访问结果。"""

from __future__ import annotations

import argparse
import socket
from urllib.parse import urlparse

import requests
from common import (
    DEFAULT_HEADERS,
    GATEWAY_URL,
    RAD_USER_INFO_URL,
    create_run_dir,
    print_run_summary,
    write_json,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="检查 rad_user_info 接口和 requests 访问网关时的行为。"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="requests 超时时间（秒）。",
    )
    parser.add_argument(
        "--label",
        help="可选标签，用于区分不同采样目录。",
    )
    return parser.parse_args()


def probe_request(url: str, *, timeout: float) -> dict:
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        return {
            "ok": True,
            "status_code": response.status_code,
            "final_url": response.url,
            "headers": dict(response.headers),
            "text": response.text,
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def infer_status(api_result: dict) -> str:
    if not api_result["ok"]:
        return "unknown_network"

    text = api_result["text"].strip()
    if text == "not_online_error":
        return "logged_out"
    if text:
        return "logged_in"
    return "logged_out"


def resolve_host(url: str) -> dict:
    host = urlparse(url).hostname
    if host is None:
        return {"ok": False, "error": "missing host"}

    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, None)})
        return {"ok": True, "host": host, "addresses": addresses}
    except socket.gaierror as exc:
        return {
            "ok": False,
            "host": host,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def main() -> None:
    args = parse_args()
    run_dir = create_run_dir("check-status-api", args.label)

    gateway_result = probe_request(GATEWAY_URL, timeout=args.timeout)
    api_result = probe_request(RAD_USER_INFO_URL, timeout=args.timeout)
    dns_result = resolve_host(GATEWAY_URL)

    if gateway_result["ok"]:
        write_text(run_dir / "gateway-response.html", gateway_result["text"])
    if api_result["ok"]:
        write_text(run_dir / "rad-user-info.txt", api_result["text"])

    summary = {
        "script": "check_status_api.py",
        "gateway_url": GATEWAY_URL,
        "status_api_url": RAD_USER_INFO_URL,
        "timeout_seconds": args.timeout,
        "dns": dns_result,
        "gateway": {
            key: value for key, value in gateway_result.items() if key != "text"
        },
        "status_api": {
            key: value for key, value in api_result.items() if key != "text"
        },
        "inferred_status": infer_status(api_result),
        "artifacts": {
            "gateway_html": "gateway-response.html" if gateway_result["ok"] else None,
            "status_api_text": "rad-user-info.txt" if api_result["ok"] else None,
        },
    }

    write_json(run_dir / "summary.json", summary)
    write_json(run_dir / "gateway-metadata.json", gateway_result)
    write_json(run_dir / "status-api-metadata.json", api_result)

    print_run_summary("check_status_api.py", run_dir)


if __name__ == "__main__":
    main()
