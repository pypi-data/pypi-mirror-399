# Publishing Fluxibly to PyPI

This guide explains how to publish the fluxibly package to PyPI (Python Package Index).

## Prerequisites

Before publishing, ensure you have:

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for both PyPI and TestPyPI:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - Store tokens securely (you'll need them for publishing)

3. **Build Tools**: Install required tools:
   ```bash
   python3 -m pip install --upgrade build twine
   ```

## Pre-Publication Checklist

Before publishing, verify:

- [ ] Version number updated in `pyproject.toml`
- [ ] `README.md` is complete and accurate
- [ ] `LICENSE` file exists
- [ ] All tests pass: `uv run --frozen pytest`
- [ ] Code is formatted: `uv run --frozen ruff format .`
- [ ] Type checks pass: `uv run --frozen pyright`
- [ ] Git repository is clean (all changes committed)
- [ ] Package builds successfully: `python3 -m build`

## Version Management

Update the version in [pyproject.toml](pyproject.toml#L3):

```toml
[project]
name = "fluxibly"
version = "0.1.0"  # Update this before each release
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New functionality, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

## Building the Package

1. **Clean Previous Builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build Distribution Files**:
   ```bash
   python3 -m build
   ```

   This creates two files in `dist/`:
   - `fluxibly-X.Y.Z-py3-none-any.whl` (wheel distribution)
   - `fluxibly-X.Y.Z.tar.gz` (source distribution)

3. **Verify Build**:
   ```bash
   ls -lh dist/
   ```

## Publishing to TestPyPI (Recommended First)

Always test on TestPyPI before publishing to production PyPI.

1. **Upload to TestPyPI**:
   ```bash
   python3 -m twine upload --repository testpypi dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: Your TestPyPI API token (including `pypi-` prefix)

2. **Test Installation from TestPyPI**:
   ```bash
   # Create a test environment
   python3 -m venv test-env
   source test-env/bin/activate

   # Install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ fluxibly

   # Test the package
   python -c "import fluxibly; print(fluxibly.__version__)"

   # Cleanup
   deactivate
   rm -rf test-env
   ```

## Publishing to PyPI (Production)

Once testing is complete:

1. **Upload to PyPI**:
   ```bash
   python3 -m twine upload dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: Your PyPI API token (including `pypi-` prefix)

2. **Verify on PyPI**:
   - Visit: https://pypi.org/project/fluxibly/
   - Check that all metadata displays correctly
   - Verify the README renders properly

3. **Test Installation**:
   ```bash
   # In a new environment
   pip install fluxibly

   # Verify
   python -c "import fluxibly; print(fluxibly.__version__)"
   ```

## Using GitHub Actions (Automated Publishing)

For automated publishing on release, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

Configure trusted publishing:
1. Go to PyPI project settings
2. Enable "Trusted Publisher" with your GitHub repository
3. Add the workflow name and environment details

## Post-Publication Steps

After successful publication:

1. **Tag the Release**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

2. **Create GitHub Release**:
   - Go to: https://github.com/Lavaflux/fluxibly/releases
   - Create a new release from the tag
   - Add release notes describing changes

3. **Update Documentation**:
   - Update any version references
   - Update changelog/release notes

## Using .pypirc (Optional)

Create `~/.pypirc` to store repository configurations:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>
```

**Security Warning**: Never commit `.pypirc` to version control!

Add to `.gitignore`:
```
.pypirc
```

With `.pypirc` configured, you can publish without entering credentials:
```bash
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload dist/*
```

## Troubleshooting

### Common Issues

1. **"File already exists" error**:
   - You cannot overwrite published versions
   - Increment version number and rebuild

2. **Invalid credentials**:
   - Ensure username is `__token__` (exactly)
   - Token must include the `pypi-` prefix
   - Check token hasn't expired

3. **Upload fails**:
   - Verify internet connection
   - Check PyPI status: https://status.python.org/
   - Try again with `--verbose` flag for details

4. **README doesn't render**:
   - Check markdown syntax
   - Verify `readme` field in pyproject.toml
   - Test locally: `python3 -m readme_renderer README.md`

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning consistently**
3. **Keep detailed changelogs**
4. **Test installation in clean environments**
5. **Use API tokens instead of passwords**
6. **Never commit sensitive tokens to git**
7. **Tag releases in git**
8. **Write comprehensive release notes**

## Quick Reference

```bash
# Complete publishing workflow
rm -rf dist/ build/ *.egg-info           # Clean
python3 -m build                          # Build
python3 -m twine upload --repository testpypi dist/*  # Test
python3 -m twine upload dist/*            # Publish
git tag -a vX.Y.Z -m "Release vX.Y.Z"    # Tag
git push origin vX.Y.Z                    # Push tag
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions for PyPI](https://github.com/marketplace/actions/pypi-publish)
