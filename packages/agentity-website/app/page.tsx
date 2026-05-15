export default function Home() {
  return (
    <main>
      <Hero />
      <ProblemSolution />
      <HowItWorks />
      <Architecture />
      <QuickStart />
      <Registry />
      <Footer />
    </main>
  );
}

function Hero() {
  return (
    <header className="px-6 pt-32 pb-24 text-center max-w-3xl mx-auto">
      <p className="text-indigo-400 text-sm font-medium tracking-widest uppercase mb-6">Open Source · Apache 2.0</p>
      <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
        Identity for <span className="text-indigo-400">AI Agents</span>
      </h1>
      <p className="text-lg md:text-xl text-zinc-400 leading-relaxed mb-10">
        Every AI agent gets a W3C-compatible DID, a signed identity document with Ed25519 keys,
        and a scope system validated against provider manifests — designed for LangChain,
        CrewAI, Vercel AI SDK, MCP, and any HTTP infrastructure.
      </p>
      <div className="flex flex-wrap justify-center gap-4">
        <a href="https://github.com/agenttity/agentity" className="bg-indigo-500 hover:bg-indigo-400 text-white px-6 py-3 rounded-lg font-medium transition-colors">
          GitHub
        </a>
        <a href="https://www.npmjs.com/package/@agentity/sdk" className="bg-zinc-800 hover:bg-zinc-700 text-zinc-100 px-6 py-3 rounded-lg font-medium transition-colors">
          npm · @agentity/sdk
        </a>
        <a href="https://pypi.org/project/agentity-sdk-python/" className="bg-zinc-800 hover:bg-zinc-700 text-zinc-100 px-6 py-3 rounded-lg font-medium transition-colors">
          PyPI · agentity-sdk-python
        </a>
      </div>
      <p className="mt-8 text-sm text-zinc-600 font-mono">did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi</p>
    </header>
  );
}

function ProblemSolution() {
  return (
    <section className="px-6 py-24 max-w-5xl mx-auto">
      <div className="grid md:grid-cols-2 gap-12">
        <div className="bg-zinc-900/50 rounded-xl p-8 border border-zinc-800">
          <p className="text-red-400 text-sm font-semibold mb-4">The Problem</p>
          <h2 className="text-2xl font-bold mb-4">Agents have no identity</h2>
          <p className="text-zinc-400 leading-relaxed">
            AI agents calling APIs today cannot prove who controls them, what they are allowed to do,
            or who is responsible for their actions. OAuth2, JWT, and API keys were designed for humans
            and static apps — not for autonomous, ephemeral software entities.
          </p>
        </div>
        <div className="bg-zinc-900/50 rounded-xl p-8 border border-zinc-800">
          <p className="text-emerald-400 text-sm font-semibold mb-4">The Solution</p>
          <h2 className="text-2xl font-bold mb-4">Three questions</h2>
          <ul className="space-y-4">
            <li className="flex gap-3">
              <span className="text-indigo-400 font-bold shrink-0">1.</span>
              <div><span className="font-semibold">Who are you?</span><p className="text-zinc-400 text-sm mt-1">Verifiable identity via Ed25519 key + self-signed DID</p></div>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-400 font-bold shrink-0">2.</span>
              <div><span className="font-semibold">What can you do?</span><p className="text-zinc-400 text-sm mt-1">Scopes validated against provider manifests</p></div>
            </li>
            <li className="flex gap-3">
              <span className="text-indigo-400 font-bold shrink-0">3.</span>
              <div><span className="font-semibold">Who is responsible?</span><p className="text-zinc-400 text-sm mt-1">Delegation chain rooted in a human via OIDC</p></div>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  return (
    <section className="px-6 py-24 max-w-5xl mx-auto text-center">
      <p className="text-indigo-400 text-sm font-semibold mb-4">How It Works</p>
      <h2 className="text-3xl font-bold mb-12">Three steps</h2>
      <div className="grid md:grid-cols-3 gap-8 text-left">
        {[
          { step: '01', title: 'Create Identity', desc: 'Generate an Ed25519 keypair, create a self-signed Agent Identity Document (AID)', code: 'kp = AgentKeyPair()\naid = kp.create_identity("human:alice", ["payments:read"])' },
          { step: '02', title: 'Sign Requests', desc: 'Every HTTP request carries the AID, a nonce, a timestamp, and an Ed25519 signature', code: 'signer = RequestSigner(kp, aid)\nheaders = signer.sign_request("GET", "/api/v1/payments")' },
          { step: '03', title: 'Verify', desc: 'The server verifies the signature, checks anti-replay, validates scopes, and confirms via Registry', code: 'verifier = RequestVerifier()\naid = verifier.verify_request(headers, "GET", "/api/v1/payments")' },
        ].map((item) => (
          <div key={item.step} className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
            <p className="text-indigo-400 text-sm font-bold mb-2">{item.step}</p>
            <h3 className="font-semibold mb-2">{item.title}</h3>
            <p className="text-zinc-400 text-sm mb-4">{item.desc}</p>
            <pre className="bg-zinc-950 rounded-lg p-3 text-xs text-zinc-300 overflow-x-auto"><code>{item.code}</code></pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function Architecture() {
  const features = [
    { title: 'OIDC Auth', desc: 'Google, GitHub, Apple, Microsoft login — verified owner_did' },
    { title: 'Rate Limiting', desc: 'Redis-based per-DID rate limiting with configurable windows' },
    { title: 'Key Rotation', desc: 'version+1, previousAid link, TTL-based expiration' },
    { title: 'Signed Audit Log', desc: 'HMAC-SHA256 on every entry, verifiable via API' },
    { title: 'Anti-Replay', desc: 'UUID nonce + 5 min timestamp window' },
    { title: 'Delegation Chain', desc: 'Max 10 levels, child ⊆ parent scopes, cascade revocation' },
  ];
  return (
    <section className="px-6 py-24 max-w-5xl mx-auto">
      <p className="text-indigo-400 text-sm font-semibold mb-4 text-center">Architecture</p>
      <h2 className="text-3xl font-bold mb-12 text-center">Four layers</h2>
      <div className="space-y-3 mb-16">
        {[
          { layer: 'User Interfaces', items: 'CLI · Inspector (Next.js dashboard)' },
          { layer: 'Service Layer', items: 'Registry (FastAPI, PostgreSQL, Redis) · Middleware (FastAPI, Express)' },
          { layer: 'Identity Layer', items: 'SDKs (Python, TypeScript) · MCP · A2A · OIDC Auth' },
          { layer: 'Core', items: 'Rust — Ed25519 · DID · AID · Scope matching' },
        ].map((l) => (
          <div key={l.layer} className="bg-zinc-900/50 rounded-lg px-5 py-3 border border-zinc-800 flex flex-wrap gap-x-4">
            <span className="text-indigo-400 text-sm font-semibold shrink-0">{l.layer}</span>
            <span className="text-zinc-400 text-sm">{l.items}</span>
          </div>
        ))}
      </div>
      <h3 className="text-xl font-semibold mb-6 text-center">Security features</h3>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((f) => (
          <div key={f.title} className="bg-zinc-900/50 rounded-lg px-5 py-4 border border-zinc-800">
            <p className="font-semibold text-sm mb-1">{f.title}</p>
            <p className="text-zinc-400 text-xs">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function QuickStart() {
  return (
    <section className="px-6 py-24 max-w-3xl mx-auto">
      <p className="text-indigo-400 text-sm font-semibold mb-4 text-center">Quick Start</p>
      <h2 className="text-3xl font-bold mb-8 text-center">Install in seconds</h2>
      <div className="space-y-6">
        {[
          { label: 'Python', code: 'pip install agentity-sdk-python agentity-registry agentity-auth' },
          { label: 'TypeScript', code: 'pnpm add @agentity/sdk' },
          { label: 'CLI', code: 'python -m agentity_cli create --owner "did:agentity:human:alice" --scope "api:read"' },
          { label: 'Docker', code: 'docker compose up -d' },
        ].map((item) => (
          <div key={item.label} className="bg-zinc-900/50 rounded-lg p-4 border border-zinc-800">
            <p className="text-xs text-zinc-500 mb-1">{item.label}</p>
            <pre className="text-sm text-zinc-200 overflow-x-auto"><code>{item.code}</code></pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function Registry() {
  const endpoints = [
    ['GET', '/health', 'Health check + auth status'],
    ['GET', '/auth/login/{provider}', 'OIDC login (google, github)'],
    ['POST', '/register', 'Register an AID'],
    ['GET', '/did/{did}', 'Get AID document'],
    ['GET', '/did/{did}/status', 'Get AID status'],
    ['POST', '/revoke', 'Revoke an AID (cascade)'],
    ['GET', '/audit/{did}', 'Signed audit log'],
    ['WS', '/ws', 'Real-time revocation events'],
  ];
  return (
    <section className="px-6 py-24 max-w-4xl mx-auto">
      <p className="text-indigo-400 text-sm font-semibold mb-4 text-center">Registry API</p>
      <h2 className="text-3xl font-bold mb-8 text-center">Self-hostable</h2>
      <p className="text-zinc-400 text-center mb-10 max-w-xl mx-auto">
        The registry is a FastAPI server that tracks agent lifecycle — registration, status, revocation, audit.
        Run it in-memory for development or with PostgreSQL + Redis via Docker Compose.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-500">
              <th className="text-left py-3 pr-4 font-medium">Method</th>
              <th className="text-left py-3 pr-4 font-medium">Path</th>
              <th className="text-left py-3 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map(([method, path, desc]) => (
              <tr key={path} className="border-b border-zinc-900 text-zinc-300">
                <td className="py-3 pr-4"><span className={`text-xs font-mono px-2 py-0.5 rounded ${method === 'GET' || method === 'WS' ? 'bg-emerald-950 text-emerald-400' : 'bg-indigo-950 text-indigo-400'}`}>{method}</span></td>
                <td className="py-3 pr-4 font-mono text-xs">{path}</td>
                <td className="py-3 text-zinc-400">{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="px-6 py-12 border-t border-zinc-800 text-center text-sm text-zinc-600">
      <p className="mb-2">Apache 2.0 — <a href="https://github.com/agenttity/agentity" className="text-zinc-400 hover:text-zinc-300">agenttity/agentity</a></p>
      <p>Agent identity for the open web.</p>
    </footer>
  );
}
