# DevHand CLI

[![PyPI](https://img.shields.io/pypi/v/devhand)](https://pypi.org/project/devhand/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-69%25-brightgreen)](htmlcov/index.html)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Context-aware CLI tool to improve developer experience for full-stack webapps.

## Installation

Install devhand globally using uv:

```bash
# From your workspace root
cd devhand
uv pip install -e .
```

Or install as a uv tool:

```bash
uv tool install /path/to/devhand
```

## Quick Start

From your workspace root (parent directory of frontend/backend projects):

1. **Setup your environment:**
   ```bash
   dh setup
   ```

2. **Validate environment:**
   ```bash
   dh validate
   ```

3. **Start development server:**
   ```bash
   cd hello-world-fe  # or hello-world-be
   dh dev
   ```

## Available Commands

- `dh setup` - Interactive environment setup
- `dh validate` - Check environment health
- `dh validate --deploy` - Check for deployment completion
- `dh dev` - Start dev server (context-aware)
- `dh build` - Build for production
- `dh build --docker` - Build Docker image
- `dh db migrate` - Run migrations
- `dh db sync-users` - Sync allowed users
- `dh clean` - Remove artifacts

See full documentation in the repository.
