"""常量模块：路径、URL"""

from pathlib import Path

from platformdirs import user_config_dir, user_log_dir

APP_NAME = "buaalogin-cli"

# 文件路径
CONFIG_FILE = Path(user_config_dir(APP_NAME, ensure_exists=True)) / "config.json"
LOG_FILE = Path(user_log_dir(APP_NAME, ensure_exists=True)) / f"{APP_NAME}.log"

# URL
GATEWAY_URL = "https://gw.buaa.edu.cn"
LOGIN_URL = GATEWAY_URL
