"""config 子命令单元测试"""

from unittest.mock import patch

from typer.testing import CliRunner

from buaalogin_cli.cli import app

runner = CliRunner()


class TestConfigCmdIntervalOnly:
    """测试仅指定 -i 时不应提示输入学号密码"""

    def test_interval_only_no_prompt(self, tmp_path):
        """仅指定 -i 时不应提示用户输入学号密码"""
        config_file = tmp_path / "config.json"
        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config") as mock_config,
        ):
            mock_config.to_dict.return_value = {}
            result = runner.invoke(app, ["config", "-i", "10"])
            assert result.exit_code == 0
            assert "配置已保存" in result.output
            # 不应出现交互式输入提示
            assert "请输入 BUAA 学号" not in result.output
            assert "请输入密码" not in result.output

    def test_interval_only_updates_interval(self, tmp_path):
        """仅指定 -i 时应只更新 interval，不改变已有的 username/password"""
        from buaalogin_cli.config import Config

        config_file = tmp_path / "config.json"
        existing = Config(username="old_user", password="old_pass", interval=5)
        existing.save_to_json(config_file)

        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config", existing),
        ):
            result = runner.invoke(app, ["config", "-i", "10"])
            assert result.exit_code == 0

        loaded = Config.load_from_json(config_file)
        assert loaded.interval == 10
        assert loaded.username == "old_user"
        assert loaded.password == "old_pass"


class TestConfigCmdUserOnly:
    """测试仅指定 -u 时不应提示输入学号"""

    def test_user_only_no_prompt_for_username(self, tmp_path):
        """仅指定 -u 时不应提示输入学号，也不应提示输入密码"""
        config_file = tmp_path / "config.json"
        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config") as mock_config,
        ):
            mock_config.to_dict.return_value = {}
            result = runner.invoke(app, ["config", "-u", "testuser"])
            assert result.exit_code == 0
            assert "配置已保存" in result.output
            assert "请输入 BUAA 学号" not in result.output
            assert "请输入密码" not in result.output


class TestConfigCmdPasswordOnly:
    """测试仅指定 -p 时不应提示输入密码"""

    def test_password_only_no_prompt(self, tmp_path):
        """仅指定 -p 时不应提示输入学号或密码"""
        config_file = tmp_path / "config.json"
        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config") as mock_config,
        ):
            mock_config.to_dict.return_value = {}
            result = runner.invoke(app, ["config", "-p", "testpass"])
            assert result.exit_code == 0
            assert "配置已保存" in result.output
            assert "请输入 BUAA 学号" not in result.output
            assert "请输入密码" not in result.output


class TestConfigCmdNoArgs:
    """测试未指定任何参数时应进入交互式输入模式"""

    def test_no_args_prompts_for_credentials(self, tmp_path):
        """未指定任何参数时应提示输入学号和密码"""
        config_file = tmp_path / "config.json"
        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config") as mock_config,
        ):
            mock_config.to_dict.return_value = {}
            result = runner.invoke(app, ["config"], input="myuser\nmypass\n")
            assert result.exit_code == 0
            assert "配置已保存" in result.output


class TestConfigCmdAllArgs:
    """测试同时指定所有参数时不应提示任何输入"""

    def test_all_args_no_prompt(self, tmp_path):
        """同时指定 -u -p -i 时不应提示任何输入"""
        config_file = tmp_path / "config.json"
        with (
            patch("buaalogin_cli.cli.CONFIG_FILE", config_file),
            patch("buaalogin_cli.cli.config") as mock_config,
        ):
            mock_config.to_dict.return_value = {}
            result = runner.invoke(
                app, ["config", "-u", "user", "-p", "pass", "-i", "15"]
            )
            assert result.exit_code == 0
            assert "配置已保存" in result.output
            assert "请输入 BUAA 学号" not in result.output
            assert "请输入密码" not in result.output
