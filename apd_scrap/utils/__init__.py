"""Utilidades para APD-Scrap."""

from apd_scrap.utils.logging import LoggerMixin, get_logger, setup_logging
from apd_scrap.utils.ssl_adapter import CIPHERS, CustomHttpAdapter, LegacyHttpAdapter
from apd_scrap.utils.retry import retry_with_backoff, RetryConfig, RetryError
from apd_scrap.utils.rate_limiter import (
    RateLimiter,
    RateLimiterConfig,
    create_rate_limiter,
    rate_limit,
)
from apd_scrap.utils.validators import (
    Validators,
    ValidationError,
    validate_cuil,
    validate_ige,
    validate_distrito,
)

__all__ = [
    "CustomHttpAdapter",
    "LegacyHttpAdapter",
    "CIPHERS",
    "setup_logging",
    "get_logger",
    "LoggerMixin",
    "retry_with_backoff",
    "RetryConfig",
    "RetryError",
    "RateLimiter",
    "RateLimiterConfig",
    "create_rate_limiter",
    "rate_limit",
    "Validators",
    "ValidationError",
    "validate_cuil",
    "validate_ige",
    "validate_distrito",
]
