# Build & Development Guide

## Build Process Options

ParentingBench supports multiple build workflows depending on your needs.

---

## Option 1: Make (Recommended)

**Quick Start:**
```bash
# Show all available targets
make help

# Run full build (format, lint, test, docs)
make build

# Individual targets
make docs      # Update documentation
make format    # Auto-format code
make lint      # Run linters
make test      # Run tests
```

**Common Workflows:**
```bash
# Development workflow
make install-dev    # Install deps + pre-commit hooks
make format         # Format before committing
make test           # Run tests

# Before committing
make build          # Full build check

# CI workflow
make ci             # Lint + test + docs (no formatting)
```

---

## Option 2: Pre-commit Hooks (Automatic)

Automatically update docs and format code before each commit.

**Setup:**
```bash
pip install pre-commit
pre-commit install
```

**Usage:**
```bash
# Runs automatically on git commit
git add .
git commit -m "Your message"
# → Pre-commit runs: update docs, format code, check YAML, etc.

# Run manually on all files
pre-commit run --all-files
```

**Configured hooks:**
- ✅ Update project structure in README
- ✅ Black (code formatting)
- ✅ isort (import sorting)
- ✅ YAML validation
- ✅ Remove trailing whitespace
- ✅ Check for large files

---

## Option 3: GitHub Actions (CI/CD)

Automatically check documentation on every push.

**Setup:**
Already configured in `.github/workflows/docs.yml`

**What it does:**
- Runs on push to `main` or `claude/*` branches
- Updates documentation with `python scripts/update_docs.py`
- Fails if README is out of date

**Trigger manually:**
```bash
git push origin your-branch
# → GitHub Actions runs automatically
```

---

## Option 4: Manual Script

Run the documentation updater manually.

```bash
# Update project structure in README
python scripts/update_docs.py

# Review changes
git diff README.md

# Commit if looks good
git add README.md
git commit -m "Update project structure"
```

---

## Recommended Workflow

### For Contributors:
```bash
# 1. Install with pre-commit hooks
make install-dev

# 2. Make changes to code

# 3. Run build before committing
make build

# 4. Commit (pre-commit runs automatically)
git commit -m "Your changes"
```

### For CI/CD:
```bash
# In GitHub Actions / GitLab CI
make ci
```

### For Quick Checks:
```bash
# Just update docs
make docs

# Just run tests
make test

# Just format code
make format
```

---

## Build Targets Explained

| Target | What it does | When to use |
|--------|--------------|-------------|
| `make help` | Show all targets | First time setup |
| `make install` | Install dependencies | After cloning |
| `make install-dev` | Install deps + hooks | Development setup |
| `make docs` | Update README structure | After adding/removing files |
| `make format` | Auto-format code | Before committing |
| `make lint` | Check code quality | Before committing |
| `make test` | Run all tests | Before committing |
| `make build` | Full build process | Before major commits |
| `make ci` | CI checks only | In CI/CD pipelines |
| `make clean` | Remove generated files | Clean workspace |

---

## Continuous Integration

The project is configured for CI/CD with:

### GitHub Actions
- **File**: `.github/workflows/docs.yml`
- **Triggers**: Push to main, pull requests
- **Checks**: Documentation up-to-date

### Pre-commit CI
- **File**: `.pre-commit-config.yaml`
- **Runs**: Before each commit
- **Checks**: Format, docs, YAML, etc.

---

## Troubleshooting

### "README out of date" error in CI
```bash
# Fix it:
make docs
git add README.md
git commit -m "Update project structure"
git push
```

### Pre-commit hooks not running
```bash
# Reinstall:
pre-commit uninstall
pre-commit install
```

### Make command not found
```bash
# On Ubuntu/Debian:
sudo apt-get install make

# On macOS:
xcode-select --install
```

---

## Development Dependencies

Optional tools for development:

```bash
# Pre-commit hooks
pip install pre-commit

# Type checking
pip install mypy

# Code coverage
pip install pytest-cov

# All dev deps are in requirements.txt under "Development dependencies"
```
