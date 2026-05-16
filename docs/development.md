# Development

## Prerequisites

- Rust 1.80+
- Python 3.11+
- Node.js 20+
- pnpm 9+

## Setup

```bash
git clone https://github.com/agenttity/agentity.git
cd agentity
```

### Rust

```bash
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
```

### Python

```bash
# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install all packages in dev mode
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pip install -e packages/agentity-auth[dev]
pip install -e packages/agentity-middleware/python[dev]
pip install -e packages/agentity-cli[dev]
pip install -e packages/agentity-mcp[dev]
pip install -e packages/agentity-a2a[dev]
pip install -e packages/agentity-evm[dev]

# Run tests per package
pytest packages/agentity-sdk-python/tests
pytest packages/agentity-registry/agentity_registry/tests
pytest packages/agentity-auth/agentity_auth/tests
pytest packages/agentity-middleware/python/tests
pytest packages/agentity-mcp/tests
pytest packages/agentity-a2a/tests
pytest packages/agentity-cli/tests

# Lint
ruff check packages/agentity-sdk-python packages/agentity-registry
```

### TypeScript

```bash
pnpm install --ignore-scripts
pnpm build
pnpm test
pnpm run lint
```

## Test matrix

| Language | Tests | Run command |
|----------|-------|-------------|
| Rust | 17 | `cargo test --workspace` |
| Python | 43 | `pytest packages/*/tests packages/*/agentity_*/tests` |
| TypeScript | 19 | `pnpm test` |
| **Total** | **79** | |

## Commit convention

```
type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

Examples:
```
feat(core): add key rotation with version+1 linking
docs(registry): add WebSocket event documentation
fix(sdk): handle empty scope array in verification
```

## Branch strategy

- Branch from `develop`
- PR to `main`
- GitHub Actions runs CI on PR and push

## Publishing

### npm

```bash
pnpm publish                 # auto-replaces workspace:* deps
```

### PyPI

```bash
# Build
python -m build

# Upload
twine upload dist/*
```

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:

- Rust: test + clippy
- Python: matrix 3.11-3.13 + ruff lint
- TypeScript: test + lint
- Release: workflow_dispatch with tag + GitHub Release + npm/PyPI publish
