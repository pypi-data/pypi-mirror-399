"""Configuration management for MiMo CLI."""

import os
from dataclasses import dataclass
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]


CONFIG_DIR = Path.home() / ".mimo"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _prompt_with_placeholder(label: str, placeholder: str, is_password: bool = False) -> str:
    """Prompt user with placeholder text that disappears on input."""
    result = prompt(
        HTML(f"<b>{label}</b>: "),
        placeholder=HTML(f"<style fg='#888888'>{placeholder}</style>"),
        is_password=is_password,
    )
    return result.strip()


def _prompt_bool(label: str, default: bool = False) -> bool:
    """Prompt user for a yes/no answer."""
    default_hint = "Y/n" if default else "y/N"
    result = prompt(HTML(f"<b>{label}</b> [{default_hint}]: "))
    result = result.strip().lower()
    if not result:
        return default
    return result in ("y", "yes", "true", "1")


@dataclass
class LLMConfig:
    """LLM-related configuration."""

    model: str = "openai/gpt-4o-mini"
    api_base: str | None = None
    api_key: str | None = None


@dataclass
class PermissionsConfig:
    """Permissions-related configuration."""

    auto_accept_editor: bool = False  # Auto-accept editor ops within cwd


@dataclass
class Config:
    """Configuration for MiMo CLI.

    Priority: CLI args > env vars > config file > defaults
    """

    llm: LLMConfig
    permissions: PermissionsConfig

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from config file and environment variables.

        Priority: env vars > config file > defaults
        """
        # Start with defaults
        llm = LLMConfig()
        permissions = PermissionsConfig()

        # Load from config file if exists
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "rb") as f:
                    config_data = tomllib.load(f)

                # Load [llm] section
                llm_data = config_data.get("llm", {})
                llm = LLMConfig(
                    model=llm_data.get("model", llm.model),
                    api_base=llm_data.get("api_base", llm.api_base),
                    api_key=llm_data.get("api_key", llm.api_key),
                )

                # Load [permissions] section
                perm_data = config_data.get("permissions", {})
                permissions = PermissionsConfig(
                    auto_accept_editor=perm_data.get("auto_accept_editor", permissions.auto_accept_editor),
                )
            except Exception:
                pass  # Ignore config file errors, use defaults

        # Override with environment variables
        llm.model = os.environ.get("MIMO_MODEL", llm.model)
        llm.api_base = os.environ.get("MIMO_API_BASE", llm.api_base)
        llm.api_key = os.environ.get("MIMO_API_KEY", llm.api_key)

        # Auto-add openai/ provider if no provider specified
        if "/" not in llm.model:
            llm.model = f"openai/{llm.model}"

        return cls(llm=llm, permissions=permissions)

    @staticmethod
    def exists() -> bool:
        """Check if config file exists."""
        return CONFIG_FILE.exists()

    @staticmethod
    def interactive_setup() -> "Config":
        """Interactively prompt user to create config file."""
        print("\n✨ Welcome to MiMo CLI! Let's set up your configuration.\n")

        # LLM settings
        api_base = _prompt_with_placeholder(
            "API Base URL",
            "https://api.openai.com/v1"
        )
        api_key = _prompt_with_placeholder(
            "API Key",
            "sk-...",
            is_password=True
        )
        model = _prompt_with_placeholder(
            "Model Name",
            "openai/gpt-4o-mini"
        )

        # Permission settings
        auto_accept_editor = _prompt_bool(
            "Auto-accept editor operations in current directory",
            default=False
        )

        # Use defaults if empty
        if not api_base:
            api_base = "https://api.openai.com/v1"
        if not model:
            model = "openai/gpt-4o-mini"

        # Build config content
        config_content = f'''# MiMo CLI Configuration

[llm]
model = "{model}"
api_base = "{api_base}"
'''
        if api_key:
            config_content += f'api_key = "{api_key}"\n'
        else:
            config_content += '# api_key = "your-api-key-here"  # Or use MIMO_API_KEY env var\n'

        config_content += f'''
[permissions]
auto_accept_editor = {str(auto_accept_editor).lower()}
'''

        # Write config file
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(config_content)

        print(f"\n✅ Config saved to {CONFIG_FILE}\n")

        # Return loaded config
        return Config.load()
