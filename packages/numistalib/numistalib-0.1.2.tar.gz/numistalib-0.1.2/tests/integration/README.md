# Integration Tests

Integration tests for the Numista CLI using real API calls.

## § 0 OVERVIEW

### § 0.0 Purpose

0. Validate CLI commands with real API responses
1. Verify model completeness with actual data
2. Ensure caching and rate limiting work correctly

### § 0.1 Requirements

0. Valid NUMISTA_API_KEY environment variable
1. Network connectivity to Numista API
2. Rate limit: 45 requests/minute

### § 0.2 Test Organization

0. One test file per CLI module
1. All current commands are READ operations
2. Test classes group related commands
3. Fixtures provide known test entity IDs

## § 1 RUNNING TESTS

### § 1.0 Set API Key

```bash
export NUMISTA_API_KEY="your_api_key_here"
```

### § 1.1 Run All Integration Tests

```bash
uv run pytest tests/integration/ -v
```

### § 1.2 Run Specific Module

```bash
uv run pytest tests/integration/test_cli_types_read.py -v
```

### § 1.3 Run Single Test

```bash
uv run pytest tests/integration/test_cli_types_read.py::TestTypesSearch::test_search_with_query -v
```

## § 2 TEST FILES

### § 2.0 Read Operations

0. test_cli_types_read.py
   0. types search (query, issuer, category, year, pagination)
   1. types get (by ID, invalid ID, language)
1. test_cli_issues_read.py
   0. issues (for type, language, invalid type ID)
2. test_cli_prices_read.py
   0. prices (type/issue, currency, language)
3. test_cli_catalogues_read.py
   0. catalogues (list, language)
4. test_cli_issuers_read.py
   0. issuers (list, language)
5. test_cli_mints_read.py
   0. mints (list, language)
   1. mint (by ID, language, invalid ID)
6. test_cli_users_read.py
   0. users get (by ID, invalid ID)
   1. users search (query, pagination)
7. test_cli_literature_read.py
   0. literature get (by ID, language)
   1. literature search (query, pagination, language)
8. test_cli_collections_read.py
   0. collections list (for user, language)
   1. collections items (for user, language, pagination)
9. test_cli_config_read.py
   0. config get (key)
   1. config list (all)
10. test_cli_image_search_read.py
    0. search-image (SKIPPED - requires image file)

### § 2.1 Write Operations

0. None currently
1. Write operations will be added if API supports POST/PUT/PATCH/DELETE

## § 3 FIXTURES

### § 3.0 Session Fixtures (conftest.py)

0. api_key: From NUMISTA_API_KEY environment variable
1. integration_settings: Settings with real API key
2. cli_runner: CliRunner instance
3. Known entity IDs:
   0. known_type_id: 420
   1. known_issue_id: 51757
   2. known_mint_id: 17
   3. known_user_id: 1
   4. known_publication_id: "1"
   5. known_catalogue_id: 3
   6. known_issuer_code: "canada"

### § 3.1 Fixture Reuse

0. Session-scoped fixtures minimize API calls
1. Known IDs verified to exist in Numista database
2. Tests skip if NUMISTA_API_KEY not set

## § 4 TEST PATTERNS

### § 4.0 Happy Path

0. Test with valid parameters
1. Verify exit code 0
2. Assert expected content in output

### § 4.1 Error Handling

0. Test with invalid IDs
1. Verify graceful failure (non-zero exit or error message)

### § 4.2 Language Support

0. Test optional language parameters (en, fr, es)
1. Verify API accepts language codes

### § 4.3 Pagination

0. Test page and count parameters
1. Verify pagination works correctly

## § 5 NOTES

### § 5.0 Rate Limiting

0. Tests run sequentially to respect 45 req/min limit
1. HTTP cache reduces duplicate requests
2. Session fixtures reuse setup data

### § 5.1 Known Limitations

0. Image search tests skipped (requires image files)
1. No write operation tests (API is read-only via current CLI)
2. Some tests may fail if test entities removed from Numista database

### § 5.2 Maintenance

0. Update known entity IDs if they become invalid
1. Add new test files for new CLI commands
2. Add write operation tests when CLI adds POST/PUT/DELETE commands
