import { AgentKeyPair } from './crypto.js';
import { AgentDid } from './did.js';

export type AidStatus = 'active' | 'revoked' | 'expired';

export interface OwnerRef {
  did: string;
  type: string;
}

export interface ModelInfo {
  provider: string;
  name: string;
  version: string;
}

export interface Proof {
  type: string;
  created: string;
  proofValue: string;
}

export interface AgentIdentityJson {
  did: string;
  version: string;
  specVersion: string;
  created: string;
  expires: string;
  owner: OwnerRef;
  parent?: string;
  previousAid?: string;
  delegationDepth: number;
  model?: ModelInfo;
  scope: string[];
  publicKey: { type: string; value: string };
  status: AidStatus;
  proof?: Proof;
}

export class AgentIdentity {
  did: string;
  version: string;
  specVersion: string;
  created: Date;
  expires: Date;
  owner: OwnerRef;
  parent?: string;
  previousAid?: string;
  delegationDepth: number;
  model?: ModelInfo;
  scope: string[];
  publicKey: { type: string; value: string };
  status: AidStatus;
  proof?: Proof;

  constructor(data: AgentIdentityJson) {
    this.did = data.did;
    this.version = data.version;
    this.specVersion = data.specVersion;
    this.created = new Date(data.created);
    this.expires = new Date(data.expires);
    this.owner = data.owner;
    this.parent = data.parent;
    this.delegationDepth = data.delegationDepth ?? 0;
    this.model = data.model;
    this.scope = data.scope;
    this.publicKey = data.publicKey;
    this.status = data.status ?? 'active';
    this.proof = data.proof;
  }

  isExpired(): boolean {
    return new Date() > this.expires;
  }

  toJSON(): AgentIdentityJson {
    return {
      did: this.did,
      version: this.version,
      specVersion: this.specVersion,
      created: this.created.toISOString(),
      expires: this.expires.toISOString(),
      owner: this.owner,
      parent: this.parent,
      delegationDepth: this.delegationDepth,
      model: this.model,
      scope: this.scope,
      publicKey: this.publicKey,
      status: this.status,
      proof: this.proof,
    };
  }

  encodeToken(kp: AgentKeyPair, nonce: string, timestamp: string, method: string, path: string, bodyHash?: string): Promise<string> {
    const json = JSON.stringify(this.toJSON());
    const aidB64 = btoa(json).replace(/=+$/, '');
    return kp.signRequest(this.did, nonce, timestamp, method, path, bodyHash).then(sig => `${aidB64}.${sig}`);
  }

  static decodeToken(token: string): AgentIdentity {
    const parts = token.split('.');
    if (parts.length !== 2) throw new Error('Invalid token format');
    const json = atob(parts[0]);
    return new AgentIdentity(JSON.parse(json));
  }
}

export async function rotateIdentity(
  previousAid: AgentIdentity,
  kp: AgentKeyPair,
): Promise<AgentIdentity> {
  const newKp = await AgentKeyPair.generate();
  const newDid = AgentDid.fromKeypair(newKp);
  const now = new Date();
  const expires = new Date(now.getTime() + 90 * 86400000);
  const oldVersion = parseInt(previousAid.version);
  const newVersion = (oldVersion + 1).toString();

  const aid = new AgentIdentity({
    did: newDid.asStr(),
    version: newVersion,
    specVersion: previousAid.specVersion,
    created: now.toISOString(),
    expires: expires.toISOString(),
    owner: previousAid.owner,
    parent: previousAid.parent,
    previousAid: previousAid.did,
    delegationDepth: previousAid.delegationDepth,
    model: previousAid.model,
    scope: [...previousAid.scope],
    publicKey: { type: 'Ed25519VerificationKey2020', value: newKp.publicKeyB64 },
    status: 'active',
  });

  const payload = `${aid.did}:${aid.version}:${aid.created.toISOString()}:${aid.expires.toISOString()}:${[...previousAid.scope].sort().join(',')}:${previousAid.owner.did}`;
  const proofValue = await newKp.sign(new TextEncoder().encode(payload));
  aid.proof = { type: 'Ed25519Signature2020', created: now.toISOString(), proofValue };
  return aid;
}

export async function createIdentity(
  kp: AgentKeyPair,
  ownerDid: string,
  scopes: string[],
  ttlDays: number = 30,
  parent?: string,
  delegationDepth: number = 0,
  model?: ModelInfo,
): Promise<AgentIdentity> {
  const did = AgentDid.fromKeypair(kp);
  const now = new Date();
  const expires = new Date(now.getTime() + ttlDays * 86400000);

  const aid = new AgentIdentity({
    did: did.asStr(),
    version: '1',
    specVersion: '0.1',
    created: now.toISOString(),
    expires: expires.toISOString(),
    owner: { did: ownerDid, type: 'human' },
    parent,
    delegationDepth,
    model,
    scope: scopes,
    publicKey: { type: 'Ed25519VerificationKey2020', value: kp.publicKeyB64 },
    status: 'active',
  });

  const payload = `${aid.did}:${aid.version}:${aid.created.toISOString()}:${aid.expires.toISOString()}:${scopes.sort().join(',')}:${ownerDid}`;
  const proofValue = await kp.sign(new TextEncoder().encode(payload));
  aid.proof = { type: 'Ed25519Signature2020', created: now.toISOString(), proofValue };
  return aid;
}
