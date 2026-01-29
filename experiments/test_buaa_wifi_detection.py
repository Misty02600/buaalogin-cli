"""实验：通过访问校园网网关判断是否连接到 BUAA WiFi

测试思路：
- 访问 https://gw.buaa.edu.cn/
- 观察在不同网络环境下的响应差异：
  1. 连接 BUAA WiFi 且已登录
  2. 连接 BUAA WiFi 但未登录
  3. 未连接 BUAA WiFi（使用其他网络）

运行方法：
    python experiments/test_buaa_wifi_detection.py
"""

import socket
import ssl
import urllib.error
import urllib.request

GATEWAY_URL = "https://gw.buaa.edu.cn/"
TIMEOUT = 5


def test_gateway_access():
    """测试访问校园网网关"""
    print(f"正在访问: {GATEWAY_URL}")
    print(f"超时设置: {TIMEOUT}s")
    print("-" * 50)

    # 创建不验证 SSL 的上下文（校园网证书可能有问题）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        request = urllib.request.Request(
            GATEWAY_URL,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response = urllib.request.urlopen(request, timeout=TIMEOUT, context=ctx)

        # 响应信息
        print("✓ 请求成功!")
        print(f"  状态码: {response.status}")
        print(f"  最终URL: {response.url}")
        print("  响应头:")
        for key, value in response.headers.items():
            print(f"    {key}: {value}")

        # 读取内容
        content = response.read()
        print(f"\n  内容长度: {len(content)} bytes")
        print("  内容预览 (前 500 字符):")
        print("-" * 50)
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("gbk", errors="replace")
        print(text[:500])
        if len(text) > 500:
            print(f"\n... (省略 {len(text) - 500} 字符)")

        return True, response.url, text

    except urllib.error.HTTPError as e:
        print("✗ HTTP 错误!")
        print(f"  状态码: {e.code}")
        print(f"  原因: {e.reason}")
        try:
            content = e.read().decode("utf-8", errors="replace")
            print(f"  响应内容: {content[:200]}")
        except Exception:
            pass
        return False, None, str(e)

    except urllib.error.URLError as e:
        print("✗ URL 错误!")
        print(f"  原因: {e.reason}")
        if isinstance(e.reason, socket.timeout):
            print("  -> 连接超时，可能未连接到 BUAA 网络")
        elif isinstance(e.reason, socket.gaierror):
            print("  -> DNS 解析失败，可能未连接到 BUAA 网络")
        elif isinstance(e.reason, ConnectionRefusedError):
            print("  -> 连接被拒绝")
        return False, None, str(e)

    except TimeoutError:
        print("✗ 连接超时!")
        print("  -> 可能未连接到 BUAA 网络")
        return False, None, "timeout"

    except Exception as e:
        print(f"✗ 其他错误: {type(e).__name__}")
        print(f"  详情: {e}")
        return False, None, str(e)


def test_with_redirect_tracking():
    """测试并追踪重定向"""
    print("\n" + "=" * 50)
    print("追踪重定向:")
    print("=" * 50)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # 创建不自动跟随重定向的 opener
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            print(f"  [{code}] 重定向到: {newurl}")
            return urllib.request.HTTPRedirectHandler.redirect_request(
                self, req, fp, code, msg, headers, newurl
            )

    opener = urllib.request.build_opener(
        NoRedirectHandler, urllib.request.HTTPSHandler(context=ctx)
    )

    try:
        request = urllib.request.Request(
            GATEWAY_URL,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response = opener.open(request, timeout=TIMEOUT)
        print(f"  最终状态码: {response.status}")
        print(f"  最终URL: {response.url}")
    except Exception as e:
        print(f"  错误: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("BUAA WiFi 检测实验")
    print("=" * 50)
    print()

    success, url, content = test_gateway_access()

    test_with_redirect_tracking()

    print("\n" + "=" * 50)
    print("结论:")
    print("=" * 50)
    if success:
        if "success" in url.lower():
            print("✓ 已连接 BUAA WiFi 且已登录")
        elif (
            "login" in content.lower()
            or "用户名" in content
            or "username" in content.lower()
        ):
            print("✓ 已连接 BUAA WiFi 但未登录（显示登录页面）")
        else:
            print("? 已连接，但需要进一步分析响应内容")
    else:
        print("✗ 可能未连接到 BUAA WiFi")
