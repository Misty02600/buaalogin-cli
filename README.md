<div align="center">

# BUAALogin CLI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

</div>

一个简易的校园网自动登录与保活工具，基于 Playwright 模拟登录。
- 开箱即用
- 省去了复杂的加密逻辑，仅依赖于登录页前端元素
- 需要安装较大的浏览器内核

## 安装

推荐使用 [uv](https://docs.astral.sh/uv/) 或 [pipx](https://pypa.github.io/pipx/) 进行安装。

### 方式一：使用 uv

```bash
# 1. 安装工具
uv tool install buaalogin-cli

# 2. 安装浏览器内核
uvx --from buaalogin-cli playwright install chromium

# 3. (仅 Linux) 安装系统依赖
uvx --from buaalogin-cli playwright install-deps chromium
```

### 方式二：使用 pipx

```bash
# 1. 安装工具
pipx install buaalogin-cli

# 2. 安装浏览器内核
# 使用 pipx 运行 playwright 命令下载浏览器（确保版本匹配）
pipx run --spec buaalogin-cli playwright install chromium

# 3. (仅 Linux) 安装系统依赖
pipx run --spec buaalogin-cli playwright install-deps chromium
```

### 方式三：使用 pip

```bash
# 1. 安装包
pip install buaalogin-cli

# 2. 安装浏览器内核
playwright install chromium

# 3. (仅 Linux) 安装系统依赖
playwright install-deps chromium
```

## 快速上手

### 1. 初始化配置

```bash
buaalogin config
```

### 2. 启动保活服务
后台常驻运行，默认每 5 分钟检查一次网络状态：

```bash
buaalogin run
```

## 使用示例

### 单次登录
```bash
buaalogin login                        # 使用已保存的配置
buaalogin login -u 学号 -p 密码        # 使用指定凭据
buaalogin login --headed               # 显示浏览器窗口
buaalogin login -v                     # 显示详细日志
```

### 持续保活
```bash
buaalogin run                          # 默认 5 分钟检测一次
buaalogin run -i 1                     # 每 1 分钟检测一次
buaalogin run --headed                 # 显示浏览器窗口
buaalogin run --headless               # 无头模式（默认）
```

### 其他命令

| 命令                  | 说明                                       |
| --------------------- | ------------------------------------------ |
| `buaalogin status`    | 检查当前网络状态（退出码: 0=在线, 1=离线） |
| `buaalogin info`      | 显示配置文件路径和日志文件位置             |
| `buaalogin config -s` | 查看当前已保存的配置信息                   |
| `buaalogin --help`    | 查看所有可用命令和参数帮助                 |

### 开机自启（仅 Windows）

设置开机时自动运行保活服务：

```bash
buaalogin startup enable   # 启用开机自启
buaalogin startup disable  # 禁用开机自启
buaalogin startup status   # 查看当前状态
```

> **注意**：启用开机自启需要管理员权限。以管理员身份运行终端，然后执行上述命令。

<details>
<summary>📋 手动设置任务计划程序</summary>

如果命令行方式不工作，可以手动通过 Windows 任务计划程序设置：

1. **打开任务计划程序**：按 `Win+R`，输入 `taskschd.msc`，回车

2. **创建基本任务**：右键"任务计划程序库" → "创建任务"

3. **常规设置**：
   - 名称：`buaalogin-cli`
   - 勾选"不管用户是否登录都要运行"
   - 勾选"使用最高权限运行"

4. **触发器**：
   - 新建 → 选择"启动时"

5. **操作**：
   - 新建 → 启动程序
   - 程序：`buaalogin`（或完整路径，可通过 `where buaalogin` 查看）
   - 参数：`run`

6. **保存**：点击确定，输入 Windows 密码

</details>

## 配置管理

### 配置文件
配置文件存储在用户目录：
- **Windows**: `%APPDATA%\buaalogin-cli\config.json`
- **macOS**: `~/Library/Application Support/buaalogin-cli/config.json`
- **Linux**: `~/.config/buaalogin-cli/config.json`

### 日志文件
日志文件存储位置：
- **Windows**: `%LOCALAPPDATA%\buaalogin-cli\Logs\buaalogin-cli.log`
- **macOS**: `~/Library/Logs/buaalogin-cli/buaalogin-cli.log`
- **Linux**: `~/.local/state/buaalogin-cli/buaalogin-cli.log`

### 环境变量
支持通过环境变量配置覆盖配置文件：
- `BUAA_USERNAME`: 学号
- `BUAA_PASSWORD`: 密码
- `BUAA_CHECK_INTERVAL`: 检查间隔（分钟）
-