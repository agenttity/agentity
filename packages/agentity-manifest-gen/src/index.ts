#!/usr/bin/env node
import { ProviderManifest, ScopeRisk } from '@agentity/sdk';
import * as fs from 'fs';

function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: agentity-manifest-gen <provider-name> <scope-id> [scope-id...]');
    process.exit(1);
  }

  const name = args[0];
  const scopeIds = args.slice(1);

  const manifest = new ProviderManifest(
    `did:agentity:provider:${name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
    name,
    scopeIds.map(id => ({
      id,
      description: `Scope ${id}`,
      risk: id.endsWith(':write') || id.endsWith(':delete') ? ScopeRisk.High : ScopeRisk.Low,
    })),
  );

  const output = {
    provider: manifest.provider,
    name: manifest.name,
    specVersion: manifest.specVersion,
    scopes: manifest.scopes,
  };

  const outPath = 'agentity-manifest.json';
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log(`Manifest written to ${outPath}`);
}

main();
