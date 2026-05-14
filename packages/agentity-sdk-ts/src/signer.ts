import { AgentKeyPair } from './crypto.js';
import { AgentIdentity } from './identity.js';
import { sha256 } from '@noble/hashes/sha256';

export class RequestSigner {
  constructor(
    private kp: AgentKeyPair,
    private aid: AgentIdentity,
  ) {}

  async signRequest(method: string, path: string, body?: Uint8Array): Promise<Record<string, string>> {
    const nonce = crypto.randomUUID();
    const timestamp = new Date().toISOString().replace('.000', '').replace(/\.\d+Z/, 'Z');
    const bodyHash = body ? bytesToHex(sha256(body)) : undefined;
    const token = await this.aid.encodeToken(this.kp, nonce, timestamp, method, path, bodyHash);
    return {
      'Agentity-Token': token,
      'Agentity-Nonce': nonce,
      'Agentity-Timestamp': timestamp,
    };
  }
}

export class RequestVerifier {
  async verifyRequest(
    headers: Record<string, string>,
    method: string,
    path: string,
    body?: Uint8Array,
    toleranceSeconds: number = 300,
    usedNonces?: Set<string>,
  ): Promise<AgentIdentity> {
    const tokenStr = headers['Agentity-Token'];
    const nonce = headers['Agentity-Nonce'];
    const timestamp = headers['Agentity-Timestamp'];

    if (!tokenStr || !nonce || !timestamp) throw new Error('Missing Agentity headers');
    if (usedNonces?.has(nonce)) throw new Error('Nonce already used (replay attack)');

    const ts = new Date(timestamp).getTime();
    const now = Date.now();
    if (Math.abs(now - ts) > toleranceSeconds * 1000) throw new Error('Timestamp out of tolerance');

    const aid = AgentIdentity.decodeToken(tokenStr);
    if (aid.isExpired()) throw new Error('AID expired');
    if (aid.status !== 'active') throw new Error(`AID status is ${aid.status}`);

    const parts = tokenStr.split('.');
    const sig = parts[1];
    const bodyHash = body ? bytesToHex(sha256(body)) : undefined;
    const valid = await AgentKeyPair.verifyRequest(
      aid.publicKey.value, aid.did, nonce, timestamp, method, path, bodyHash, sig,
    );
    if (!valid) throw new Error('Invalid signature');

    usedNonces?.add(nonce);
    return aid;
  }
}

function bytesToHex(buf: Uint8Array): string {
  return Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join('');
}
