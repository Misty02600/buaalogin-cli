"""诊断脚本共用工具。"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeout

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from buaalogin_cli.config import config
from buaalogin_cli.constants import GATEWAY_URL, LOGIN_URL, RAD_USER_INFO_URL

ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts"
DIAGNOSTICS_ROOT = ARTIFACTS_ROOT / "diagnostics"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}

_SENSITIVE_PATTERNS = [
    re.compile(r"((?:pass|password|passwd|pwd)=)([^&\\s]+)", re.IGNORECASE),
    re.compile(r"((?:user|username)=)([^&\\s]+)", re.IGNORECASE),
]


def slugify(value: str) -> str:
    """将标签转换为适合文件名的短字符串。"""
    slug = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip())
    return slug.strip("-._") or "run"


def create_run_dir(script_name: str, label: str | None = None) -> Path:
    """创建本次诊断运行目录。"""
    DIAGNOSTICS_ROOT.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{timestamp}-{script_name}"
    if label:
        name = f"{name}-{slugify(label)}"

    run_dir = DIAGNOSTICS_ROOT / name
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_json(path: Path, payload: Any) -> None:
    """写入 UTF-8 JSON。"""
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, content: str) -> None:
    """写入 UTF-8 文本。"""
    path.write_text(content, encoding="utf-8")


def wait_for_page_ready(page, timeout_ms: int) -> None:
    """尽量等待页面稳定，避免卡在 networkidle。"""
    page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    try:
        page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 10000))
    except PlaywrightTimeout:
        pass


def attach_page_recorders(
    page,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """附加请求、响应和控制台日志记录器。"""
    request_events: list[dict[str, Any]] = []
    response_events: list[dict[str, Any]] = []
    console_events: list[dict[str, Any]] = []

    def on_request(request) -> None:
        post_data = request.post_data or ""
        request_events.append(
            {
                "method": request.method,
                "url": redact_sensitive_text(request.url),
                "resource_type": request.resource_type,
                "is_navigation_request": request.is_navigation_request(),
                "post_data_length": len(post_data),
                "post_data_preview": redact_sensitive_text(post_data[:200])
                if post_data
                else "",
            }
        )

    def on_response(response) -> None:
        try:
            content_type = response.headers.get("content-type", "")
        except Exception:
            content_type = ""

        response_events.append(
            {
                "url": redact_sensitive_text(response.url),
                "status": response.status,
                "ok": response.ok,
                "content_type": content_type,
            }
        )

    def on_console(message) -> None:
        console_events.append(
            {
                "type": message.type,
                "text": redact_sensitive_text(message.text),
            }
        )

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("console", on_console)

    return request_events, response_events, console_events


def collect_page_inventory(page) -> dict[str, Any]:
    """采集页面上的表单、输入框、按钮和关键文本。"""
    return page.evaluate(
        """() => {
            const isVisible = (element) => Boolean(
                element &&
                (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
            );
            const clean = (value) => String(value ?? "").replace(/\\s+/g, " ").trim();
            const clip = (value, max = 160) => clean(value).slice(0, max);

            const inputs = Array.from(document.querySelectorAll("input, textarea, select"))
                .map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    id: element.id || "",
                    name: element.getAttribute("name") || "",
                    type: element.getAttribute("type") || "",
                    placeholder: element.getAttribute("placeholder") || "",
                    autocomplete: element.getAttribute("autocomplete") || "",
                    className: clean(element.className || ""),
                    visible: isVisible(element),
                }));

            const buttons = Array.from(
                document.querySelectorAll("button, input[type='submit'], input[type='button'], [role='button'], a")
            )
                .map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    id: element.id || "",
                    name: element.getAttribute("name") || "",
                    type: element.getAttribute("type") || "",
                    className: clean(element.className || ""),
                    text: clip(element.innerText || element.textContent || element.value || ""),
                    href: element.getAttribute("href") || "",
                    visible: isVisible(element),
                }))
                .filter((element) => element.visible || element.text || element.id || element.className)
                .slice(0, 120);

            const forms = Array.from(document.querySelectorAll("form"))
                .map((form) => ({
                    id: form.id || "",
                    name: form.getAttribute("name") || "",
                    action: form.getAttribute("action") || "",
                    method: (form.getAttribute("method") || "get").toLowerCase(),
                    className: clean(form.className || ""),
                    visible: isVisible(form),
                    fieldNames: Array.from(form.elements)
                        .map((element) => element.getAttribute ? (element.getAttribute("name") || element.id || "") : "")
                        .filter(Boolean),
                }));

            const interestingText = /login|logout|success|error|用户名|密码|登录|注销|下线|认证|失败|账号/i;
            const textMatches = Array.from(document.querySelectorAll("body *"))
                .map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    id: element.id || "",
                    className: clean(element.className || ""),
                    text: clip(element.innerText || element.textContent || ""),
                    visible: isVisible(element),
                }))
                .filter((item) => item.text && interestingText.test(item.text))
                .slice(0, 80);

            return {
                url: window.location.href,
                title: document.title,
                htmlLength: document.documentElement.outerHTML.length,
                forms,
                inputs,
                buttons,
                textMatches,
            };
        }"""
    )


def resolve_credentials(
    cli_username: str | None,
    cli_password: str | None,
) -> dict[str, Any]:
    """按 CLI > 环境变量 > 配置文件 解析凭据。"""
    saved = config.to_dict()

    username, username_source = _resolve_value(
        cli_username,
        env_var="BUAA_USERNAME",
        config_value=saved.get("username"),
    )
    password, password_source = _resolve_value(
        cli_password,
        env_var="BUAA_PASSWORD",
        config_value=saved.get("password"),
    )

    return {
        "username": username,
        "password": password,
        "sources": {
            "username": username_source,
            "password": password_source,
        },
    }


def _resolve_value(
    cli_value: str | None,
    *,
    env_var: str,
    config_value: str | None,
) -> tuple[str | None, str]:
    if cli_value:
        return cli_value, "cli"

    env_value = os.getenv(env_var)
    if env_value:
        return env_value, "env"

    if config_value:
        return config_value, "config"

    return None, "missing"


def redact_sensitive_text(text: str) -> str:
    """脱敏 URL / 表单串中的账号密码。"""
    redacted = text
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(r"\\1<redacted>", redacted)
    return redacted


def redact_visible_form_values(page) -> None:
    """在截图前覆盖表单中的可见值，避免泄露凭据。"""
    page.evaluate(
        """() => {
            const isVisible = (element) => Boolean(
                element &&
                (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
            );

            for (const input of document.querySelectorAll("input, textarea")) {
                if (!isVisible(input)) {
                    continue;
                }

                const type = String(input.getAttribute("type") || "").toLowerCase();
                if (type === "password") {
                    input.value = "********";
                    continue;
                }

                if (!type || ["text", "email", "tel", "number", "search"].includes(type)) {
                    input.value = "<redacted>";
                }
            }
        }"""
    )


def print_run_summary(script_name: str, run_dir: Path) -> None:
    """打印产物位置。"""
    sys.stdout.write(f"[{script_name}] 产物目录: {run_dir}\n")
    sys.stdout.write(f"[{script_name}] 可查看: {run_dir / 'summary.json'}\n")


__all__ = [
    "ARTIFACTS_ROOT",
    "DEFAULT_HEADERS",
    "DIAGNOSTICS_ROOT",
    "GATEWAY_URL",
    "LOGIN_URL",
    "PROJECT_ROOT",
    "RAD_USER_INFO_URL",
    "attach_page_recorders",
    "collect_page_inventory",
    "create_run_dir",
    "print_run_summary",
    "redact_sensitive_text",
    "redact_visible_form_values",
    "resolve_credentials",
    "wait_for_page_ready",
    "write_json",
    "write_text",
]
