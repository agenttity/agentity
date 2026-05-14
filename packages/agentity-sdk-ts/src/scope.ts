export enum ScopeRisk {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Critical = 'critical',
}

export interface ScopeEntry {
  id: string;
  description: string;
  risk: ScopeRisk;
  requires?: string[];
}

export class ProviderManifest {
  constructor(
    public provider: string,
    public name: string,
    public scopes: ScopeEntry[],
    public description?: string,
    public specVersion: string = '0.1',
    public baseUrl?: string,
  ) {}

  static scopeMatches(needle: string, haystack: string): boolean {
    if (haystack === '*:*:*' || haystack === '*') return true;
    const needleParts = needle.split(':');
    const hayParts = haystack.split(':');
    if (needleParts.length !== hayParts.length) return false;
    return needleParts.every((n, i) => hayParts[i] === '*' || n === hayParts[i]);
  }

  verifyScope(scope: string): boolean {
    return this.scopes.some(s => ProviderManifest.scopeMatches(scope, s.id));
  }

  validateScopes(agentScopes: string[]): string[] {
    return agentScopes.filter(s => !this.verifyScope(s));
  }
}
