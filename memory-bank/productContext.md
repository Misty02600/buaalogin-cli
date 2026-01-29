# Product Context: buaalogin-cli

## 为什么创建这个项目

校园网认证系统通常需要用户频繁手动登录，尤其是：
- 网络超时自动断开后需要重新登录
- 设备重启后需要重新认证
- 服务器等无人值守设备无法手动登录

传统的自动登录工具通常需要逆向加密协议，实现复杂且容易失效。本项目采用浏览器自动化方案，直接模拟用户操作，避免了协议逆向的复杂性。

## 解决的问题

1. **重复登录问题**：用户不再需要手动输入账号密码登录
2. **网络断开问题**：自动检测并重连，保持网络稳定
3. **无人值守问题**：服务器等设备可以自动保持网络连接

## 产品工作方式

### 核心流程

```
用户配置账号 → 启动保活服务 → 定期检测网络 → 断开时自动登录 → 循环
```

### 网络检测机制

通过访问校园网网关 URL (`https://gw.buaa.edu.cn/`) 判断网络状态：
- URL 包含 "success" 表示已登录
- 请求失败或超时表示非校园网环境
- 其他情况表示未登录，需要认证

### 登录机制

使用 Playwright 控制 Chromium 浏览器：
1. 打开登录页面 `https://gw.buaa.edu.cn`
2. 填写用户名和密码
3. 点击登录按钮
4. 检查登录结果

## 用户体验目标

- **开箱即用**：最少配置即可使用
- **静默运行**：后台运行不干扰用户
- **可靠稳定**：长期运行不崩溃
- **日志完善**：问题可追溯

## 文件路径

### 配置文件

- Windows: `%APPDATA%/buaalogin-cli/config.json`
- Linux: `~/.config/buaalogin-cli/config.json`
- macOS: `~/Library/Application Support/buaalogin-cli/config.json`

### 日志文件

- Windows: `%LOCALAPPDATA%/buaalogin-cli/Logs/buaalogin-cli.log`
- Linux: `~/.local/state/buaalogin-cli/buaalogin-cli.log`
- macOS: `~/Library/Logs/buaalogin-cli/buaalogin-cli.log`
