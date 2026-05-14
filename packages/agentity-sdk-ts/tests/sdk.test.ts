import { describe, it, expect } from 'vitest';
import { AgentKeyPair, AgentDid, AgentIdentity, createIdentity, RequestSigner, RequestVerifier, ProviderManifest, ScopeRisk } from '../src/index.js';

describe('AgentKeyPair', () => {
  it('should generate keypair with valid fingerprint', async () => {
    const kp = await AgentKeyPair.generate();
    expect(kp.publicKeyBytes).toHaveLength(32);
    expect(kp.fingerprint).toBeTruthy();
  });

  it('should sign and verify', async () => {
    const kp = await AgentKeyPair.generate();
    const msg = new TextEncoder().encode('hello');
    const sig = await kp.sign(msg);
    expect(await AgentKeyPair.verify(kp.publicKeyB64, msg, sig)).toBe(true);
  });

  it('should reject bad signature', async () => {
    const kp = await AgentKeyPair.generate();
    expect(await AgentKeyPair.verify(kp.publicKeyB64, new TextEncoder().encode('msg'), 'bad')).toBe(false);
  });

  it('should create deterministic keys from bytes', async () => {
    const secret = new Uint8Array(32);
    const kp1 = await AgentKeyPair.fromBytes(secret);
    const kp2 = await AgentKeyPair.fromBytes(secret);
    expect(kp1.publicKeyB64).toBe(kp2.publicKeyB64);
  });
});

describe('AgentDid', () => {
  it('should format DID correctly', async () => {
    const kp = await AgentKeyPair.generate();
    const did = AgentDid.fromKeypair(kp);
    expect(did.asStr()).toMatch(/^did:agentity:agent:/);
  });

  it('should create DID from parts', () => {
    const did = AgentDid.fromParts('human', 'abc123');
    expect(did.asStr()).toBe('did:agentity:human:abc123');
  });
});

describe('AgentIdentity', () => {
  it('should create and verify identity', async () => {
    const kp = await AgentKeyPair.generate();
    const aid = await createIdentity(kp, 'did:agentity:human:alice', ['test:read'], 30);
    expect(aid.did).toMatch(/^did:agentity:agent:/);
    expect(aid.isExpired()).toBe(false);
    expect(aid.scope).toContain('test:read');
  });

  it('should encode and decode token', async () => {
    const kp = await AgentKeyPair.generate();
    const aid = await createIdentity(kp, 'did:agentity:human:bob', ['data:read'], 30);
    const token = await aid.encodeToken(kp, 'nonce-1', '2026-05-14T12:00:00Z', 'GET', '/api/data');
    const decoded = AgentIdentity.decodeToken(token);
    expect(decoded.did).toBe(aid.did);
  });
});

describe('RequestSigner & Verifier', () => {
  it('should sign and verify request', async () => {
    const kp = await AgentKeyPair.generate();
    const aid = await createIdentity(kp, 'did:agentity:human:carol', ['api:read'], 1);
    const signer = new RequestSigner(kp, aid);
    const headers = await signer.signRequest('GET', '/api/test');
    expect(headers['Agentity-Token']).toBeTruthy();
    expect(headers['Agentity-Nonce']).toBeTruthy();
    expect(headers['Agentity-Timestamp']).toBeTruthy();
  });

  it('should detect replay', async () => {
    const kp = await AgentKeyPair.generate();
    const aid = await createIdentity(kp, 'did:agentity:human:dave', ['svc:read'], 1);
    const signer = new RequestSigner(kp, aid);
    const headers = await signer.signRequest('GET', '/api/data');
    const verifier = new RequestVerifier();
    const used = new Set<string>();
    await verifier.verifyRequest(headers, 'GET', '/api/data', undefined, 300, used);
    await expect(verifier.verifyRequest(headers, 'GET', '/api/data', undefined, 300, used)).rejects.toThrow('replay');
  });
});

describe('ProviderManifest', () => {
  it('should match scopes exactly', () => {
    expect(ProviderManifest.scopeMatches('stripe:payments:read', 'stripe:payments:read')).toBe(true);
    expect(ProviderManifest.scopeMatches('stripe:payments:read', 'stripe:payments:write')).toBe(false);
  });

  it('should match scopes with wildcards', () => {
    expect(ProviderManifest.scopeMatches('stripe:payments:read', 'stripe:payments:*')).toBe(true);
    expect(ProviderManifest.scopeMatches('stripe:payments:read', 'stripe:*:*')).toBe(true);
    expect(ProviderManifest.scopeMatches('stripe:payments:read', '*:*:*')).toBe(true);
  });

  it('should validate scopes', () => {
    const manifest = new ProviderManifest('did:agentity:provider:test', 'Test', [
      { id: 'test:read', description: 'Read', risk: ScopeRisk.Low },
    ]);
    expect(manifest.verifyScope('test:read')).toBe(true);
    expect(manifest.verifyScope('test:write')).toBe(false);
    expect(manifest.validateScopes(['test:read'])).toEqual([]);
    expect(manifest.validateScopes(['test:write'])).toEqual(['test:write']);
  });
});
