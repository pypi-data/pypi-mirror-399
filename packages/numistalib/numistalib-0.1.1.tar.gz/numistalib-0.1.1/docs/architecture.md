# Architecture

Understanding numistalib's internal architecture.

## § 1 Overview

numistalib follows a layered architecture:

```
┌─────────────────────────────────┐
│         CLI Layer               │  Rich UI, Click commands
├─────────────────────────────────┤
│      Services Layer             │  Business logic per API tag
├─────────────────────────────────┤
│       Client Layer              │  HTTP, caching, rate limiting
├─────────────────────────────────┤
│       Models Layer              │  Pydantic validation
├─────────────────────────────────┤
│      Transport Layer            │  httpx + hishel + pyrate-limiter
└─────────────────────────────────┘
```

---

## § 2 Core Components

### § 2.1 Client (`client.py`)

Central HTTP abstraction providing:

- **Sync/Async Support**: Both `httpx.Client` and `httpx.AsyncClient`
- **Caching**: RFC 9111-compliant via hishel with SQLite backend
- **Rate Limiting**: 45 requests/minute default via pyrate-limiter
- **Retry Logic**: Exponential backoff with jitter via tenacity
- **Response Wrapping**: `NumistaResponse` with cache indicator

**Key Classes:**

- `NumistaApiClient`: Main client (sync)
- `NumistaResponse`: Wrapper exposing `cached` boolean
- Cache strategy: 7-day TTL, persistent SQLite storage

**Design Principles:**

- Single responsibility: HTTP concerns only
- Stateful: Manages connection pool, cache, rate limiter
- Injectable: Services receive client instance
- Context manager: Proper resource cleanup

### § 2.2 Services (`services/`)

One service per Swagger tag, implementing business logic.

**Structure:**

```
services/
├── base/
│   ├── service.py       # BaseService ABC
│   └── helpers.py       # Shared utilities
├── types/
│   ├── base.py          # TypeServiceBase ABC
│   └── service.py       # TypeService implementation
├── catalogues/
│   ├── base.py
│   └── service.py
└── ...
```

**Base Classes:**

- `BaseService`: Foundation for all services
  - Requires `to_models()` abstract method
  - Provides `client` and `logger` injection
  
- `SimpleListService`: For endpoints returning `{"key": [...]}`
  - Auto-extracts via `CLASS_ITEMS_KEY`
  - Example: `/catalogues` → `{"catalogues": [...]}`

- `NestedResourceService`: For paths like `/types/{id}/issues`
  - Handles resource nesting
  
- `EntityService`: For single-entity endpoints like `/types/{id}`

**Design Principles:**

- One service per API tag
- Stateless except injected client/logger
- No I/O beyond client calls
- Immediate validation to Pydantic models
- Abstract base defines contract
- Sync and async methods paired

### § 2.3 Models (`models/`)

Pydantic models validating API payloads immediately upon receipt.

**Structure:**

```
models/
├── base/
│   └── base_model.py    # BaseModel foundation
├── types.py             # Type-related models
├── catalogues.py
├── issuer.py
└── ...
```

**Key Models:**

- `TypeBasic`: Search result representation
- `TypeFull`: Complete type details
- `Issue`: Issue information
- `Catalogue`: Reference catalogue
- `Issuer`: Country/entity issuing coins

**Features:**

- Strict validation
- Optional field handling
- Rich rendering methods (`as_table()`, `format_fields()`)
- Serialization (`model_dump()`, `model_dump_json()`)

**Design Principles:**

- Models own presentation logic
- One file per entity domain
- Inherit from `BaseModel`
- Full type hints
- NumPy-style docstrings for public APIs

### § 2.4 CLI (`cli/`)

Rich command-line interface with consistent UX.

**Structure:**

```
cli/
├── main.py          # Entry point, command registration
├── theme.py         # Rich v14 theming
├── types.py         # Types commands
├── catalogues.py
└── ...
```

**Patterns:**

- One file per command group
- Registration function: `register_<group>_commands(cli)`
- Services are headless; CLI owns all I/O
- Consistent panel/table formatting
- Cache indicators (💾/🌐)
- Short/long option flags (`-q`/`--query`)

**Design Principles:**

- CLI contains all user interaction
- Services provide data only
- No prompts without flags
- Consistent Rich theming
- Error handling with rich.console
- Model-driven rendering (call `Model.as_table()`)

### § 2.5 Configuration (`config.py`)

Pydantic Settings for environment-based configuration.

**Features:**

- `.env` file loading
- Environment variable overrides
- Validation
- Type hints
- Defaults

**Settings:**

- API key (required)
- Base URL
- Cache directory & TTL
- Rate limits
- Retry settings
- Log level

---

## § 3 Data Flow

### § 3.1 Typical Request

```
User/Python Code
     │
     ├─> CLI Command / Service Method
     │
     ├─> Service
     │   │
     │   ├─> Build parameters
     │   ├─> Call client.get()
     │   │
     │   └─> Client
     │       │
     │       ├─> Check rate limit (pyrate-limiter)
     │       ├─> Check cache (hishel SQLite)
     │       ├─> Make HTTP request (httpx)
     │       ├─> Retry on failure (tenacity)
     │       └─> Return NumistaResponse
     │
     ├─> Service validates to Pydantic models
     │
     └─> Return typed data
```

### § 3.2 Search with Pagination (Async)

```
User Code
     │
     ├─> async for item in service.paginated_search()
     │
     ├─> Service (async generator)
     │   │
     │   ├─> page = 1
     │   │
     │   └─> while True:
     │       │
     │       ├─> results = await client.get(page=page)
     │       ├─> validate to models
     │       ├─> yield each item
     │       ├─> page += 1
     │       └─> break if no more results
     │
     └─> Process items as they arrive
```

---

## § 4 Caching Strategy

### § 4.1 Implementation

- **Library**: hishel (RFC 9111-compliant)
- **Storage**: SQLite (persistent across runs)
- **Location**: `.numista_cache/` (configurable)
- **TTL**: 7 days default (configurable)
- **Scope**: All GET requests

### § 4.2 Cache Key

Based on:

- Full URL (including query parameters)
- Request headers (API key hashed)

### § 4.3 Cache Indicators

Every `NumistaResponse` exposes:

- `cached` (bool): True if served from cache
- `cached_indicator` (str): "💾" if cached, "🌐" if fresh

CLI displays indicator alongside results.

### § 4.4 Invalidation

- Automatic: After TTL expires
- Manual: Delete cache directory or specific files

---

## § 5 Rate Limiting

### § 5.1 Implementation

- **Library**: pyrate-limiter
- **Strategy**: Sliding window
- **Default**: 45 requests per 60 seconds
- **Scope**: Per-client instance

### § 5.2 Behavior

- Blocks request if limit exceeded
- Waits until window resets
- Transparent to caller

### § 5.3 Configuration

```python
settings = Settings(
    rate_limit=30,         # 30 requests
    rate_limit_window=60   # per 60 seconds
)
```

---

## § 6 Retry Logic

### § 6.1 Implementation

- **Library**: tenacity
- **Strategy**: Exponential backoff with jitter
- **Max Attempts**: 3 (configurable)
- **Backoff Factor**: 2.0 (configurable)

### § 6.2 Retry Conditions

- Network errors (connection timeout, etc.)
- HTTP 5xx errors
- HTTP 429 (rate limit) after wait

### § 6.3 Non-Retry Conditions

- HTTP 4xx (except 429)
- Validation errors
- API key errors

---

## § 7 Error Handling

### § 7.1 Error Hierarchy

```
NumistaError (base)
├── AuthenticationError (401)
├── NotFoundError (404)
├── RateLimitError (429)
├── ValidationError (Pydantic)
└── NetworkError (connection issues)
```

### § 7.2 Error Flow

```
Client detects error
     │
     ├─> HTTP error?
     │   ├─> 401 → AuthenticationError
     │   ├─> 404 → NotFoundError
     │   ├─> 429 → RateLimitError (retry)
     │   └─> 5xx → NetworkError (retry)
     │
     ├─> Network error?
     │   └─> NetworkError (retry)
     │
     ├─> Validation error?
     │   └─> ValidationError
     │
     └─> Propagate to caller
```

### § 7.3 Chaining

All exceptions use `raise X from err` to preserve causality.

---

## § 8 Dependency Injection

### § 8.1 Pattern

Services receive dependencies via constructor:

```python
class TypeService:
    def __init__(self, client: NumistaApiClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
```

### § 8.2 Benefits

- Testability: Mock client easily
- Flexibility: Swap client implementations
- Explicit dependencies: No hidden globals

### § 8.3 Usage

```python
with NumistaApiClient(settings) as client:
    service = TypeService(client)
    results = service.search_types(query="dollar")
```

---

## § 9 Async/Sync Parity

### § 9.1 Implementation

- Shared service class
- Paired methods: `get_type()` and `get_type_async()`
- Client supports both `httpx.Client` and `httpx.AsyncClient`

### § 9.2 Method Naming

- Sync: `get_type()`
- Async: `get_type_async()`

### § 9.3 Usage

Sync:

```python
with NumistaApiClient(settings) as client:
    service = TypeService(client)
    result = service.get_type(95420)
```

Async:

```python
async with NumistaApiClient(settings) as client:
    service = TypeService(client)
    result = await service.get_type_async(95420)
```

---

## § 10 Model-Driven Rendering

### § 10.1 Philosophy

Models own their presentation logic.

### § 10.2 Methods

Each model implements:

- `as_table(items, title)`: Class method returning Rich Table
- `format_fields(fields)`: Class method formatting field values

### § 10.3 CLI Integration

CLI calls model methods:

```python
# CLI layer
types = service.search_types(query="dollar")

# Model renders
from numistalib.models.types import TypeBasic
table = TypeBasic.as_table(types, "Search Results")

# CLI displays
console.print(table)
```

No rendering logic in CLI; it orchestrates only.

---

## § 11 Testing Strategy

### § 11.1 Approach

- Mock network calls
- Isolate cache directories
- Test models, services, CLI separately

### § 11.2 Structure

```
tests/
├── test_models.py            # Model validation
├── test_rich_renderables.py  # Rendering tests
└── integration/              # Full workflow tests
    ├── test_cli_types_read.py
    └── ...
```

### § 11.3 Patterns

- Use `pytest` fixtures for client/service setup
- Mock HTTP responses at client layer
- Validate Pydantic models with sample data
- Integration tests use real cache (isolated)

---

## § 12 Design Principles Summary

### § 12.1 DRY (Don't Repeat Yourself)

- ABC patterns for service hierarchy
- Shared base models
- Centralized HTTP logic in client

### § 12.2 Single Responsibility

- Client: HTTP concerns only
- Services: Business logic per API tag
- Models: Data validation and representation
- CLI: User interaction only

### § 12.3 Dependency Injection

- Services receive client
- No ad-hoc client instantiation
- Testable and flexible

### § 12.4 Type Safety

- Full type hints everywhere
- Pydantic validation
- mypy/pyright strict mode

### § 12.5 Separation of Concerns

- CLI owns I/O
- Services provide data
- Models validate and present
- Client handles transport

---

## § 13 Extension Points

### § 13.1 Adding a Service

0. Create `services/<tag>/` directory
1. Define ABC in `base.py`
2. Implement in `service.py`
3. Create models in `models/<tag>.py`
4. Register CLI in `cli/<tag>.py`

### § 13.2 Custom Cache Backend

Extend hishel storage:

```python
from hishel import Storage

class CustomStorage(Storage):
    # Implement storage interface
    pass

# Use in client
storage = CustomStorage()
client = NumistaApiClient(settings, storage=storage)
```

### § 13.3 Custom Rate Limiter

Replace pyrate-limiter:

```python
from pyrate_limiter import Limiter

class CustomLimiter(Limiter):
    # Implement limiter interface
    pass

# Use in client
limiter = CustomLimiter()
client = NumistaApiClient(settings, limiter=limiter)
```

---

## Next Steps

- [Contributing](contributing.md) - Contribute to numistalib
- [API Reference](api/services.rst) - Full API documentation
