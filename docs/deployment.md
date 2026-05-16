# Deployment

## Quick start (Docker Compose)

```bash
# Clone
git clone https://github.com/agenttity/agentity.git
cd agentity

# Configure OIDC (optional)
cp .env.example .env
# Edit .env with your Google/GitHub OAuth2 credentials

# Start all services
docker compose up -d
```

This starts:
- Registry API on `http://localhost:8765`
- PostgreSQL on `:5432`
- Redis on `:6379`

## Production configuration

### Environment variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `AGENTITY_STORE` | `memory` | No | `memory` or `postgres` |
| `DATABASE_URL` | — | If postgres | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379` | If postgres | Redis connection string |
| `HOST` | `0.0.0.0` | No | Bind address |
| `PORT` | `8000` | No | Port |

### OIDC variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | If using Google | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | If using Google | Google OAuth2 client secret |
| `GITHUB_CLIENT_ID` | If using GitHub | GitHub OAuth2 client ID |
| `GITHUB_CLIENT_SECRET` | If using GitHub | GitHub OAuth2 client secret |

Apple and Microsoft follow the same pattern.

### EVM bridge variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENTITY_EVM_RPC_URL` | If using EVM | EVM RPC endpoint |
| `AGENTITY_EVM_CONTRACT` | If using EVM | Deployed contract address |
| `AGENTITY_EVM_PRIVATE_KEY` | If using EVM | Wallet private key |
| `AGENTITY_EVM_CHAIN_ID` | No | Default `1337` |

## Docker Compose

See `docker-compose.yml` at repo root. Configuration includes:

```yaml
services:
  registry:
    build: packages/agentity-registry
    ports: ["8765:8000"]
    env_file: .env
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
```

## Manual deployment

```bash
# Install
pip install agentity-registry agentity-auth

# Start with PostgreSQL
AGENTITY_STORE=postgres \
DATABASE_URL=postgresql://user:pass@host:5432/agentity \
REDIS_URL=redis://host:6379/0 \
uvicorn agentity_registry.main:app --host 0.0.0.0 --port 8000
```

## Deploying the inspector

```bash
cd packages/agentity-inspector
pnpm build     # static export → out/
```

Deploy `out/` to any static host. Configure the registry URL in the UI.

## Deploying the website

The landing page auto-deploys via Vercel GitHub integration. See `vercel.json`:

```json
{
  "rootDirectory": "packages/agentity-website"
}
```

## Health check

```
GET /health
```

Returns store type and auth status:
```json
{
  "status": "ok",
  "store": "postgres",
  "auth": true
}
```
