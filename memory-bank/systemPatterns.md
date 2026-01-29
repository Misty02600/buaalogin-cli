# System Patterns: buaalogin-cli

## 目录
- [System Patterns: buaalogin-cli](#system-patterns-buaalogin-cli)
  - [目录](#目录)
  - [系统架构](#系统架构)
  - [模块职责](#模块职责)
  - [登录流程](#登录流程)
  - [保活流程](#保活流程)
  - [设计模式](#设计模式)
    - [1. 单例配置](#1-单例配置)
    - [2. 上下文管理](#2-上下文管理)
    - [3. 命令模式](#3-命令模式)
  - [关键技术决策](#关键技术决策)
    - [使用 Playwright 而非 HTTP 请求](#使用-playwright-而非-http-请求)
    - [使用微软连接测试检测网络](#使用微软连接测试检测网络)
    - [配置优先级](#配置优先级)
  - [错误处理策略](#错误处理策略)

## 系统架构

```mermaid
flowchart TB
    subgraph Entry["Entry Point"]
        MAIN[__main__.py<br/>main()]
    end

    subgraph CLI["CLI Layer (cli.py + typer)"]
        direction LR
        CMD[命令行接口<br/>app]
    end

    subgraph Service["Service Layer"]
        direction TB
        CS[get_status<br/>HTTP 检测]
        LG[login<br/>Playwright]
        CS --> KA[keep_alive<br/>保活循环]
        LG --> KA
    end

    subgraph Infra["Infrastructure"]
        direction LR
        CFG[config]
        LOG[log]
        CONST[constants]
    end

    Entry --> CLI
    CLI --> Service
    Service --> Infra
```

## 模块职责

| 模块      | 文件           | 职责                                  |
| --------- | -------------- | ------------------------------------- |
| Entry     | `__main__.py`  | 程序入口，定义 `main()` 函数          |
| CLI       | `cli.py`       | 命令行接口，参数解析，定义 `app` 对象 |
| Service   | `service.py`   | 核心业务逻辑：检测、登录、保活        |
| Config    | `config.py`    | 配置加载与保存                        |
| Log       | `log.py`       | 日志配置与管理                        |
| Constants | `constants.py` | 常量定义：路径、URL、APP_NAME         |

## 登录流程

基于 `login()` 的浏览器自动化步骤（详见 [src/buaalogin_cli/service.py](src/buaalogin_cli/service.py)）：

1. 启动 Playwright：读取 Chromium 可执行路径并以 `headless=True` 默认无头模式启动浏览器，创建上下文与新页面。
2. 打开登录页：访问 `https://gw.buaa.edu.cn`，设置 `goto` 30s 超时与 `networkidle` 10s 等待，保证资源加载完成。
3. 已登录检查：若当前 URL 已含 `success`，直接判定已登录并返回。
4. 填充表单：定位 `#username:visible` 与 `#password:visible` 输入用户名、密码，避免隐藏元素干扰。
5. 提交动作：点击选择器 `#login-account, button:has-text("登录"), button:has-text("Login")` 中可见的第一个，兼容不同按钮文案。
6. 结果判定：等待 3s 后再次检查 URL 是否包含 `success`；成功则记录登录成功。
7. 失败诊断：失败时按顺序抓取 `.error-message`、`.alert-danger`、`#error-msg`、错误文案文本等，提取可见错误提示，未获取到则返回"未知错误"，并抛出 `LoginError`。
8. 超时与异常：`PlaywrightTimeout` 与其他异常统一转换为 `LoginError`，最终块确保浏览器关闭。

## 保活流程

`keep_alive()` 驱动的持续在线循环（详见 [src/buaalogin_cli/service.py](src/buaalogin_cli/service.py) 与 [src/buaalogin_cli/constants.py](src/buaalogin_cli/constants.py)）：

1. 周期配置：将 `check_interval_min` 转换为秒，记录当前账户与日志位置。
2. 状态探测：调用 `get_status()` 访问网关 URL `https://gw.buaa.edu.cn/`。
   - 若 URL 包含 "success" → 已登录 (LOGGED_IN)
   - 若请求失败或超时 → 非校园网 (UNKNOWN_NETWORK)
   - 其他情况 → 未登录 (LOGGED_OUT)
3. 自动重连：未登录 (LOGGED_OUT) 时调用 `login()` 重试；登录失败捕获 `LoginError` 并记录警告。非校园网环境则等待。
4. 间隔休眠：每轮结束按配置休眠；异常则记录错误并回退 10 秒后重试，`KeyboardInterrupt` 时优雅退出。
5. 运行模式：`headless` 选项沿用到登录阶段，可在需要可视化调试时关闭无头。

## 设计模式

### 1. 单例配置

`config.py` 在模块加载时创建全局配置实例：

```python
config = Config.load_from_json(CONFIG_FILE)
```

### 2. 上下文管理

Playwright 浏览器使用上下文管理器确保资源正确释放：

```python
with sync_playwright() as p:
    browser = p.chromium.launch(...)
    # ...
    browser.close()
```

### 3. 命令模式

使用 Typer 框架实现命令行子命令：
- `login` - 单次登录
- `run` - 持续保活
- `config` - 配置管理
- `status` - 状态检查
- `info` - 信息显示

## 关键技术决策

### 使用 Playwright 而非 HTTP 请求

**理由**：
- 避免逆向加密协议
- 适应登录页面变化
- 支持 JavaScript 渲染的页面

**代价**：
- 需要安装浏览器内核（~100MB）
- 启动速度较慢

### 使用网关 URL 检测网络

**URL**: `https://gw.buaa.edu.cn/`

**理由**：
- 直接访问校园网网关，结果更准确
- 通过重定向 URL 即可判断状态，无需解析内容
- 避免依赖外部服务（如微软测试站点）

### 使用 Requests 库进行网络请求

**理由**：
- 替代标准库 `urllib`，API 更简洁易用
- 自动处理重定向
- **SSL 验证**：默认启用 SSL 验证，但在代码中保留了处理潜在证书问题的灵活性（原计划禁用，后经测试确认网关证书有效，遂保持启用）。

### 配置优先级

```mermaid
flowchart LR
    A[命令行参数] --> B[环境变量] --> C[配置文件] --> D[默认值]
    style A fill:#f96
    style B fill:#fc6
    style C fill:#9f6
    style D fill:#6cf
```

## 错误处理策略

1. **网络检测失败**：视为未登录，触发登录流程
2. **登录超时**：抛出 `LoginError`，记录日志
3. **保活循环异常**：捕获异常，等待后重试
4. **用户中断**：捕获 `KeyboardInterrupt`，优雅退出
