# [TASK001] - 整理测试文件结构并补充单元/集成测试

**Status:** Completed
**Added:** 2026-01-26
**Updated:** 2026-01-26

## Original Request

把 tests 里实验性的代码放入 experiments 文件夹。然后在 test 补充单元和集成测试。

## Thought Process

### 问题分析

当前 `tests/` 目录包含以下文件：
- `debug_page.py` - 调试脚本，用于检查登录页面 DOM 结构
- `test_login_detection.py` - 测试登录状态检测的多种方案
- `test_login_offline.py` - 离线测试脚本，用于测试登录功能
- `test_login_success_detection.py` - 测试登录成功后页面状态的调试脚本
- `test_login_detection.log` - 测试日志文件

### 文件分类分析

**实验性代码（应移至 experiments/）：**
1. `debug_page.py` - 纯调试脚本，用于查看页面结构
2. `test_login_detection.py` - 探索性测试，比较不同检测方法
3. `test_login_offline.py` - 手动运行的登录测试脚本
4. `test_login_success_detection.py` - 登录成功检测的探索脚本
5. `test_login_detection.log` - 测试产生的日志

这些文件都是手动运行的调试/探索脚本，不是标准的单元测试或集成测试。

**需要补充的测试：**
1. **单元测试**：
   - `test_config.py` - 测试配置加载、验证
   - `test_service_utils.py` - 测试 service.py 中的辅助函数

2. **集成测试**：
   - `test_integration.py` - 测试完整的登录流程（mock 网络请求）

## Implementation Plan

### Phase 1: 创建 experiments 目录并移动文件
- [ ] 1.1 创建 `experiments/` 目录
- [ ] 1.2 移动 `debug_page.py` 到 `experiments/`
- [ ] 1.3 移动 `test_login_detection.py` 到 `experiments/`
- [ ] 1.4 移动 `test_login_offline.py` 到 `experiments/`
- [ ] 1.5 移动 `test_login_success_detection.py` 到 `experiments/`
- [ ] 1.6 移动 `test_login_detection.log` 到 `experiments/`
- [ ] 1.7 创建 `experiments/README.md` 说明文件

### Phase 2: 创建测试基础设施
- [ ] 2.1 创建 `tests/__init__.py`
- [ ] 2.2 创建 `tests/conftest.py` - pytest fixtures
- [ ] 2.3 更新 `pyproject.toml` 添加测试依赖（pytest, pytest-mock）

### Phase 3: 编写单元测试
- [ ] 3.1 创建 `tests/unit/__init__.py`
- [ ] 3.2 创建 `tests/unit/test_config.py` - 配置模块测试
- [ ] 3.3 创建 `tests/unit/test_constants.py` - 常量测试
- [ ] 3.4 创建 `tests/unit/test_service.py` - service 模块单元测试

### Phase 4: 编写集成测试
- [ ] 4.1 创建 `tests/integration/__init__.py`
- [ ] 4.2 创建 `tests/integration/test_login_flow.py` - 登录流程集成测试
- [ ] 4.3 创建 `tests/integration/test_keepalive.py` - 保活功能集成测试

### Phase 5: 验证和文档
- [ ] 5.1 运行所有测试确保通过
- [x] 5.2 更新 README.md 添加测试说明

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 创建 experiments/ 目录 | Complete | 2026-01-26 | |
| 1.2 | 移动 debug_page.py | Complete | 2026-01-26 | |
| 1.3 | 移动 test_login_detection.py | Complete | 2026-01-26 | |
| 1.4 | 移动 test_login_offline.py | Complete | 2026-01-26 | |
| 1.5 | 移动 test_login_success_detection.py | Complete | 2026-01-26 | |
| 1.6 | 移动 test_login_detection.log | Complete | 2026-01-26 | |
| 1.7 | 创建 experiments/README.md | Complete | 2026-01-26 | |
| 2.1 | 创建 tests/__init__.py | Complete | 2026-01-26 | |
| 2.2 | 创建 tests/conftest.py | Complete | 2026-01-26 | |
| 2.3 | 更新 pyproject.toml | Complete | 2026-01-26 | 添加 pytest-mock 和 pytest 配置 |
| 3.1 | 创建 tests/unit/__init__.py | Complete | 2026-01-26 | |
| 3.2 | 创建 test_config.py | Complete | 2026-01-26 | 14 个测试 |
| 3.3 | 创建 test_constants.py | Complete | 2026-01-26 | 5 个测试 |
| 3.4 | 创建 test_service.py | Complete | 2026-01-26 | 14 个测试 |
| 4.1 | 创建 tests/integration/__init__.py | Complete | 2026-01-26 | |
| 4.2 | 创建 test_login_flow.py | Complete | 2026-01-26 | 10 个测试 |
| 4.3 | 创建 test_keepalive.py | Complete | 2026-01-26 | 7 个测试 |
| 5.1 | 运行测试验证 | Complete | 2026-01-26 | 50 passed |
| 5.2 | 更新 README.md | Complete | 2026-01-26 | 添加开发和测试说明 |

## Progress Log

### 2026-01-26
- 创建任务文件
- 分析现有 tests/ 目录结构
- 确定实验性代码和正式测试的划分
- 制定详细的实施计划

### 2026-01-26 (实施)
- Phase 1: 创建 experiments/ 目录，移动 4 个调试脚本和 1 个日志文件
- Phase 1: 创建 experiments/README.md 说明文件
- Phase 2: 创建测试基础设施 (conftest.py, __init__.py)
- Phase 2: 更新 pyproject.toml 添加 pytest-mock 和 pytest 配置
- Phase 3: 编写单元测试 (test_constants.py, test_config.py, test_service.py)
- Phase 4: 编写集成测试 (test_login_flow.py, test_keepalive.py)
- Phase 5: 运行测试，修复 1 个失败的测试（mock URL 属性问题）
- Phase 5: 所有 50 个测试通过
- Phase 5: 更新 README.md 添加开发和测试说明
