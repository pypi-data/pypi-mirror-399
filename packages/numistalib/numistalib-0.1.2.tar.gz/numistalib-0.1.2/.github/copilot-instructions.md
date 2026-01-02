# numistalib Copilot Instructions

## Project Overview

Numista API (Swagger v3 [official docs](https://en.numista.com/api/doc/index.php)) Python wrapper with sync/async support, persistent HTTP caching (hishel SQLite 7d TTL), rate limiting (45/min), retry (exp backoff+jitter).

## Core Architecture

- **[client.py](src/numistalib/client.py)**: Central HTTP (httpx+hishel/pyrate-limiter). Inject to services. NumistaResponse exposes `cached` bool, `cached_indicator` 💾/🌐.
- **services/<tag>/**: One per API tag. [`services/<tag>/base.py`](src/numistalib/services/catalogues/base.py) ABC → `service.py` impl. Inherit [`services/base/service.py`](src/numistalib/services/base/service.py) BaseService(client). Impl abstract `to_models(raw_list → [Pydantic])`.
  - Subclasses: SimpleListService (e.g. /catalogues → {"catalogues": [...]}) extracts via CLASS_ITEMS_KEY.
  - NestedResourceService/EntityService for paths like /types/{id}/issues.
- **models/<entity>.py**: Pydantic from [`models/base/base_model.py`](src/numistalib/models/base/base_model.py). Validate API payloads immediately.
- **cli/<tag>.py**: Click cmds registered in [`cli/main.py`](src/numistalib/cli/main.py). Rich tables/panels (v14 theme, consistent width). Services headless; CLI owns all I/O, no prompts w/o flags.
- Data flow: CLI/Python → Service(client) → client.get/post → Pydantic → Rich/return.

## Coding Standards (from [AGENTS.md](AGENTS.md))

- **Tooling**: `uv` only (`uv sync`, `uv run ruff/mypy/pyright/pytest`).
- **Naming**: snake_case vars/fns/modules; PascalCase classes (\*Service); UPPER_SNAKE_CASE consts; full words; plural collections; files=nouns; `base/` not `_base`.
- **Imports**: Post-docstring, stdlib → 3rd → local; absolute; one-per-from [`examples`](AGENTS.md#314).
- **Types**: Full hints everywhere; discourage Any; mypy/pyright strict.
- **No**: print(); ad-hoc clients; untyped payloads; cyclomatic>8 (radon); cognitive>10B (xenon).
- **Yes**: Chained exceptions (`raise X from err`); module loggers; NumPy public docs; context mgrs; DRY via ABCs/abstractmethods.

## Developer Workflows

- **Lint/Fix**: `uv run ruff check --fix src/`
- **Types**: `uv run pyright src/` `uv run mypy --strict .`
- **Complexity**: `uv run radon cc src/numistalib/ -a -nb` `uv run xenon --max-absolute B src/numistalib/`
- **Test**: `uv run pytest tests/ -v` (mocks network; isolate cache dirs)
- **CLI**: `numistalib types search -q "dollar"` (short/long opts, --help)
- **Python**: `from numistalib.services.types.service import TypeService; with NumistaApiClient(settings) as client: service=TypeService(client); service.search_types(q="dollar")`

## Patterns to Follow

- Services stateless except client/logger; no I/O.
- Params: `_build_params(base, **opt)` excludes None.
- Pagination: Async generators yield lazily; params internal.
- Cache: All GET cached; no bypass flags yet.
- Errors: Central in client retry; services validate/raise typed.

Reference [AGENTS.md](AGENTS.md) (§ refs) for full rules. Re-read after changes.
