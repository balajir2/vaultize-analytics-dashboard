"""
Configuration Module

Loads and validates configuration from environment variables.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Alerting service settings loaded from environment variables.
    """

    # Application
    app_name: str = "Vaultize Alerting Service"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Management API
    api_host: str = Field(default="0.0.0.0", env="ALERTING_API_HOST")
    api_port: int = Field(default=8001, env="ALERTING_API_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # OpenSearch
    opensearch_host: str = Field(default="localhost", env="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, env="OPENSEARCH_PORT")
    opensearch_scheme: str = Field(default="http", env="OPENSEARCH_SCHEME")
    opensearch_user: str = Field(default="admin", env="OPENSEARCH_ADMIN_USERNAME")
    opensearch_password: str = Field(default="admin", env="OPENSEARCH_ADMIN_PASSWORD")
    opensearch_verify_certs: bool = Field(default=False, env="OPENSEARCH_VERIFY_CERTS")
    opensearch_timeout: int = Field(default=30, env="OPENSEARCH_TIMEOUT")

    # Authentication (opt-in: disabled by default for development)
    auth_enabled: bool = Field(default=False, env="AUTH_ENABLED")
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION", env="API_SECRET_KEY")
    algorithm: str = "HS256"

    # Alerting
    alert_rules_dir: str = Field(default="configs/alert-rules", env="ALERT_RULES_DIR")
    alert_state_index: str = Field(default=".alerts-state", env="ALERT_STATE_INDEX")
    alert_history_index: str = Field(default=".alerts-history", env="ALERT_HISTORY_INDEX")
    webhook_timeout: int = Field(default=10, env="WEBHOOK_TIMEOUT")
    webhook_retries: int = Field(default=3, env="WEBHOOK_RETRIES")

    @property
    def opensearch_url(self) -> str:
        return f"{self.opensearch_scheme}://{self.opensearch_host}:{self.opensearch_port}"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v_upper

    @field_validator("opensearch_scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        if v not in ["http", "https"]:
            raise ValueError("OpenSearch scheme must be 'http' or 'https'")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


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

    if settings.environment in ("production", "staging"):
        if settings.secret_key == "CHANGE_ME_IN_PRODUCTION":
            errors.append("API_SECRET_KEY must be changed in production/staging")

        if settings.debug:
            warnings.append("DEBUG is enabled in production (security risk)")

        if settings.opensearch_scheme == "http":
            warnings.append("Using HTTP for OpenSearch in production (use HTTPS)")

    if warnings:
        logger = logging.getLogger(__name__)
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


validate_settings()
