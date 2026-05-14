import type { Request, Response, NextFunction } from 'express';
import { AgentKeyPair, AgentIdentity } from '@agentity/sdk';
import { sha256 } from '@noble/hashes/sha256';

export interface AgentityMiddlewareOptions {
  registryUrl?: string;
  toleranceSeconds?: number;
}

export function agentityMiddleware(opts: AgentityMiddlewareOptions = {}) {
  const usedNonces = new Set<string>();
  const tolerance = opts.toleranceSeconds ?? 300;

  return async (req: Request, res: Response, next: NextFunction) => {
    if (req.path === '/health') return next();

    const token = req.headers['agentity-token'] as string;
    const nonce = req.headers['agentity-nonce'] as string;
    const timestamp = req.headers['agentity-timestamp'] as string;

    if (!token || !nonce || !timestamp) {
      res.status(401).json({ error: 'Missing Agentity headers' });
      return;
    }

    if (usedNonces.has(nonce)) {
      res.status(403).json({ error: 'Nonce replayed' });
      return;
    }

    const ts = new Date(timestamp).getTime();
    if (Math.abs(Date.now() - ts) > tolerance * 1000) {
      res.status(403).json({ error: 'Timestamp out of tolerance' });
      return;
    }

    try {
      const aid = AgentIdentity.decodeToken(token);
      if (aid.isExpired()) {
        res.status(403).json({ error: 'AID expired' });
        return;
      }

      const parts = token.split('.');
      const sig = parts[1];
      const bodyStr = JSON.stringify(req.body || {});
      const bodyHash = bytesToHex(sha256(new TextEncoder().encode(bodyStr)));
      const valid = await AgentKeyPair.verifyRequest(
        aid.publicKey.value, aid.did, nonce, timestamp,
        req.method, req.path, bodyHash, sig,
      );
      if (!valid) {
        res.status(403).json({ error: 'Invalid signature' });
        return;
      }

      usedNonces.add(nonce);
      (req as any).agentDid = aid.did;
      (req as any).agentScopes = aid.scope;
      next();
    } catch (err) {
      res.status(400).json({ error: 'Invalid token' });
    }
  };
}

function bytesToHex(buf: Uint8Array): string {
  return Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join('');
}
