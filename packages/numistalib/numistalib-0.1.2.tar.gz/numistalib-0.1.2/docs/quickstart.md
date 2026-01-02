# Quickstart Guide

This guide will get you up and running with numistalib in 5 minutes.

## Prerequisites

Before starting, ensure you have:

0. Python 3.13+ installed
1. Completed the [installation](installation.md) steps
2. A valid Numista API key in your `.env` file

## Your First Commands

### Search for Coins

Search for coins using keywords:

```bash
numistalib types search -q "dollar"
```

This returns a table with:

- Type ID
- Title
- Issuer
- Year range
- Category
- Cache indicator (💾 = cached, 🌐 = fresh)

### Filter by Country

Search for coins from a specific issuer:

```bash
numistalib types search --issuer united-states --year 2020
```

### Get Detailed Information

Get full details about a specific coin type:

```bash
numistalib types get 95420
```

This displays:

- Physical specifications (weight, size, composition)
- Descriptions of obverse, reverse, and edge
- Mints
- Related types
- References

### List Reference Catalogues

See all available coin catalogues:

```bash
numistalib catalogues
```

### List Issuers

View all issuing countries/entities:

```bash
numistalib issuers
```

With language support:

```bash
numistalib issuers --lang es
```

## Python API Usage

### Basic Search

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.types.service import TypeService

settings = Settings()

with NumistaApiClient(settings) as client:
    service = TypeService(client)
    
    # Search for types
    results = service.search_types(query="dollar", page=1, count=10)
    
    for coin_type in results:
        print(f"{coin_type.numista_id}: {coin_type.title}")
        print(f"  Issuer: {coin_type.issuer}")
        print(f"  Years: {coin_type.min_year}-{coin_type.max_year}")
```

### Get Full Details

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.types.service import TypeService

settings = Settings()

with NumistaApiClient(settings) as client:
    service = TypeService(client)
    
    # Get full type details
    full_type = service.get_type(95420)
    
    print(f"Title: {full_type.title}")
    print(f"Weight: {full_type.weight}g")
    print(f"Composition: {full_type.composition}")
    print(f"Obverse: {full_type.obverse.description}")
```

### Search with Multiple Filters

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.types.service import TypeService

settings = Settings()

with NumistaApiClient(settings) as client:
    service = TypeService(client)
    
    # Advanced search
    results = service.search_types(
        query="commemorative",
        issuer="france",
        year="2000-2010",
        category="coin",
        page=1,
        count=20
    )
    
    for coin_type in results:
        print(f"{coin_type.title} ({coin_type.min_year})")
```

### Using Catalogues

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.catalogues.service import CataloguesService

settings = Settings()

with NumistaApiClient(settings) as client:
    service = CataloguesService(client)
    
    # Get all catalogues
    catalogues = service.get_catalogues()
    
    for cat in catalogues:
        print(f"{cat.name} - {cat.author}")
```

## Understanding Cache Indicators

numistalib uses persistent HTTP caching. When you see:

- 💾 **Cached**: Response served from local cache (fast, no API quota used)
- 🌐 **Fresh**: Response fetched from Numista API (counts against quota)

The default cache TTL is 7 days. Cached responses are served instantly and don't consume your API quota.

## Next Steps

Now that you've tried the basics:

- Explore all [CLI commands](cli_guide.md)
- Learn the [Python API](python_api_guide.md) in depth
- Configure [advanced settings](configuration.md)
- Read about [architecture](architecture.md)
