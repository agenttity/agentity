import { AgentKeyPair, AgentIdentity } from '@agentity/sdk';
import { sha256 } from '@noble/hashes/sha256';
export function agentityMiddleware(opts = {}) {
    const usedNonces = new Set();
    const tolerance = opts.toleranceSeconds ?? 300;
    return async (req, res, next) => {
        if (req.path === '/health')
            return next();
        const token = req.headers['agentity-token'];
        const nonce = req.headers['agentity-nonce'];
        const timestamp = req.headers['agentity-timestamp'];
        if (!token || !nonce || !timestamp) {
            res.status(401).json({ error: 'Missing Agentity headers' });
            return;
        }
        if (usedNonces.has(nonce)) {
            res.status(403).json({ error: 'Nonce replayed' });
            return;
        }
        usedNonces.add(nonce);
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
            const valid = await AgentKeyPair.verifyRequest(aid.publicKey.value, aid.did, nonce, timestamp, req.method, req.path, bodyHash, sig);
            if (!valid) {
                res.status(403).json({ error: 'Invalid signature' });
                return;
            }
            req.agentDid = aid.did;
            req.agentScopes = aid.scope;
            next();
        }
        catch (err) {
            res.status(400).json({ error: 'Invalid token' });
        }
    };
}
function bytesToHex(buf) {
    return Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join('');
}
