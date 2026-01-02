# Advanced Usage

Advanced techniques and patterns for using numistalib.

## § 1 Async Operations

### Concurrent Requests

Make multiple requests concurrently:

```python
import asyncio
from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.services.types.service import TypeService

async def get_multiple_types(type_ids: list[int]):
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = TypeService(client)
        
        # Fetch all types concurrently
        tasks = [service.get_type_async(type_id) for type_id in type_ids]
        results = await asyncio.gather(*tasks)
        
        return results

# Usage
type_ids = [95420, 95421, 95422]
results = asyncio.run(get_multiple_types(type_ids))

for coin_type in results:
    print(f"{coin_type.title}: {coin_type.weight}g")
```

### Paginated Search with Processing

Process results as they arrive:

```python
import asyncio
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

async def process_all_french_coins():
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = TypeService(client)
        
        count = 0
        async for coin_type in service.paginated_search(
            issuer="france",
            category="coin"
        ):
            count += 1
            
            # Process each result
            print(f"{count}. {coin_type.title} ({coin_type.min_year})")
            
            # Could also fetch details asynchronously
            # details = await service.get_type_async(coin_type.numista_id)
        
        print(f"\nTotal: {count} coins")

asyncio.run(process_all_french_coins())
```

---

## § 2 Batch Operations

### Bulk Data Collection

Collect data for multiple entities:

```python
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService
from numistalib.services.issues.service import IssuesService
from numistalib.services.prices.service import PricesService

def collect_complete_dataset(type_ids: list[int]):
    settings = Settings()
    dataset = []
    
    with NumistaApiClient(settings) as client:
        types_service = TypeService(client)
        issues_service = IssuesService(client)
        prices_service = PricesService(client)
        
        for type_id in type_ids:
            # Get type
            coin_type = types_service.get_type(type_id)
            
            # Get issues
            issues = issues_service.get_issues(type_id)
            
            # Get prices for each issue
            prices_data = []
            for issue in issues:
                prices = prices_service.get_prices(
                    type_id,
                    issue.id,
                    currency="USD"
                )
                prices_data.append({
                    "issue_id": issue.id,
                    "prices": prices
                })
            
            dataset.append({
                "type": coin_type,
                "issues": issues,
                "prices": prices_data
            })
    
    return dataset

# Collect data for specific types
type_ids = [95420, 95421, 95422]
data = collect_complete_dataset(type_ids)
```

---

## § 3 Custom Caching Strategies

### Per-Query Cache Invalidation

Selectively invalidate cache entries:

```python
from pathlib import Path
import shutil
from numistalib.config import Settings

def clear_cache_for_type(type_id: int):
    """Clear cached data for a specific type."""
    settings = Settings()
    cache_dir = Path(settings.cache_dir)
    
    # Cache keys follow a pattern
    # This is implementation-specific and may change
    pattern = f"*type*{type_id}*"
    
    for cache_file in cache_dir.glob(pattern):
        cache_file.unlink()
        print(f"Cleared: {cache_file}")

# Usage
clear_cache_for_type(95420)
```

### Cache Warming

Pre-populate cache for commonly accessed data:

```python
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

def warm_cache(type_ids: list[int]):
    """Pre-fetch and cache type data."""
    settings = Settings()
    
    with NumistaApiClient(settings) as client:
        service = TypeService(client)
        
        for type_id in type_ids:
            coin_type = service.get_type(type_id)
            print(f"Cached: {coin_type.title}")

# Warm cache for popular types
popular_types = [95420, 95421, 95422, 95423]
warm_cache(popular_types)
```

---

## § 4 Error Handling Patterns

### Retry with Custom Logic

Implement custom retry behavior:

```python
import time
from numistalib.client import NumistaApiClient
from numistalib.models.errors import NumistaError

def get_type_with_retry(type_id: int, max_attempts: int = 5):
    """Get type with custom retry logic."""
    settings = Settings()
    
    for attempt in range(max_attempts):
        try:
            with NumistaApiClient(settings) as client:
                service = TypeService(client)
                return service.get_type(type_id)
        
        except NumistaError as e:
            if e.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.status_code >= 500:  # Server error
                print(f"Server error. Attempt {attempt + 1}/{max_attempts}")
                time.sleep(1)
            else:
                raise  # Don't retry client errors
    
    raise NumistaError("Max retries exceeded")
```

### Graceful Degradation

Handle missing data gracefully:

```python
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService
from numistalib.models.errors import NumistaError

def get_type_safe(type_id: int):
    """Get type with safe fallbacks."""
    settings = Settings()
    
    try:
        with NumistaApiClient(settings) as client:
            service = TypeService(client)
            coin_type = service.get_type(type_id)
            
            return {
                "id": coin_type.numista_id,
                "title": coin_type.title or "Unknown",
                "weight": coin_type.weight or 0.0,
                "composition": coin_type.composition or "Unknown",
                "issuer": coin_type.issuer or "Unknown",
            }
    
    except NumistaError as e:
        print(f"Error fetching type {type_id}: {e}")
        return {
            "id": type_id,
            "title": "Error loading data",
            "error": str(e)
        }
```

---

## § 5 Data Processing

### Export to CSV

Export search results to CSV:

```python
import csv
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

def export_search_to_csv(query: str, output_file: str):
    """Export search results to CSV."""
    settings = Settings()
    
    with NumistaApiClient(settings) as client:
        service = TypeService(client)
        results = service.search_types(query=query, count=50)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'title', 'issuer', 'min_year', 'max_year', 'category'
            ])
            writer.writeheader()
            
            for coin_type in results:
                writer.writerow({
                    'id': coin_type.numista_id,
                    'title': coin_type.title,
                    'issuer': coin_type.issuer,
                    'min_year': coin_type.min_year,
                    'max_year': coin_type.max_year,
                    'category': coin_type.category
                })
    
    print(f"Exported {len(results)} results to {output_file}")

# Usage
export_search_to_csv("dollar", "dollar_coins.csv")
```

### Export to JSON

Export complete type data:

```python
import json
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

def export_type_to_json(type_id: int, output_file: str):
    """Export complete type data to JSON."""
    settings = Settings()
    
    with NumistaApiClient(settings) as client:
        service = TypeService(client)
        coin_type = service.get_type(type_id)
        
        # Convert to dict (Pydantic model)
        data = coin_type.model_dump()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported type {type_id} to {output_file}")

# Usage
export_type_to_json(95420, "type_95420.json")
```

---

## § 6 Collection Management

### Bulk Add to Collection

Add multiple items to a collection:

```python
import asyncio
from numistalib.client import NumistaApiClient
from numistalib.services.collections.service import CollectionsService

async def bulk_add_to_collection(
    user_id: int,
    type_ids: list[int],
    collection_id: int
):
    """Add multiple types to a collection."""
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = CollectionsService(client)
        
        for type_id in type_ids:
            await service.add_collected_item_async(
                user_id=user_id,
                type_id=type_id,
                collection_id=collection_id,
                quantity=1
            )
            print(f"Added type {type_id}")

# Usage
type_ids = [95420, 95421, 95422]
asyncio.run(bulk_add_to_collection(
    user_id=12345,
    type_ids=type_ids,
    collection_id=67890
))
```

### Collection Statistics

Analyze your collection:

```python
from collections import Counter
from numistalib.client import NumistaApiClient
from numistalib.services.collections.service import CollectionsService

def analyze_collection(user_id: int):
    """Analyze collection statistics."""
    settings = Settings()
    
    with NumistaApiClient(settings) as client:
        service = CollectionsService(client)
        items = service.get_collected_items(user_id)
        
        # Statistics
        total_items = len(items)
        total_quantity = sum(item.quantity for item in items)
        
        # By grade
        grades = Counter(item.grade for item in items if item.grade)
        
        # By category
        categories = Counter(item.category for item in items if item.category)
        
        print(f"Collection Statistics for User {user_id}")
        print(f"Total unique items: {total_items}")
        print(f"Total quantity: {total_quantity}")
        print(f"\nBy Grade:")
        for grade, count in grades.most_common():
            print(f"  {grade}: {count}")
        print(f"\nBy Category:")
        for category, count in categories.most_common():
            print(f"  {category}: {count}")

# Usage
analyze_collection(12345)
```

---

## § 7 Image Search Optimization

### Batch Image Search

Search multiple images:

```python
import asyncio
from pathlib import Path
from numistalib.client import NumistaApiClient
from numistalib.services.image_search.service import ImageSearchService

async def batch_image_search(image_paths: list[Path]):
    """Search multiple images concurrently."""
    settings = Settings()
    
    async with NumistaApiClient(settings) as client:
        service = ImageSearchService(client)
        
        tasks = [
            service.search_by_image_async(path)
            for path in image_paths
        ]
        
        results = await asyncio.gather(*tasks)
        
        for path, matches in zip(image_paths, results):
            print(f"\n{path.name}:")
            for match in matches[:3]:  # Top 3
                print(f"  {match.title} (score: {match.score})")

# Usage
images = [
    Path("coin1.jpg"),
    Path("coin2.jpg"),
    Path("coin3.jpg")
]
asyncio.run(batch_image_search(images))
```

---

## § 8 Rate Limit Management

### Dynamic Rate Limiting

Adjust rate limits based on response headers:

```python
from numistalib.client import NumistaApiClient
from numistalib.config import Settings

class AdaptiveClient:
    """Client with adaptive rate limiting."""
    
    def __init__(self):
        self.settings = Settings()
        self.current_limit = self.settings.rate_limit
    
    def search_types(self, **kwargs):
        """Search with adaptive rate limiting."""
        with NumistaApiClient(self.settings) as client:
            service = TypeService(client)
            
            try:
                results = service.search_types(**kwargs)
                return results
            
            except Exception as e:
                if "429" in str(e):  # Rate limit error
                    # Reduce rate limit
                    self.current_limit = max(10, self.current_limit - 5)
                    self.settings = Settings(rate_limit=self.current_limit)
                    print(f"Reduced rate limit to {self.current_limit}")
                raise

# Usage
client = AdaptiveClient()
results = client.search_types(query="dollar")
```

---

## § 9 Testing Patterns

### Mock Responses

Test code using numistalib:

```python
from unittest.mock import Mock, patch
from numistalib.models.types import TypeBasic

def test_my_function():
    """Test function that uses numistalib."""
    
    # Create mock type
    mock_type = TypeBasic(
        numista_id=95420,
        title="Test Coin",
        issuer="france",
        min_year=2020,
        max_year=2020,
        category="coin"
    )
    
    # Mock service
    with patch('numistalib.services.types.service.TypeService') as MockService:
        mock_service = MockService.return_value
        mock_service.search_types.return_value = [mock_type]
        
        # Test your code
        results = mock_service.search_types(query="test")
        assert len(results) == 1
        assert results[0].title == "Test Coin"
```

---

## § 10 Performance Optimization

### Connection Pooling

Reuse client connections:

```python
from numistalib.client import NumistaApiClient
from numistalib.services.types.service import TypeService

class CoinDatabase:
    """Persistent client for batch operations."""
    
    def __init__(self):
        self.settings = Settings()
        self.client = None
    
    def __enter__(self):
        self.client = NumistaApiClient(self.settings)
        self.client.__enter__()
        return self
    
    def __exit__(self, *args):
        if self.client:
            self.client.__exit__(*args)
    
    def get_type(self, type_id: int):
        service = TypeService(self.client)
        return service.get_type(type_id)
    
    def search(self, **kwargs):
        service = TypeService(self.client)
        return service.search_types(**kwargs)

# Usage - single client for multiple operations
with CoinDatabase() as db:
    # Reuses connection
    results1 = db.search(query="dollar")
    results2 = db.search(query="euro")
    type1 = db.get_type(95420)
    type2 = db.get_type(95421)
```

---

## Next Steps

- [API Reference](api/services.rst) - Full API documentation
- [Contributing](contributing.md) - Contribute to numistalib
- [Architecture](architecture.md) - Understand internals
