from pydantic import Field
from pydantic_settings import BaseSettings


class TestConfig(BaseSettings):
    """
    Global configuration management for the test automation suite.

    Key QA Concepts Implemented:
    - Single Source of Truth: Centralizes all environmental variables (URLs, timeouts, toggles).
    - Configuration & Environment Separation: Decouples test code from execution environment details using .env support.
    - Fail Fast / Type Safety: Validates environment variables at runtime instantiation (e.g., ensuring timeouts are positive integers),
      preventing silent failures deep in the execution phase.
    """

    base_url: str = Field(
        default="https://conduit-realworld-example-app.fly.dev/#/",
        description="The entry point for the UI tests."
    )
    api_base_url: str = Field(
        default="https://conduit-realworld-example-app.fly.dev",
        description="The base endpoint for API interactions."
    )
    default_timeout: int = Field(
        default=10,
        gt=0,  # QA Validation: Must be a positive integer to prevent logic errors in Wait strategies
        description="Global explicit wait timeout in seconds."
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode. Recommended for CI/CD pipelines and parallel execution."
    )

    class Config:
        """Pydantic internal configuration for environment variable mapping."""
        env_file = ".env"
        env_prefix = "TEST_"
        extra = "ignore"


# ==========================================================
# INSTANTIATION & EXPORTS
# ==========================================================

# Validation happens immediately upon instantiation
config = TestConfig()

# Compatibility exports for existing infrastructure modules
# These allow modules like 'browser_wrapper.py' to import specific constants if needed,
# though using the 'config' object directly is preferred.
BASE_URL = config.base_url
API_URL = config.api_base_url
DEFAULT_TIMEOUT = config.default_timeout