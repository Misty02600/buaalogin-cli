# Experiments / 实验性代码

本目录包含开发过程中用于调试和探索的脚本，**不是正式的自动化测试**。

## 文件说明

| 文件 | 用途 |
|------|------|
| `debug_page.py` | 调试登录页面 DOM 结构，查看表单元素 |
| `test_login_detection.py` | 探索不同的登录状态检测方案 |
| `test_login_offline.py` | 离线环境下手动测试登录功能 |
| `test_login_success_detection.py` | 测试登录成功后的页面状态检测 |

## 运行方式

这些脚本需要手动运行，通常用于：
- 开发新功能前的探索
- 调试网络或页面问题
- 验证检测逻辑

```bash
# 示例：运行调试脚本
uv run python experiments/debug_page.py
```

## 注意事项

- 部分脚本需要有效的 `.env` 配置（BUAA_USERNAME, BUAA_PASSWORD）
- 部分脚本需要连接校园网环境
- 这些脚本不会被 pytest 自动发现和运行
