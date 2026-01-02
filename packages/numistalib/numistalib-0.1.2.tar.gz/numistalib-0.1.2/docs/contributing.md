# Contributing to numistalib

Thank you for your interest in contributing! This guide will help you get started.

## § 1 Getting Started

### § 1.1 Prerequisites

- Python 3.13 or higher
- `uv` package manager
- Git
- A Numista API key (for testing)

### § 1.2 Development Setup

0. Fork the repository on GitHub

1. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/numistalib.git
cd numistalib
```

1. Install dependencies:

```bash
uv sync
```

1. Create `.env` file:

```bash
cp .env.example .env
# Add your API key to .env
```

1. Verify installation:

```bash
uv run pytest tests/ -v
```

---

## § 2 Code Standards

### § 2.1 Important Reading

**Read `AGENTS.md` (in repository root) completely before contributing.**

This file contains authoritative coding standards including:

- Naming conventions
- Type hints requirements
- Complexity limits
- Documentation requirements
- Architecture patterns

### § 2.2 Key Rules

- Use `uv` for tooling
- Full type hints everywhere
- NumPy-style docstrings for public APIs
- Cognitive complexity ≤ 10
- Cyclomatic complexity ≤ 8
- No `print()` statements (use logging)
- Always use exception chaining

### § 2.3 Code Quality Tools

Run before committing:

```bash
# Lint and format
uv run ruff check --fix src/
uv run ruff format src/

# Type checking
uv run mypy .
uv run pyright .

# Complexity checks
uv run radon cc src/numistalib/ -a -nb
uv run xenon --max-absolute B src/numistalib/

# Tests
uv run pytest tests/ -v
```

---

## § 3 Development Workflow

### § 3.1 Branch Strategy

1. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

1. Make your changes

2. Commit with descriptive messages:

```bash
git commit -m "Add search by catalogue reference

- Implement catalogue parameter in search_types
- Add tests for catalogue filtering
- Update CLI with --catalogue flag"
```

1. Push to your fork:

```bash
git push origin feature/your-feature-name
```

1. Create a pull request

### § 3.2 Commit Messages

Follow this format:

```
<type>: <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**

```
feat: Add mint details endpoint

- Implement get_mint() in MintsService
- Add Mint model with full validation
- Create CLI command `numistalib mints get <id>`
- Add integration tests

Closes #42
```

---

## § 4 Adding Features

### § 4.1 New Service

0. **Check Swagger spec** at [official API docs](https://en.numista.com/api/doc/swagger.yaml?v=3.29.0)

1. **Create models** in `models/<entity>.py`:

```python
from numistalib.models.base.base_model import BaseModel

class YourModel(BaseModel):
    """Your model description."""
    
    id: int
    name: str
```

1. **Create service ABC** in `services/<tag>/base.py`:

```python
from abc import ABC, abstractmethod
from numistalib.services.base.service import BaseService

class YourServiceBase(BaseService, ABC):
    """ABC for YourService."""
    
    @abstractmethod
    def get_items(self) -> list[YourModel]:
        """Get items."""
        pass
```

1. **Implement service** in `services/<tag>/service.py`:

```python
from numistalib.services.<tag>.base import YourServiceBase
from numistalib.models.<entity> import YourModel

class YourService(YourServiceBase):
    """Service for <tag> endpoints."""
    
    def get_items(self) -> list[YourModel]:
        """Get items."""
        response = self.client.get("/your-endpoint")
        return self.to_models(response["items"])
    
    def to_models(self, items: list[dict]) -> list[YourModel]:
        """Convert raw data to models."""
        return [YourModel(**item) for item in items]
```

1. **Create CLI** in `cli/<tag>.py`:

```python
import click
from rich.console import Console
from numistalib.services.<tag>.service import YourService

console = Console()

def register_your_commands(cli: click.Group) -> None:
    """Register <tag> commands."""
    
    @cli.command()
    def your_command():
        """Your command description."""
        # Implementation
        pass
```

1. **Register in main** in `cli/main.py`:

```python
from numistalib.cli.<tag> import register_your_commands

def main():
    # ...
    register_your_commands(cli)
    # ...
```

1. **Add tests** in `tests/integration/test_cli_<tag>_read.py`:

```python
def test_your_command(runner):
    """Test your command."""
    result = runner.invoke(cli, ["your-command"])
    assert result.exit_code == 0
```

### § 4.2 New CLI Command

Follow CLI patterns in existing commands:

- Use Click decorators
- Accept settings via context or instantiate
- Use Rich for output
- Call model rendering methods
- Handle errors gracefully
- Provide short/long flags

### § 4.3 New Model Fields

0. Check Swagger spec for field types
1. Add field to Pydantic model with proper type
2. Add validation if needed
3. Update rendering methods if displayed
4. Add tests

---

## § 5 Testing

### § 5.1 Test Structure

```
tests/
├── test_models.py              # Model validation tests
├── test_rich_renderables.py    # Rendering tests
└── integration/                # Integration tests
    ├── conftest.py             # Fixtures
    └── test_cli_<tag>_read.py  # CLI integration tests
```

### § 5.2 Writing Tests

**Unit Test:**

```python
def test_model_validation():
    """Test model validates correctly."""
    data = {"id": 1, "name": "Test"}
    model = YourModel(**data)
    assert model.id == 1
    assert model.name == "Test"
```

**Integration Test:**

```python
def test_cli_command(runner):
    """Test CLI command."""
    result = runner.invoke(cli, ["your-command", "--option", "value"])
    assert result.exit_code == 0
    assert "Expected output" in result.output
```

### § 5.3 Test Coverage

- Aim for >80% coverage
- Test happy paths and error cases
- Mock network calls
- Test both sync and async methods

### § 5.4 Running Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_models.py -v

# With coverage
uv run pytest tests/ --cov=numistalib --cov-report=html
```

---

## § 6 Documentation

### § 6.1 Docstrings

**Public APIs** use NumPy style:

```python
def search_types(
    self,
    query: str | None = None,
    issuer: str | None = None,
    count: int = 50
) -> list[TypeBasic]:
    """
    Search the catalogue for types.
    
    Parameters
    ----------
    query : str, optional
        Search keywords
    issuer : str, optional
        Issuer code (e.g., "france")
    count : int, default=50
        Results per page (max 50)
    
    Returns
    -------
    list[TypeBasic]
        List of matching types
    
    Raises
    ------
    NumistaError
        If API request fails
    
    Examples
    --------
    >>> service.search_types(query="dollar", count=10)
    [TypeBasic(...), ...]
    """
    pass
```

**Private methods** use one-liners:

```python
def _build_params(self, **kwargs) -> dict:
    """Build request parameters from kwargs."""
    pass
```

### § 6.2 User Documentation

Update relevant docs in `docs/`:

- `cli_guide.md` for new CLI commands
- `python_api_guide.md` for new service methods
- `api/*.rst` for API reference changes

### § 6.3 Changelog

Add entry to `docs/changelog.md`:

```markdown
## [Unreleased]

### Added
- New `get_mint()` method in MintsService
- CLI command `numistalib mints get <id>`

### Fixed
- Cache key collision for identical queries

### Changed
- Rate limit default reduced to 40 requests/minute
```

---

## § 7 Pull Request Process

### § 7.1 Before Submitting

1. **Run all checks:**

```bash
uv run ruff check --fix src/
uv run ruff format src/
uv run mypy .
uv run pyright .
uv run radon cc src/numistalib/ -a -nb
uv run xenon --max-absolute B src/numistalib/
uv run pytest tests/ -v
```

1. **Update documentation**
2. **Add tests**
3. **Update changelog**

### § 7.2 PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist

- [ ] Code follows AGENTS.md standards
- [ ] All tests pass
- [ ] Docstrings added/updated
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No increase in complexity metrics

## Testing

Describe testing performed.

## Related Issues

Closes #XX
```

### § 7.3 Review Process

0. Automated checks run on PR
1. Maintainer reviews code
2. Feedback addressed
3. Approved and merged

---

## § 8 Code Review Guidelines

### § 8.1 For Reviewers

Check:

- AGENTS.md compliance
- Test coverage
- Documentation completeness
- No complexity violations
- Type safety
- Error handling

### § 8.2 For Contributors

Expect feedback on:

- Code clarity
- Architecture fit
- Performance implications
- API design
- Testing thoroughness

Be responsive to feedback and iterate.

---

## § 9 Common Pitfalls

### § 9.1 Avoid

- Using `print()` instead of logging
- Missing type hints
- Exceeding complexity limits
- Ad-hoc client instantiation
- Unvalidated API responses
- Missing docstrings
- Bare exceptions

### § 9.2 Remember

- Read AGENTS.md before coding
- Run all quality checks before PR
- Test both sync and async paths
- Update documentation
- Follow existing patterns

---

## § 10 Getting Help

### § 10.1 Resources

- **AGENTS.md**: Authoritative coding standards
- **Architecture docs**: `docs/architecture.md`
- **API docs**: `docs/api/`
- **Examples**: Existing code in `src/numistalib/`

### § 10.2 Questions

- Open an issue for clarification
- Check existing issues/PRs
- Review similar implementations

---

## § 11 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to numistalib! 🎉
