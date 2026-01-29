# [TASK005] - 验证登录页面选择器

**Status:** Pending
**Added:** 2026-01-29
**Updated:** 2026-01-29

## Original Request

`login` 函数和 `_get_error_message` 函数中的选择器是猜测的，需要实际验证 BUAA 校园网登录页面的真实元素。

当前代码中猜测的选择器：

**登录按钮** (第 115 行)：
```python
'#login-account, button:has-text("登录"), button:has-text("Login")'
```

**错误信息** (第 144-150 行)：
```python
error_selectors = [
    ".error-message",
    ".alert-danger",
    "#error-msg",
    "text=用户名或密码错误",
    "text=认证失败",
]
```

## Thought Process

1. 需要实际访问 BUAA 校园网登录页面
2. 使用浏览器开发者工具检查登录按钮的 DOM 结构
3. 故意输入错误密码触发错误，检查错误信息元素
4. 确认真实的 CSS 选择器
5. 更新代码中的选择器

## Implementation Plan

- [ ] 1. 在校园网环境下访问登录页面 (https://gw.buaa.edu.cn/)
- [ ] 2. 用开发者工具 (F12) 检查登录按钮元素
- [ ] 3. 故意输入错误的用户名/密码组合
- [ ] 4. 检查错误信息元素的选择器
- [ ] 5. 更新 `service.py` 中的登录按钮选择器
- [ ] 6. 更新 `_get_error_message` 函数中的错误选择器
- [ ] 7. 添加相应的测试用例

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 5.1 | 访问登录页面 | Not Started | - | 需要校园网环境 |
| 5.2 | 检查登录按钮 DOM | Not Started | - | 使用 F12 开发者工具 |
| 5.3 | 触发错误并检查错误元素 | Not Started | - | 输入错误密码 |
| 5.4 | 更新登录按钮选择器 | Not Started | - | service.py 第 115 行 |
| 5.5 | 更新错误信息选择器 | Not Started | - | service.py 第 144-150 行 |
| 5.6 | 添加测试用例 | Not Started | - | - |

## Progress Log

### 2026-01-29
- 任务创建
- 扩展范围：同时验证登录按钮和错误信息选择器

## Notes

- 验证需要在 BUAA 校园网环境下进行
- 可以考虑使用 `experiments/` 目录下的脚本辅助测试
- 登录页面 URL: https://gw.buaa.edu.cn/
