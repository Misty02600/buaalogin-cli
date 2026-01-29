# [TASK003] - 重构 service.py 模块函数

**Status:** Completed
**Added:** 2026-01-26
**Updated:** 2026-01-26

## Original Request

service 部分函数细节有些模糊，例如没说清楚到底应该用哪个，还有检测是否登录和是否成功登录明显冗余，以及 check_login_status 也是检查登录。先不管其他地方，这个模块要确定好我们到底应该需要哪些函数，具体如何实现。之前经过测试，Microsoft Connect Test 可以确定是否有成功连接网络，`"success" in page.url.lower()` 这种方法可以确定是否连上了校园网，而且这些函数要尽量不依赖 playwright，因为占用稍微比较大。

## Thought Process

### 当前问题分析

1. **函数冗余问题**：
   - `check_login_status()` - 使用 HTTP 请求检测是否联网
   - `_check_already_logged_in(page)` - 使用 playwright 检测 URL 中是否有 "success"
   - `_check_login_success(page)` - 同样检测 URL 中是否有 "success"
   - 后两者完全相同，且都依赖 playwright

2. **命名不清晰**：
   - `check_login_status` 实际检测的是"能否访问外网"，而非"校园网登录状态"
   - `_check_already_logged_in` 和 `_check_login_success` 名称不同但实现相同

3. **依赖问题**：
   - 检测功能应尽量不依赖 playwright（开销大）
   - playwright 只在必须进行浏览器操作（填表登录）时使用

### 核心需求梳理

网络状态可以简化为三种情况，通过访问校园网网关 (`https://gw.buaa.edu.cn/`) 一次性判断：

1. **非校园网环境**：请求失败（DNS错误或超时）。
   - 动作：等待，不尝试登录。
2. **校园网-已登录**：请求成功，且 URL 包含 "success"。
   - 动作：无需操作。
3. **校园网-未登录**：请求成功，但 URL 不含 "success"（通常跳转到 login 页面）。
   - 动作：执行登录。

这种方案最精简，去除了冗余的 Microsoft Connect Test 请求。

### 设计方案

#### 函数职责划分

| 函数名 | 职责 | 依赖 | 场景 |
|--------|------|------|------|
| `get_status()` | **核心检测函数**。返回当前网络状态枚举。 | urllib | 保活循环 |
| `login()` | 执行登录操作 | playwright | 需要认证时 |
| `keep_alive()` | 保活主循环 | 以上两者 | 服务运行 |

#### 状态定义

引入枚举 `NetworkStatus`：
- `UNKNOWN_NETWORK`: 非校园网环境
- `LOGGED_OUT`: 在校园网但未登录
- `LOGGED_IN`: 已登录

### 关键设计决策

1. **单一检测源 `get_status()`**
   - 替代之前的 `check_buaa_wifi` 和 `check_network`。
   - 实现逻辑：
     - 访问 `https://gw.buaa.edu.cn/` (无 SSL 验证)
     - 异常 -> `UNKNOWN_NETWORK`
     - URL 含 "success" -> `LOGGED_IN`
     - 其他 -> `LOGGED_OUT`

2. **login 流程优化**
   - 只有当状态为 `LOGGED_OUT` 时才调用 playwright。
   - 登录成功后，playwright 内部会看到 success 页面，直接返回。

3. **去除冗余**
   - 移除 `check_network()` (Microsoft Connect Test)。
   - 移除独立的 SSID 检测（网关访问不通即视为不在环境）。

### 关键设计决策

1. **单一检测源 `get_status()`**
   - 替代之前的 `check_buaa_wifi` 和 `check_network`。
   - 实现逻辑：
     - 访问 `https://gw.buaa.edu.cn/` (无 SSL 验证)
     - 异常 -> `UNKNOWN_NETWORK`
     - URL 含 "success" -> `LOGGED_IN`
     - 其他 -> `LOGGED_OUT`

2. **login 流程优化**
   - 只有当状态为 `LOGGED_OUT` 时才调用 playwright。
   - 登录成功后，playwright 内部会看到 success 页面，直接返回。

3. **去除冗余**
   - 移除 `check_network()` (Microsoft Connect Test)。
   - 移除独立的 SSID 检测（网关访问不通即视为不在环境）。

## Implementation Plan

- [x] 分析当前 service.py 函数结构
- [x] 实验验证网关访问方案 (experiments/test_buaa_wifi_detection.py)
- [x] 定义 `NetworkStatus` 枚举
- [x] 实现 `get_status()` 函数
- [x] 更新 `login()` 函数使用内部 helper `_is_on_success_page()`
- [x] 重构 `keep_alive()` 使用 `get_status()`
- [x] 更新单元测试 `tests/unit/test_service.py`
- [x] 验证功能正常

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 3.1 | 分析当前函数结构 | Complete | 2026-01-26 | 已识别冗余和命名问题 |
| 3.2 | 实验验证检测方案 | Complete | 2026-01-26 | DNS 解析失败确认非校园网环境 |
| 3.3 | 定义状态枚举和 API | Complete | 2026-01-26 | NetworkStatus 枚举 |
| 3.4 | 实现 `get_status()` | Complete | 2026-01-26 | 三态检测逻辑 |
| 3.5 | 更新 `login()` | Complete | 2026-01-26 | 使用 `_is_on_success_page()` |
| 3.6 | 更新 `keep_alive()` | Complete | 2026-01-26 | 新流程实现 |
| 3.7 | 更新测试 | Complete | 2026-01-26 | 51 tests passed |
| 3.8 | 功能验证 | Complete | 2026-01-26 | 全部测试通过 |

## Progress Log

### 2026-01-26 (实施完成)
- 完成所有重构工作
- 修改的文件：
  - `src/buaalogin/constants.py`: 移除 `PING_URL`，添加 `GATEWAY_URL`
  - `src/buaalogin/service.py`: 完整重构
  - `tests/unit/test_service.py`: 适配新 API
  - `tests/unit/test_constants.py`: 适配新常量
  - `tests/integration/test_keepalive.py`: 适配新 API
  - `tests/conftest.py`: 更新 fixtures
- 运行全部 51 个测试，全部通过

### 2026-01-26 (设计阶段)
- 创建任务文件
- 分析了当前 service.py 的函数结构
- 识别了三个主要问题：函数冗余、命名不清晰、不必要的 playwright 依赖
- 最终方案：使用 `NetworkStatus` 枚举 + `get_status()` 函数
  - 三态检测：UNKNOWN_NETWORK / LOGGED_OUT / LOGGED_IN
  - 通过访问校园网网关一次性判断环境和登录状态
- 确定设计原则：检测功能不依赖 playwright，只在必须进行浏览器操作时才使用

## API 设计参考

### 重构后的公开 API

```python
from enum import Enum, auto

class NetworkStatus(Enum):
    UNKNOWN_NETWORK = auto()  # 不在校园网环境 (DNS/Timeout)
    LOGGED_OUT = auto()       # 在校园网环境，未登录
    LOGGED_IN = auto()        # 在校园网环境，已登录

def get_status() -> NetworkStatus:
    """获取当前网络状态。

    请求 https://gw.buaa.edu.cn/ 检测。

    Returns:
        NetworkStatus 枚举值
    """

def login(username: str, password: str, *, headless: bool = True) -> None:
    """执行校园网登录。"""

def keep_alive(username: str, password: str, check_interval_min: int, *, headless: bool = True):
    """保活服务主循环。

    Loop:
      status = get_status()
      if status == UNKNOWN: wait
      elif status == LOGGED_IN: wait
      elif status == LOGGED_OUT: login()
    """
```

### 内部辅助函数

```python
def _is_on_success_page(page) -> bool:
    """检查当前页面是否为登录成功页面。

    用于 login() 内部，登录提交后的校验。
    """
```
    通过访问 Microsoft Connect Test 判断是否有外网访问能力。
    不依赖 playwright，开销小，适合频繁调用。

    Returns:
        True 表示有外网访问能力（已通过校园网认证）
    """

def login(username: str, password: str, *, headless: bool = True) -> None:
    """执行校园网登录。

    使用 playwright 打开登录页面并填写凭据。

    Args:
        username: 用户名
        password: 密码
        headless: 是否无头模式

    Raises:
        LoginError: 登录失败
    """

### 内部辅助函数

```python
def _is_on_success_page(page) -> bool:
    """检查当前页面是否为登录成功页面。

    用于 login() 内部，登录提交后的校验。
    """
```
