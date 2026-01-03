"""MiMo CLI - Your terminal assistant."""


def main() -> None:
    """Entry point - delegates to cli.main()."""
    from .cli import main as _main
    _main()


__all__ = ["main"]
