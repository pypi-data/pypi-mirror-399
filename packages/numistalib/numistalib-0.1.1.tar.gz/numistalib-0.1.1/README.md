# numistalib

[![Documentation Status](https://readthedocs.org/projects/numistalib/badge/?version=latest)](https://numistalib.readthedocs.io/en/latest/?badge=latest) [![PyPI](https://img.shields.io/pypi/v/numistalib)](https://pypi.org/project/numistalib/) [![Release](https://github.com/wells01440/numistalib/actions/workflows/release.yml/badge.svg)](https://github.com/wells01440/numistalib/actions/workflows/release.yml)

Python wrapper for the Numista API with caching, rate limiting, and retry logic.

## 📖 Documentation

**[Read the Docs](https://numistalib.readthedocs.io/)** — Complete documentation with search, versioning, and offline formats.

**Quick Links:**

- [Installation](https://numistalib.readthedocs.io/en/latest/installation.html)
- [Quickstart](https://numistalib.readthedocs.io/en/latest/quickstart.html)
- [CLI Guide](https://numistalib.readthedocs.io/en/latest/cli_guide.html)
- [Python API Guide](https://numistalib.readthedocs.io/en/latest/python_api_guide.html)
- [API Reference](https://numistalib.readthedocs.io/en/latest/api/)
- [Configuration](https://numistalib.readthedocs.io/en/latest/configuration.html)
- [Architecture](https://numistalib.readthedocs.io/en/latest/architecture.html)

## Features

- **Complete API Coverage**: Search types, get details, catalogues, issuers, and more
- **HTTP Caching**: RFC 9111-compliant persistent caching with hishel
- **Rate Limiting**: Configurable rate limits to respect API quotas
- **Retry Logic**: Exponential backoff with jitter for resilient requests
- **Rich CLI**: Beautiful command-line interface with tables and colors
- **Type Safety**: Full Pydantic models with strict validation

## Installation

```bash
uv pip install -e .
```

## Configuration

1. Get your API key from [Numista API](https://en.numista.com/api/)
2. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

3. Add your API key to `.env`:

   ```bash
   NUMISTA_API_KEY=your_api_key_here
   ```

## CLI Usage

### Search for types

```bash
numistalib types search -q "dollar"
numistalib types search --issuer united-states --year 2020
```

### Get type details

```bash
numistalib types get 95420
```

### List catalogues

```bash
numistalib catalogues
```

### List issuers

```bash
numistalib issuers
numistalib issuers --lang es
```

### Configuration management

```bash
numistalib config list
numistalib config get cache_dir
```

## Python Usage

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings, logger
from numistalib.services import TypeService

settings = Settings()

with NumistaApiClient(settings, logger) as client:
    service = TypeService(client, logger)
    
    # Search for types
    results = service.search_types(query="dollar", page=1, count=10)
    for coin_type in results:
        print(f"{coin_type.numista_id}: {coin_type.title}")
    
    # Get full details
    full_type = service.get_type(95420)
    print(f"Weight: {full_type.weight}g")
    print(f"Composition: {full_type.composition}")
```

## Development

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Check code quality

```bash
uv run ruff check src/
uv run ruff format src/
uv run pyright src/
```

### Check complexity

```bash
uv run radon cc src/numistalib/ -a -nb
uv run xenon --max-absolute B src/numistalib/
```

## Architecture

- **models/**: Pydantic models for API entities
- **client.py**: HTTP client with caching, rate limiting, retry
- **services/**: Business logic for each API endpoint
- **config.py**: Settings management with Pydantic BaseSettings
- **cli/**: Click-based command-line interface

## License

MIT License - see [license.txt](license.txt)

## Contributing

## Legal & Attribution

- Unofficial: This library is an independent, community project and is not affiliated with Numista.
- Attribution: Numista is a trademark/service of Numista. Please attribute Numista when data from their API is displayed.
- Terms: Users of this library must comply with Numista’s published terms. Review:
  - Conditions of use: <https://en.numista.com/conditions.php>
  - Legal information: <https://en.numista.com/legal.php>
  - Pricing API terms: <https://en.numista.com/api/pricing.php>
- Data usage: Follow Numista’s guidelines for caching, rate limits, and redistribution. If Numista’s terms restrict retention or republication (especially for pricing), configure your deployments accordingly.
- Rate limiting: This project implements conservative rate limiting by default; always respect Numista’s limits and guidance.

See [AGENTS.md](AGENTS.md) for coding standards and guidelines.
