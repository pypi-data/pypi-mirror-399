"""Integration tests for numistalib CLI.

Integration tests make real API calls and require:
- Valid NUMISTA_API_KEY environment variable
- Network connectivity to api.numista.com
- Respect for API rate limits (45 requests/minute)

Run with: pytest tests/integration/ -v
Skip with: pytest tests/ --ignore=tests/integration/
"""
