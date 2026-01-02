"""Numista API wrapper library.

A Python wrapper for the Numista API with caching, rate limiting, and retry logic.
"""

__version__ = "0.1.1"

import logging
from pathlib import Path

from rich import logging as rich_logging

from numistalib.client import (
    NumistaApiClient,
    NumistaClient,
    NumistaClientAsync,
    NumistaClientSync,
)
from numistalib.config import Settings

# Constants
CACHE_HIT_ICON = "💾"
CACHE_MISS_ICON = "🌐"
DEFAULT_CACHE_HIT_ICON = "💾"
DEFAULT_CACHE_MISS_ICON = "🌐"
DEFAULT_CACHE_DIR = ".cache/numistalib/hishel"
DEFAULT_CACHE_DB = "hishel_cache.db"
DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_API_VERSION = "v3"
DEFAULT_API_BASE_URL = f"https://api.numista.com/{DEFAULT_API_VERSION}"
DEFAULT_CACHE_TTL = 604800  # 7 days
DEFAULT_CACHE_TTL_TYPES = DEFAULT_CACHE_TTL
DEFAULT_CACHE_TTL_CATALOGUES = DEFAULT_CACHE_TTL
DEFAULT_CACHE_TTL_PRICES = 86400  # 1 day
DEFAULT_RATE_LIMIT_REQUESTS = 45  # requests
DEFAULT_RATE_LIMIT_PERIOD = 60  # seconds
DEFAULT_CACHE_REFRESH_ON_ACCESS = True
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_MAX_WAIT = 10  # seconds
DEFAULT_CACHE_ALLOW_STALE = True
DEFAULT_CACHE_SHARED = True
ENVIRONMENT_PREFIX = "NUMISTA_"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "INFO"
LOGGER_NAME = "numistalib"

# Logger setup
handler = rich_logging.RichHandler(
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    markup=True,
    log_time_format="%Y-%m-%d %H:%M:%S",
    show_path=False,
    locals_max_length=120,
    locals_max_string=80,
)
handler.setLevel(DEFAULT_LOG_LEVEL)

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(handler)

# Get environment file and initialize settings
default_settings = Settings()

__all__ = [
    "CACHE_HIT_ICON",
    "CACHE_MISS_ICON",
    "DEFAULT_API_BASE_URL",
    "DEFAULT_API_VERSION",
    "DEFAULT_CACHE_ALLOW_STALE",
    "DEFAULT_CACHE_DB",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_CACHE_HIT_ICON",
    "DEFAULT_CACHE_MISS_ICON",
    "DEFAULT_CACHE_REFRESH_ON_ACCESS",
    "DEFAULT_CACHE_SHARED",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_CACHE_TTL_CATALOGUES",
    "DEFAULT_CACHE_TTL_PRICES",
    "DEFAULT_CACHE_TTL_TYPES",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_RATE_LIMIT_PERIOD",
    "DEFAULT_RATE_LIMIT_REQUESTS",
    "DEFAULT_RETRY_ATTEMPTS",
    "DEFAULT_RETRY_MAX_WAIT",
    "DEFAULT_TIMEOUT",
    "ENVIRONMENT_PREFIX",
    "LOGGER_NAME",
    "LOG_LEVELS",
    "PROJECT_ROOT",
    "NumistaApiClient",
    "NumistaClient",
    "NumistaClientAsync",
    "NumistaClientSync",
    "Settings",
    "__version__",
    "default_settings",
    "logger",
]
