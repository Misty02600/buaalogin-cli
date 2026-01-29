"""登录流程集成测试

使用 mock 模拟 Playwright 和网络请求，测试完整的登录流程。
"""

from unittest.mock import MagicMock, patch

import pytest

from buaalogin_cli.service import LoginError, NetworkStatus, login


class TestLoginFlow:
    """测试完整的登录流程"""

    @patch("buaalogin_cli.service.get_status")
    def test_login_success_flow(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试成功登录流程"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]

        # 模拟登录后跳转到成功页
        type(mock_page).url = property(lambda self: "https://gw.buaa.edu.cn/success")

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

        # 验证页面操作被调用
        mock_page.goto.assert_called_once()
        mock_page.wait_for_load_state.assert_called()

    @patch("buaalogin_cli.service.get_status")
    def test_login_already_logged_in(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试已登录状态直接返回，不启动浏览器"""
        mock_get_status.return_value = NetworkStatus.LOGGED_IN

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

        # 已登录时不应启动 playwright
        mock_playwright["playwright"].assert_not_called()

    @patch("buaalogin_cli.service.get_status")
    def test_login_fills_credentials(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试登录时填写用户名和密码"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]

        # 模拟提交后跳转到成功页
        type(mock_page).url = property(lambda self: "https://gw.buaa.edu.cn/success")

        # 设置 locator mock
        mock_locator = MagicMock()
        mock_locator.fill = MagicMock()
        mock_locator.click = MagicMock()
        mock_page.locator.return_value = mock_locator

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

        # 验证 locator 被调用（填写用户名、密码、点击按钮）
        assert mock_page.locator.call_count >= 3

    @patch("buaalogin_cli.service.get_status")
    def test_login_headless_mode(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试无头模式参数传递"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        type(mock_page).url = property(lambda self: "https://gw.buaa.edu.cn/success")

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

        # 验证浏览器以无头模式启动
        mock_playwright[
            "playwright"
        ].return_value.__enter__.return_value.chromium.launch.assert_called_with(
            headless=True, executable_path="/mock/chromium"
        )

    @patch("buaalogin_cli.service.get_status")
    def test_login_visible_mode(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试可见模式参数传递"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        type(mock_page).url = property(lambda self: "https://gw.buaa.edu.cn/success")

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=False,
        )

        # 验证浏览器以可见模式启动
        mock_playwright[
            "playwright"
        ].return_value.__enter__.return_value.chromium.launch.assert_called_with(
            headless=False, executable_path="/mock/chromium"
        )

    @patch("buaalogin_cli.service.get_status")
    def test_login_browser_closed_on_success(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试成功后关闭浏览器"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        type(mock_page).url = property(lambda self: "https://gw.buaa.edu.cn/success")
        mock_browser = mock_playwright["browser"]

        login(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

        # 验证浏览器被关闭
        mock_browser.close.assert_called_once()

    @patch("buaalogin_cli.service.get_status")
    def test_login_browser_closed_on_error(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试异常时也关闭浏览器"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        type(mock_page).url = property(
            lambda self: "https://gw.buaa.edu.cn/srun_portal_pc"
        )
        mock_page.goto.side_effect = Exception("Network error")
        mock_browser = mock_playwright["browser"]

        with pytest.raises(LoginError):
            login(
                sample_credentials["username"],
                sample_credentials["password"],
                headless=True,
            )

        # 验证浏览器被关闭
        mock_browser.close.assert_called_once()


class TestLoginErrorHandling:
    """测试登录错误处理"""

    @patch("buaalogin_cli.service.get_status")
    def test_login_timeout_error(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试页面超时错误"""
        from playwright.sync_api import TimeoutError as PlaywrightTimeout

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        mock_page.goto.side_effect = PlaywrightTimeout("Timeout")

        with pytest.raises(LoginError) as exc_info:
            login(
                sample_credentials["username"],
                sample_credentials["password"],
                headless=True,
            )

        assert "超时" in str(exc_info.value)

    @patch("buaalogin_cli.service.get_status")
    def test_login_generic_error(
        self, mock_get_status, mock_playwright, sample_credentials
    ):
        """测试通用错误转换为 LoginError"""
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_page = mock_playwright["page"]
        mock_page.goto.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(LoginError):
            login(
                sample_credentials["username"],
                sample_credentials["password"],
                headless=True,
            )

    def test_login_unknown_network_error(self, sample_credentials):
        """测试非校园网环境时抛出 LoginError"""
        with patch("buaalogin_cli.service.get_status") as mock_get_status:
            mock_get_status.return_value = NetworkStatus.UNKNOWN_NETWORK

            with pytest.raises(LoginError) as exc_info:
                login(
                    sample_credentials["username"],
                    sample_credentials["password"],
                    headless=True,
                )

            assert "未检测到校园网环境" in str(exc_info.value)
