"""开机自启管理模块（Windows Task Scheduler）"""

import os
import shutil
import subprocess
from pathlib import Path

from .constants import APP_NAME, CLI_CMD


def get_exe_path() -> Path:
    """获取可执行文件的绝对路径"""
    exe_path = shutil.which(CLI_CMD)
    if not exe_path:
        raise FileNotFoundError(f"未找到 {CLI_CMD}，请确保已安装并在 PATH 中")
    return Path(exe_path)


def is_admin() -> bool:
    """检查当前是否以管理员权限运行"""
    import ctypes

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def enable_startup() -> None:
    """启用开机自启（需要管理员权限）

    以当前用户身份在开机时运行，可以访问用户配置文件。
    使用 getpass 获取密码，使任务能够"不管用户是否登录都运行"。
    """
    import getpass

    exe_path = get_exe_path()
    username = os.environ["USERNAME"]
    password = getpass.getpass(f"请输入 {username} 的 Windows 登录密码: ")

    cmd = [
        "schtasks",
        "/create",
        "/tn",
        APP_NAME,
        "/tr",
        f'"{exe_path}" run',
        "/sc",
        "onstart",
        "/ru",
        username,
        "/rp",
        password,
        "/rl",
        "highest",
        "/f",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("创建计划任务失败，请检查密码是否正确")


def disable_startup() -> None:
    """禁用开机自启"""
    cmd = ["schtasks", "/delete", "/tn", APP_NAME, "/f"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        raise RuntimeError(f"删除计划任务失败: {result.stderr.strip()}")


def is_startup_enabled() -> bool:
    """检查开机自启是否已启用"""
    cmd = ["schtasks", "/query", "/tn", APP_NAME]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0
