# Changelog

All notable changes to numistalib will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [0.1.1] - 2025-12-28

### Added

- Initial release
- Complete Numista API v3 coverage
- HTTP caching with hishel (7-day TTL)
- Rate limiting (45 requests/minute)
- Retry logic with exponential backoff
- Rich CLI with tables and panels
- Full Pydantic model validation
- Sync and async support
- Comprehensive documentation
- ReadTheDocs configuration

### Features

#### Client

- `NumistaApiClient` with sync/async support
- RFC 9111-compliant HTTP caching
- Persistent SQLite cache storage
- Rate limiting with pyrate-limiter
- Exponential backoff with jitter
- Cache indicators (💾/🌐)

#### Services

- Types: Search and retrieve coin/banknote/exonumia types
- Catalogues: List reference catalogues
- Issuers: List countries and entities
- Issues: Get issue information
- Mints: List and retrieve mint details
- Collections: Manage user collections (OAuth)
- Image Search: Search by coin images
- Literature: Get publication information
- Prices: Get price estimates
- Users: Get user profiles

#### CLI

- Rich v14 theming
- Consistent panel/table display
- Cache indicators
- Short/long option flags
- Command aliases (cat, isr, isu)
- Error handling with rich console

#### Models

- Full Pydantic validation
- Type safety with strict hints
- Rich rendering methods
- Serialization support

### Documentation

- Installation guide
- Quickstart tutorial
- Complete CLI reference
- Python API guide
- Configuration reference
- Advanced usage patterns
- Architecture documentation
- Contributing guide
- API reference (Sphinx)

## [0.1.0] - 2025-12-27

Initial development version.
