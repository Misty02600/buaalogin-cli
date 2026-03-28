
# BUAALogin CLI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)


一个简易的校园网自动登录与保活工具，基于 Playwright 模拟登录。
- 开箱即用，首次运行时会自动安装 Chromium 浏览器
- 省去了复杂的加密逻辑，仅依赖于登录页前端元素
- 并不轻量，需要安装较大的浏览器内核

## 安装

推荐使用 [uv](https://docs.astral.sh/uv/) 或 [pipx](https://pypa.github.io/pipx/) 进行安装。

### 方式一：使用 uv

```bash
# 安装或更新工具
uv tool install buaalogin-cli
```

### 方式二：使用 pipx

```bash
# 安装或更新工具
pipx upgrade --install buaalogin-cli
```

### 方式三：使用 pip

```bash
# 安装或更新工具
pip install -U buaalogin-cli
```

> 在首次运行 `buaalogin login` 或 `buaalogin run` 时自动检测并安装 Chromium。


## 快速上手

### 1. 初始化配置

```bash
buaalogin config set
```

### 2. 查看当前配置

```bash
buaalogin config show
```

### 3. 启动保活服务
后台常驻运行，默认每 60 秒检查一次网络状态：

```bash
buaalogin run
```

## 使用示例

### 配置与凭据管理
```bash
buaalogin config set                               # 交互式输入学号和密码
buaalogin config set -u 学号 -p 密码              # 只保存账号和密码
buaalogin config set -i 60                        # 只修改检测间隔为 60 秒
buaalogin config set -u 学号 -p 密码 -i 120       # 一次性写入完整配置
buaalogin config show                             # 查看当前已保存配置
buaalogin info                                    # 查看配置文件和日志文件位置
```

### 使用环境变量
```bash
# PowerShell
$env:BUAA_USERNAME="学号"
$env:BUAA_PASSWORD="密码"
$env:BUAA_CHECK_INTERVAL="60"
buaalogin run
```

```bash
# bash / zsh
export BUAA_USERNAME="学号"
export BUAA_PASSWORD="密码"
export BUAA_CHECK_INTERVAL="60"
buaalogin run
```

### 单次登录
```bash
buaalogin login                                   # 使用已保存的配置或环境变量
buaalogin login -u 学号 -p 密码                   # 直接使用命令行参数登录
buaalogin login --headed                          # 显示浏览器窗口，便于观察登录过程
buaalogin -v login                                # 输出详细日志
buaalogin -v login -u 学号 -p 密码 --headed       # 带详细日志的可视化登录
```

### 持续保活
```bash
buaalogin run                                     # 默认每 60 秒检测一次
buaalogin run -i 30                               # 每 30 秒检测一次
buaalogin run -u 学号 -p 密码 -i 120              # 不依赖配置文件，直接运行保活
buaalogin run --headed                            # 显示浏览器窗口
buaalogin run --headless                          # 无头模式（默认）
buaalogin -v run -i 60                            # 输出详细日志，便于排查问题
```

### 状态检查与帮助
```bash
buaalogin status                                  # 检查当前网络状态（退出码: 0=在线, 1=离线）
buaalogin info                                    # 显示配置文件路径和日志文件位置
buaalogin --help                                  # 查看所有命令
buaalogin login --help                            # 查看 login 子命令帮助
buaalogin run --help                              # 查看 run 子命令帮助
buaalogin config --help                           # 查看 config 子命令帮助
```

### 开机自启（仅 Windows）

设置开机时自动运行保活服务：

```bash
buaalogin config set -u 学号 -p 密码 -i 60   # 先保存保活所需配置
buaalogin startup enable                     # 启用开机自启
buaalogin startup status                     # 查看当前状态
buaalogin startup disable                    # 禁用开机自启
```

> **注意**：启用开机自启需要管理员权限。以管理员身份运行终端，然后执行上述命令。

<details>
<summary>📋 Windows 手动设置任务计划程序</summary>

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
   - 程序：完整路径（cmd 里通过 `where buaalogin` 查看，如 uv 安装路径一般在 `C:\Users\xxx\.local\bin\buaalogin.exe`）
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
- `BUAA_CHECK_INTERVAL`: 检查间隔（秒）
