"""Integration test configuration and fixtures.

Integration tests make real API calls and require a valid API key.
Set NUMISTA_API_KEY environment variable before running.
"""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner
from dotenv import load_dotenv

from numistalib.cli.catalogues import register_catalogues_commands
from numistalib.cli.collections import register_collections_commands
from numistalib.cli.config import register_config_commands
from numistalib.cli.image_search import register_image_search_commands
from numistalib.cli.issuers import register_issuers_commands
from numistalib.cli.issues import register_issues_commands
from numistalib.cli.literature import register_literature_commands
from numistalib.cli.main import cli as base_cli
from numistalib.cli.mints import register_mints_commands
from numistalib.cli.prices import register_prices_commands
from numistalib.cli.types import register_types_commands
from numistalib.cli.users import register_users_commands
from numistalib.client import close_all_clients
from numistalib.config import Settings

# Load .env file if it exists
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


@pytest.fixture(scope="session")
def api_key() -> str:
    """Get API key from environment."""
    key = os.getenv("NUMISTA_API_KEY")
    if not key:
        pytest.skip("NUMISTA_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def integration_settings(api_key: str) -> Settings:
    """Provide settings for integration tests."""
    return Settings(api_key=api_key)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Click CLI test runner."""
    return CliRunner()


@pytest.fixture(scope="session")
def cli():
    """Provide CLI with all commands registered."""
    # Register all commands
    register_config_commands(base_cli)
    register_types_commands(base_cli)
    register_catalogues_commands(base_cli)
    register_issuers_commands(base_cli)
    register_issues_commands(base_cli)
    register_mints_commands(base_cli)
    register_collections_commands(base_cli)
    register_image_search_commands(base_cli)
    register_literature_commands(base_cli)
    register_prices_commands(base_cli)
    register_users_commands(base_cli)

    return base_cli


@pytest.fixture(scope="session")
def known_type_id() -> int:
    """Well-known type ID for testing (Canadian 5 cents Victoria)."""
    return 420


@pytest.fixture(scope="session")
def known_issue_id() -> int:
    """Well-known issue ID for testing."""
    return 51757


@pytest.fixture(scope="session")
def known_mint_id() -> int:
    """Well-known mint ID for testing (Royal Mint)."""
    return 17


@pytest.fixture(scope="session")
def known_user_id() -> int:
    """Well-known user ID for testing."""
    return 1


@pytest.fixture(scope="session")
def known_publication_id() -> str:
    """Well-known publication ID for testing."""
    return "1"


@pytest.fixture(scope="session")
def known_catalogue_id() -> int:
    """Well-known catalogue ID for testing (Krause)."""
    return 3


@pytest.fixture(scope="session")
def known_issuer_code() -> str:
    """Well-known issuer code for testing."""
    return "canada"


@pytest.fixture(scope="session", autouse=True)
def _close_clients_after_session() -> None:
    """Ensure cache clients and sqlite storages are closed to silence ResourceWarnings."""
    yield
    close_all_clients()
