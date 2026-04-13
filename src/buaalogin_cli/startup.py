"""开机自启管理模块（Windows Task Scheduler）。"""

import getpass
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from .constants import APP_NAME, CLI_CMD


def get_exe_path() -> Path:
    """获取可执行文件的绝对路径。"""
    exe_path = shutil.which(CLI_CMD)
    if not exe_path:
        raise FileNotFoundError(f"未找到 {CLI_CMD}，请确保已安装并在 PATH 中")
    return Path(exe_path)


def is_admin() -> bool:
    """检查当前是否以管理员权限运行。"""
    import ctypes

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def build_task_xml(exe_path: Path, username: str) -> str:
    """生成计划任务 XML，显式关闭执行时限。"""
    start_boundary = datetime.now(UTC).replace(microsecond=0).isoformat()
    escaped_exe = escape(str(exe_path))
    escaped_user = escape(username)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>{escaped_user}</Author>
    <Description>Automatically run {APP_NAME} keepalive service at system startup.</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>{start_boundary}</StartBoundary>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{escaped_user}</UserId>
      <LogonType>Password</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{escaped_exe}</Command>
      <Arguments>run</Arguments>
    </Exec>
  </Actions>
</Task>
"""


def enable_startup() -> None:
    """启用开机自启（需要管理员权限）。"""
    exe_path = get_exe_path()
    username = os.environ["USERNAME"]
    password = getpass.getpass(f"请输入 {username} 的 Windows 登录密码: ")
    task_xml = build_task_xml(exe_path, username)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".xml",
        delete=False,
    ) as temp_file:
        temp_file.write(task_xml)
        temp_path = Path(temp_file.name)

    try:
        cmd = [
            "schtasks",
            "/create",
            "/tn",
            APP_NAME,
            "/xml",
            str(temp_path),
            "/ru",
            username,
            "/rp",
            password,
            "/f",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        temp_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError("创建计划任务失败，请检查密码是否正确")


def disable_startup() -> None:
    """禁用开机自启。"""
    cmd = ["schtasks", "/delete", "/tn", APP_NAME, "/f"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        raise RuntimeError(f"删除计划任务失败: {result.stderr.strip()}")


def is_startup_enabled() -> bool:
    """检查开机自启是否已启用。"""
    cmd = ["schtasks", "/query", "/tn", APP_NAME]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0
