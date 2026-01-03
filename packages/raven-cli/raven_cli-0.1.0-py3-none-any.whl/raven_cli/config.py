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
    model_alias: str = "openai/raven-core"

    # Coding assistant settings
    edit_format: str = "diff"
    auto_commits: bool = True
    dirty_commits: bool = True

    def to_env_dict(self) -> dict:
        """Convert config to environment variables"""
        return {
            "OPENAI_API_BASE": self.api_base,
            "OPENAI_API_KEY": self.api_key,
        }

    def get_backend_args(self) -> list:
        """Get command line arguments for the coding backend"""
        args = [
            "--model", self.model_alias,
            "--edit-format", self.edit_format,
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
