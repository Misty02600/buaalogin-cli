# Tech Context: buaalogin-cli

## 技术栈

### 运行时

| 组件     | 版本要求          | 用途         |
| -------- | ----------------- | ------------ |
| Python   | >=3.11            | 运行时环境   |
| Chromium | (Playwright 管理) | 浏览器自动化 |

### 核心依赖

| 包名         | 版本     | 用途               |
| ------------ | -------- | ------------------ |
| playwright   | >=1.40.0 | 浏览器自动化       |
| typer        | >=0.9.0  | CLI 框架           |
| platformdirs | >=4.0.0  | 跨平台目录管理     |
| loguru       | >=0.7.0  | 日志框架           |
| msgspec      | >=0.18.0 | 高性能 JSON 序列化 |
| requests     | >=2.31.0 | HTTP 客户端        |

### 开发依赖

| 包名         | 用途           |
| ------------ | -------------- |
| pytest       | 测试框架       |
| pytest-cov   | 测试覆盖率     |
| ruff         | 代码格式化检查 |
| basedpyright | 类型检查       |

## 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/Misty02600/buaalogin-cli.git
cd buaalogin-cli
```

### 2. 创建虚拟环境（推荐使用 uv）

```bash
uv venv
uv sync
```

### 3. 安装浏览器

```bash
uv run playwright install chromium
```

### 4. 运行测试

```bash
uv run pytest
```

## 项目结构

```
buaalogin-cli/
├── src/
│   └── buaalogin_cli/
│       ├── __init__.py      # 包初始化
│       ├── __main__.py      # 程序入口（python -m buaalogin_cli）
│       ├── cli.py           # CLI 命令定义
│       ├── service.py       # 核心服务（登录、保活、状态检测）
│       ├── startup.py       # 开机自启管理（Windows Task Scheduler）
│       ├── config.py        # 配置管理
│       ├── log.py           # 日志配置
│       └── constants.py     # 常量和 URL 定义
├── tests/                   # 测试文件
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试
├── experiments/             # 实验脚本
├── memory-bank/             # 项目文档
├── pyproject.toml           # 项目配置
├── README.md                # 使用说明
└── uv.lock                  # 依赖锁定
```

## 命名规范

| 项目         | 值              | 说明            |
| ------------ | --------------- | --------------- |
| **包名**     | `buaalogin-cli` | PyPI 安装名     |
| **模块名**   | `buaalogin_cli` | Python 导入名   |
| **CLI 命令** | `buaalogin`     | 终端执行命令    |
| **APP_NAME** | `buaalogin-cli` | 配置/日志目录名 |

## 构建与发布

### 构建系统

使用 `uv_build` 作为构建后端：

```toml
[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

### 入口点

```toml
[project.scripts]
buaalogin = "buaalogin_cli.__main__:main"
```

## 文件路径

### 配置文件

- Windows: `%APPDATA%/buaalogin-cli/config.json`
- Linux: `~/.config/buaalogin-cli/config.json`
- macOS: `~/Library/Application Support/buaalogin-cli/config.json`

### 日志文件

- Windows: `%LOCALAPPDATA%/buaalogin-cli/Logs/buaalogin-cli.log`
- Linux: `~/.local/state/buaalogin-cli/buaalogin-cli.log`
- macOS: `~/Library/Logs/buaalogin-cli/buaalogin-cli.log`

## 技术约束

1. **Python 3.11+**：使用了较新的类型注解语法
2. **浏览器依赖**：需要额外安装 Chromium（约 100+MB）
3. **网络环境**：仅支持 BUAA 校园网环境
