"""
测试登录状态检测方案

运行方式：
1. 在已登录状态下运行：python test_login_detection.py
2. 注销校园网账号
3. 再次运行：python test_login_detection.py

对比两次输出，找出可靠的检测方法
"""

import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# 日志文件
LOG_FILE = Path(__file__).parent / "test_login_detection.log"


# 用于同时输出到控制台和文件
class Logger:
    def __init__(self, file_path: Path):
        self.file = open(file_path, "a", encoding="utf-8")

    def print(self, *args, **kwargs):
        print(*args, **kwargs)
        print(*args, **kwargs, file=self.file)

    def close(self):
        self.file.close()


log: Logger = None


def init_logger():
    """初始化日志对象"""
    global log
    log = Logger(LOG_FILE)


def test_method_1():
    """方法1: 检测是否能访问百度（检查状态码）"""
    global log
    log.print("\n=== 方法1: 访问 http://www.baidu.com ===")
    try:
        req = urllib.request.Request(
            "http://www.baidu.com", headers={"User-Agent": "Mozilla/5.0"}
        )
        response = urllib.request.urlopen(req, timeout=5)
        final_url = response.geturl()
        status_code = response.getcode()

        log.print(f"状态码: {status_code}")
        log.print(f"最终URL: {final_url}")
        log.print(f"是否被重定向: {final_url != 'http://www.baidu.com/'}")

        # 判断逻辑
        if "gw.buaa.edu.cn" in final_url or "srun" in final_url:
            log.print(">>> 判断: 未登录（被重定向到校园网登录页）")
            return False
        else:
            log.print(">>> 判断: 已登录")
            return True

    except Exception as e:
        log.print(f"异常类型: {type(e).__name__}")
        log.print(f"异常信息: {e}")
        log.print(">>> 判断: 网络异常或未登录")
        return False


def test_method_2():
    """方法2: 访问 HTTP 204 端点（微软连接检测）- 当前使用的方法"""
    global log
    log.print("\n=== 方法2: 访问 http://www.msftconnecttest.com/connecttest.txt ===")
    log.print(">>> 这是当前 check_login_status() 使用的方法")
    try:
        response = urllib.request.urlopen(
            "http://www.msftconnecttest.com/connecttest.txt", timeout=5
        )
        content = response.read().decode("utf-8").strip()
        final_url = response.geturl()
        status_code = response.getcode()
        headers = dict(response.headers)

        log.print(f"状态码: {status_code}")
        log.print(f"最终URL: {final_url}")
        log.print(f"返回内容: '{content}'")
        log.print(f"内容长度: {len(content)} 字符")
        log.print(f"Content-Type: {headers.get('Content-Type', 'N/A')}")

        # 检查是否被重定向
        is_redirected = "msftconnecttest.com" not in final_url
        log.print(f"是否被重定向: {is_redirected}")
        if is_redirected:
            log.print(f"  重定向目标: {final_url}")

        # 判断逻辑
        if content == "Microsoft Connect Test":
            log.print(">>> 判断: 已登录（返回了正确内容）")
            return True
        else:
            log.print(
                f">>> 判断: 未登录（内容不匹配，实际内容前100字符: '{content[:100]}...'）"
            )
            return False

    except urllib.error.HTTPError as e:
        log.print(f"HTTP 错误: {e.code} {e.reason}")
        log.print(f"异常类型: {type(e).__name__}")
        return False
    except urllib.error.URLError as e:
        log.print(f"URL 错误: {e.reason}")
        log.print(f"异常类型: {type(e).__name__}")
        if isinstance(e.reason, socket.timeout):
            log.print("  原因: 连接超时")
        elif isinstance(e.reason, socket.gaierror):
            log.print("  原因: DNS 解析失败（可能没有网络）")
        elif isinstance(e.reason, ConnectionRefusedError):
            log.print("  原因: 连接被拒绝")
        return False
    except TimeoutError:
        log.print("异常类型: socket.timeout")
        log.print("  原因: 连接超时")
        return False
    except Exception as e:
        log.print(f"异常类型: {type(e).__name__}")
        log.print(f"异常信息: {e}")
        return False


def test_method_3():
    """方法3: 访问阿里云检测端点"""
    global log
    log.print("\n=== 方法3: 访问 http://www.aliyun.com ===")
    try:
        response = urllib.request.urlopen("http://www.aliyun.com", timeout=5)
        final_url = response.geturl()
        status_code = response.getcode()

        log.print(f"状态码: {status_code}")
        log.print(f"最终URL: {final_url}")

        # 判断逻辑
        if "gw.buaa.edu.cn" in final_url or "srun" in final_url:
            log.print(">>> 判断: 未登录")
            return False
        else:
            log.print(">>> 判断: 已登录")
            return True

    except Exception as e:
        log.print(f"异常类型: {type(e).__name__}")
        log.print(f"异常信息: {e}")
        log.print(">>> 判断: 未登录或网络异常")
        return False


def test_method_4():
    """方法4: 直接访问校园网检测页面"""
    global log
    log.print("\n=== 方法4: 访问 http://gw.buaa.edu.cn ===")
    try:
        response = urllib.request.urlopen("http://gw.buaa.edu.cn", timeout=5)
        content = response.read().decode("utf-8", errors="ignore")
        final_url = response.geturl()

        log.print(f"最终URL: {final_url}")

        # 检查关键字
        has_login_form = "username" in content and "password" in content
        has_logout_btn = "注销" in content or "logout" in content or "下线" in content
        has_success = "success" in final_url.lower()

        log.print(f"URL 包含 success: {has_success}")
        log.print(f"包含登录表单: {has_login_form}")
        log.print(f"包含注销按钮: {has_logout_btn}")

        # 判断逻辑
        if has_success or has_logout_btn:
            log.print(">>> 判断: 已登录")
            return True
        elif has_login_form:
            log.print(">>> 判断: 未登录（显示登录表单）")
            return False
        else:
            log.print(">>> 判断: 无法确定")
            return None

    except Exception as e:
        log.print(f"异常类型: {type(e).__name__}")
        log.print(f"异常信息: {e}")
        log.print(">>> 判断: 无法访问校园网页面")
        return False


def test_method_5():
    """方法5: 测试网络连通性（ping 检测）"""
    global log
    log.print("\n=== 方法5: 基础网络连通性测试 ===")

    # 测试 DNS 解析
    log.print("1. 测试 DNS 解析...")
    try:
        ip = socket.gethostbyname("www.baidu.com")
        log.print(f"   www.baidu.com -> {ip}")
        dns_ok = True
    except socket.gaierror as e:
        log.print(f"   DNS 解析失败: {e}")
        dns_ok = False

    # 测试 TCP 连接
    log.print("2. 测试 TCP 连接 (baidu.com:80)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(("www.baidu.com", 80))
        sock.close()
        log.print("   TCP 连接成功")
        tcp_ok = True
    except Exception as e:
        log.print(f"   TCP 连接失败: {type(e).__name__}: {e}")
        tcp_ok = False

    if dns_ok and tcp_ok:
        log.print(">>> 网络基础连通性正常")
    elif dns_ok and not tcp_ok:
        log.print(">>> DNS 正常但 TCP 被阻断（可能是防火墙或未登录校园网）")
    else:
        log.print(">>> 网络不通（无 DNS 或无网络连接）")


if __name__ == "__main__":
    # 询问当前状态
    print("请选择当前网络状态：")
    print("  1. 已登录校园网")
    print("  2. 连接校园网 WiFi 但未登录")
    print("  3. 完全断网")
    print("  q. 退出")

    choice = input("\n请输入选项 (1/2/3/q): ").strip()

    if choice == "q":
        sys.exit(0)

    status_map = {
        "1": "已登录校园网",
        "2": "连接WiFi未登录",
        "3": "完全断网",
    }

    status = status_map.get(choice, f"未知状态({choice})")

    # 初始化日志
    init_logger()

    log.print("\n" + "=" * 60)
    log.print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.print(f"网络状态: {status}")
    log.print("=" * 60)

    test_method_5()  # 先测试基础连通性
    test_method_1()
    test_method_2()
    test_method_3()
    test_method_4()

    log.print("\n" + "=" * 60)
    log.print(f"测试完成！结果已保存到: {LOG_FILE}")
    log.print("=" * 60 + "\n")

    log.close()

    print(f"\n日志文件: {LOG_FILE}")
