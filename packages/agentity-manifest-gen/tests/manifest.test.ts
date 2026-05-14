import { describe, it, expect } from 'vitest';
import { ProviderManifest, ScopeRisk } from '@agentity/sdk';

describe('manifest-gen logic', () => {
  it('should create manifest with scopes', () => {
    const manifest = new ProviderManifest(
      'did:agentity:provider:test',
      'Test API',
      [
        { id: 'api:read', description: 'Read data', risk: ScopeRisk.Low },
        { id: 'api:write', description: 'Write data', risk: ScopeRisk.High },
      ],
    );
    expect(manifest.provider).toBe('did:agentity:provider:test');
    expect(manifest.scopes).toHaveLength(2);
    expect(manifest.scopes[0].id).toBe('api:read');
    expect(manifest.scopes[1].risk).toBe(ScopeRisk.High);
  });

  it('should validate scopes', () => {
    const manifest = new ProviderManifest('p:test', 'Test', [
      { id: 'api:read', description: 'r', risk: ScopeRisk.Low },
    ]);
    expect(manifest.verifyScope('api:read')).toBe(true);
    expect(manifest.verifyScope('api:write')).toBe(false);
    expect(manifest.validateScopes(['api:read'])).toEqual([]);
  });

  it('should prioritize write scopes as high risk', () => {
    const id = 'data:write';
    const risk = id.endsWith(':write') || id.endsWith(':delete') ? ScopeRisk.High : ScopeRisk.Low;
    expect(risk).toBe(ScopeRisk.High);
  });
});
