"""网络状态检测、登录、持续保活"""

import sys
import time
from enum import Enum, auto

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from .constants import GATEWAY_URL, LOG_FILE, LOGIN_URL
from .log import logger


class LoginError(Exception):
    """登录失败异常。"""

    pass


class NetworkStatus(Enum):
    """网络状态枚举。"""

    UNKNOWN_NETWORK = auto()  # 非校园网环境（DNS 解析失败或超时）
    LOGGED_OUT = auto()  # 校园网环境，未登录
    LOGGED_IN = auto()  # 校园网环境，已登录


# region 网络状态检测


def get_status() -> NetworkStatus:
    """获取当前网络状态。

    通过访问校园网网关 (https://gw.buaa.edu.cn/) 检测：
    - 请求失败（DNS/超时）→ UNKNOWN_NETWORK
    - URL 包含 "success" → LOGGED_IN
    - 其他情况 → LOGGED_OUT

    Returns:
        NetworkStatus 枚举值。
    """
    log = logger.bind(trigger="status")
    log.debug("正在检测网络状态...")

    try:
        response = requests.get(
            GATEWAY_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
            allow_redirects=True,
        )
        final_url = response.url

        if "success" in final_url.lower():
            log.debug(f"网络状态: 已登录 (URL: {final_url})")
            return NetworkStatus.LOGGED_IN
        else:
            log.debug(f"网络状态: 未登录 (URL: {final_url})")
            return NetworkStatus.LOGGED_OUT

    except requests.RequestException as e:
        log.debug(f"网络状态: 非校园网环境 ({e})")
        return NetworkStatus.UNKNOWN_NETWORK


# endregion


# region 登录


def login(username: str, password: str, *, headless: bool = True) -> None:
    """使用 Playwright 模拟浏览器登录校园网。

    Args:
        username: 用户名。
        password: 密码。
        headless: 是否使用无头模式。

    Raises:
        LoginError: 登录失败时抛出，包含错误信息。
    """
    log = logger.bind(trigger="login")

    # 先快速检查状态，避免不必要地启动浏览器
    status = get_status()
    if status == NetworkStatus.LOGGED_IN:
        log.info("已经处于登录状态")
        return
    if status == NetworkStatus.UNKNOWN_NETWORK:
        raise LoginError("未检测到校园网环境")

    # 只有 LOGGED_OUT 时才启动浏览器
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        log.debug(f"使用浏览器: {browser_path}")

        browser = p.chromium.launch(headless=headless, executable_path=browser_path)
        context = browser.new_context()
        page = context.new_page()

        try:
            log.info("正在打开登录页面...")
            page.goto(LOGIN_URL, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 填写用户名和密码
            log.debug("正在填写登录信息...")
            page.locator("#username:visible").fill(username)
            page.locator("#password:visible").fill(password)

            # 点击登录按钮
            log.info("正在提交登录...")
            page.locator("#login").click()

            page.wait_for_timeout(3000)

            # 检查登录结果
            if "success" in page.url.lower():
                log.success("登录成功！")
                return
            else:
                error_msg = _get_error_message(page)
                log.warning(f"登录失败：{error_msg}")
                raise LoginError(error_msg)

        except PlaywrightTimeout as e:
            log.error(f"页面加载超时：{e}")
            raise LoginError(f"页面加载超时：{e}") from e
        except LoginError:
            raise
        except Exception as e:
            log.error(f"登录过程出错：{e}")
            raise LoginError(f"{e}") from e
        finally:
            log.debug("正在关闭浏览器...")
            browser.close()
            log.debug("浏览器已关闭")


def _get_error_message(page) -> str:
    """获取登录错误信息。"""
    try:
        # layer.js 弹窗错误信息
        elem = page.locator(".layui-layer-content").first
        if elem.is_visible(timeout=1000):
            return elem.text_content() or "未知错误"
        return "未知错误"
    except Exception:
        return "无法获取错误信息"


# endregion


# region 持续保活


def keep_alive(
    username: str, password: str, check_interval_min: int, *, headless: bool = True
):
    """持续保持在线，检查登录状态并自动重连。

    Args:
        username: 校园网用户名。
        password: 校园网密码。
        check_interval_min: 检查间隔（分钟）。
        headless: 是否使用无头模式运行浏览器。
    """
    log = logger.bind(trigger="run")
    check_interval_sec = check_interval_min * 60

    log.info(f"保活服务已启动，检查间隔: {check_interval_min} 分钟")
    log.info(f"使用账户: {username}")
    log.info(f"日志文件: {LOG_FILE}")

    while True:
        try:
            status = get_status()

            if status == NetworkStatus.UNKNOWN_NETWORK:
                log.warning("未检测到校园网环境，等待下次检查...")
            elif status == NetworkStatus.LOGGED_IN:
                log.info("已登录，无需操作")
            else:  # LOGGED_OUT
                log.warning("未登录，正在启动浏览器登录...")
                try:
                    login(username, password, headless=headless)
                    log.success("登录成功")
                except LoginError as e:
                    log.warning(f"登录未成功: {e}")

            time.sleep(check_interval_sec)
        except KeyboardInterrupt:
            log.info("User Exit.")
            sys.exit(0)
        except Exception as e:
            log.error(f"发生错误: {e}")
            time.sleep(10)


# endregion
