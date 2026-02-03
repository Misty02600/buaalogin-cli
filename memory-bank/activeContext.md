# Active Context: buaalogin-cli

## 当前工作焦点

项目已完成两个重要功能：开机自启 (TASK007) 和网络状态检测修复 (TASK008)。

## 最近变更

- **2026-02-02**: 修复网络状态检测逻辑 (TASK008)
  - 发现原有 URL 检测无法工作（深澜使用 JS 重定向）
  - 改用深澜 `rad_user_info` API 直接检测登录状态
  - 精确匹配 `not_online_error` 判断未登录
  - 能正确区分三种状态：已登录、未登录、非校园网
  - 添加 `RAD_USER_INFO_URL` 常量
  - 更新单元测试，33 个测试通过

- **2026-02-02**: 完成开机自启功能 (TASK007)
  - 使用 Windows Task Scheduler + onstart 触发器
  - 以当前用户身份运行，可访问用户配置
  - 使用 Typer 子命令组：`buaalogin startup enable/disable/status`
  - 使用 getpass 获取密码，避免中文终端问题
  - 更新 README 添加使用说明和手动设置指南

- **2026-01-29**: 完成模块命名规范化 (TASK006)
  - 将源码目录从 `src/buaalogin/` 重命名为 `src/buaalogin_cli/`
  - 将 `APP_NAME` 从 `"buaalogin"` 改为 `"buaalogin-cli"`
  - 更新所有测试文件的导入路径

## 命名规范

| 项目                   | 值              | 说明            |
| ---------------------- | --------------- | --------------- |
| **包名 (pip install)** | `buaalogin-cli` | PyPI 包名       |
| **模块名 (import)**    | `buaalogin_cli` | Python 导入名   |
| **CLI 命令**           | `buaalogin`     | 终端命令        |
| **APP_NAME**           | `buaalogin-cli` | 配置/日志目录名 |

## 关键 URL/API

| 用途     | URL/API                                        |
| -------- | ---------------------------------------------- |
| 网关首页 | `https://gw.buaa.edu.cn`                       |
| 状态检测 | `https://gw.buaa.edu.cn/cgi-bin/rad_user_info` |

## 文件路径

### 配置文件

- Windows: `%APPDATA%/buaalogin-cli/config.json`
- Linux: `~/.config/buaalogin-cli/config.json`
- macOS: `~/Library/Application Support/buaalogin-cli/config.json`

### 日志文件

- Windows: `%LOCALAPPDATA%/buaalogin-cli/Logs/buaalogin-cli.log`
- Linux: `~/.local/state/buaalogin-cli/buaalogin-cli.log`
- macOS: `~/Library/Logs/buaalogin-cli/buaalogin-cli.log`

## 下一步计划

1. **功能完善**
   - 添加 `--verbose` 选项到 status 命令
   - 考虑添加网络诊断功能

2. **发布准备**
   - v0.1.0 正式版本发布
   - PyPI 包发布
   - CI/CD 流程完善

3. **文档和社区**
   - API 文档完善
   - 贡献指南编写

## 活跃决策与考虑

### 网络状态检测决策 ✅

**决策**: 使用深澜 `rad_user_info` API 检测登录状态

- **原方案问题**：`requests` 无法执行 JS 重定向，URL 检测失败
- **新方案优势**：API 直接返回状态，无需页面解析
- **精确匹配**：`not_online_error` = 未登录，其他非空响应 = 已登录
- **验证完成**：三种场景（已登录/未登录/非校园网）全部测试通过

### 开机自启决策 ✅

**决策**: 使用 Windows Task Scheduler + onstart 触发器

- 以当前用户运行，可访问用户配置
- 使用 `getpass` 获取密码，避免终端问题
- 使用 Typer 子命令组组织命令

## 工作笔记

### 项目现状观察

1. **代码结构清晰**：模块划分合理，职责明确
2. **命名规范**：包名、模块名、APP_NAME 保持一致
3. **功能完整**：核心功能 + 开机自启 + 状态检测
4. **架构优化**：使用 API 检测，消除 JS 重定向问题
5. **测试完善**：33+ 测试用例，全部通过
6. **文档完善**：Memory Bank 提供详细技术文档
