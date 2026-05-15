# Protocole Agentity

| 🇬🇧 [English](README.md) | 🇫🇷 [Français](README.fr.md) |
|---|---|

[![CI](https://github.com/agenttity/agentity/actions/workflows/ci.yml/badge.svg)](https://github.com/agenttity/agentity/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@agentity/sdk)](https://www.npmjs.com/package/@agentity/sdk)
[![PyPI](https://img.shields.io/pypi/v/agentity-sdk-python)](https://pypi.org/project/agentity-sdk-python/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/agenttity/agentity/blob/main/LICENSE)

**Protocole open source d'identité cryptographique pour agents IA.**

Chaque agent IA reçoit un DID compatible W3C (`did:agentity`), un document d'identité signé (AID) avec clés Ed25519, et un système de scopes validés contre les manifestes des fournisseurs de services. Chaînes de délégation, révocations en cascade, anti-replay, vérification du propriétaire via OIDC, rate limiting, rotation de clés et logs d'audit signés — conçu pour LangChain, CrewAI, Vercel AI SDK, MCP, A2A et toute infrastructure HTTP.

```
did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi
```

---

## Architecture

```
═══════════════════════════════════════════════════════════════════
                     INTERFACES UTILISATEUR
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────┐    ┌──────────────────────────────────┐
  │     agentity-cli     │    │      agentity-inspector          │
  │  create · inspect    │    │   Dashboard Next.js · WebSocket  │
  │  verify · sign       │    │   liste agents · révocations live│
  │  manifest            │    │   explorateur de scopes          │
  └──────────┬───────────┘    └──────────────┬───────────────────┘
             │                               │
             │          HTTP / WS            │
             ▼                               ▼
═══════════════════════════════════════════════════════════════════
                     COUCHE SERVICE
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-registry                         │
  │   FastAPI · PostgreSQL · Redis                               │
  │   POST /register · GET /did/{did} · POST /revoke · WS /ws   │
  │   Auth OIDC · rate limiting · logs d'audit signés            │
  └───────┬────────────────────────────────────┬─────────────────┘
          │                                    │
          │   HTTP + en-tête Agentity-Token    │
          ▼                                    ▼
  ┌─────────────────┐                ┌──────────────────────────┐
  │  agentity-sdk   │                │  agentity-middleware     │
  │  Python / TS    │◄──────────────►│  FastAPI / Express       │
  │                 │                │  vérification automatique │
  │  + agentity-mcp │                │                          │
  │  + agentity-a2a │                │                          │
  +  + agentity-auth│                │                          │
  └────────┬────────┘                └──────────────────────────┘
           │
           │    s'appuie sur
           ▼
═══════════════════════════════════════════════════════════════════
                     COUCHE IDENTITÉ
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-sdk                               │
  │  AgentKeyPair · AgentIdentity · RequestSigner · RequestVer.  │
  │  ProviderManifest · Scope matching · Chaîne de délégation    │
  │  Rotation de clés · Intégration LangChain · Vercel AI SDK    │
  └────────┬──────────────────────────────────┬──────────────────┘
           │                                  │
           ▼                                  ▼
═══════════════════════════════════════════════════════════════════
                      COUCHE CŒUR
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-core (Rust)                       │
  │  Paires de clés Ed25519 · Empreintes SHA-256 · DIDs base58   │
  │  Document d'identité agent · Signature et vérification       │
  │  Encodage de token · Filtrage de scopes avec wildcards       │
  └──────────────────────────────────────────────────────────────┘
```

### Flux d'une requête

```
Agent SDK             Middleware              Registre
    │                     │                      │
    │  1. Signe requête   │                      │
    │  avec Agent-Token   │                      │
    │────────────────────►│                      │
    │                     │  2. Vérifie token    │
    │                     │  + nonce + timestamp │
    │                     │──────────────────────►
    │                     │  3. Vérifie statut   │
    │                     │◄──────────────────────│
    │                     │  4. Valide : transmet│
    │                     │                      │
    │  5. Réponse         │                      │
    │◄────────────────────│                      │
```

---

## Packages

| Package | Langage | Description |
|---------|---------|-------------|
| `agentity-core` | Rust | Clés Ed25519, génération DID, signature/vérification AID, matching de scopes |
| `agentity-spec` | Markdown | Spécification RFC du protocole (SPEC.md) |
| `agentity-sdk-python` | Python | AgentKeyPair, AgentIdentity, RequestSigner, Intégration LangChain/CrewAI, rotation de clés |
| `agentity-sdk-ts` | TypeScript | SDK complet pour Node.js/Next.js, compatible Vercel AI SDK, rotation de clés |
| `agentity-registry` | Python | API REST FastAPI : enregistrement, lookup, révocation (cascade), logs d'audit, WebSocket, rate limiting |
| `agentity-auth` | Python | Authentification OIDC : connexion via Google, GitHub, Apple, Microsoft |
| `agentity-middleware` | Python/TS | Middleware FastAPI + Express (vérification automatique des tokens) |
| `agentity-cli` | Python | CLI : `create`, `inspect`, `verify`, `sign`, `manifest` |
| `agentity-mcp` | Python | Plugin protocole MCP Anthropic (signe les appels d'outils) |
| `agentity-a2a` | Python | Plugin protocole A2A Google (signe les requêtes agent-à-agent) |
| `agentity-inspector` | TypeScript | Dashboard Next.js — liste des agents en temps réel + révocations WebSocket |
| `agentity-manifest-gen` | TypeScript | Générateur de manifeste JSON pour fournisseur |

---

## Fonctionnalités de sécurité

| Fonctionnalité | Package | Description |
|---|---|---|
| **Auth OIDC** | `agentity-auth` | Connexion via Google/GitHub/Apple/Microsoft — `owner_did` vérifié |
| **Rate limiting** | `agentity-registry` | Limitation par DID basée sur Redis (fenêtre configurable) |
| **Rotation de clés** | SDKs | `rotate()` génère une nouvelle paire, `version+1`, référence l'AID précédent |
| **Logs d'audit signés** | `agentity-registry` | Signature HMAC-SHA256 sur chaque entrée, vérifiable via `/audit/{did}/verify` |
| **Anti-replay** | SDKs | Nonce UUID + fenêtre de 5 min |
| **Chaîne de délégation** | SDKs | Max 10 niveaux, scopes enfant ⊆ scopes parent, révocation en cascade |

---

## Démarrage rapide

### 1. Installation

```bash
# Python
pip install agentity-sdk-python agentity-registry agentity-auth

# TypeScript
pnpm add @agentity/sdk
```

### 2. Créer une identité agent

```python
from agentity_sdk import AgentKeyPair

kp = AgentKeyPair()
aid = kp.create_identity(
    owner_did="did:agentity:human:alice",
    scopes=["stripe:payments:read", "calendar:events:write"],
    ttl_days=30,
)
print(f"DID : {aid.did}")
print(f"Signature valide : {aid.verify_signature()}")
```

### 3. Signer une requête

```python
from agentity_sdk import RequestSigner

signer = RequestSigner(kp, aid)
headers = signer.sign_request("GET", "/api/v1/payments")
# headers = {
#   "Agentity-Token": "<base64url(AID)>.<base64url(signature)>",
#   "Agentity-Nonce": "<uuid-v4>",
#   "Agentity-Timestamp": "<ISO-8601>",
# }
```

### 4. Vérifier côté serveur

```python
from agentity_sdk import RequestVerifier

verifier = RequestVerifier()
used_nonces = set()
aid = verifier.verify_request(headers, "GET", "/api/v1/payments",
    used_nonces=used_nonces)
# Lève PermissionError si la requête est invalide, malformée ou rejouée
```

### 5. Ou utiliser le middleware (automatique)

```python
# FastAPI
from fastapi import FastAPI
from agentity_middleware_python import AgentityMiddleware

app = FastAPI()
app.add_middleware(AgentityMiddleware, registry_url="http://localhost:8000")
```

```typescript
// Express
import { agentityMiddleware } from '@agentity/middleware-express';
app.use(agentityMiddleware({ registryUrl: 'http://localhost:8000' }));
```

### 6. Rotation de clés

```python
new_aid = kp.rotate(aid, ttl_days=90)
print(f"Nouvelle version : {new_aid.version}")  # 2
print(f"AID précédent : {new_aid.previousAid}")
```

---

## CLI

```bash
# Créer une nouvelle identité agent
python -m agentity_cli create --owner "did:agentity:human:alice" \
  --scope "api:read" --scope "api:write" --output agent.json

# Inspecter un fichier AID
python -m agentity_cli inspect agent.json

# Vérifier une signature AID
python -m agentity_cli verify agent.json

# Signer une requête
python -m agentity_cli sign --key agent.json \
  --url https://api.example.com/data --method GET

# Générer un manifeste de fournisseur
python -m agentity_cli manifest --name "Mon API" --scopes "data:read,data:write"
```

---

## API du Registre

```bash
# Démarrer (mémoire, aucune dépendance)
uvicorn agentity_registry.main:app --port 8000

# Démarrer avec auth OIDC (Google + GitHub)
cp .env.example .env   # remplir les identifiants
uvicorn agentity_registry.main:app --port 8765

# Démarrer (PostgreSQL + Redis)
AGENTITY_STORE=postgres docker compose up -d
```

### Points d'accès

| Méthode | Chemin | Description |
|---------|--------|-------------|
| `GET` | `/health` | Vérification + type de stockage + statut auth |
| `GET` | `/auth/login/{provider}` | Connexion OIDC (google, github, apple, microsoft) |
| `GET` | `/auth/callback/{provider}` | Retour OIDC |
| `GET` | `/auth/session/{token}` | Récupérer une session propriétaire vérifiée |
| `POST` | `/register` | Enregistrer un AID |
| `GET` | `/did/{did}` | Récupérer le document AID complet |
| `GET` | `/did/{did}/status` | Statut de l'AID (actif/révoqué/expiré) |
| `POST` | `/revoke` | Révoquer un AID (cascade optionnelle) |
| `GET` | `/audit/{did}` | Logs d'audit signés pour un DID |
| `GET` | `/audit/{did}/verify` | Vérifier la signature d'une entrée d'audit |
| `GET` | `/agents` | Lister tous les agents enregistrés |
| `WS` | `/ws` | WebSocket — événements de révocation en temps réel |

### Modes de stockage

| `AGENTITY_STORE` | Stockage | Dépendances |
|---|---|---|
| `memory` (défaut) | Dictionnaire en mémoire | Aucune |
| `postgres` | PostgreSQL + Redis | `docker compose up` |

---

## Développement

```bash
# Cloner
git clone https://github.com/agenttity/agentity.git
cd agentity

# Rust
. "$HOME/.cargo/env"
cargo test --workspace                            # 17 tests

# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pip install -e packages/agentity-auth[dev]
pip install -e packages/agentity-middleware/python[dev]
pip install -e packages/agentity-cli[dev]
pip install -e packages/agentity-mcp[dev]
pip install -e packages/agentity-a2a[dev]

pytest packages/agentity-sdk-python/tests          # 10 tests
pytest packages/agentity-registry/agentity_registry/tests  # 6 tests
pytest packages/agentity-auth/agentity_auth/tests  # 5 tests
pytest packages/agentity-middleware/python/tests   # 6 tests
pytest packages/agentity-mcp/tests                 # 4 tests
pytest packages/agentity-a2a/tests                 # 4 tests
pytest packages/agentity-cli/tests                 # 4 tests

# TypeScript
pnpm install --ignore-scripts
pnpm build
pnpm test                                          # 19 tests TS

# Tout en une commande
cargo test --workspace && pnpm test && pytest ...  # 74 tests au total
```

---

## Licence

Apache 2.0 — voir [LICENSE](LICENSE).
