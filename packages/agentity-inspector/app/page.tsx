export default function Page() {
  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem', maxWidth: 960, margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        Agentity Inspector
      </h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        AI Agent Identity Dashboard
      </p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
          Active Agents
        </h2>
        <div style={{
          border: '1px solid #ddd', borderRadius: 8, padding: '2rem',
          textAlign: 'center', color: '#999',
        }}>
          Connect to a registry to view active agents.
        </div>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
          Recent Revocations
        </h2>
        <div style={{
          border: '1px solid #ddd', borderRadius: 8, padding: '2rem',
          textAlign: 'center', color: '#999',
        }}>
          No recent revocations.
        </div>
      </section>

      <section>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
          Scope Explorer
        </h2>
        <div style={{
          border: '1px solid #ddd', borderRadius: 8, padding: '2rem',
          textAlign: 'center', color: '#999',
        }}>
          Load a provider manifest to explore scopes.
        </div>
      </section>

      <footer style={{ marginTop: '3rem', paddingTop: '1rem', borderTop: '1px solid #eee', fontSize: '0.875rem', color: '#999' }}>
        Agentity Protocol v0.1
      </footer>
    </main>
  );
}
