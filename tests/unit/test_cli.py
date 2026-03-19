"""cli 模块单元测试"""

from unittest.mock import Mock

from typer.testing import CliRunner

from buaalogin_cli import cli


runner = CliRunner()


class TestRunCommand:
    """测试 run 命令"""

    def test_run_uses_seconds_default_interval(self, monkeypatch):
        """测试 run 默认检测间隔为 60 秒"""
        keep_alive = Mock()
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "username": "test_user",
            "password": "test_pass",
        }

        monkeypatch.setattr(cli.service, "keep_alive", keep_alive)
        monkeypatch.setattr(cli, "config", mock_config)

        result = runner.invoke(cli.app, ["run"])

        assert result.exit_code == 0
        keep_alive.assert_called_once_with(
            "test_user",
            "test_pass",
            60,
            headless=True,
        )
