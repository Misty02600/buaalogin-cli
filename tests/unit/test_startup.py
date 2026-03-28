"""startup 模块单元测试。"""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from buaalogin_cli import startup
from buaalogin_cli.constants import APP_NAME


class TestBuildTaskXml:
    """测试任务 XML 生成。"""

    def test_build_task_xml_disables_execution_time_limit(self):
        """生成的 XML 应显式关闭执行时限。"""
        xml = startup.build_task_xml(Path(r"C:\Tools\buaalogin.exe"), "test_user")

        assert "<ExecutionTimeLimit>PT0S</ExecutionTimeLimit>" in xml
        assert "<Command>C:\\Tools\\buaalogin.exe</Command>" in xml
        assert "<Arguments>run</Arguments>" in xml
        assert "<BootTrigger>" in xml
        assert "<LogonType>Password</LogonType>" in xml
        assert "<RunLevel>HighestAvailable</RunLevel>" in xml


class TestEnableStartup:
    """测试启用开机自启。"""

    def test_enable_startup_creates_task_from_xml(self, monkeypatch):
        """应通过 schtasks /xml 创建任务。"""
        command_calls = []
        temp_path = Path(".sandbox/test-startup-success.xml")

        monkeypatch.setattr(
            startup, "get_exe_path", lambda: Path(r"C:\Tools\buaalogin.exe")
        )
        monkeypatch.setattr(startup.getpass, "getpass", lambda _: "secret")
        monkeypatch.setattr(
            startup.tempfile,
            "NamedTemporaryFile",
            _named_temp_file_factory(temp_path),
        )
        monkeypatch.setattr(
            startup.subprocess,
            "run",
            lambda cmd, **_: command_calls.append(cmd) or Mock(returncode=0),
        )
        monkeypatch.setitem(os.environ, "USERNAME", "test_user")

        startup.enable_startup()

        assert len(command_calls) == 1
        assert command_calls[0][:6] == [
            "schtasks",
            "/create",
            "/tn",
            APP_NAME,
            "/xml",
            str(temp_path),
        ]
        assert command_calls[0][6:] == [
            "/ru",
            "test_user",
            "/rp",
            "secret",
            "/f",
        ]
        assert not temp_path.exists()

    def test_enable_startup_raises_when_schtasks_fails(self, monkeypatch):
        """schtasks 创建失败时应抛出错误。"""
        temp_path = Path(".sandbox/test-startup-failure.xml")

        monkeypatch.setattr(
            startup, "get_exe_path", lambda: Path(r"C:\Tools\buaalogin.exe")
        )
        monkeypatch.setattr(startup.getpass, "getpass", lambda _: "secret")
        monkeypatch.setattr(
            startup.tempfile,
            "NamedTemporaryFile",
            _named_temp_file_factory(temp_path),
        )
        monkeypatch.setattr(
            startup.subprocess,
            "run",
            lambda *args, **kwargs: Mock(returncode=1, stderr="ERROR"),
        )
        monkeypatch.setitem(os.environ, "USERNAME", "test_user")

        with pytest.raises(RuntimeError, match="创建计划任务失败"):
            startup.enable_startup()

        assert not temp_path.exists()


def _named_temp_file_factory(temp_path: Path):
    """构造一个可预测的 NamedTemporaryFile 替身。"""

    class _TempFile:
        def __init__(self):
            self.name = str(temp_path)
            self._path = temp_path
            self._handle = None

        def __enter__(self):
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._handle = self._path.open("w", encoding="utf-8")
            return self

        def write(self, content: str) -> int:
            assert self._handle is not None
            return self._handle.write(content)

        def __exit__(self, exc_type, exc, tb):
            if self._handle is not None:
                self._handle.close()

    return lambda **kwargs: _TempFile()
