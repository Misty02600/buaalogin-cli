# Tasks Index

任务索引文件，记录所有任务及其状态。

## In Progress

*当前没有进行中的任务*

## Pending

- [TASK008] 修复网络状态检测逻辑
  - 添加时间：2026-02-02
  - 目标：修复 `get_status()` 函数的登录状态判断逻辑
  - 问题：URL 不包含 "success" 导致误判为未登录

- [TASK005] 验证登录页面选择器
  - 添加时间：2026-01-29
  - 目标：验证登录按钮和错误信息的真实 DOM 选择器

## Completed

- [TASK007] 开机自启功能
  - 完成时间：2026-02-02
  - 成果：Task Scheduler + onstart 触发器，当前用户运行

- [TASK006] 模块命名规范化
  - 完成时间：2026-01-29
  - 成果：模块名改为 `buaalogin_cli`，APP_NAME 改为 `buaalogin-cli`

- [TASK004] 添加 requests 库并解释 SSL 验证
  - 完成时间：2026-01-26
  - 成果：requests 库集成、SSL 验证启用

- [TASK003] 重构 service.py 模块函数
  - 完成时间：2026-01-26
  - 成果：三态检测、消除冗余、精简架构

- [TASK002] 新建 __main__ 文件作为运行入口
  - 完成时间：2026-01-26
  - 成果：标准化入口，支持两种运行方式

- [TASK001] 整理测试文件结构并补充单元/集成测试
  - 完成时间：2026-01-26
  - 成果：50+ 测试用例，单元和集成测试分层

## Abandoned

*当前没有已废弃的任务*

---

## 命名规范

| 项目     | 值              |
| -------- | --------------- |
| 包名     | `buaalogin-cli` |
| 模块名   | `buaalogin_cli` |
| CLI 命令 | `buaalogin`     |
| APP_NAME | `buaalogin-cli` |

---

## 任务创建指南

使用以下命令创建新任务：

```
add task <任务描述>
```

或

```
create task <任务描述>
```

任务文件将创建在 `tasks/` 目录下，格式为 `TASKXXX-taskname.md`。
