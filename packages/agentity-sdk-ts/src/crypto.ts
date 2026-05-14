import { sha256 } from './base58.js';
import { base58Encode } from './base58.js';
import { AgentityError } from './errors.js';

function b64Encode(buf: Uint8Array): string {
  return btoa(String.fromCharCode(...buf)).replace(/=+$/, '');
}

function b64Decode(s: string): Uint8Array {
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}

export class AgentKeyPair {
  private _secretKey: Uint8Array;
  private _publicKey: Uint8Array;

  private constructor(secretKey: Uint8Array, publicKey: Uint8Array) {
    this._secretKey = secretKey;
    this._publicKey = publicKey;
  }

  static async generate(): Promise<AgentKeyPair> {
    const { utils } = await import('@noble/ed25519');
    const privateKey = utils.randomPrivateKey();
    const { getPublicKeyAsync } = await import('@noble/ed25519');
    const publicKey = await getPublicKeyAsync(privateKey);
    return new AgentKeyPair(privateKey, publicKey);
  }

  static async fromBytes(secret: Uint8Array): Promise<AgentKeyPair> {
    if (secret.length !== 32) throw new AgentityError('Invalid secret key length');
    const { getPublicKeyAsync } = await import('@noble/ed25519');
    const publicKey = await getPublicKeyAsync(secret);
    return new AgentKeyPair(secret, publicKey);
  }

  get publicKeyBytes(): Uint8Array {
    return this._publicKey;
  }

  get publicKeyB64(): string {
    return b64Encode(this._publicKey);
  }

  get secretKeyB64(): string {
    return b64Encode(this._secretKey);
  }

  get fingerprint(): string {
    const hash = sha256(this._publicKey);
    return base58Encode(hash);
  }

  async sign(payload: Uint8Array): Promise<string> {
    const { signAsync } = await import('@noble/ed25519');
    const sig = await signAsync(payload, this._secretKey);
    return b64Encode(sig);
  }

  static async verify(publicKeyB64: string, payload: Uint8Array, sigB64: string): Promise<boolean> {
    try {
      const { verifyAsync } = await import('@noble/ed25519');
      const pk = b64Decode(publicKeyB64);
      const sig = b64Decode(sigB64);
      return await verifyAsync(sig, payload, pk);
    } catch {
      return false;
    }
  }

  async signRequest(did: string, nonce: string, timestamp: string, method: string, path: string, bodyHash?: string): Promise<string> {
    const payload = `${did}:${nonce}:${timestamp}:${method}:${path}:${bodyHash ?? ''}`;
    return this.sign(new TextEncoder().encode(payload));
  }

  static async verifyRequest(
    publicKeyB64: string, did: string, nonce: string, timestamp: string,
    method: string, path: string, bodyHash: string | undefined, sigB64: string,
  ): Promise<boolean> {
    const payload = `${did}:${nonce}:${timestamp}:${method}:${path}:${bodyHash ?? ''}`;
    return AgentKeyPair.verify(publicKeyB64, new TextEncoder().encode(payload), sigB64);
  }
}


