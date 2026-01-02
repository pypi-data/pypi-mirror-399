# § PyPI Publishing Setup

## § 0 Quick Start

Follow these steps **once** to enable automated PyPI publishing.

## § 1 PyPI Account Setup

### § 1.0 Create PyPI Account

0. Visit <https://pypi.org/account/register/>
1. Create account with email verification
2. Enable 2FA (required for publishing)

### § 1.1 Register Project Name

**First time only** - reserve the package name:

```bash
# Build package locally
uv build

# Install twine for manual upload
uv pip install twine

# Upload first release (creates project on PyPI)
uv run twine upload dist/numistalib-0.1.0*
# Enter PyPI username and password when prompted
```

**Alternative**: Register via web UI at <https://pypi.org/manage/projects/>

## § 2 Configure Trusted Publishing

**Recommended method** - no API tokens needed.

### § 2.0 Add Publisher on PyPI

0. Go to <https://pypi.org/manage/account/publishing/>
1. Scroll to "Add a new pending publisher"
2. Fill in:

   ```
   PyPI Project Name: numistalib
   Owner: wells01440

  Repository name: numistalib
   Workflow name: release.yml
   Environment name: (leave blank)

   ```

3. Click "Add"

### § 2.1 Verify Configuration

After first workflow run (even if it fails initially), you can verify at:
<https://pypi.org/manage/project/numistalib/settings/publishing/>

The pending publisher becomes active after first successful publish.

## § 3 Alternative: API Token Method

If trusted publishing doesn't work:

### § 3.0 Generate PyPI Token

0. Go to <https://pypi.org/manage/account/token/>
1. Click "Add API token"
2. Token name: `GitHub Actions - numistalib`
3. Scope: "Project: numistalib"
4. Click "Add token"
5. **Copy token immediately** (shown only once)

### § 3.1 Add to GitHub Secrets

0. Go to <https://github.com/wells01440/numistalib/settings/secrets/actions>
1. Click "New repository secret"
2. Name: `PYPI_API_TOKEN`
3. Value: (paste token from § 3.0)
4. Click "Add secret"

### § 3.2 Update Workflow

Edit `.github/workflows/release.yml`:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

Remove the `id-token: write` permission from the top.

## § 4 Test Release

### § 4.0 Manual Test

0. Go to <https://github.com/wells01440/numistalib/actions/workflows/release.yml>
1. Click "Run workflow"
2. Branch: `main`
3. Bump type: `patch`
4. Click "Run workflow"
5. Monitor execution in Actions tab

### § 4.1 Verify Success

**Check PyPI**:

- <https://pypi.org/project/numistalib/>

**Check GitHub Release**:

- <https://github.com/wells01440/numistalib/releases>

**Test Install**:

```bash
pip install numistalib
python -c "import numistalib; print(numistalib.__version__)"
```

## § 5 Troubleshooting

### § 5.0 First Publish Fails - Project Not Found

**Problem**: PyPI project doesn't exist yet.

**Solution**: Do manual first upload (see § 1.1) or:

1. Visit <https://pypi.org/manage/account/publishing/>
2. Add as "pending publisher"
3. First workflow run will create project

### § 5.1 Authentication Error

**Problem**: `403 Forbidden` or authentication failure.

**Solution**:
0. **Trusted publishing**: Verify exact spelling of `numistalib`, `wells01440`, `numistalib`, `release.yml`

1. **API token**: Regenerate token, ensure it's scoped to project, update secret

### § 5.2 Version Already Exists

**Problem**: `400 Bad Request - File already exists`

**Solution**: PyPI doesn't allow re-uploading same version:

```bash
# Bump version again
uv run bump2version patch  # 0.1.1 → 0.1.2
git push origin main --follow-tags
```

### § 5.3 Tag Exists

**Problem**: Workflow fails because git tag already created.

**Solution**:

```bash
# Delete local and remote tag
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1

# Re-run workflow
```

## § 6 Production Checklist

Before first release to PyPI:

- [ ] PyPI account created with 2FA enabled
- [ ] Project name `numistalib` registered (manual first upload or pending publisher)
- [ ] Trusted publishing configured at PyPI
- [ ] `CHANGELOG.md` updated with release notes
- [ ] All tests passing locally: `uv run pytest`
- [ ] Build successful: `uv build`
- [ ] README.md has PyPI badge ready:

  ```markdown
  ![PyPI](https://img.shields.io/pypi/v/numistalib)
  ```

- [ ] Documentation built successfully: `cd docs && uv run sphinx-build -b html . _build/html`
- [ ] Version number correct in `pyproject.toml` and `src/numistalib/__init__.py`

## § 7 Post-Setup Workflow

**After one-time setup**, normal workflow is:

0. Develop feature
1. Update `CHANGELOG.md` under `[Unreleased]`
2. Open PR to `main`
3. Merge → **automatic release**
4. Check <https://pypi.org/project/numistalib/>
5. Verify install: `pip install -U numistalib`

**Manual version control**:

- Go to Actions → Release & Publish → Run workflow
- Select bump type (patch/minor/major)
- Workflow handles everything

## § 8 References

0. [PyPI Trusted Publishers Guide](https://docs.pypi.org/trusted-publishers/)
1. [PyPI Help - First Upload](https://pypi.org/help/#publishing)
2. [GitHub Actions - PyPI Publish](https://github.com/pypa/gh-action-pypi-publish)
3. **AGENTS.md §9** - CI standards
