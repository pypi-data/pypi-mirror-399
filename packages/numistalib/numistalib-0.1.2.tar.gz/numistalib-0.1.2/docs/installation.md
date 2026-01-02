# Installation

## Requirements

- Python 3.13 or higher
- `uv` package manager (recommended)

## Installing uv

If you don't have `uv` installed, install it first:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installing numistalib

### From Source (Recommended for Development)

1. Clone the repository:

```bash
git clone https://github.com/wells01440/numistalib.git
cd numistalib
```

1. Install dependencies:

```bash
uv sync
```

1. Install in editable mode:

```bash
uv pip install -e .
```

### From PyPI (Future)

Once published to PyPI:

```bash
uv pip install numistalib
```

## Configuration

### API Key Setup

1. Get your API key from [Numista API](https://en.numista.com/api/)

2. Create a `.env` file in your project root:

```bash
cp .env.example .env
```

1. Add your API key to `.env`:

```bash
NUMISTA_API_KEY=your_api_key_here
```

### Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `NUMISTA_API_KEY` | *required* | Your Numista API key |
| `NUMISTA_BASE_URL` | `https://api.numista.com/v3` | Base API URL |
| `CACHE_DIR` | `.numista_cache` | Directory for HTTP cache |
| `CACHE_TTL_SECONDS` | `604800` (7 days) | Cache time-to-live |
| `RATE_LIMIT` | `45` | Requests per minute |
| `RATE_LIMIT_WINDOW` | `60` | Time window in seconds |

### Cache Directory

By default, numistalib creates a `.numista_cache` directory in your current working directory for persistent HTTP caching. You can customize this:

```bash
export CACHE_DIR=/path/to/custom/cache
```

## Verification

Verify your installation:

```bash
# Check CLI is installed
numistalib --version

# Test API connection
numistalib config list
```

## Next Steps

- [Quickstart Guide](quickstart.md) - Get started quickly
- [CLI Guide](cli_guide.md) - Learn CLI commands
- [Python API Guide](python_api_guide.md) - Use the library in your code
