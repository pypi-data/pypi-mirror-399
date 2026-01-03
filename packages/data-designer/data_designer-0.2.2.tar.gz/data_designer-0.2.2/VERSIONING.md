# Versioning Guide

DataDesigner uses **semantic versioning** with automated version management via `hatch-vcs`.

## How It Works

Versions are automatically derived from git tags:

- **No tag**: `0.1.0.dev<N>+g<commit-hash>` (development version)
- **Tagged commit**: `1.2.3` (release version)
- **After tag**: `1.2.4.dev<N>+g<commit-hash>` (next development version)

## Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

## Creating a Release

When ready to release version `X.Y.Z`:

```bash
# Tag the release
git tag vX.Y.Z

# Push the tag
git push origin vX.Y.Z

# Build and publish
uv build
uv publish
```

Example:
```bash
git tag v0.1.0
git push origin v0.1.0
```

## Accessing Version in Code

Users can access the version:

```python
import data_designer

print(data_designer.__version__)
# Output: 0.1.0 (or 0.1.0.dev18+ga7496d01a if between releases)
```

## Technical Details

- Version source: Git tags via `hatch-vcs`
- Version file: `src/data_designer/_version.py` (auto-generated, not tracked in git)
- Fallback strategy:
  1. Try to import from `_version.py` (generated during build)
  2. Fall back to `importlib.metadata.version()` (works for editable installs)
  3. Final fallback: `0.0.0.dev0+unknown` (if package not installed)
- Configuration: [pyproject.toml](pyproject.toml)

## For Collaborators

When you clone the repository and run `uv sync`, you won't have `_version.py` in your local directory. This is expected! The version system has a fallback:

```bash
git clone <repo>
uv sync
uv run python -c "from data_designer import __version__; print(__version__)"
# Works! Uses importlib.metadata fallback
```

The `_version.py` file is auto-generated during:
- Editable installs (`uv pip install -e .`)
- Package builds (`uv build`)
- CI/CD builds

You don't need to commit or manually create this file.

## Development Workflow

1. **During development**: Commit normally, version auto-increments as dev versions
2. **Ready to release**: Create and push a git tag (e.g., `v0.1.0`)
3. **After release**: Continue development, version becomes next dev version (e.g., `0.1.1.dev1`)

No manual version bumping required!
