# Configuration

Complete guide to configuring numistalib.

## Configuration Methods

numistalib can be configured through:

0. Environment variables (recommended)
1. `.env` file
2. Direct Settings object

## § 1 Environment Variables

### Core Settings

#### NUMISTA_API_KEY

**Required**. Your Numista API key.

```bash
export NUMISTA_API_KEY="your_api_key_here"
```

Get your key at: <https://en.numista.com/api/>

#### NUMISTA_BASE_URL

Base URL for the Numista API.

- **Default**: `https://api.numista.com/v3`
- **Type**: string

```bash
export NUMISTA_BASE_URL="https://api.numista.com/v3"
```

### Cache Settings

#### CACHE_DIR

Directory for persistent HTTP cache.

- **Default**: `.numista_cache`
- **Type**: string (path)

```bash
export CACHE_DIR="/path/to/cache"
```

#### CACHE_TTL_SECONDS

Time-to-live for cached responses.

- **Default**: `604800` (7 days)
- **Type**: integer (seconds)

```bash
export CACHE_TTL_SECONDS=86400  # 1 day
```

### Rate Limiting

#### RATE_LIMIT

Maximum number of requests per time window.

- **Default**: `45`
- **Type**: integer

```bash
export RATE_LIMIT=30
```

#### RATE_LIMIT_WINDOW

Time window for rate limiting.

- **Default**: `60` (seconds)
- **Type**: integer

```bash
export RATE_LIMIT_WINDOW=60
```

### Retry Settings

#### MAX_RETRIES

Maximum number of retry attempts for failed requests.

- **Default**: `3`
- **Type**: integer

```bash
export MAX_RETRIES=5
```

#### RETRY_BACKOFF_FACTOR

Multiplier for exponential backoff.

- **Default**: `2.0`
- **Type**: float

```bash
export RETRY_BACKOFF_FACTOR=1.5
```

### Logging

#### LOG_LEVEL

Logging verbosity level.

- **Default**: `INFO`
- **Type**: string
- **Valid values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
export LOG_LEVEL=DEBUG
```

---

## § 2 .env File Configuration

Create a `.env` file in your project root:

```bash
# Numista API
NUMISTA_API_KEY=your_api_key_here
NUMISTA_BASE_URL=https://api.numista.com/v3

# Cache
CACHE_DIR=.numista_cache
CACHE_TTL_SECONDS=604800

# Rate Limiting
RATE_LIMIT=45
RATE_LIMIT_WINDOW=60

# Retry
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0

# Logging
LOG_LEVEL=INFO
```

The `.env` file is automatically loaded when using `Settings()`.

---

## § 3 Programmatic Configuration

### Using Settings Object

```python
from numistalib.config import Settings

# Load from environment/.env
settings = Settings()

# Override specific values
settings = Settings(
    numista_api_key="your_key",
    cache_ttl_seconds=86400,  # 1 day
    rate_limit=30
)

# Use with client
from numistalib.client import NumistaApiClient

with NumistaApiClient(settings) as client:
    # Use client
    pass
```

### Custom Cache Directory

```python
from pathlib import Path
from numistalib.config import Settings

cache_path = Path.home() / ".cache" / "numista"
settings = Settings(cache_dir=str(cache_path))
```

### Disable Caching

```python
settings = Settings(cache_ttl_seconds=0)
```

Note: This will still create the cache directory but responses won't be stored.

### Aggressive Rate Limiting

For API quota conservation:

```python
settings = Settings(
    rate_limit=20,        # 20 requests
    rate_limit_window=60  # per minute
)
```

### Increase Retry Attempts

For unreliable networks:

```python
settings = Settings(
    max_retries=10,
    retry_backoff_factor=3.0
)
```

---

## § 4 Configuration Validation

Settings are validated using Pydantic:

```python
from numistalib.config import Settings

try:
    settings = Settings(
        rate_limit=-5  # Invalid!
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

---

## § 5 Viewing Current Configuration

### Via CLI

```bash
numistalib config list
```

Shows all current settings including:

- API key (masked)
- Cache directory
- TTL
- Rate limits
- Retry settings

### Programmatically

```python
from numistalib.config import Settings

settings = Settings()

print(f"API Key: {settings.numista_api_key[:8]}...")
print(f"Cache Dir: {settings.cache_dir}")
print(f"Cache TTL: {settings.cache_ttl_seconds}s")
print(f"Rate Limit: {settings.rate_limit}/{settings.rate_limit_window}s")
```

---

## § 6 Multi-Environment Setup

### Development

`.env.development`:

```bash
NUMISTA_API_KEY=dev_key
CACHE_DIR=.cache_dev
CACHE_TTL_SECONDS=3600
LOG_LEVEL=DEBUG
```

### Production

`.env.production`:

```bash
NUMISTA_API_KEY=prod_key
CACHE_DIR=/var/cache/numista
CACHE_TTL_SECONDS=604800
LOG_LEVEL=WARNING
```

Load specific environment:

```python
from numistalib.config import Settings
from pathlib import Path

env_file = Path(".env.production")
settings = Settings(_env_file=env_file)
```

---

## § 7 Docker Configuration

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  numistalib:
    image: python:3.13
    environment:
      - NUMISTA_API_KEY=${NUMISTA_API_KEY}
      - CACHE_DIR=/cache
      - CACHE_TTL_SECONDS=604800
      - RATE_LIMIT=45
    volumes:
      - ./cache:/cache
      - ./app:/app
    working_dir: /app
    command: python your_script.py
```

---

## § 8 Best Practices

### Security

0. **Never commit `.env` files** to version control
1. Add `.env` to `.gitignore`
2. Use environment-specific files (`.env.local`, `.env.production`)
3. Rotate API keys periodically

### Performance

0. **Use default cache TTL** (7 days) for stable data
1. Reduce cache TTL for frequently changing data
2. Adjust rate limits based on your API tier
3. Use async methods for batch operations

### Reliability

0. **Keep retry settings moderate** (3-5 attempts)
1. Use exponential backoff factor ≥ 2.0
2. Monitor rate limit usage
3. Handle errors gracefully

---

## § 9 Troubleshooting

### "API key not found"

Ensure `NUMISTA_API_KEY` is set:

```bash
echo $NUMISTA_API_KEY
```

Or check `.env` file exists and contains the key.

### "Permission denied" (cache directory)

Ensure the cache directory is writable:

```bash
mkdir -p .numista_cache
chmod 755 .numista_cache
```

### Rate limit errors

Check your rate limit settings:

```bash
numistalib config get rate_limit
numistalib config get rate_limit_window
```

Reduce request frequency or increase limits if your API tier supports it.

### Cache not working

Verify cache directory and TTL:

```bash
numistalib config get cache_dir
numistalib config get cache_ttl_seconds
ls -la .numista_cache/
```

---

## § 10 Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `numista_api_key` | str | *required* | Numista API key |
| `numista_base_url` | str | `https://api.numista.com/v3` | API base URL |
| `cache_dir` | str | `.numista_cache` | Cache directory path |
| `cache_ttl_seconds` | int | `604800` | Cache TTL (7 days) |
| `rate_limit` | int | `45` | Requests per window |
| `rate_limit_window` | int | `60` | Rate limit window (seconds) |
| `max_retries` | int | `3` | Maximum retry attempts |
| `retry_backoff_factor` | float | `2.0` | Exponential backoff multiplier |
| `log_level` | str | `INFO` | Logging level |

---

## Next Steps

- [Advanced Usage](advanced_usage.md) - Complex configuration scenarios
- [Architecture](architecture.md) - Understanding how configuration works
- [CLI Guide](cli_guide.md) - Using configuration with CLI
