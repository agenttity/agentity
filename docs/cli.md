# CLI Reference

## Installation

```bash
pip install agentity-cli
```

## Usage

```
agentity <command> [options]
```

## Commands

### `create`

Generate an Ed25519 keypair and signed Agent Identity Document.

```
agentity create --owner <did> [options]

Options:
  --owner TEXT     Owner DID (required)
  --scope TEXT     Scope(s), repeatable
  --ttl INTEGER    TTL in days (default: 30)
  --parent TEXT    Parent DID for delegation
  --depth INTEGER  Delegation depth (default: 0)
  -o, --output     Output file (default: stdout)
```

Example:
```bash
agentity create \
  --owner "did:agentity:human:alice" \
  --scope "api:read" --scope "api:write" \
  --output agent.json
```

### `inspect`

Parse and display an AID JSON file.

```
agentity inspect <file>

Arguments:
  file    Path to AID JSON file
```

Output: DID, status, owner, dates, scopes, parent, delegation depth, signature validity.

### `verify`

Verify AID signature, expiry, and status.

```
agentity verify <file>

Arguments:
  file    Path to AID JSON file
```

Exit code: `0` = valid, `1` = invalid.

### `sign`

Sign an HTTP request using a key file.

```
agentity sign --key <file> --url <url> [options]

Options:
  --key TEXT      Path to key/AID file (required)
  --url TEXT      Request URL (required)
  --method TEXT   HTTP method (default: GET)
  --body TEXT     Request body string
```

Outputs the three Agentity headers as JSON.

Example:
```bash
agentity sign --key agent.json \
  --url https://api.example.com/data \
  --method POST --body '{"query": "test"}'
```

### `manifest`

Generate a provider manifest JSON.

```
agentity manifest --name <name> [options]

Options:
  --name TEXT          Provider name (required)
  --description TEXT   Provider description
  --base-url TEXT      Provider base URL
  --fingerprint TEXT   Provider fingerprint
  --scopes TEXT        Comma-separated scope IDs
  -o, --output TEXT    Output file (default: stdout)
```

Example:
```bash
agentity manifest \
  --name "Stripe API" \
  --description "Payment processing" \
  --scopes "payments:read,payments:write,customers:read" \
  --output manifest.json
```
