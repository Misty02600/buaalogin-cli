# Active Context: buaalogin-cli

## 当前工作焦点

项目基础架构已完善，模块命名已规范化，测试全部通过。

## 最近变更

- **2026-01-29**: 完成模块命名规范化
  - 将源码目录从 `src/buaalogin/` 重命名为 `src/buaalogin_cli/`
  - 删除 `[tool.uv.build-backend]` 自定义配置，使用默认规则
  - 更新 `[project.scripts]` 入口点为 `buaalogin_cli.__main__:main`
  - 将 `APP_NAME` 从 `"buaalogin"` 改为 `"buaalogin-cli"`
  - 更新所有测试文件的导入路径和 mock patch 路径
  - 所有 33 个单元测试通过

- **2026-01-29**: 修复 `uv sync` 构建错误
  - 原问题：`[tool.uv-build]` 配置节名错误，应为 `[tool.uv.build-backend]`
  - 最终方案：删除自定义 module-name，使用包名自动派生的模块名

- **2026-01-26**: 完成网络检测和请求库重构 (TASK004)
  - 添加 `requests` 库依赖
  - 用 `requests` 替代 `urllib`，API 更简洁
  - 启用 SSL 验证（测试确认网关证书有效）
  - 更新单元测试，所有测试通过

- **2026-01-26**: 完成 service.py 模块重构 (TASK003)
  - 定义 `NetworkStatus` 枚举（三态：UNKNOWN_NETWORK / LOGGED_OUT / LOGGED_IN）
  - 实现 `get_status()` 核心检测函数
  - 精简 `login()` 和 `keep_alive()` 逻辑
  - 消除函数冗余，减少不必要的 Playwright 依赖

## 命名规范

| 项目                   | 值              | 说明            |
| ---------------------- | --------------- | --------------- |
| **包名 (pip install)** | `buaalogin-cli` | PyPI 包名       |
| **模块名 (import)**    | `buaalogin_cli` | Python 导入名   |
| **CLI 命令**           | `buaalogin`     | 终端命令        |
| **APP_NAME**           | `buaalogin-cli` | 配置/日志目录名 |

## 文件路径（更新后）

### 配置文件

- Windows: `%APPDATA%/buaalogin-cli/config.json`
- Linux: `~/.config/buaalogin-cli/config.json`
- macOS: `~/Library/Application Support/buaalogin-cli/config.json`

### 日志文件

- Windows: `%LOCALAPPDATA%/buaalogin-cli/Logs/buaalogin-cli.log`
- Linux: `~/.local/state/buaalogin-cli/buaalogin-cli.log`
- macOS: `~/Library/Logs/buaalogin-cli/buaalogin-cli.log`

## 下一步计划

1. **进一步优化和扩展**
   - 考虑添加更多的网络检测端点选项
   - 改进错误消息的用户友好性
   - 探索支持其他学校认证系统的可能性

2. **部署和发布**
   - 准备首个稳定版本 v0.1.0
   - 撰写详细的安装和使用指南
   - 完善 CI/CD 流程

3. **文档和社区**
   - API 文档完善
   - 贡献指南编写
   - 收集和应对用户反馈

## 活跃决策与考虑

### 模块命名决策 ✅

**决策**: 使用 `buaalogin_cli` 作为模块名，与包名 `buaalogin-cli` 保持一致

- 遵循 Python 命名规范（模块名使用下划线）
- 遵循 PyPA 规范（包名连字符自动转换为下划线）
- 删除 `[tool.uv.build-backend]` 自定义配置，使用 uv_build 默认行为
- `APP_NAME` 使用 `"buaalogin-cli"` 保持与包名一致

### 网络检测和请求库方案 ✅

**决策**: 使用 `requests` 库 + 启用 SSL 验证
- 相比 `urllib`，`requests` API 更简洁、易用
- 原计划禁用 SSL 验证，后经测试确认北航网关证书有效
- 最终保持默认 SSL 验证启用，提高安全性
- 所有网络检测通过 `requests.get()` 统一实现

## 工作笔记

### 项目现状观察

1. **代码结构清晰**：模块划分合理，职责明确
2. **命名规范**：包名、模块名、APP_NAME 保持一致
3. **功能完整**：核心功能（登录、保活、配置）已全部实现
4. **架构优化**：service 模块已重构，消除冗余，架构清晰
5. **入口规范**：`__main__.py` 提供标准化入口，支持多种运行方式
6. **测试完善**：33+ 测试用例，单元和集成测试分层组织，全部通过
7. **文档完善**：Memory Bank 提供详细的技术和流程文档
8. **依赖合理**：使用 `requests` 替代 `urllib`，代码更简洁，安全更完善
