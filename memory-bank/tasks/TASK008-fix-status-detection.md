# [TASK008] - 修复网络状态检测逻辑

**Status:** Completed
**Added:** 2026-02-02
**Updated:** 2026-02-02
**Priority:** High
**Type:** Bug Fix

## Original Request

用户报告 `buaalogin status` 命令返回"未登录或无法访问外网"，但实际已登录。

## 问题分析

### 现象

```bash
❯ uv run buaalogin status
❌ 未登录或无法访问外网
```

但浏览器访问 `gw.buaa.edu.cn` 显示 success 页面。

### 根本原因

原检测逻辑使用 `requests` 检查 URL 是否包含 "success"，但：

1. **深澜网关使用 JavaScript 重定向**：`requests` 无法执行 JS，只能接收 HTTP 重定向
2. **对比验证**：
   - `requests` → `srun_portal_pc?ac_id=76` (登录页面)
   - `Playwright` → `srun_portal_success?ac_id=76` (成功页面)

### 解决方案

发现深澜系统提供 **`rad_user_info` API** 可直接查询登录状态：

| 场景         | API 响应                          | 判断结果        |
| ------------ | --------------------------------- | --------------- |
| 校园网已登录 | `93830,1770015058,...` (用户信息) | LOGGED_IN       |
| 校园网未登录 | `not_online_error`                | LOGGED_OUT      |
| 非校园网     | 请求失败 (DNS/超时)               | UNKNOWN_NETWORK |

## Implementation

### 修改的文件

1. **`constants.py`**：添加 `RAD_USER_INFO_URL`
   ```python
   RAD_USER_INFO_URL = f"{GATEWAY_URL}/cgi-bin/rad_user_info"
   ```

2. **`service.py`**：重写 `get_status()` 使用 API 精确匹配
   ```python
   def get_status() -> NetworkStatus:
       response = requests.get(RAD_USER_INFO_URL, timeout=5)
       text = response.text.strip()

       if text == "not_online_error":
           return NetworkStatus.LOGGED_OUT
       elif text:
           return NetworkStatus.LOGGED_IN
       else:
           return NetworkStatus.LOGGED_OUT
   ```

3. **`tests/unit/test_service.py`**：更新测试用例匹配新逻辑

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description                 | Status   | Updated    | Notes                    |
| --- | --------------------------- | -------- | ---------- | ------------------------ |
| 8.1 | 对比 requests vs Playwright | Complete | 2026-02-02 | 发现 JS 重定向问题       |
| 8.2 | 发现 rad_user_info API      | Complete | 2026-02-02 | 深澜系统内置 API         |
| 8.3 | 验证三种网络状态            | Complete | 2026-02-02 | 已登录、未登录、非校园网 |
| 8.4 | 重写 get_status() 函数      | Complete | 2026-02-02 | 使用 API 精确匹配        |
| 8.5 | 更新单元测试                | Complete | 2026-02-02 | 33 个测试全部通过        |

## Progress Log

### 2026-02-02
- 任务创建，初步调试确认问题
- 创建 `experiments/compare_status_detection.py` 对比脚本
- 发现 requests 和 Playwright 返回不同 URL（JS 重定向问题）
- 发现深澜 `rad_user_info` API 可直接检测登录状态
- 验证三种场景的 API 响应：
  - 已登录: `93830,1770015058,...`
  - 未登录: `not_online_error`
  - 非校园网: DNS 解析失败
- 更新 `constants.py` 添加 `RAD_USER_INFO_URL`
- 重写 `service.py` 的 `get_status()` 使用精确匹配
- 更新单元测试，33 个测试全部通过
- 实际验证 `buaalogin status` 命令正常工作

## Related Files

- `src/buaalogin_cli/service.py` - `get_status()` 函数
- `src/buaalogin_cli/constants.py` - `RAD_USER_INFO_URL` 常量
- `tests/unit/test_service.py` - 状态检测测试
- `experiments/compare_status_detection.py` - 验证脚本

## Notes

- 深澜 (Srun) 系统提供 `/cgi-bin/rad_user_info` API
- API 使用精确匹配 `not_online_error` 判断未登录
- 不再依赖 URL 中的 "success" 关键词
