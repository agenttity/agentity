# agentity-cli

**Command-line interface for the Agentity Protocol.**
Create agent identities, inspect AIDs, verify signatures, sign requests, and generate provider manifests.

## Installation

```bash
pip install agentity-cli
```

## Usage

```bash
# Create a new agent identity
agentity create --owner "did:agentity:human:alice" \
  --scope "api:read" --scope "api:write" --output agent.json

# Inspect an AID file
agentity inspect agent.json

# Verify signature and expiry
agentity verify agent.json

# Sign an HTTP request
agentity sign --key agent.json \
  --url https://api.example.com/data --method GET

# Generate a provider manifest
agentity manifest --name "My API" --scopes "data:read,data:write" --output manifest.json
```

## Commands

### `create`

Generate an Ed25519 keypair and create a signed Agent Identity Document.

```
Options:
  --owner TEXT         Owner DID (required)
  --scope TEXT         Scope(s), repeatable
  --ttl INTEGER        TTL in days (default: 30)
  --parent TEXT        Parent DID for delegation
  --depth INTEGER      Delegation depth (default: 0)
  -o, --output TEXT    Output file (default: stdout)
```

### `inspect`

Parse and display an AID JSON file — DID, owner, scopes, dates, status, delegation, signature validity.

```
Arguments:
  file                Path to AID JSON file
```

### `verify`

Verify the AID signature, expiry, and status. Exits with code 0 on success, 1 on failure.

```
Arguments:
  file                Path to AID JSON file
```

### `sign`

Sign an HTTP request using a key file. Outputs Agentity-Token, Agentity-Nonce, Agentity-Timestamp headers.

```
Options:
  --key TEXT           Path to key/AID file (required)
  --url TEXT           Request URL (required)
  --method TEXT        HTTP method (default: GET)
  --body TEXT          Request body string
```

### `manifest`

Generate a provider manifest JSON file.

```
Options:
  --name TEXT          Provider name (required)
  --description TEXT   Provider description
  --base-url TEXT      Provider base URL
  --fingerprint TEXT   Provider fingerprint
  --scopes TEXT        Comma-separated scope IDs (--scopes "read,write")
  -o, --output TEXT    Output file (default: stdout)
```

## Output formats

All commands accept `--output <file>` or pipe to stdout. The `inspect` and `verify` commands output human-readable text. The `create`, `sign`, and `manifest` commands output JSON.

License: Apache 2.0
