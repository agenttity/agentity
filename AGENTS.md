# AGENTS.md — Agentity Protocol

## Repo structure

Monorepo, 3 languages, 11 packages under `packages/`. GitHub org is **`agenttity`** (double t).

| Lang | Packages | Tech |
|---|---|---|
| Rust | `agentity-core` | ed25519-dalek, 17 tests |
| Python | `agentity-sdk-python`, `agentity-registry`, `agentity-middleware/python`, `agentity-cli`, `agentity-mcp`, `agentity-a2a` | FastAPI, pytest, ruff |
| TS | `agentity-sdk-ts`, `agentity-middleware/typescript`, `agentity-inspector`, `agentity-manifest-gen` | pnpm, vitest, Next.js 15 |

## Build / test / lint

### Rust
```
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
```
- `verify_request` has 8 args → needs `#[allow(clippy::too_many_arguments)]`

### Python
```
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pip install -e packages/agentity-middleware/python[dev]
pip install -e packages/agentity-mcp[dev]
pip install -e packages/agentity-a2a[dev]
pip install -e packages/agentity-cli[dev]
```
Test per-package (never `pytest packages/` — too broad):
```
pytest packages/agentity-sdk-python/tests
pytest packages/agentity-registry/agentity_registry/tests
pytest packages/agentity-middleware/python/tests
pytest packages/agentity-mcp/tests
pytest packages/agentity-a2a/tests
pytest packages/agentity-cli/tests
```
Lint: `ruff check packages/agentity-sdk-python packages/agentity-registry`

### TypeScript
```
pnpm install --ignore-scripts    # CI: avoids blocked esbuild/sharp builds
pnpm build                       # tsc for each package
pnpm test                        # vitest run for each
pnpm run lint                    # tsc --noEmit for each
```

## Architecture notes

- **Core Rust** is reference implementation. Python and TS SDKs reimplement crypto independently (no FFI/bindings).
- **Registry** store switchable via `AGENTITY_STORE=memory|postgres`. Memory = no deps, prod uses Docker Compose (postgres + redis).
- **pnpm workspace** includes `agentity-cli` (Python package) — harmless, pnpm ignores non-JS packages.
- `.gitignore` has `**/dist/`. For npm publish, each TS `package.json` must have `"files": ["dist"]` to override gitignore.
- `workspace:*` deps in package.json → use `pnpm publish` (not `npm publish`) to auto-replace with semver on publish.
- **Inspector** is Next.js 15 static export (`next build`).

## Key conventions

- Commits: `type(scope): description` (feat/fix/docs/refactor/test/chore/ci)
- License: MIT
- Branch from `develop`, PR to `main`
- CLI entrypoint: `packages/agentity-cli/agentity_cli/main.py`
- Docker Compose at root: `docker compose up -d` starts registry + postgres + redis
