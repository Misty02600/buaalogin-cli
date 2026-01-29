"""pytest 配置和共享 fixtures"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_config_file(tmp_path: Path):
    """创建临时配置文件。"""
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"username": "test_user", "password": "test_pass", "interval": 5}'
    )
    return config_file


@pytest.fixture
def empty_config_file(tmp_path: Path):
    """创建空配置文件。"""
    config_file = tmp_path / "config.json"
    config_file.write_text("{}")
    return config_file


@pytest.fixture
def mock_urlopen():
    """Mock urllib.request.urlopen。"""
    with patch("buaalogin_cli.service.urllib.request.urlopen") as mock:
        yield mock


@pytest.fixture
def mock_response_logged_in(mock_urlopen):
    """模拟已登录状态的响应（URL 包含 success）。"""
    mock_response = MagicMock()
    mock_response.url = "https://gw.buaa.edu.cn/srun_portal_success"
    mock_urlopen.return_value = mock_response
    return mock_urlopen


@pytest.fixture
def mock_response_logged_out(mock_urlopen):
    """模拟未登录状态的响应（跳转到登录页）。"""
    mock_response = MagicMock()
    mock_response.url = "https://gw.buaa.edu.cn/srun_portal_pc"
    mock_urlopen.return_value = mock_response
    return mock_urlopen


@pytest.fixture
def mock_playwright():
    """Mock Playwright 浏览器。"""
    with patch("buaalogin_cli.service.sync_playwright") as mock_pw:
        # 设置 mock 链
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
            mock_browser
        )
        mock_pw.return_value.__enter__.return_value.chromium.executable_path = (
            "/mock/chromium"
        )
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        yield {
            "playwright": mock_pw,
            "browser": mock_browser,
            "context": mock_context,
            "page": mock_page,
        }


@pytest.fixture
def sample_credentials():
    """测试用凭据。"""
    return {
        "username": "test_user",
        "password": "test_password",
    }
