"""BUAA 校园网自动登录 CLI 工具"""

import typer

from . import service, startup
from .config import config
from .constants import CONFIG_FILE, LOG_FILE
from .log import setup_console

app = typer.Typer(
    help="BUAA 校园网自动登录工具",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """BUAA 校园网登录工具。

    在任何子命令执行前调用，加载配置文件并设置默认参数值。
    如果未指定子命令则显示帮助信息。
    """
    # 这些值会覆盖子命令中的参数默认值
    file_config = config.to_dict()

    # 子命令会继承配置文件的值（如果命令行未显式指定参数）
    ctx.default_map = {
        "login": file_config,
        "run": file_config,
    }

    # 若未指定子命令，显示帮助信息后退出
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("login")
def login_cmd(
    username: str | None = typer.Option(
        None,
        "--user",
        "-u",
        envvar="BUAA_USERNAME",
        metavar="学号",
        help="校园网账号",
        show_default=False,
    ),
    password: str | None = typer.Option(
        None,
        "--pass",
        "-p",
        envvar="BUAA_PASSWORD",
        metavar="密码",
        help="校园网密码",
        show_default=False,
    ),
    headless: bool = typer.Option(
        True,
        "--headless/--headed",
        help="是否使用无头模式运行浏览器",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细调试信息"),
):
    """执行单次登录。"""
    setup_console(verbose=verbose)
    _do_login_cmd(username, password, headless)


@app.command("run")
def run_cmd(
    username: str | None = typer.Option(
        None,
        "--user",
        "-u",
        envvar="BUAA_USERNAME",
        metavar="学号",
        help="校园网账号",
        show_default=False,
    ),
    password: str | None = typer.Option(
        None,
        "--pass",
        "-p",
        envvar="BUAA_PASSWORD",
        metavar="密码",
        help="校园网密码",
        show_default=False,
    ),
    interval: int = typer.Option(
        5,
        "--interval",
        "-i",
        envvar="BUAA_CHECK_INTERVAL",
        metavar="分钟",
        min=1,
        help="检测间隔",
    ),
    headless: bool = typer.Option(
        True,
        "--headless/--headed",
        help="是否使用无头模式运行浏览器",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细调试信息"),
):
    """持续保持在线，定期检测并自动重连。"""
    setup_console(verbose=verbose)

    passwd = password

    if username is None or passwd is None:
        typer.secho("❌ 缺少账号或密码", fg=typer.colors.RED)
        typer.echo("\n请通过以下方式之一提供凭据：")
        typer.echo("  1. 运行 `buaalogin config` 配置")
        typer.echo("  2. 使用命令行参数: --user <账号> --pass <密码>")
        typer.echo("  3. 设置环境变量: BUAA_USERNAME, BUAA_PASSWORD")
        raise typer.Exit(1)

    service.keep_alive(username, passwd, interval, headless=headless)


@app.command("config")
def config_cmd(
    username: str | None = typer.Option(
        None, "--user", "-u", metavar="学号", help="校园网账号"
    ),
    password: str | None = typer.Option(
        None, "--pass", "-p", metavar="密码", help="校园网密码"
    ),
    interval: int | None = typer.Option(
        None, "--interval", "-i", metavar="分钟", min=1, help="保活检测间隔"
    ),
    show: bool = typer.Option(
        False, "--show", "-s", is_flag=True, help="仅显示当前配置", show_default=True
    ),
):
    """配置账户信息。"""
    if show:
        typer.secho(f"配置文件: {CONFIG_FILE}", fg=typer.colors.CYAN)
        saved = config.to_dict()
        if saved:
            for key, value in saved.items():
                typer.echo(f"  {key} = {value}")
        else:
            typer.echo("  （尚未配置）")
        return

    # 若未指定任何参数，进入交互式输入模式
    if username is None and password is None and interval is None:
        username = typer.prompt("请输入 BUAA 学号")
        while not username:
            typer.secho("学号不能为空", fg=typer.colors.RED)
            username = typer.prompt("请输入 BUAA 学号")
        password = typer.prompt("请输入密码")
        while not password:
            typer.secho("密码不能为空", fg=typer.colors.RED)
            password = typer.prompt("请输入密码")

    # 仅更新用户显式指定的配置项
    if username is not None:
        config.username = username
    if password is not None:
        config.password = password
    if interval is not None:
        config.interval = interval
    config.save_to_json(CONFIG_FILE)
    typer.secho("✅ 配置已保存!", fg=typer.colors.GREEN)
    typer.echo(f"   位置: {CONFIG_FILE}")


@app.command("status")
def status_cmd():
    """检查当前网络连接状态。"""
    if service.get_status() == service.NetworkStatus.LOGGED_IN:
        typer.secho("✅ 网络正常", fg=typer.colors.GREEN)
        raise typer.Exit(0)
    else:
        typer.secho("❌ 未登录或无法访问外网", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("info")
def info_cmd():
    """显示配置文件和日志文件的存储位置。"""
    config_file = CONFIG_FILE

    typer.echo("配置文件:")
    typer.echo(f"  {config_file}")
    if config_file.exists():
        typer.secho("  ✅ 已存在", fg=typer.colors.GREEN)
    else:
        typer.secho("  ⚠️ 未配置", fg=typer.colors.YELLOW)

    typer.echo()
    typer.echo("日志文件:")
    typer.echo(f"  {LOG_FILE}")
    if LOG_FILE.exists():
        size = LOG_FILE.stat().st_size
        typer.secho(f"  ✅ 文件大小: {size / 1024:.1f} KB", fg=typer.colors.GREEN)
    else:
        typer.secho("  📝 尚未生成", fg=typer.colors.BLUE)


# region 开机自启子命令组

startup_app = typer.Typer(help="管理开机自启（仅 Windows）")
app.add_typer(startup_app, name="startup")


@startup_app.command("enable")
def startup_enable():
    """启用开机自启。"""

    if not startup.is_admin():
        typer.secho(
            "❌ 需要管理员权限，请以管理员身份运行终端后重试",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    try:
        startup.enable_startup()
        typer.secho("✅ 开机自启已启用", fg=typer.colors.GREEN)
    except RuntimeError as e:
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from None


@startup_app.command("disable")
def startup_disable():
    """禁用开机自启。"""

    startup.disable_startup()
    typer.secho("✅ 开机自启已禁用", fg=typer.colors.GREEN)


@startup_app.command("status")
def startup_status():
    """查看开机自启状态。"""

    if startup.is_startup_enabled():
        typer.secho("✅ 开机自启: 已启用", fg=typer.colors.GREEN)
    else:
        typer.secho("⚪ 开机自启: 未启用", fg=typer.colors.YELLOW)


# endregion


def _do_login_cmd(
    cli_username: str | None,
    cli_pass: str | None,
    headless: bool = True,
):
    """执行单次登录的 CLI 逻辑（含错误提示）。"""
    if cli_username is None or cli_pass is None:
        typer.secho("❌ 缺少账号或密码", fg=typer.colors.RED)
        typer.echo("\n请通过以下方式之一提供凭据：")
        typer.echo("  1. 运行 `buaalogin config` 配置")
        typer.echo("  2. 使用命令行参数: --user <账号> --pass <密码>")
        typer.echo("  3. 设置环境变量: BUAA_USERNAME, BUAA_PASSWORD")
        raise typer.Exit(1)

    try:
        service.login(cli_username, cli_pass, headless=headless)
        typer.secho("✅ 登录成功", fg=typer.colors.GREEN)
    except service.LoginError as e:
        typer.secho(f"❌ 登录失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
