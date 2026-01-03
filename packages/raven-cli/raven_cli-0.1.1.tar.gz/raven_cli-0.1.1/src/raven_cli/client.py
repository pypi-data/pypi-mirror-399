"""
Raven Client - AI coding assistant with Raven Core backend
"""

import os
import sys
from typing import Optional, List

from .config import RavenConfig, default_config


class RavenClient:
    """Client for running Raven coding assistant"""

    def __init__(self, config: Optional[RavenConfig] = None):
        self.config = config or default_config

    def setup_environment(self):
        """Set up environment variables for Raven Core"""
        env_vars = self.config.to_env_dict()
        for key, value in env_vars.items():
            os.environ[key] = value

    def run(self, extra_args: Optional[List[str]] = None):
        """Run Raven coding assistant"""
        self.setup_environment()

        # Build the full argument list
        args = self.config.get_backend_args()
        if extra_args:
            args.extend(extra_args)

        # Import and run the backend
        try:
            from aider.main import main as backend_main

            original_argv = sys.argv.copy()
            sys.argv = ["raven"] + args

            try:
                return backend_main()
            finally:
                sys.argv = original_argv

        except ImportError as e:
            print(f"Error: Backend not available. Run: pip install raven-cli")
            print(f"Details: {e}")
            sys.exit(1)

    def chat(self, message: str) -> str:
        """Send a single message to Raven Core"""
        import openai

        client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
        )

        response = client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": message}],
        )

        return response.choices[0].message.content

    def check_connection(self) -> dict:
        """Check connection to Raven Core API"""
        import openai

        client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
        )

        try:
            models = client.models.list()
            return {
                "status": "connected",
                "models": [m.id for m in models.data],
                "endpoint": self.config.api_base,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "endpoint": self.config.api_base,
            }
