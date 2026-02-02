# [TASK008] - 修复网络状态检测逻辑

**Status:** Pending
**Added:** 2026-02-02
**Updated:** 2026-02-02
**Priority:** High
**Type:** Bug Fix

## Original Request

用户报告 `buaalogin status` 命令返回"未登录或无法访问外网"，但用户认为自己应该处于登录状态。

## 问题分析

### 现象

```bash
❯ uv run buaalogin status
❌ 未登录或无法访问外网
```

### 调试过程

1. **检查 `get_status()` 函数逻辑**：
   - 访问 `https://gw.buaa.edu.cn/`
   - 如果最终 URL 包含 "success" → `LOGGED_IN`
   - 否则 → `LOGGED_OUT`

2. **实际请求测试**：
   ```python
   import requests
   r = requests.get('https://gw.buaa.edu.cn', headers={'User-Agent': 'Mozilla/5.0'}, timeout=3, allow_redirects=True)
   print(r.url)
   # 输出: https://gw.buaa.edu.cn/srun_portal_pc?ac_id=1&theme=buaa
   ```

3. **页面内容检查**：
   - 页面显示"网络准入认证系统"登录页面
   - 包含"忘记密码"、"自助服务"、"用户激活"等链接
   - 提示"扫这里 进入迅连小程序上网"

### 根本原因

当前的检测逻辑依赖 URL 中包含 "success" 关键词，但：

1. **URL 格式可能已变化**：网关重定向的 URL 格式可能不再使用 "success"
2. **认证机制问题**：
   - 校园网认证可能基于 MAC 地址/IP 绑定
   - `requests` 库发起的请求可能没有携带认证 session
   - 与浏览器的认证状态可能不一致

3. **可能的场景**：
   - 用户通过微信小程序"迅连"认证，但 HTTP 请求未被关联
   - 认证超时需要重新登录
   - 网络环境变化（IP 变更等）

## Implementation Plan

- [ ] 1. 确认正确的登录状态检测方法
  - 研究北航网关的认证机制
  - 确定登录成功后的 URL 格式或页面特征
  - 考虑检查页面内容而非仅依赖 URL

- [ ] 2. 改进 `get_status()` 函数
  - 增加页面内容解析逻辑
  - 可能需要检查特定的 DOM 元素或文本
  - 添加更多的状态判断条件

- [ ] 3. 考虑认证 session 的持久化
  - 是否需要保存和复用认证 cookie
  - 考虑使用 `requests.Session` 保持会话

- [ ] 4. 添加更详细的状态反馈
  - `status` 命令增加 `--verbose` 选项
  - 输出更多诊断信息（URL、页面标题等）

- [ ] 5. 更新测试用例
  - 添加更多 URL 格式的测试
  - 模拟不同的网关响应场景

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID  | Description                       | Status      | Updated    | Notes                |
| --- | --------------------------------- | ----------- | ---------- | -------------------- |
| 8.1 | 确认登录成功的 URL/页面特征       | Not Started | 2026-02-02 | 需要实际登录后观察   |
| 8.2 | 改进 get_status() 检测逻辑        | Not Started | 2026-02-02 | 可能需要解析页面内容 |
| 8.3 | 添加 --verbose 选项到 status 命令 | Not Started | 2026-02-02 | 便于调试             |
| 8.4 | 更新单元测试                      | Not Started | 2026-02-02 | 覆盖新的检测逻辑     |

## Progress Log

### 2026-02-02
- 任务创建
- 完成初步调试，确认问题：URL 不包含 "success" 导致误判
- 获取实际 URL：`https://gw.buaa.edu.cn/srun_portal_pc?ac_id=1&theme=buaa`
- 确认页面内容为登录页面

## Related Files

- `src/buaalogin_cli/service.py` - `get_status()` 函数
- `src/buaalogin_cli/cli.py` - `status_cmd()` 命令
- `src/buaalogin_cli/constants.py` - `GATEWAY_URL` 常量

## Notes

- 北航网关使用深澜（Srun）认证系统
- 可能需要参考其他使用深澜系统的项目了解检测方法
- 登录成功页面的 URL 特征需要实际验证
