"""
Configuration for Raven CLI
"""

import os
from dataclasses import dataclass, field


@dataclass
class RavenConfig:
    """Configuration for Raven Core backend"""

    # Raven Core API endpoint
    api_base: str = field(
        default_factory=lambda: os.environ.get(
            "RAVEN_API_BASE",
            "https://ravenapi-production.up.railway.app/v1"
        )
    )

    # API key for authentication
    api_key: str = field(
        default_factory=lambda: os.environ.get(
            "RAVEN_API_KEY",
            "raven-railway-production"
        )
    )

    # Model to use
    model: str = field(
        default_factory=lambda: os.environ.get(
            "RAVEN_MODEL",
            "raven-core"
        )
    )

    # Model alias for backend compatibility
    # Using openai/ prefix tells litellm to use OpenAI-compatible API
    model_alias: str = "openai/raven-core"

    # Skip model validation
    skip_model_check: bool = True

    # Coding assistant settings
    # Use "whole" format as it's more compatible with custom models
    edit_format: str = "whole"
    auto_commits: bool = True
    dirty_commits: bool = True

    def to_env_dict(self) -> dict:
        """Convert config to environment variables for aider"""
        return {
            "OPENAI_API_BASE": self.api_base,
            "OPENAI_API_KEY": self.api_key,
            # Aider-specific env vars
            "AIDER_OPENAI_API_BASE": self.api_base,
            "AIDER_OPENAI_API_KEY": self.api_key,
            "AIDER_MODEL": self.model_alias,
        }

    def get_backend_args(self) -> list:
        """Get command line arguments for the coding backend"""
        args = [
            # Disable config file loading to prevent global configs from overriding
            "--config", "/dev/null",
            "--no-aiderignore",
            "--model", self.model_alias,
            "--openai-api-base", self.api_base,
            "--openai-api-key", self.api_key,
            "--edit-format", self.edit_format,
            "--no-show-model-warnings",
            "--no-check-model-accepts-settings",
            # Disable model verification to avoid issues with custom models
            "--no-verify-ssl",  # In case of SSL issues
        ]

        if self.auto_commits:
            args.append("--auto-commits")
        else:
            args.append("--no-auto-commits")

        if self.dirty_commits:
            args.append("--dirty-commits")
        else:
            args.append("--no-dirty-commits")

        return args


# Default configuration instance
default_config = RavenConfig()
