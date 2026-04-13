# Scripts

该目录用于放置仓库内可重复执行的辅助脚本。

当前约定：

- 面向校园网升级排障的脚本统一放在 `scripts/diagnostics/`
- 运行产物统一输出到 `artifacts/diagnostics/`
- 诊断脚本优先做到“可脱离当前会话独立运行”
- 不通过 `justfile` 暴露这些脚本，直接使用 `uv run python ...`

## 目录结构

```text
scripts/
  README.md
  diagnostics/
    common.py
    capture_gateway_snapshot.py
    probe_login_flow.py
    check_status_api.py
```

## 运行方式

在项目根目录执行：

```bash
uv run python scripts/diagnostics/capture_gateway_snapshot.py
uv run python scripts/diagnostics/check_status_api.py
uv run python scripts/diagnostics/probe_login_flow.py --submit-mode invalid
```

若需要在断开校园网后直接尝试真实登录，可使用：

```bash
uv run python scripts/diagnostics/probe_login_flow.py --submit-mode real
```

## 凭据来源

`probe_login_flow.py` 在 `--submit-mode real` 下按以下优先级读取账号密码：

1. 命令行参数 `--user` / `--password`
2. 环境变量 `BUAA_USERNAME` / `BUAA_PASSWORD`
3. 已保存的配置文件（`buaalogin config set` 写入）

脚本不会把真实密码写入产物；如果使用真实凭据模式，登录后截图会先对表单值做脱敏处理。

## 输出目录

每次运行都会创建独立目录，格式如下：

```text
artifacts/diagnostics/<timestamp>-<script-name>[-label]/
```

常见产物包括：

- `summary.json`
- `page.html`
- `page.png`
- `inventory.json`
- `network-requests.json`
- `network-responses.json`
- `console.json`

如果排障结束后需要清理现场文件，直接删除 `artifacts/diagnostics/` 中对应运行目录即可。
