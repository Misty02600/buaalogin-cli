"""constants 模块单元测试"""

from pathlib import Path


class TestConstants:
    """测试常量定义"""

    def test_app_name_defined(self):
        """测试 APP_NAME 常量存在且为字符串"""
        from buaalogin_cli.constants import APP_NAME

        assert isinstance(APP_NAME, str)
        assert APP_NAME == "buaalogin-cli"

    def test_config_file_is_path(self):
        """测试 CONFIG_FILE 是 Path 对象"""
        from buaalogin_cli.constants import CONFIG_FILE

        assert isinstance(CONFIG_FILE, Path)

    def test_log_file_is_path(self):
        """测试 LOG_FILE 是 Path 对象"""
        from buaalogin_cli.constants import LOG_FILE

        assert isinstance(LOG_FILE, Path)

    def test_gateway_url_format(self):
        """测试 GATEWAY_URL 是有效的 HTTPS URL"""
        from buaalogin_cli.constants import GATEWAY_URL

        assert isinstance(GATEWAY_URL, str)
        assert GATEWAY_URL.startswith("https://")
        assert "buaa.edu.cn" in GATEWAY_URL

    def test_login_url_format(self):
        """测试 LOGIN_URL 是有效的 URL"""
        from buaalogin_cli.constants import LOGIN_URL

        assert isinstance(LOGIN_URL, str)
        assert LOGIN_URL.startswith("http://") or LOGIN_URL.startswith("https://")
        assert "buaa.edu.cn" in LOGIN_URL
