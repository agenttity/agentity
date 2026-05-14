import argparse
import json
import sys
import base64

from agentity_sdk import AgentKeyPair, AgentDid, RequestSigner, AgentIdentity


def cmd_create(args):
    kp = AgentKeyPair()
    did = AgentDid.from_keypair(kp)
    aid = kp.create_identity(
        owner_did=args.owner,
        scopes=args.scope,
        ttl_days=args.ttl,
        parent=args.parent,
        delegation_depth=args.depth,
    )
    data = {
        "did": aid.did,
        "publicKey": kp.public_key_b64(),
        "secretKey": kp.secret_key_b64(),
        "fingerprint": kp.fingerprint(),
        "aid": aid.model_dump(),
    }
    text = json.dumps(data, indent=2, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Saved to {args.output}")
    else:
        print(text)


def cmd_inspect(args):
    try:
        with open(args.file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    aid_json = data.get("aid") or data
    aid = AgentIdentity(**aid_json)
    print(f"DID:        {aid.did}")
    print(f"Status:     {aid.status}")
    print(f"Owner:      {aid.owner.did}")
    print(f"Created:    {aid.created}")
    print(f"Expires:    {aid.expires}")
    print(f"Expired:    {'YES' if aid.is_expired() else 'no'}")
    print(f"Scopes:     {', '.join(aid.scope)}")
    print(f"Parent:     {aid.parent or 'none'}")
    print(f"Delegation: {aid.delegationDepth}")
    print(f"Signature:  {'VALID' if aid.verify_signature() else 'INVALID'}")


def cmd_verify(args):
    try:
        with open(args.file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    aid_json = data.get("aid") or data
    aid = AgentIdentity(**aid_json)

    if not aid.verify_signature():
        print("SIGNATURE: INVALID", file=sys.stderr)
        sys.exit(1)
    if aid.is_expired():
        print("STATUS: EXPIRED", file=sys.stderr)
        sys.exit(1)
    if aid.status != "active":
        print(f"STATUS: {aid.status.upper()}", file=sys.stderr)
        sys.exit(1)
    print("VERIFIED: signature OK, status active")


def cmd_sign(args):
    with open(args.key) as f:
        kp_data = json.load(f)
    secret = base64.urlsafe_b64decode(kp_data["secretKey"] + "==")
    kp = AgentKeyPair.from_bytes(secret)
    aid = AgentIdentity(**kp_data["aid"])

    signer = RequestSigner(kp, aid)
    body = None
    if args.body:
        with open(args.body, "rb") as f:
            body = f.read()
    headers = signer.sign_headers(args.url, args.method, body)
    print(json.dumps(headers, indent=2))


def cmd_manifest(args):
    manifest = {
        "provider": f"did:agentity:provider:{args.fingerprint or 'local'}",
        "name": args.name,
        "description": args.description,
        "specVersion": "0.1",
        "baseUrl": args.base_url,
        "scopes": [],
    }
    if args.scopes:
        for s in args.scopes.split(","):
            manifest["scopes"].append({
                "id": s.strip(),
                "description": f"Scope {s.strip()}",
                "risk": "medium",
            })
    print(json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Agentity CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new agent identity")
    p_create.add_argument("--owner", required=True, help="Owner DID")
    p_create.add_argument("--scope", nargs="+", default=[], help="Scopes")
    p_create.add_argument("--ttl", type=int, default=30, help="TTL in days")
    p_create.add_argument("--parent", help="Parent DID")
    p_create.add_argument("--depth", type=int, default=0, help="Delegation depth")
    p_create.add_argument("-o", "--output", help="Output file path")

    p_inspect = sub.add_parser("inspect", help="Inspect an AID file")
    p_inspect.add_argument("file", help="AID JSON file")

    p_verify = sub.add_parser("verify", help="Verify an AID file")
    p_verify.add_argument("file", help="AID JSON file")

    p_sign = sub.add_parser("sign", help="Sign a request")
    p_sign.add_argument("--key", required=True, help="Key file (JSON)")
    p_sign.add_argument("--url", required=True, help="Request URL")
    p_sign.add_argument("--method", default="GET", help="HTTP method")
    p_sign.add_argument("--body", help="Request body file")

    p_manifest = sub.add_parser("manifest", help="Generate a provider manifest")
    p_manifest.add_argument("--name", default="My API", help="Provider name")
    p_manifest.add_argument("--description", help="Provider description")
    p_manifest.add_argument("--base-url", help="Provider base URL")
    p_manifest.add_argument("--fingerprint", help="Provider fingerprint")
    p_manifest.add_argument("--scopes", help="Comma-separated scopes")

    args = parser.parse_args()

    cmds = {
        "create": cmd_create,
        "inspect": cmd_inspect,
        "verify": cmd_verify,
        "sign": cmd_sign,
        "manifest": cmd_manifest,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
