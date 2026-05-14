'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface Agent {
  did: string;
  status: string;
  owner_did: string;
  scopes: string[];
  created_at: string;
  expires_at?: string;
}

interface WsEvent {
  type: string;
  did: string;
  timestamp: string;
}

export default function Page() {
  const [registryUrl, setRegistryUrl] = useState('http://localhost:8000');
  const [connected, setConnected] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [revocations, setRevocations] = useState<WsEvent[]>([]);
  const [error, setError] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  const connectWs = useCallback(() => {
    const wsUrl = registryUrl.replace(/^http/, 'ws') + '/ws';
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const ev: WsEvent = JSON.parse(e.data);
        if (ev.type === 'revocation') {
          setRevocations((prev) => [ev, ...prev].slice(0, 50));
          setAgents((prev) =>
            prev.map((a) => (a.did === ev.did ? { ...a, status: 'revoked' } : a)),
          );
        }
      } catch { /* ignore */ }
    };
    ws.onerror = () => setConnected(false);
    wsRef.current = ws;
  }, [registryUrl]);

  const disconnectWs = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch(`${registryUrl}/agents`);
      if (res.ok) {
        setAgents(await res.json());
        setError('');
      }
    } catch (e: any) {
      setError(e.message);
    }
  }, [registryUrl]);

  useEffect(() => {
    return () => disconnectWs();
  }, [disconnectWs]);

  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem', maxWidth: 960, margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        Agentity Inspector
      </h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        AI Agent Identity Dashboard
      </p>

      <section style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input
          value={registryUrl}
          onChange={(e) => setRegistryUrl(e.target.value)}
          placeholder="http://localhost:8000"
          style={{ flex: 1, padding: '0.5rem', borderRadius: 6, border: '1px solid #ddd', fontSize: '0.9rem' }}
        />
        {!connected ? (
          <button onClick={() => { connectWs(); fetchAgents(); }}
            style={{ padding: '0.5rem 1rem', borderRadius: 6, border: 'none', background: '#6366f1', color: '#fff', cursor: 'pointer' }}>
            Connect
          </button>
        ) : (
          <button onClick={disconnectWs}
            style={{ padding: '0.5rem 1rem', borderRadius: 6, border: 'none', background: '#ef4444', color: '#fff', cursor: 'pointer' }}>
            Disconnect
          </button>
        )}
        <button onClick={fetchAgents}
          style={{ padding: '0.5rem 1rem', borderRadius: 6, border: '1px solid #ddd', background: '#fff', cursor: 'pointer' }}>
          Refresh
        </button>
        <span style={{ fontSize: '0.8rem', color: connected ? '#22c55e' : '#ef4444' }}>
          {connected ? '● Connected' : '○ Disconnected'}
        </span>
      </section>

      {error && (
        <div style={{ background: '#fef2f2', color: '#dc2626', padding: '0.75rem', borderRadius: 6, marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
          Active Agents ({agents.filter((a) => a.status === 'active').length})
        </h2>
        {agents.length === 0 ? (
          <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: '2rem', textAlign: 'center', color: '#999' }}>
            No agents registered yet.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {agents.map((a) => (
              <div key={a.did} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.75rem 1rem', borderRadius: 8, border: '1px solid #eee',
                background: a.status === 'active' ? '#f0fdf4' : '#fef2f2',
              }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{a.did}</div>
                  <div style={{ fontSize: '0.8rem', color: '#666' }}>
                    Owner: {a.owner_did} · Scopes: {a.scopes.join(', ') || 'none'}
                  </div>
                </div>
                <span style={{
                  padding: '0.25rem 0.75rem', borderRadius: 999, fontSize: '0.8rem',
                  background: a.status === 'active' ? '#dcfce7' : '#fecaca',
                  color: a.status === 'active' ? '#166534' : '#991b1b',
                }}>
                  {a.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
          Recent Revocations
        </h2>
        {revocations.length === 0 ? (
          <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: '2rem', textAlign: 'center', color: '#999' }}>
            No recent revocations.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {revocations.slice(0, 20).map((ev, i) => (
              <div key={i} style={{
                padding: '0.5rem 0.75rem', borderRadius: 6,
                background: '#fef2f2', border: '1px solid #fecaca',
                fontSize: '0.85rem',
              }}>
                <strong>revoked</strong> {ev.did} · {new Date(ev.timestamp).toLocaleString()}
              </div>
            ))}
          </div>
        )}
      </section>

      <footer style={{ marginTop: '3rem', paddingTop: '1rem', borderTop: '1px solid #eee', fontSize: '0.875rem', color: '#999' }}>
        Agentity Protocol v0.1
      </footer>
    </main>
  );
}
