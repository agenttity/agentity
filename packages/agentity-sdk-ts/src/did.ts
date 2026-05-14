import { AgentKeyPair } from './crypto.js';

export class AgentDid {
  constructor(public readonly did: string) {}

  static fromKeypair(kp: AgentKeyPair): AgentDid {
    return new AgentDid(`did:agentity:agent:${kp.fingerprint}`);
  }

  static fromParts(didType: string, fingerprint: string): AgentDid {
    return new AgentDid(`did:agentity:${didType}:${fingerprint}`);
  }

  asStr(): string {
    return this.did;
  }

  toString(): string {
    return this.did;
  }
}
