"""service 模块单元测试"""

import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

from buaalogin_cli.service import (
    LOGIN_BUTTON_SELECTOR,
    PASSWORD_SELECTOR,
    USERNAME_SELECTOR,
    LoginError,
    NetworkStatus,
    _get_error_message,
    _install_browser,
    get_status,
)


class TestGetStatus:
    """测试 get_status 函数"""

    def test_logged_in_returns_logged_in(self):
        """测试已登录状态返回 LOGGED_IN（API 返回用户信息）"""
        with patch("buaalogin_cli.service.requests.get") as mock_get:
            mock_response = MagicMock()
            # API 返回逗号分隔的用户信息表示已登录
            mock_response.text = "93830,1770015058,1770020128,59831052"
            mock_get.return_value = mock_response

            result = get_status()
            assert result == NetworkStatus.LOGGED_IN

    def test_logged_out_with_not_online_error(self):
        """测试 API 返回 not_online_error 时返回 LOGGED_OUT"""
        with patch("buaalogin_cli.service.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "not_online_error"
            mock_get.return_value = mock_response

            result = get_status()
            assert result == NetworkStatus.LOGGED_OUT

    def test_connection_error_returns_unknown_network(self):
        """测试连接错误返回 UNKNOWN_NETWORK"""
        with patch("buaalogin_cli.service.requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection failed")

            result = get_status()
            assert result == NetworkStatus.UNKNOWN_NETWORK

    def test_timeout_returns_unknown_network(self):
        """测试超时返回 UNKNOWN_NETWORK"""
        with patch("buaalogin_cli.service.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timed out")

            result = get_status()
            assert result == NetworkStatus.UNKNOWN_NETWORK


class TestLogin:
    """测试 login 函数"""

    @patch("buaalogin_cli.service.get_status")
    def test_login_returns_early_when_already_logged_in(self, mock_get_status):
        """测试已登录时直接返回，不启动浏览器"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.LOGGED_IN

        # 不应抛出异常，也不应启动 playwright
        with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
            login("user", "pass")
            mock_pw.assert_not_called()

    @patch("buaalogin_cli.service.get_status")
    def test_login_raises_error_when_not_on_campus(self, mock_get_status):
        """测试非校园网环境时抛出 LoginError"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.UNKNOWN_NETWORK

        with pytest.raises(LoginError) as exc_info:
            login("user", "pass")
        assert "未检测到校园网环境" in str(exc_info.value)

    @patch("buaalogin_cli.service.get_status")
    def test_login_uses_fallback_selectors_for_inputs_and_button(self, mock_get_status):
        """测试登录时使用候选选择器填写输入框并点击按钮。"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT

        with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_pw.return_value.__enter__.return_value.chromium.executable_path = (
                "C:/fake/chromium"
            )
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            type(mock_page).url = property(
                lambda self: "https://gw.buaa.edu.cn/success"
            )

            username_locator = MagicMock()
            password_locator = MagicMock()
            button_locator = MagicMock()
            username_locator.first = username_locator
            password_locator.first = password_locator
            button_locator.first = button_locator

            mock_page.locator.side_effect = [
                username_locator,
                password_locator,
                button_locator,
            ]

            login("user", "pass")

        assert mock_page.locator.call_args_list[0].args[0] == USERNAME_SELECTOR
        assert mock_page.locator.call_args_list[1].args[0] == PASSWORD_SELECTOR
        assert mock_page.locator.call_args_list[2].args[0] == LOGIN_BUTTON_SELECTOR
        username_locator.fill.assert_called_once_with("user")
        password_locator.fill.assert_called_once_with("pass")
        button_locator.click.assert_called_once_with()


class TestInstallBrowser:
    """测试浏览器安装逻辑"""

    @patch("buaalogin_cli.service.subprocess.run")
    def test_install_browser_success(self, mock_run):
        """测试浏览器安装成功"""
        mock_run.return_value = MagicMock(returncode=0)

        _install_browser()

        mock_run.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "playwright",
                "install",
                "--with-deps",
                "chromium",
            ],
            check=False,
        )

    @patch("buaalogin_cli.service.subprocess.run")
    def test_install_browser_failure(self, mock_run):
        """测试浏览器安装失败时抛出 RuntimeError"""
        mock_run.return_value = MagicMock(returncode=1)

        with pytest.raises(RuntimeError, match="Chromium 浏览器安装失败") as exc_info:
            _install_browser()

        assert "playwright install --with-deps chromium" in str(exc_info.value)


class TestBrowserAutoInstall:
    """测试浏览器自动安装"""

    @patch("buaalogin_cli.service.get_status")
    @patch("buaalogin_cli.service._install_browser")
    def test_login_installs_browser_when_missing(self, mock_install, mock_get_status):
        """测试浏览器不存在时自动安装"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT

        with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_pw.return_value.__enter__.return_value.chromium.executable_path = (
                "/nonexistent/chromium"
            )
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            type(mock_page).url = property(
                lambda self: "https://gw.buaa.edu.cn/success"
            )

            login("user", "pass")

        mock_install.assert_called_once()

    @patch("buaalogin_cli.service.get_status")
    @patch("buaalogin_cli.service._install_browser")
    def test_login_skips_install_when_browser_exists(
        self, mock_install, mock_get_status, tmp_path
    ):
        """测试浏览器已存在时跳过安装"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        fake_browser = tmp_path / "chromium"
        fake_browser.write_text("")

        with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_pw.return_value.__enter__.return_value.chromium.executable_path = str(
                fake_browser
            )
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            type(mock_page).url = property(
                lambda self: "https://gw.buaa.edu.cn/success"
            )

            login("user", "pass")

        mock_install.assert_not_called()

    @patch("buaalogin_cli.service.get_status")
    @patch(
        "buaalogin_cli.service._install_browser",
        side_effect=RuntimeError("install failed"),
    )
    def test_login_wraps_install_failure_as_login_error(
        self, mock_install, mock_get_status
    ):
        """测试自动安装失败时转换为 LoginError"""
        from buaalogin_cli.service import login

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT

        with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
            chromium = mock_pw.return_value.__enter__.return_value.chromium
            chromium.executable_path = "/nonexistent/chromium"

            with pytest.raises(LoginError, match="install failed"):
                login("user", "pass")

        chromium.launch.assert_not_called()
        mock_install.assert_called_once()


class TestGetErrorMessage:
    """测试 _get_error_message 函数"""

    def test_error_message_found(self):
        """测试找到错误信息"""
        mock_page = MagicMock()
        mock_elem = MagicMock()
        mock_elem.is_visible.return_value = True
        mock_elem.text_content.return_value = "用户名或密码错误"
        mock_page.locator.return_value.first = mock_elem

        result = _get_error_message(mock_page)
        assert result == "用户名或密码错误"

    def test_no_error_message(self):
        """测试未找到错误信息"""
        mock_page = MagicMock()
        mock_elem = MagicMock()
        mock_elem.is_visible.return_value = False
        mock_page.locator.return_value.first = mock_elem

        result = _get_error_message(mock_page)
        assert result == "未知错误"

    def test_exception_handling(self):
        """测试异常处理"""
        mock_page = MagicMock()
        mock_page.locator.side_effect = Exception("Locator error")

        result = _get_error_message(mock_page)
        assert result == "无法获取错误信息"


class TestLoginError:
    """测试 LoginError 异常类"""

    def test_login_error_message(self):
        """测试 LoginError 携带消息"""
        error = LoginError("Authentication failed")
        assert str(error) == "Authentication failed"

    def test_login_error_is_exception(self):
        """测试 LoginError 是 Exception 子类"""
        assert issubclass(LoginError, Exception)


class TestNetworkStatus:
    """测试 NetworkStatus 枚举"""

    def test_enum_values_exist(self):
        """测试枚举值存在"""
        assert hasattr(NetworkStatus, "UNKNOWN_NETWORK")
        assert hasattr(NetworkStatus, "LOGGED_OUT")
        assert hasattr(NetworkStatus, "LOGGED_IN")

    def test_enum_values_are_unique(self):
        """测试枚举值唯一"""
        values = [
            NetworkStatus.UNKNOWN_NETWORK,
            NetworkStatus.LOGGED_OUT,
            NetworkStatus.LOGGED_IN,
        ]
        assert len(values) == len(set(values))
