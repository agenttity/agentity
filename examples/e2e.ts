/**
 * Agentity Protocol — TypeScript example
 */
import { AgentKeyPair, createIdentity, RequestSigner, RequestVerifier } from '@agentity/sdk';

async function main() {
  console.log('=== Agentity Protocol TypeScript Example ===\n');

  // 1. Create agent identity
  console.log('[1] Creating agent identity...');
  const kp = await AgentKeyPair.generate();
  const aid = await createIdentity(
    kp,
    'did:agentity:human:alice',
    ['stripe:payments:read', 'calendar:events:write'],
    30,
    undefined,
    0,
    { provider: 'anthropic', name: 'claude-sonnet-4-6', version: '20251001' },
  );
  console.log(`    DID:     ${aid.did}`);
  console.log(`    Owner:   ${aid.owner.did}`);
  console.log(`    Scopes:  ${aid.scope.join(', ')}`);

  // 2. Sign a request
  console.log('\n[2] Signing a request...');
  const signer = new RequestSigner(kp, aid);
  const headers = await signer.signRequest('GET', '/api/v1/payments');
  console.log(`    Agentity-Token:     ${headers['Agentity-Token']!.substring(0, 50)}...`);
  console.log(`    Agentity-Nonce:     ${headers['Agentity-Nonce']}`);
  console.log(`    Agentity-Timestamp: ${headers['Agentity-Timestamp']}`);

  // 3. Verify the request
  console.log('\n[3] Verifying request...');
  const verifier = new RequestVerifier();
  const used = new Set<string>();
  const result = await verifier.verifyRequest(headers, 'GET', '/api/v1/payments', undefined, 300, used);
  console.log(`    ✓ Verified: ${result.did}`);

  // 4. Replay detection
  console.log('\n[4] Testing replay protection...');
  try {
    await verifier.verifyRequest(headers, 'GET', '/api/v1/payments', undefined, 300, used);
    console.log('    ✗ Replay not detected!');
  } catch (e) {
    console.log(`    ✓ Replay detected: ${(e as Error).message}`);
  }

  console.log('\n=== Done ===');
}

main().catch(console.error);
