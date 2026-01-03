"""CLI entry point for MiMo CLI."""

import sys


def main() -> None:
    """MiMo CLI - Your terminal assistant."""
    # Show instant greeting before heavy imports
    print("\033[2mLoading...\033[0m", end="\r", flush=True)

    # Now do the heavy imports
    import click
    from .agent import Agent
    from .config import Config

    @click.command()
    @click.option("--model", "-m", help="Model to use (overrides config)")
    @click.option("--api-base", help="API base URL (overrides config)")
    def _main(model: str | None, api_base: str | None) -> None:
        # Clear the "Loading..." line
        print(" " * 20, end="\r", flush=True)

        # Interactive setup if no config exists
        if Config.exists():
            config = Config.load()
        else:
            config = Config.interactive_setup()

        # Override with CLI args
        if model:
            config.llm.model = model
        if api_base:
            config.llm.api_base = api_base

        agent = Agent(config)
        agent.run()

    _main()


if __name__ == "__main__":
    main()
