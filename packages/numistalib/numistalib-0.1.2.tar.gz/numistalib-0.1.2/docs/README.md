# numistalib Documentation

This directory contains comprehensive documentation for numistalib, production-ready and configured for ReadTheDocs deployment.

## § 0 Build Status

✅ **Clean Build - Zero Warnings**

- Sphinx build: ✅ 0 warnings
- Python package: ✅ Built successfully
- RTD configuration: ✅ Ready

## § 1 Documentation Structure

### User Guides

- [installation.md](installation.md) - Installation and setup
- [quickstart.md](quickstart.md) - 5-minute getting started guide
- [cli_guide.md](cli_guide.md) - Complete CLI command reference
- [python_api_guide.md](python_api_guide.md) - Python API usage guide
- [configuration.md](configuration.md) - Configuration reference
- [advanced_usage.md](advanced_usage.md) - Advanced patterns and techniques

### Reference Documentation

- [architecture.md](architecture.md) - System architecture and design
- [contributing.md](contributing.md) - Contribution guidelines
- [CHANGELOG](CHANGELOG) - Version history
- [license.md](license.md) - MIT License

### API Reference

- [API Reference](api/index.rst) - Sphinx autodoc API reference
  - [client.rst](api/client.rst) - HTTP client
  - [services.rst](api/services.rst) - Service layer
  - [models.rst](api/models.rst) - Data models
  - [cli.rst](api/cli.rst) - CLI commands

### Technical Reference

- [Official Numista API Docs](https://en.numista.com/api/doc/index.php) - Numista API specification

## § 2 Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
uv sync --group docs
```

### Build HTML

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

Or using Make:

```bash
cd docs
make html
```

### View Documentation

Open `docs/_build/html/index.html` in your browser.

### Build Other Formats

PDF:

```bash
cd docs
make latexpdf
```

EPUB:

```bash
cd docs
make epub
```

## § 3 ReadTheDocs Deployment

### Configuration Files

- [.readthedocs.yml](../.readthedocs.yml) - RTD build configuration
- [conf.py](conf.py) - Sphinx configuration
- Documentation dependencies managed via `pyproject.toml` (docs group)

### Project Setup

0. **RTD Account**: <https://readthedocs.org/accounts/signup/>
1. **Import Project**: Connect GitHub, select `wells01440/numistalib`
2. **Configure**:
   - Name: `numistalib`
   - Language: English
   - Programming Language: Python
3. **Build**: Click "Build Version" (~1 minute)
4. **Live**: <https://numistalib.readthedocs.io>

### Enable Auto-Builds

In RTD Admin → Integrations → Add webhook

Documentation rebuilds automatically on every push to main.

## § 4 What Was Fixed

### Sphinx Build (19 warnings → 0)

0. **docs/conf.py** - Added `source_suffix` for markdown support
1. **docs/api/client.rst** - Removed non-existent autodoc methods, added `:no-index:`
2. **docs/index.rst** - Fixed toctree formatting, included orphan documents
3. **docs/api/index.rst** - Marked as orphan to suppress toctree warning
4. **docs/contributing.md** - Fixed cross-reference to AGENTS.md
5. **docs/CHANGELOG.md** - Created symlink to `../CHANGELOG`

### Legal & Attribution

Added Numista attribution and compliance notices:

0. Main README.md - Legal & Attribution section with official links
1. [index.rst](index.rst) - Visible legal notice in docs index
2. This file - Documentation-specific legal section
3. [../pyproject.toml](../pyproject.toml) - Project URLs including Numista terms
4. [../src/numistalib/client.py](../src/numistalib/client.py) - Module docstring with Pricing API usage considerations

## Documentation Standards

### Formatting

- Use § numbering for sections
- Markdown for user guides
- reStructuredText for API reference
- Code examples should be runnable
- Include "Next Steps" links at guide ends

### Content

- Progressive complexity (basic → advanced)
- Concrete, copy-pasteable examples
- Clear explanations
- Complete coverage of features
- Cross-references between docs

### Maintenance

- Update changelog for releases
- Keep API reference in sync with code
- Test all code examples
- Update screenshots/diagrams as needed

## Legal & Attribution

- This project is an unofficial wrapper and is not affiliated with Numista.
- When using data from Numista, provide appropriate attribution to Numista.
- All usage must comply with Numista’s terms and policies:
  - Conditions of use: <https://en.numista.com/conditions.php>
  - Legal information: <https://en.numista.com/legal.php>
  - Pricing API terms: <https://en.numista.com/api/pricing.php>
- Respect Numista’s rate limits and any restrictions on caching or redistribution, particularly for pricing data.

## § 1 Numista API Endpoint Trees

Each section below mirrors the OpenAPI file ([official spec](https://en.numista.com/api/doc/swagger.yaml?v=3.29.0)) and lists every path, method, and request
parameter set per API version.
All calls require the `Numista-API-Key` header; endpoints under “User” additionally need the
OAuth scopes noted in the swagger comments.

## § 1.1 Version 3 (`https://api.numista.com/v3`)

- `/types`
  - `GET` Search the catalogue (at least one of `q`, `issuer`, `catalogue`, `date`, or `year` is required).
    - Query: `lang` (enum en/es/fr, default `en`), `category` (coin|banknote|exonumia), `q` (string),
      `issuer` (string code), `catalogue` (int), `number` (string, requires `catalogue`), `ruler` (int),
      `material` (int), `year` (string/range), `date` (string/range), `size` (string/range in mm),
      `weight` (string/range in g), `page` (int, default `1`), `count` (int, default `50`, max `50`).
  - `POST` Add a type to the catalogue (requires catalogue-edit permission).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `type_update` JSON including localized `title`, `category`, `issuer`, `value`, `ruling_authority`, `shape`,
      `composition`, physical data (`weight`, `size`, `thickness`, `orientation`), demonetization/calendar metadata,
      `obverse`/`reverse`/`edge` descriptions, `mints`, rich `comments`, `related_coins`, `tags`, and `references`.
- `/types/{type_id}`
  - `GET` Get details about a type.
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/types/{type_id}/issues`
  - `GET` List every issue of a type.
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
  - `POST` Add an issue (requires catalogue-edit permission).
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `issue_update` JSON covering `is_dated`, year span, `mint_letter`, `mintage`,
      localized `comment`, and related catalogue references.
- `/types/{type_id}/issues/{issue_id}/prices`
  - `GET` Return price estimates stratified by grade.
    - Path: `type_id` (int), `issue_id` (int).
    - Query: `currency` (ISO 4217 code, default `EUR`), `lang` (enum en/es/fr, default `en`).
- `/issuers`
  - `GET` Enumerate issuers.
    - Query: `lang` (enum en/es/fr, default `en`).
- `/mints`
  - `GET` Enumerate mints.
    - Query: `lang` (enum en/es/fr, default `en`).
- `/mints/{mint_id}`
  - `GET` Fetch mint details.
    - Path: `mint_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/catalogues`
  - `GET` List available reference catalogues (no parameters).
- `/search_by_image`
  - `POST` Find candidate types via up to two reference photos.
    - Query: `lang` (enum en/es/fr, default `en`),
      `activate_experimental_features` (bool, default `false`, unlocks year/grade beta output).
    - Body: JSON with optional `category` (coin|banknote|exonumia), required `images` array (1–2 items each containing
      `mime_type` of `image/jpeg` or `image/png` plus base64 `image_data`), and optional `max_results` (int 1–100,
      default `100`).
- `/publications/{id}`
  - `GET` Return information about a specific publication.
    - Path: `id` (string such as `L123456`).
- `/oauth_token`
  - `GET` Exchange for an OAuth token (authorization-code or client-credentials flows).
    - Query: `grant_type` (`authorization_code` default or `client_credentials`), `code`, `client_id`, `client_secret`,
      `redirect_uri`, `scope` (comma-delimited list when using client credentials). Mandatory fields depend on
      `grant_type` exactly as described in the API docs.
- `/users/{user_id}`
  - `GET` Fetch public profile data.
    - Path: `user_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/users/{user_id}/collections`
  - `GET` List the user’s collections (path `user_id` only).
- `/users/{user_id}/collected_items`
  - `GET` List collected items (requires OAuth scope `view_collection`).
    - Path: `user_id` (int).
    - Query: `category` (coin|banknote|exonumia), `type` (int), `collection` (int).
  - `POST` Add an item (requires `edit_collection` scope).
    - Path: `user_id` (int).
    - Body: JSON with `type` (int, required), optional `issue` (int), `quantity` (int, default `1`), `grade`
      (enum g/vg/f/vf/xf/au/unc), `for_swap` (bool), `private_comment`, `public_comment`, `price` (value+currency),
      `collection` (int), `storage_location`, `acquisition_place`, `acquisition_date` (YYYY-MM-DD), `serial_number`,
      `internal_id`, `weight`, `size`, `axis`, and nested `grading_details` (company, slab IDs, CAC sticker, strike,
      surface, designations).
- `/users/{user_id}/collected_items/{item_id}`
  - `GET` Retrieve a single collection item.
    - Path: `user_id` (int), `item_id` (int).
  - `PATCH` Update an item (requires `edit_collection` scope).
    - Path: `user_id` (int), `item_id` (int).
    - Body: Same structure as the `POST` payload, with every field optional and nullable where noted (e.g., `grade`,
      `issue`, `price`).
  - `DELETE` Remove an item (requires `edit_collection` scope).
    - Path: `user_id` (int), `item_id` (int).

## § 1.2 Version 2 (`https://api.numista.com/v2`)

Version 2 exposes every endpoint listed for version 3 with the same request parameters. In addition, the following
legacy paths remain accessible through `/v2` (all were removed from `/v3`):

- `/coins`
  - `GET` Search for coins.
    - Query: `lang` (enum en/es/fr, default `en`), `q` (string, required), `issuer` (string code),
      `page` (int, default `1`), `count` (int, default `50`).
  - `POST` Add a coin type using the deprecated `coin_update` schema (requires catalogue-edit permission).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `coin_update` JSON (localized `title`, `issuer`, `type`, `value`, `ruling_authority`, `shape`,
      `composition`, measurements, `orientation`, demonetization, calendar, `obverse`/`reverse`/`edge`, `mints`,
      `comments`, `related_coins`, `tags`, `references`).
- `/coins/{coin_id}`
  - `GET` Retrieve coin metadata (deprecated in favor of `/types/{type_id}`).
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/coins/{coin_id}/issues`
  - `GET` List issues of a legacy coin entry.
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
  - `POST` Insert a legacy issue (same `issue_update` body as `/types/{type_id}/issues`).
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/coins/{coin_id}/issues/{issue_id}/prices`
  - `GET` Return price estimates for a legacy issue.
    - Path: `coin_id` (int), `issue_id` (int).
    - Query: `currency` (ISO 4217 code, default `EUR`), `lang` (enum en/es/fr, default `en`).
- `/users/{user_id}/collected_coins`
  - `GET` Legacy summary of collected coins (requires OAuth scope `view_collection`).
    - Path: `user_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`), `coin` (int coin-type filter).

## § 1.3 Version 1 (`https://api.numista.com/v1`)

Version 1 shares the same endpoint tree as version 2 (including the `/coins` and `/users/{user_id}/collected_coins`
legacy paths above). Parameter names are identical, but some response fields remain in their original camelCase form
(`minYear`, `maxYear`, `value`, etc.) as noted in the [official API spec](https://en.numista.com/api/doc/swagger.yaml?v=3.29.0).
