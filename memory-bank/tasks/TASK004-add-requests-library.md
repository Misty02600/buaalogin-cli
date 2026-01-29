# [TASK004] - 添加 requests 库并解释 SSL 验证

**Status:** Completed
**Added:** 2026-01-26
**Updated:** 2026-01-26

## Original Request

解释什么叫禁用 SSL 验证以及为什么要用，以及计划添加 requests 库替代当前的 urllib 实现。

## Thought Process

### 什么是 SSL/TLS 验证？

**SSL（Secure Sockets Layer）** 和 **TLS（Transport Layer Security）** 是用于加密网络通信的协议。当你访问 `https://` 网站时，浏览器会：

1. **证书验证**：检查服务器提供的 SSL 证书是否由受信任的证书颁发机构（CA）签发
2. **主机名验证**：确保证书中的域名与你访问的域名匹配
3. **有效期检查**：确保证书未过期
4. **证书链验证**：验证从服务器证书到根证书的信任链完整

### 为什么需要禁用 SSL 验证？

在某些特殊场景下需要禁用验证：

1. **自签名证书**：校园网、企业内网常使用自签名证书，未经 CA 认证b
2. **证书配置问题**：服务器证书配置不当（过期、域名不匹配等）
3. **开发/测试环境**：快速测试时临时跳过验证
4. **遗留系统**：老旧系统无法更新证书

本项目中，北航校园网网关 (`gw.buaa.edu.cn`) 的 SSL 证书可能存在问题，导致标准验证失败，因此需要禁用验证才能正常检测网络状态。

### 安全注意事项

禁用 SSL 验证存在安全风险：
- **中间人攻击**：攻击者可能冒充服务器
- **数据窃取**：加密通信可能被截获

但在本项目场景中风险可控：
- 仅用于检测网络状态，不传输敏感数据
- 登录操作由 Playwright 浏览器处理，有完整的 SSL 验证

### 当前实现 vs requests 库

**当前实现（urllib + ssl）**：
```python
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

request = urllib.request.Request(GATEWAY_URL, headers={"User-Agent": "Mozilla/5.0"})
response = urllib.request.urlopen(request, timeout=5, context=ctx)
```

**requests 库实现**：
```python
response = requests.get(GATEWAY_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
```

**requests 库优势**：
- API 更简洁直观
- 自动处理重定向
- 统一的异常处理
- 更好的 session 管理
- 社区广泛使用，文档完善

## Implementation Plan

- [ ] 1. 添加 `requests` 库到项目依赖
- [ ] 2. 修改 `service.py` 中的 `get_status()` 函数使用 requests
- [ ] 3. 添加警告抑制代码（禁止 InsecureRequestWarning）
- [ ] 4. 更新相关的单元测试
- [ ] 5. 更新文档说明 SSL 验证的处理方式

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description                      | Status    | Updated    | Notes                        |
| --- | -------------------------------- | --------- | ---------- | ---------------------------- |
| 1.1 | 添加 requests 到 pyproject.toml  | Completed | 2026-01-26 | -                            |
| 1.2 | 重构 get_status() 使用 requests  | Completed | 2026-01-26 | 已启用 SSL 验证              |
| 1.3 | 添加 InsecureRequestWarning 抑制 | Skipped   | 2026-01-26 | 用户决定启用验证，不需要抑制 |
| 1.4 | 更新单元测试                     | Completed | 2026-01-26 | -                            |
| 1.5 | 更新技术文档                     | Completed | 2026-01-26 | -                            |

## Progress Log

### 2026-01-26
- 创建任务
- 完成 SSL 验证机制的技术分析
- 对比了 urllib 和 requests 的实现方式
- 制定了实施计划
- 执行了实际的 SSL 连接测试，发现网关证书有效，可以直接通过 SSL 验证
- 用户决定保持启用 SSL 验证
- 添加了 requests 依赖并重构了代码
- 更新了单元测试并通过
- 完成了任务相关的所有开发工作
