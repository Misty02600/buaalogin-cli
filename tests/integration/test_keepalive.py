"""保活功能集成测试

测试 keep_alive 函数的行为逻辑。
由于 keep_alive 是无限循环，测试时需要控制循环次数。
"""

from unittest.mock import patch

import pytest


class TestKeepAliveLogic:
    """测试保活逻辑"""

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_when_logged_in(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试已登录时不执行登录"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        # 模拟已登录状态
        mock_get_status.return_value = NetworkStatus.LOGGED_IN

        # 在第一次 sleep 后抛出异常退出循环
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        # 验证检查登录状态被调用
        assert mock_get_status.call_count >= 1
        # 已登录时不应调用 login
        mock_login.assert_not_called()

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_triggers_login_when_not_logged_in(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试未登录时触发登录"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        # 模拟未登录状态
        mock_get_status.return_value = NetworkStatus.LOGGED_OUT

        # 在 sleep 后退出
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        # 验证 login 被调用
        mock_login.assert_called_once_with(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=True,
        )

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_unknown_network_skips_login(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试非校园网环境时不尝试登录"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        # 模拟非校园网环境
        mock_get_status.return_value = NetworkStatus.UNKNOWN_NETWORK

        # 在 sleep 后退出
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        # 非校园网环境不应调用 login
        mock_login.assert_not_called()

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_handles_login_error(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试登录失败时继续运行"""
        from buaalogin_cli.service import LoginError, NetworkStatus, keep_alive

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_login.side_effect = LoginError("Auth failed")

        # 第一次循环登录失败，第二次退出
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        # 登录失败不应阻止继续运行
        assert mock_get_status.call_count >= 1

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_interval_conversion(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试检查间隔转换为秒"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        mock_get_status.return_value = NetworkStatus.LOGGED_IN
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=5,  # 5 分钟
            )

        # 验证 sleep 被调用时使用秒数 (5 * 60 = 300)
        mock_sleep.assert_called_with(300)

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_headless_parameter(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试无头模式参数传递"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        mock_get_status.return_value = NetworkStatus.LOGGED_OUT
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
                headless=False,
            )

        mock_login.assert_called_with(
            sample_credentials["username"],
            sample_credentials["password"],
            headless=False,
        )

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.login")
    @patch("buaalogin_cli.service.get_status")
    def test_keep_alive_recovers_from_exception(
        self, mock_get_status, mock_login, mock_sleep, sample_credentials
    ):
        """测试从异常中恢复"""
        from buaalogin_cli.service import NetworkStatus, keep_alive

        # 第一次检查抛出异常，然后正常
        mock_get_status.side_effect = [
            Exception("Network error"),
            NetworkStatus.LOGGED_IN,
        ]
        # 异常后短暂 sleep，然后正常 sleep，然后退出
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with pytest.raises(SystemExit):
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        # 应该有两次检查（第一次异常，第二次正常）
        assert mock_get_status.call_count == 2


class TestKeepAliveUserInterrupt:
    """测试用户中断"""

    @patch("buaalogin_cli.service.time.sleep")
    @patch("buaalogin_cli.service.get_status")
    def test_keyboard_interrupt_exits_gracefully(
        self, mock_get_status, mock_sleep, sample_credentials
    ):
        """测试 Ctrl+C 优雅退出"""
        from buaalogin_cli.service import keep_alive

        mock_get_status.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            keep_alive(
                sample_credentials["username"],
                sample_credentials["password"],
                check_interval_min=1,
            )

        assert exc_info.value.code == 0
