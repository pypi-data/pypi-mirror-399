# AGENTS.MD

Agent Rules for Python API Wrapper Code

## § 0 META

### § 0.0 Purpose

0. Define a machine-readable, internally consistent rule system.
1. Enable agents to reference rules unambiguously via § x.x.x.x.
2. Prevent conflicting guidance through consolidation.

### § 0.1 Overview

0. This project is a Python wrapper around a Swagger v3 HTTP API.
1. It supports synchronous and asynchronous operation.
2. It enforces caching, throttling, and retry behavior centrally.
3. This file is optimized for agents, not humans.
4. Use Context7 MCP server for documentation retrieval
that assume and cause hallucinations.
5. Use these serena tools liberally:
   1. think_about_task_adherence
      1. Run after each task
   2. think_about_whether_you_are_done
      1. Run after each task
      2. Run when you are done
   3. think_about_collected_information
      1. Run when you collect information
      2. Run when you are prompted to continue
   4. read_memory
   5. edit_memory
   6. delete_memory
      1. Obsolete memories will be removed when deprecated
   7. list_memories
      1. The agent will examine memories for context management.  
   8. write_memory
      1. Run when agent finishes steps, answers questions, debugs, or learns, or makes ADR decisions.
      2. The agent will use a memory for a working task list
      3. Never label items as revised, final, nor other AI naming conventions
      4. Taxonomical naming of each memory will be used from broadest to narrowest topic.  eg year_month_day_hour_seconds, or world_continent_country_state_county_city_etc...
   9. search_for_pattern

### § 0.2 Project Stage

0. INITIAL_DEV (current)
1. ALPHA
2. BETA
3. STABLE

### § 0.3 Format Invariants

0. Purpose
   0. Every section must declare intent explicitly.
1. Rules
   0. Each rule is atomic.
   1. One rule per line.
2. Exceptions
   1. Exceptions are a subtree of the rule they modify.
3. Enforcement
   1. Enforcement is explicit or states `None`.
4. Examples
   1. Examples are non-normative.
   2. Examples use placeholders only.
   3. Examples must not contain domain nouns.
5. Numbering
   1. All lists are zero-indexed.
   2. Unnumbered prose is forbidden.

## § 1 CORE COMMANDMENTS

### § 1.0 Purpose

1. Establish absolute constraints overriding all other sections.

### § 1.1 Rules

0. Use `uv` for all tooling and execution.
1. Write all logic exactly once.
2. Place tests only in `tests/`.
3. Create additional markdown only when explicitly requested.
4. Create debugging, sprawlware, helpers only when explicitly requested.
5. Re-read this file after context compression or file changes.
6. Use module-level loggers only.
7. D-R-Y > simplicity > cleverness > complexity

## § 2 CODE QUALITY STANDARDS

### § 2.1 Cognitive Complexity

#### § 2.1.0 Purpose

1. Keep code understandable by humans and agents.

#### § 2.1.1 Rules

0. Cognitive complexity ≤ 10 per function or method.
1. Cyclomatic complexity ≤ 8 per function or method.

#### § 2.1.3 Enforcement

0. Run cyclomatic analysis:
   0. `uv run radon cc src/ -a -nb`
1. Run cognitive analysis:
   0. `uv run xenon --max-absolute B src/`

### § 2.2 Naming

#### § 2.2.0 Purpose

1. Ensure semantic clarity and searchability.

#### § 2.2.1 Rules

0. snake_case for variables, functions, modules.
1. PascalCase for classes.
2. UPPER_SNAKE_CASE for constants.
3. Names use full words.
4. Plural names indicate collections.
5. File names are nouns.
6. Service classes end with `Service`.
7. base modules/submodules are named base (not _base)
8. Do not use _hidden class properties to complicate simple code

#### § 2.2.3 Enforcement

1. `uv run ruff check --select N`

#### § 2.2.3 Exceptions

1. _hidden class properties may be used when required
2. _hidden class properties may be used when it simplifies
3. _hidden class properties may be used for security

### § 2.3 Typing

#### § 2.3.0 Purpose

1. Eliminate ambiguity and runtime surprises.

#### § 2.3.1 Rules

0. Full type hints everywhere.
1. `Any` is discouraged.
2. External payloads must be validated immediately.
3. All public APIs are typed.

#### § 2.3.2 Exceptions

0. Untyped third-party base classes.
1. Over-complicated workarounds to accomodate string typing

#### § 2.3.3 Enforcement

1. `uv run mypy .`
2. `uv run pyright .`

## § 3 PYTHON STANDARDS

### § 3.1 Imports

#### § 3.1.0 Purpose

1. Maintain deterministic module loading.

#### § 3.1.1 Rules

0. Imports appear immediately after module docstring.
1. Order:
   0. Standard library
   1. Third-party
   2. Local
2. Absolute imports only.
3. One symbol per `from` import.
4. No deferred imports.

#### § 3.1.3 Enforcement

1. `uv run ruff check --select I`

#### § 3.1.4 Examples

```python
"""Module docstring."""

# Standard library
from pathlib import Path

# Third-party
from pydantic import BaseModel

# Local
from foo_lib.config import bar_settings
```

### § 3.2 Exceptions & Chaining

#### § 3.2.0 Purpose

1. Preserve causality and debugging signal.

#### § 3.2.1 Rules

0. Always use `raise X from err` or `from None`.
1. Never raise a new exception without chaining.
2. Bare re-raise allowed only for same exception.

#### § 3.2.2 Exceptions

1. Not enforced in /tests

#### § 3.2.3 Enforcement

1. Code review rejection.

### § 3.3 Resource Management

#### § 3.3.0 Purpose

1. Prevent leaks and undefined lifetimes.

#### § 3.3.1 Rules

0. Use context managers for resources.
1. Prefer `with` over manual close.

#### § 3.3.2 Exceptions

1. Third-party objects without context support.

#### § 3.3.3 Enforcement

1. Code review rejection.

### § 3.4 Logging

#### § 3.4.0 Purpose

1. Provide structured, non-interactive observability.

#### § 3.4.1 Rules

0. Configure logging once at entry.
1. Use module-level loggers only.
2. `print()` is forbidden.
3. Use Rich for logging
   1. Rich v14 Themes

#### § 3.4.3 Enforcement

1. CI failure on `print()` detection.

### § 3.5 HTTP

#### § 3.5.0 Purpose

1. Ensure consistent sync and async behavior.

#### § 3.5.1 Rules

0. Use a single HTTP client abstraction.
1. Underlying transport must support sync and async.
2. Clients are injected, never instantiated ad-hoc.

#### § 3.5.3 Enforcement

1. Code review rejection.

## § 4 DOCUMENTATION

### § 4.1 Docstrings

#### § 4.1.0 Purpose

1. Enable static and agent understanding.

#### § 4.1.1 Rules

0. Public APIs use NumPy style.
1. Private methods use one-line docstrings.

#### § 4.1.2 Exceptions

1. Not enforced in /tests

#### § 4.1.3 Enforcement

1. Code review rejection.

### § 4.2 User Documentation

#### § 4.2.1 Purpose

1. Documentation consumed by humans
2. Documentation created by humans

#### § 4.2.4 Rules

1. New documentation in markdown
2. Strict numbering
3. § Indicates sections
4. README.md in root
5. CONTRIBUTING.md in root
6. Other documentation in docs/ or Serena MCP Memories
7. FORBIDDEN UNLESS REQUESTED:
   1. Ad hoc reports
   2. AI sprawlware helper docs
   3. wrap-ups
   4. Garbage in root

### § 4.3 AI Documentation

#### § 4.3.1 Purpose

1. Documentation consumed by Agents
2. Documentation created by Agents

#### § 4.2.2 Rules

1. New documentation in markdown
2. Strict numbering and hierarchy
3. § Indicates sections
4. AGENTS.md in root
5. Other documentation in docs/
6. FORBIDDEN UNLESS REQUESTED:
   1. Ad hoc reports
   2. AI sprawlware helper docs
   3. wrap-ups
   4. Garbage in root

#### § 4.2.3 Exceptions

1. AGENTS.md may be created in subdirectories IF there there are special, divergent instructions at this scope.

## § 5 ARCHITECTURE

### § 5.1 Services

#### § 5.1.0 Purpose

1. Isolate business logic per API tag.

#### § 5.1.1 Rules

0. One service per Swagger tag.
1. Services inherit `BaseService`.
2. Each service has an ABC interface.
3. Services are stateful and injected.

#### § 5.1.3 Enforcement

1. CI architectural review.

### § 5.2 Clients

#### § 5.2.0 Purpose

1. Centralize HTTP, caching, throttling, retry.

#### § 5.2.1 Rules

0. One abstract client interface.
1. One sync implementation.
2. One async implementation.
3. All network calls go through client.
4. Retry, rate-limit, cache live here.

##### § 5.2.1.1 Exceptions

1. Large datasets, (type, e.g.) need not expose syncronous methods

#### § 5.2.3 Enforcement

1. Code review rejection.

### § 5.3 Pagination

#### § 5.3.0 Purpose

1. Enable memory-safe traversal of large datasets.

#### § 5.3.1 Rules

0. Async pagination uses async generators.
1. Pagination parameters are internal.
2. Yield items lazily.

#### § 5.3.3 Examples

```python
async for item in service.search_things_paginated(query="flerp"):
    await sink.write(item)
```

### § 5.4 Structure & Parity

#### § 5.1.1 Purpose

1. Maximize DRY by preferring ABC design patterns
2. Create predictable file structure by using consistent naming in submodues
3. Create predictable python structure by aggresive use of AbstractBaseClass and abstract methods

#### § 5.1.2 Rules

1. Services, Models, Cli should all contain submodules based upon:
   1. API Specification (Swagger)
   2. Architectural Needs
   3. Design Specifications
2. Each submodule contains:
   1. base
      1. Base can by a submodule or module if small
         1. Submodule should be named base
         2. _base (hidden) forbidden
      2. Should contain:
         1. AbstractBaseClass: [ServiceBase, ModelBase, CliBase, etc.]
            1. Inhereted by other Submodules and ABC's in Submodules
         2. Helper methods, ABC's, etc within that scope
      3. Rigorous use of abstractmethods to control design
   2. __init__.py
      1. __all__ definition
      2. Constants should be promoted to parent __init__.py when possible
   3. Submodules
      1. Submodule Base Class
         1. Inherits from Base Class in 2.1.
         2. Inerited by other Classes in same module file

#### § 5.1.3 Exceptions

1. Do not create empty patterns:
   1. If an ABC in a submodule adds complexity by using a class In Name Only, skip it
2. Do not split into submodules unless it provides clarity by isolating like objects.

## § 6 DEPENDENCIES & INFRASTRUCTURE

### § 6.1 Environment

#### § 6.1.0 Purpose

1. Ensure deterministic builds.

#### § 6.1.1 Rules

0. Dependencies declared in `pyproject.toml`.
1. Lockfile committed.
2. Virtual environment via `uv`.

#### § 6.1.3 Enforcement

1. CI failure.

### § 6.2 Caching

#### § 6.2.0 Purpose

1. Minimize redundant network calls.

#### § 6.2.1 Rules

0. Cache all responses.
1. In-memory TTL for hot paths.
2. Persistent HTTP cache for durability.
3. Cache hit/miss indicator in wrapped record

#### § 6.2.2 Exceptions

1. Explicit cache-bypass flags.

#### § 6.2.3 Enforcement

1. Code review rejection.

### § 6.3 Rate Limiting & Retry

#### § 6.3.0 Purpose

1. Protect upstream and callers.

#### § 6.3.1 Rules

0. Apply conservative rate limits.
1. Use exponential backoff with jitter.
2. Retry logic lives in client.

#### § 6.3.2 Exceptions

#### § 6.3.3 Enforcement

1. CI review.

## § 7 CLI

### § 7.0 Purpose

1. Provide user interaction.

### § 7.1 Rules

0. CLI contains all I/O.
1. Services are headless.
2. No prompts without flags.
3. All params have short/long variants -h/--help
4. Consistent header, footer, param format
   1. version and MIT license blurb in footer
   2. Rich theming
5. Rich:
   1. Consistent Panel width across all methods
   2. Rich v14 Theming.
   3. Consistent predictable formatting
   4. Error console is also using Rich 14 and should follow same themes
6. Provide user-centric CLI aliases (shortcuts) alongside canonical names (e.g., catalogues→cat, issuers→isr, issues→isu with -t/--table flag for table mode)
7. Model-driven rendering:
   0. All table generation: use `Model.as_table(items, title)` only.
   1. All field rendering: use `Model.format_fields(fields)` only.
   2. Panel construction: triple-quoted f-string template calling model methods; no `add_columns_to_table()`, `infer_columns_from_model()`, or `add_model_row()` in CLI layer.
   3. Rationale: Models own presentation logic; CLI owns orchestration.

### § 7.2 Exceptions

### § 7.3 Enforcement

1. Code review rejection.

## § 8 TESTING

### § 8.0 Purpose

1. Prove correctness, not vanity metrics.

### § 8.1 Rules

0. Mock all network calls.
1. Do not clear caches by default (wastes API calls)
2. Isolate test cache directories.

### § 8.2 Exceptions

1. Cache invalidation tests.

### § 8.3 Enforcement

1. CI failure.

## § 9 CI

### § 9.0 Purpose

1. Enforce invariants automatically.

### § 9.1 Rules

0. Run ruff.
1. Run mypy.
2. Run pyright.
3. Run radon
4. Run xenon.

### § 9.3 Enforcement

1. Merge blocked.

## § 10 FINAL

### § 10.0 Wrapup

0. Violations are rejected without review.
1. Conflicts resolve toward stricter rule.
2. This file is authoritative.
3. _Fake Winston Churchill_ Now build something that lasts a decade.
