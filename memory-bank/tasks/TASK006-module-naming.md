# [TASK006] - 模块命名规范化

**Status:** Completed
**Added:** 2026-01-29
**Updated:** 2026-01-29

## Original Request

将模块名改为 `buaalogin_cli`，删除 `[tool.uv.build-backend]` 自定义配置，将 `APP_NAME` 改为 `buaalogin-cli`。

## Thought Process

### 背景

原项目使用了自定义的模块名配置 `[tool.uv-build] module-name = "buaalogin"`，但存在以下问题：
1. 配置节名错误（应为 `[tool.uv.build-backend]`）
2. 模块名与包名不一致，容易造成混淆
3. 在 CI 环境中导致 `uv sync` 失败

### 决策

统一命名规范：
- **包名**: `buaalogin-cli`（PyPI 安装名）
- **模块名**: `buaalogin_cli`（Python 导入名，包名自动派生）
- **CLI 命令**: `buaalogin`（终端命令）
- **APP_NAME**: `buaalogin-cli`（配置/日志目录名）

这样更符合 Python 包命名规范，也消除了自定义配置的维护成本。

## Implementation Plan

1. ✅ 删除 `[tool.uv.build-backend]` 配置节
2. ✅ 更新 `[project.scripts]` 入口点
3. ✅ 重命名源码目录 `src/buaalogin/` → `src/buaalogin_cli/`
4. ✅ 更新所有源文件的导入
5. ✅ 更新所有测试文件的导入和 mock patch 路径
6. ✅ 更新 `APP_NAME` 为 `buaalogin-cli`
7. ✅ 更新测试断言
8. ✅ 更新 Memory Bank 文档

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description                 | Status   | Updated    | Notes                                                |
| --- | --------------------------- | -------- | ---------- | ---------------------------------------------------- |
| 6.1 | 删除 uv.build-backend 配置  | Complete | 2026-01-29 | 使用默认派生规则                                     |
| 6.2 | 更新 project.scripts 入口点 | Complete | 2026-01-29 | `buaalogin_cli.__main__:main`                        |
| 6.3 | 重命名源码目录              | Complete | 2026-01-29 | `src/buaalogin_cli/`                                 |
| 6.4 | 更新源文件导入              | Complete | 2026-01-29 | 只需更新 `__main__.py`                               |
| 6.5 | 更新测试文件导入            | Complete | 2026-01-29 | 所有 `from buaalogin.` → `from buaalogin_cli.`       |
| 6.6 | 更新 mock patch 路径        | Complete | 2026-01-29 | 所有 `@patch("buaalogin.` → `@patch("buaalogin_cli.` |
| 6.7 | 更新 APP_NAME               | Complete | 2026-01-29 | `"buaalogin"` → `"buaalogin-cli"`                    |
| 6.8 | 更新测试断言                | Complete | 2026-01-29 | `test_constants.py`                                  |
| 6.9 | 更新 Memory Bank            | Complete | 2026-01-29 | 全部 6 个核心文件 + _index.md                        |

## Progress Log

### 2026-01-29
- 修复 `uv sync` 构建错误，发现配置节名应为 `[tool.uv.build-backend]` 而非 `[tool.uv-build]`
- 决定删除自定义模块名配置，改用默认派生规则
- 重命名源码目录 `src/buaalogin/` → `src/buaalogin_cli/`
- 更新 `pyproject.toml` 入口点
- 使用 PowerShell 批量替换测试文件导入（遇到编码问题）
- 使用 git checkout 恢复测试文件，手动更新导入
- 更新所有 mock patch 路径
- 更新 `APP_NAME` 为 `buaalogin-cli`
- 更新测试断言
- 运行测试，33 个单元测试全部通过 ✅
- 更新 Memory Bank 所有相关文档

## 最终命名规范

| 项目         | 值              | 说明                        |
| ------------ | --------------- | --------------------------- |
| **包名**     | `buaalogin-cli` | `pip install buaalogin-cli` |
| **模块名**   | `buaalogin_cli` | `import buaalogin_cli`      |
| **CLI 命令** | `buaalogin`     | 终端执行命令                |
| **APP_NAME** | `buaalogin-cli` | 配置/日志目录名             |

## 文件路径（更新后）

- 配置文件: `~/.config/buaalogin-cli/config.json`（Linux）
- 日志文件: `~/.local/state/buaalogin-cli/buaalogin-cli.log`（Linux）
