# Python API Guide

Complete guide to using numistalib as a Python library.

## Overview

numistalib provides a clean, type-safe Python API for accessing Numista data programmatically. All responses are validated Pydantic models with full type hints.

## Basic Usage

### Client Setup

Every interaction starts with the client:

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings

settings = Settings()  # Loads from .env

with NumistaApiClient(settings) as client:
    # Use services with this client
    pass
```

The client supports both synchronous and asynchronous operations.

---

## § 1 Types Service

Search and retrieve coin/banknote/exonumia types.

### Import

```python
from numistalib.services.types.service import TypeService
```

### Create Service

```python
service = TypeService(client)
```

### Search Types

```python
results = service.search_types(
    query="dollar",
    page=1,
    count=10,
    lang="en"
)

for coin_type in results:
    print(f"{coin_type.numista_id}: {coin_type.title}")
    print(f"  Issuer: {coin_type.issuer}")
    print(f"  Years: {coin_type.min_year}-{coin_type.max_year}")
```

**Parameters:**

- `query` (str, optional): Search keywords
- `issuer` (str, optional): Issuer code
- `category` (str, optional): "coin", "banknote", or "exonumia"
- `year` (str, optional): Year or range (e.g., "2020" or "2000-2010")
- `catalogue` (int, optional): Catalogue ID
- `number` (str, optional): Catalogue number
- `ruler` (int, optional): Ruler ID
- `material` (int, optional): Material ID
- `date` (str, optional): Date or range
- `size` (str, optional): Size in mm or range
- `weight` (str, optional): Weight in grams or range
- `page` (int): Page number (default: 1)
- `count` (int): Results per page (default: 50, max: 50)
- `lang` (str): Language code (default: "en")

**Returns:** `list[TypeBasic]`

### Get Type Details

```python
full_type = service.get_type(95420, lang="en")

print(f"Title: {full_type.title}")
print(f"Weight: {full_type.weight}g")
print(f"Diameter: {full_type.size}mm")
print(f"Composition: {full_type.composition}")
print(f"Obverse: {full_type.obverse.description}")
print(f"Reverse: {full_type.reverse.description}")
```

**Parameters:**

- `type_id` (int): Numista type ID
- `lang` (str): Language code (default: "en")

**Returns:** `TypeFull`

### Async Search (Paginated)

For large datasets, use the async paginated search:

```python
import asyncio
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

async def search_all_dollars():
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = TypeService(client)
        
        all_results = []
        async for coin_type in service.paginated_search(query="dollar"):
            all_results.append(coin_type)
            print(f"Found: {coin_type.title}")
        
        print(f"Total: {len(all_results)}")

asyncio.run(search_all_dollars())
```

---

## § 2 Catalogues Service

Access reference catalogue information.

### Import & Create

```python
from numistalib.services.catalogues.service import CataloguesService

service = CataloguesService(client)
```

### Get All Catalogues

```python
catalogues = service.get_catalogues()

for cat in catalogues:
    print(f"{cat.id}: {cat.name}")
    print(f"  Author: {cat.author}")
    print(f"  Type: {cat.type}")
```

**Returns:** `list[Catalogue]`

---

## § 3 Issuers Service

Access issuer (country/entity) information.

### Import & Create

```python
from numistalib.services.issuer.service import IssuerService

service = IssuerService(client)
```

### Get All Issuers

```python
issuers = service.get_issuers(lang="en")

for issuer in issuers:
    print(f"{issuer.code}: {issuer.name}")
    if issuer.wikidata_id:
        print(f"  Wikidata: {issuer.wikidata_id}")
```

**Parameters:**

- `lang` (str): Language code (default: "en")

**Returns:** `list[Issuer]`

---

## § 4 Issues Service

Get issue information for types.

### Import & Create

```python
from numistalib.services.issues.service import IssuesService

service = IssuesService(client)
```

### Get Type Issues

```python
issues = service.get_issues(type_id=95420, lang="en")

for issue in issues:
    print(f"Issue {issue.id}:")
    print(f"  Years: {issue.min_year}-{issue.max_year}")
    print(f"  Mintage: {issue.mintage}")
    if issue.mint:
        print(f"  Mint: {issue.mint.name}")
```

**Parameters:**

- `type_id` (int): Type ID
- `lang` (str): Language code (default: "en")

**Returns:** `list[Issue]`

---

## § 5 Mints Service

Access mint information.

### Import & Create

```python
from numistalib.services.mints.service import MintsService

service = MintsService(client)
```

### List All Mints

```python
mints = service.get_mints(lang="en")

for mint in mints:
    print(f"{mint.id}: {mint.name}")
    if mint.location:
        print(f"  Location: {mint.location}")
```

**Parameters:**

- `lang` (str): Language code (default: "en")

**Returns:** `list[Mint]`

### Get Mint Details

```python
mint = service.get_mint(mint_id=42, lang="en")

print(f"Name: {mint.name}")
print(f"Location: {mint.location}")
print(f"Period: {mint.start_year}-{mint.end_year}")
```

**Parameters:**

- `mint_id` (int): Mint ID
- `lang` (str): Language code (default: "en")

**Returns:** `Mint`

---

## § 6 Collections Service

Manage user collections (requires OAuth).

### Import & Create

```python
from numistalib.services.collections.service import CollectionsService

service = CollectionsService(client)
```

### List User Collections

```python
collections = service.get_collections(user_id=12345)

for collection in collections:
    print(f"{collection.id}: {collection.name}")
    print(f"  Items: {collection.count}")
```

**Parameters:**

- `user_id` (int): User ID

**Returns:** `list[Collection]`

### Get Collection Items

```python
items = service.get_collected_items(
    user_id=12345,
    category="coin",
    collection_id=67890
)

for item in items:
    print(f"Type {item.type}:")
    print(f"  Quantity: {item.quantity}")
    print(f"  Grade: {item.grade}")
```

**Parameters:**

- `user_id` (int): User ID
- `category` (str, optional): Filter by category
- `type_id` (int, optional): Filter by type
- `collection_id` (int, optional): Filter by collection

**Returns:** `list[CollectionItem]`

---

## § 7 Image Search Service

Search using coin images.

### Import & Create

```python
from numistalib.services.image_search.service import ImageSearchService

service = ImageSearchService(client)
```

### Search by Image

```python
from pathlib import Path

image_path = Path("/path/to/coin.jpg")

results = service.search_by_image(
    image_path=image_path,
    category="coin",
    max_results=20,
    experimental=False,
    lang="en"
)

for result in results:
    print(f"Type {result.type_id}: {result.title}")
    print(f"  Confidence: {result.score}")
```

**Parameters:**

- `image_path` (Path): Path to image file
- `category` (str, optional): "coin", "banknote", or "exonumia"
- `max_results` (int): Maximum results (default: 100, max: 100)
- `experimental` (bool): Enable experimental features (default: False)
- `lang` (str): Language code (default: "en")

**Returns:** `list[ImageSearchResult]`

---

## § 8 Literature Service

Get publication information.

### Import & Create

```python
from numistalib.services.literature.service import LiteratureService

service = LiteratureService(client)
```

### Get Publication

```python
pub = service.get_publication("L123456")

print(f"Title: {pub.title}")
print(f"Author: {pub.author}")
print(f"Year: {pub.year}")
print(f"Type: {pub.type}")
```

**Parameters:**

- `publication_id` (str): Publication ID (e.g., "L123456")

**Returns:** `Publication`

---

## § 9 Prices Service

Get price estimates for issues.

### Import & Create

```python
from numistalib.services.prices.service import PricesService

service = PricesService(client)
```

### Get Price Estimates

```python
prices = service.get_prices(
    type_id=95420,
    issue_id=1,
    currency="USD",
    lang="en"
)

for grade, price in prices.items():
    print(f"{grade}: ${price}")
```

**Parameters:**

- `type_id` (int): Type ID
- `issue_id` (int): Issue ID
- `currency` (str): ISO 4217 currency code (default: "EUR")
- `lang` (str): Language code (default: "en")

**Returns:** `dict[str, float]`

---

## § 10 Users Service

Get user profile information.

### Import & Create

```python
from numistalib.services.users.service import UsersService

service = UsersService(client)
```

### Get User Profile

```python
user = service.get_user(user_id=12345, lang="en")

print(f"Username: {user.username}")
print(f"Member since: {user.member_since}")
print(f"Collection: {user.collection_count} items")
```

**Parameters:**

- `user_id` (int): User ID
- `lang` (str): Language code (default: "en")

**Returns:** `User`

---

## § 11 Async Usage

All services support async operations with `_async` methods:

```python
import asyncio
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

async def main():
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = TypeService(client)
        
        # Async get
        coin_type = await service.get_type_async(95420)
        print(f"Title: {coin_type.title}")
        
        # Async search with pagination
        async for result in service.paginated_search(query="dollar"):
            print(f"Found: {result.title}")

asyncio.run(main())
```

---

## § 12 Working with Models

All responses are Pydantic models with full validation.

### Accessing Fields

```python
coin_type = service.get_type(95420)

# Direct access
print(coin_type.title)
print(coin_type.weight)

# Optional fields (may be None)
if coin_type.obverse:
    print(coin_type.obverse.description)

# Nested models
if coin_type.mints:
    for mint in coin_type.mints:
        print(mint.name)
```

### Model Serialization

```python
# To dict
data = coin_type.model_dump()

# To JSON
json_str = coin_type.model_dump_json()

# From dict
from numistalib.models.types import TypeFull
coin_type = TypeFull(**data)
```

---

## § 13 Cache Awareness

Check if a response was cached:

```python
from numistalib.client import NumistaResponse

response = service.get_type(95420)

# Access via service's last response (if exposed)
# Or use client directly:
raw_response = client.get("/types/95420")
if isinstance(raw_response, NumistaResponse):
    if raw_response.cached:
        print("💾 Served from cache")
    else:
        print("🌐 Fresh from API")
```

---

## § 14 Error Handling

```python
from numistalib.models.errors import NumistaError

try:
    coin_type = service.get_type(99999999)
except NumistaError as e:
    print(f"Error: {e}")
    print(f"Status code: {e.status_code}")
```

---

## Complete Example

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.types.service import TypeService
from numistalib.services.issues.service import IssuesService
from numistalib.services.prices.service import PricesService

settings = Settings()

with NumistaApiClient(settings) as client:
    # Search for types
    types_service = TypeService(client)
    results = types_service.search_types(
        query="commemorative",
        issuer="france",
        year="2010-2020",
        count=5
    )
    
    # Process each type
    for coin_type in results:
        print(f"\n{coin_type.title}")
        print(f"ID: {coin_type.numista_id}")
        
        # Get full details
        full = types_service.get_type(coin_type.numista_id)
        print(f"Weight: {full.weight}g")
        print(f"Composition: {full.composition}")
        
        # Get issues
        issues_service = IssuesService(client)
        issues = issues_service.get_issues(coin_type.numista_id)
        print(f"Issues: {len(issues)}")
        
        # Get prices for first issue
        if issues:
            prices_service = PricesService(client)
            prices = prices_service.get_prices(
                coin_type.numista_id,
                issues[0].id,
                currency="EUR"
            )
            print(f"Prices: {prices}")
```

---

## Next Steps

- [Advanced Usage](advanced_usage.md) - Complex scenarios
- [Configuration](configuration.md) - Customize behavior
- [API Reference](api/services.rst) - Full API documentation
