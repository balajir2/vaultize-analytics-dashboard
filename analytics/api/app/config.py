"""
Configuration Module

Loads and validates configuration from environment variables.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have defaults for development but should be overridden
    in production via environment variables or .env file.
    """

    # ========================================================================
    # Application Settings
    # ========================================================================

    app_name: str = "Vaultize Analytics API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    api_root_path: str = Field(default="/api/v1", env="API_ROOT_PATH")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_reload: bool = Field(default=False, env="API_RELOAD")

    # Logging
    log_level: str = Field(default="INFO", env="API_LOG_LEVEL")

    # CORS
    cors_origins: str = Field(default="*", env="API_CORS_ORIGINS")

    # ========================================================================
    # OpenSearch Settings
    # ========================================================================

    opensearch_host: str = Field(default="localhost", env="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, env="OPENSEARCH_PORT")
    opensearch_scheme: str = Field(default="http", env="OPENSEARCH_SCHEME")
    opensearch_user: str = Field(default="admin", env="OPENSEARCH_ADMIN_USERNAME")
    opensearch_password: str = Field(default="admin", env="OPENSEARCH_ADMIN_PASSWORD")
    opensearch_verify_certs: bool = Field(default=False, env="OPENSEARCH_VERIFY_CERTS")

    # Connection pool settings
    opensearch_max_connections: int = Field(default=100, env="OPENSEARCH_MAX_CONNECTIONS")
    opensearch_timeout: int = Field(default=30, env="OPENSEARCH_TIMEOUT")

    # ========================================================================
    # Security Settings
    # ========================================================================

    # Authentication (opt-in: disabled by default for development)
    auth_enabled: bool = Field(default=False, env="AUTH_ENABLED")
    auth_admin_username: str = Field(default="admin", env="AUTH_ADMIN_USERNAME")
    auth_admin_password: str = Field(default="admin", env="AUTH_ADMIN_PASSWORD")

    # JWT settings
    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",  # Must be changed in production!
        env="API_SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, env="API_ACCESS_TOKEN_EXPIRE_MINUTES")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="API_RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=1000, env="API_RATE_LIMIT_PER_MINUTE")

    # ========================================================================
    # Query Settings
    # ========================================================================

    # Default query limits
    default_page_size: int = 100
    max_page_size: int = 10000

    # Search settings
    default_search_timeout: str = "30s"
    max_result_window: int = 10000

    # ========================================================================
    # Computed Properties
    # ========================================================================

    @property
    def opensearch_url(self) -> str:
        """Construct OpenSearch URL from components."""
        return f"{self.opensearch_scheme}://{self.opensearch_host}:{self.opensearch_port}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ========================================================================
    # Validators
    # ========================================================================

    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is valid."""
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    @validator("opensearch_scheme")
    def validate_scheme(cls, v):
        """Ensure scheme is valid."""
        if v not in ["http", "https"]:
            raise ValueError("OpenSearch scheme must be 'http' or 'https'")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v_upper

    # ========================================================================
    # Configuration
    # ========================================================================

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# ============================================================================
# Global Settings Instance
# ============================================================================

# Initialize settings (loads from environment + .env file)
settings = Settings()


# ============================================================================
# Validation
# ============================================================================

def validate_settings():
    """
    Validate critical settings and warn about insecure configurations.

    Raises:
        ValueError: If critical settings are missing or invalid
    """
    errors = []
    warnings = []

    # Critical validations
    if not settings.opensearch_host:
        errors.append("OPENSEARCH_HOST is required")

    # Security warnings for production/staging
    if settings.environment in ("production", "staging"):
        if settings.debug:
            warnings.append("DEBUG is enabled in production (security risk)")

        if settings.secret_key == "CHANGE_ME_IN_PRODUCTION":
            errors.append("API_SECRET_KEY must be changed in production/staging")

        if settings.auth_enabled and settings.auth_admin_password == "admin":
            errors.append(
                "AUTH_ADMIN_PASSWORD must be changed when auth is enabled in production/staging"
            )

        if settings.opensearch_scheme == "http":
            warnings.append("Using HTTP for OpenSearch in production (use HTTPS)")

        if not settings.opensearch_verify_certs and settings.opensearch_scheme == "https":
            warnings.append("SSL certificate verification is disabled")

        if settings.cors_origins == "*":
            errors.append(
                "CORS allows all origins in production/staging — "
                "set API_CORS_ORIGINS to specific origins"
            )

    # Log warnings
    if warnings:
        import logging
        logger = logging.getLogger(__name__)
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")

    # Raise errors
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Validate settings on import
validate_settings()
