# § GitHub Actions Workflows

## § 0 Overview

Automated quality enforcement and release management per **AGENTS.md §9**.

## § 1 Workflows

### § 1.0 release.yml

**Purpose**: Automated versioning, changelog management, and PyPI publishing.

**Triggers**:
0. Push to `main` branch (modifying `src/**`, `pyproject.toml`, or `CHANGELOG`)

1. Manual dispatch with version bump type selection (patch/minor/major)

**Actions**:
0. **Version Bump** - Uses bump2version to increment version in `pyproject.toml` and `__init__.py`

1. **Changelog Update** - Moves `[Unreleased]` section to dated version, creates new `[Unreleased]` template
2. **Git Commit & Tag** - Commits version changes and creates git tag (`v0.1.0`, etc.)
3. **Build** - Creates wheel and sdist using `uv build`
4. **PyPI Publish** - Uploads to PyPI using trusted publishing (OIDC)
5. **GitHub Release** - Creates GitHub release with changelog notes and distribution files

**Configuration**:

- `.bumpversion.cfg` - Version bump rules
- `CHANGELOG` - Keep a Changelog format
- PyPI trusted publishing (no API tokens needed)

**Manual Release**:

```bash
# Trigger via GitHub UI → Actions → Release & Publish → Run workflow
# Select bump type: patch (0.1.0 → 0.1.1), minor (0.1.0 → 0.2.0), or major (0.1.0 → 1.0.0)
```

**Automatic Release**:

- Merging to `main` with source changes triggers patch version bump
- Update `CHANGELOG` `[Unreleased]` section before merging

### § 1.1 docstring-agent.yml (Future)

**Purpose**: Maintain fastidious NumPy-style docstrings per **AGENTS.md §4.1.1**.

**Status**: Planned - awaiting CI budget allocation

## § 2 PyPI Publishing Setup

### § 2.0 Trusted Publishing (Recommended)

**One-time PyPI Setup**:

0. Go to <https://pypi.org/manage/account/publishing/>
1. Add trusted publisher:
   - **PyPI Project Name**: `numistalib`
   - **Owner**: `wells01440`
    - **Repository**: `numistalib`
   - **Workflow**: `release.yml`
   - **Environment**: (leave blank)

**No API tokens needed** - GitHub OIDC handles authentication.

### § 2.1 Alternative: API Token Method

If trusted publishing unavailable:

0. Generate PyPI API token: <https://pypi.org/manage/account/token/>
1. Add to GitHub Secrets: Settings → Secrets → `PYPI_API_TOKEN`
2. Update workflow to use token instead of OIDC

## § 3 Release Workflow

### § 3.0 Standard Release Process

0. **Develop** - Make changes in feature branch
1. **Update CHANGELOG** - Add changes under `[Unreleased]` section:

   ```markdown
   ## [Unreleased]
   
   ### Added
   - New feature X
   
   ### Changed
   - Modified behavior Y
   
   ### Fixed
   - Bug Z
   ```

2. **Create PR** - Open pull request to `main`
3. **Merge** - Workflow auto-triggers:
   - Bumps patch version (0.1.0 → 0.1.1)
   - Moves `[Unreleased]` → `[0.1.1] - 2025-12-28`
   - Creates git tag `v0.1.1`
   - Builds & publishes to PyPI
   - Creates GitHub release

### § 3.1 Manual Version Bump

For minor/major releases:

0. Navigate: GitHub → Actions → Release & Publish
1. Click "Run workflow"
2. Select branch: `main`
3. Choose bump type:
   - **patch**: 0.1.0 → 0.1.1 (bug fixes)
   - **minor**: 0.1.0 → 0.2.0 (new features, backward compatible)
   - **major**: 0.1.0 → 1.0.0 (breaking changes)
4. Click "Run workflow"

### § 3.2 Hotfix Process

0. Create hotfix branch from `main`
1. Make urgent fix
2. Update `CHANGELOG` under `[Unreleased]` → `### Fixed`
3. Merge to `main`
4. Auto-publishes patch version

## § 4 Local Testing

### § 4.0 Test Version Bump

```bash
# Install bump2version
uv sync

# Dry run (shows what would change)
uv run bump2version --dry-run --verbose patch

# Actual bump (manual, don't commit)
uv run bump2version patch
```

### § 4.1 Test Build

```bash
# Build distribution
uv build

# Check output
ls -lh dist/

# Verify wheel contents
unzip -l dist/numistalib-0.1.0-py3-none-any.whl
```

### § 4.2 Test Install

```bash
# Install from local build
uv pip install dist/numistalib-0.1.0-py3-none-any.whl

# Verify
python -c "import numistalib; print(numistalib.__version__)"
```

## § 5 Changelog Management

### § 5.0 Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/):

```markdown
## [Unreleased]

### Added
- For new features

### Changed
- For changes in existing functionality

### Deprecated
- For soon-to-be removed features

### Removed
- For now removed features

### Fixed
- For bug fixes

### Security
- For vulnerability fixes

## [1.0.0] - 2025-12-28

### Added
- Initial stable release
```

### § 5.1 Update Before Merge

**Always** update `CHANGELOG` before merging to `main`:

```bash
# Edit CHANGELOG
vim CHANGELOG

# Add under [Unreleased] section
# Example:
## [Unreleased]

### Added
- New `types.get_variants()` method
- CLI command `numistalib types variants`

### Fixed
- Cache key collision in collections service
```

Workflow automatically moves `[Unreleased]` to versioned section.

## § 6 Version Numbering

Per [Semantic Versioning](https://semver.org/):

**MAJOR.MINOR.PATCH** (e.g., `1.2.3`)

- **MAJOR**: Incompatible API changes (breaking)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Examples**:

- `0.1.0` → `0.1.1`: Bug fix (patch)
- `0.1.1` → `0.2.0`: New service added (minor)
- `0.9.9` → `1.0.0`: Stable API declared (major)
- `1.2.0` → `2.0.0`: Breaking change in client interface (major)

## § 7 Troubleshooting

### § 7.0 PyPI Upload Failed

**Check**:
0. Trusted publishing configured correctly

1. Project name matches exactly (`numistalib`)
2. Version not already published (PyPI doesn't allow overwrites)

**Solution**: Bump version again if duplicate.

### § 7.1 Git Tag Conflict

**Error**: `tag already exists`

**Solution**:

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :refs/tags/v0.1.0

# Re-run workflow
```

### § 7.2 Changelog Format Error

**Check**: `CHANGELOG` follows Keep a Changelog format:

- `## [Unreleased]` section exists
- Date format: `YYYY-MM-DD`
- Links at bottom reference GitHub tags

**Solution**: Fix format per template in § 5.0

## § 8 References

0. **AGENTS.md §9** - CI enforcement standards
1. [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
2. [Semantic Versioning](https://semver.org/)
3. [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
4. [bump2version docs](https://github.com/c4urself/bump2version)

**Triggers**:
0. Pull requests modifying `src/**/*.py`

1. Pushes to `main` branch
2. Manual via `workflow_dispatch`

**Actions**:
0. **pydocstyle** - Validates NumPy convention compliance

1. **interrogate** - Measures docstring coverage (fail-under: 80%)
2. **darglint** - Validates parameter/return documentation matches signatures
3. **Issue Creation** - Auto-files GitHub issue with validation reports when failures detected
4. **PR Comments** - Posts coverage summary on pull requests
5. **Badge Generation** - Updates `docs/docstring-coverage.svg` on main branch

**Configuration**:

- Settings in `setup.cfg`
- Dev dependencies in `pyproject.toml`

**Reference Examples**:

- `src/numistalib/services/catalogues/service.py` - Complete NumPy docstrings
- **AGENTS.md §4.1** - Docstring standards

## § 2 Local Validation

Run validation locally before committing:

```bash
# Validate NumPy convention
uv run pydocstyle --convention=numpy --add-ignore=D100,D104,D105 src/

# Check coverage
uv run interrogate --verbose --fail-under=80 --exclude tests src/

# Validate arguments
uv run darglint --docstring-style=numpy src/
```

## § 3 Standards

### § 3.1 Public APIs

**Required sections** (NumPy format):

```python
def method_name(param1: str, param2: int) -> list[str]:
    """Short one-line summary.

    Optional extended description providing additional context.

    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2

    Returns
    -------
    list[str]
        Description of return value

    Raises
    ------
    ValueError
        When invalid input provided
    """
```

### § 3.2 Private Methods

One-line docstrings only:

```python
def _internal_helper(self, data: dict) -> bool:
    """Process internal data structure."""
```

## § 4 Enforcement

**Merge Blocking**: Per **AGENTS.md §9.3**
0. All public APIs must have complete NumPy docstrings

1. Coverage must meet 80% threshold
2. Parameters/returns must match signatures

**Review Process**:
0. Workflow runs automatically on PR

1. Issues created for violations
2. PR comments guide fixes
3. Re-run after corrections

## § 5 Exceptions

Per **AGENTS.md §4.1.2**:
0. Tests excluded (`tests/` directory)

1. Private methods use simplified format
2. Magic methods may omit sections when self-evident

## § 6 References

0. **AGENTS.md §4.1** - Documentation standards
1. **AGENTS.md §9** - CI enforcement
2. [NumPy Docstring Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
3. Example: `src/numistalib/services/catalogues/service.py`
