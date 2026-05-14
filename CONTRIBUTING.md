# Contributing

## Development Setup

```bash
git clone https://github.com/agenttity/agentity.git
cd agentity

# Rust
cargo build --workspace
cargo test --workspace

# Python
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pytest packages/

# TypeScript
pnpm install
pnpm build
pnpm test
```

## Commit Convention

`type(scope): description`

Types: feat, fix, docs, refactor, test, chore, ci

## Pull Request Process

1. Create a feature branch from `develop`
2. Add tests for new functionality
3. Ensure CI passes
4. Request review from a maintainer
