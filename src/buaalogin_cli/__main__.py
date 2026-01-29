"""Allow running as `python -m buaalogin_cli`."""

from buaalogin_cli.cli import app


def main() -> None:
    """程序主入口函数。"""
    app()


if __name__ == "__main__":
    main()
