# @agentity/manifest-gen

**CLI tool to generate Agentity provider manifests.**
Create a signed `agentity-manifest.json` file declaring your service's scopes, risk levels, and dependencies.

## Installation

```bash
pnpm add -g @agentity/manifest-gen
```

## Usage

```bash
agentity-manifest-gen "Stripe API" payments:read payments:write customers:read
```

Outputs `agentity-manifest.json`:

```json
{
  "provider": "did:agentity:provider:stripe-api",
  "name": "Stripe API",
  "specVersion": "0.1",
  "scopes": [
    { "id": "payments:read", "description": "payments:read", "risk": "low" },
    { "id": "payments:write", "description": "payments:write", "risk": "high" },
    { "id": "customers:read", "description": "customers:read", "risk": "low" }
  ]
}
```

Risk is auto-assigned: scopes ending in `:write` or `:delete` get `high` risk; all others get `low`.

## Arguments

```
Usage: agentity-manifest-gen <provider-name> <scope-id> [scope-id...]
```

License: Apache 2.0
