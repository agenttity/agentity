export default function Home() {
  return (
    <main className="max-w-6xl mx-auto px-6">
      <Nav />
      <Hero />
      <ProblemSolution />
      <HowItWorks />
      <Features />
      <PackagesSection />
      <QuickStart />
      <Endpoints />
      <DocsSection />
      <Footer />
    </main>
  );
}

import { GitBranch, Package, DownloadSimple, BookOpenText, PuzzlePiece, Terminal, Cloud, FileCode, Cube, SealCheck, Plugs, PlugsConnected, Lockers, ChartBar, CoinVertical } from '@phosphor-icons/react/dist/ssr';

function Nav() {
  return (
    <nav className="flex items-center justify-between py-4 border-b border-border-ash">
      <span className="font-ibm-plex-mono text-sm font-semibold text-text-jet">Agentity</span>
      <div className="flex items-center gap-3">
        <a href="/docs" className="flex items-center gap-1.5 text-text-graphite text-caption font-rubik-variable font-medium px-3 py-1.5 rounded-md border border-border-ash hover:border-primary-violet hover:text-primary-violet transition-colors">
          <BookOpenText size={16} />
          Docs
        </a>
        <a href="https://github.com/agenttity/agentity" className="flex items-center gap-1.5 text-text-graphite text-caption font-rubik-variable font-medium px-3 py-1.5 rounded-md border border-border-ash hover:border-primary-violet hover:text-primary-violet transition-colors">
          <GitBranch size={16} />
          GitHub
        </a>
        <a href="https://www.npmjs.com/package/@agentity/sdk" className="flex items-center gap-1.5 text-text-graphite text-caption font-rubik-variable font-medium px-3 py-1.5 rounded-md border border-border-ash hover:border-primary-violet hover:text-primary-violet transition-colors">
          <Package size={16} />
          npm
        </a>
        <a href="https://pypi.org/project/agentity-sdk-python/" className="flex items-center gap-1.5 text-primary-violet text-caption font-rubik-variable font-medium px-3 py-1.5 rounded-md border border-primary-violet hover:bg-primary-violet hover:text-white transition-colors">
          <DownloadSimple size={16} />
          PyPI
        </a>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="grid md:grid-cols-2 gap-12 pt-24 pb-32 items-center">
      <div>
        <h1 className="font-ibm-plex-mono font-semibold text-5xl leading-[1.00] text-text-jet mb-6">
          Identity for <br />
          <span className="text-primary-violet">AI Agents</span>
        </h1>
        <p className="text-text-graphite text-body leading-relaxed mb-8 max-w-md">
          Every AI agent gets a W3C-compatible DID, a signed identity document with Ed25519 keys, and a scope system validated against provider manifests.
        </p>
        <p className="text-text-slate text-caption font-ibm-plex-mono mb-8">
          <span className="text-text-slate">$</span> pip install agentity-sdk-python
        </p>
        <div className="flex flex-wrap gap-3">
          <a href="https://github.com/agenttity/agentity" className="bg-primary-violet text-white text-caption font-rubik-variable font-normal px-4 py-2 rounded-md hover:opacity-90 transition-opacity">
            View on GitHub
          </a>
          <a href="#quickstart" className="border border-border-ash text-text-graphite text-caption font-rubik-variable font-normal px-4 py-2 rounded-md hover:border-primary-violet hover:text-primary-violet transition-colors">
            Quick Start
          </a>
        </div>
      </div>
      <CodeCard />
    </section>
  );
}

function CodeCard() {
  const html = `<span class="syntax-rose">from</span> <span class="syntax-magenta">agentity_sdk</span> <span class="syntax-rose">import</span> <span class="syntax-magenta">AgentKeyPair</span>

<span class="syntax-magenta">kp</span> <span class="syntax-rose">=</span> <span class="syntax-indigo">AgentKeyPair</span>()
<span class="syntax-magenta">aid</span> <span class="syntax-rose">=</span> <span class="syntax-indigo">kp</span>.<span class="syntax-magenta">create_identity</span>(
    <span class="syntax-teal">owner_did</span><span class="syntax-rose">=</span><span class="syntax-indigo">"did:agentity:human:alice"</span>,
    <span class="syntax-teal">scopes</span><span class="syntax-rose">=[</span><span class="syntax-indigo">"payments:read"</span><span class="syntax-rose">],</span>
)

<span class="syntax-sky"># DID: did:agentity:agent:7Xj3mK...</span>`;
  return (
    <div className="bg-page-white rounded-lg shadow-[0px_1px_3px_rgba(0,0,0,0.1),0px_1px_2px_rgba(0,0,0,0.06)] p-6 border border-border-ash">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-3 h-3 rounded-full bg-red-400" />
        <span className="w-3 h-3 rounded-full bg-yellow-400" />
        <span className="w-3 h-3 rounded-full bg-green-400" />
      </div>
      <pre className="font-ibm-plex-mono text-sm leading-relaxed overflow-x-auto whitespace-pre">
        <code dangerouslySetInnerHTML={{ __html: html }} />
      </pre>
    </div>
  );
}

function ProblemSolution() {
  return (
    <section className="grid md:grid-cols-2 gap-8 py-24">
      <div className="bg-page-white rounded-lg p-8 border border-border-ash">
        <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide">The Problem</p>
        <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-4">Agents have no identity</h2>
        <p className="text-text-graphite text-body leading-relaxed">
          AI agents calling APIs today cannot prove who controls them, what they are allowed to do,
          or who is responsible for their actions. OAuth2, JWT, and API keys were designed for humans
          and static apps — not for autonomous, ephemeral software entities.
        </p>
      </div>
      <div className="bg-page-white rounded-lg p-8 border border-border-ash">
        <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide">The Solution</p>
        <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-4">Three questions</h2>
        <ul className="space-y-5">
          {[
            { num: '01', q: 'Who are you?', a: 'Verifiable identity via Ed25519 key + self-signed DID' },
            { num: '02', q: 'What can you do?', a: 'Scopes validated against provider manifests' },
            { num: '03', q: 'Who is responsible?', a: 'Delegation chain rooted in a human via OIDC' },
          ].map((item) => (
            <li key={item.num} className="flex gap-4">
              <span className="font-ibm-plex-mono text-xs text-primary-violet font-semibold shrink-0 mt-0.5">{item.num}</span>
              <div>
                <p className="font-semibold text-text-graphite text-body">{item.q}</p>
                <p className="text-text-slate text-caption leading-relaxed">{item.a}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function HowItWorks() {
  return (
    <section className="py-24 text-center">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide">How It Works</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-16">Three steps</h2>
      <div className="grid md:grid-cols-3 gap-8 text-left">
        {[
          {
            step: '01', title: 'Create Identity',
            desc: 'Generate an Ed25519 keypair, create a self-signed Agent Identity Document (AID)',
            code: `kp = AgentKeyPair()
aid = kp.create_identity(
    "human:alice",
    ["payments:read"]
)`,
          },
          {
            step: '02', title: 'Sign Requests',
            desc: 'Every HTTP request carries the AID, a nonce, a timestamp, and an Ed25519 signature',
            code: `signer = RequestSigner(kp, aid)
headers = signer.sign_request(
    "GET", "/api/v1/payments"
)`,
          },
          {
            step: '03', title: 'Verify',
            desc: 'The server verifies signature, checks anti-replay, validates scopes, and confirms via Registry',
            code: `verifier = RequestVerifier()
aid = verifier.verify_request(
    headers, "GET",
    "/api/v1/payments"
)`,
          },
        ].map((item) => (
          <div key={item.step} className="bg-page-white rounded-lg p-6 border border-border-ash">
            <p className="font-ibm-plex-mono text-xs text-primary-violet font-semibold mb-3">{item.step}</p>
            <h3 className="font-semibold text-text-graphite text-body mb-2">{item.title}</h3>
            <p className="text-text-slate text-caption leading-relaxed mb-4">{item.desc}</p>
            <pre className="bg-page-white border border-border-ash rounded-md p-4 text-xs leading-relaxed overflow-x-auto font-ibm-plex-mono">
              <code>{item.code}</code>
            </pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function Features() {
  const features = [
    { title: 'OIDC Auth', desc: 'Google, GitHub, Apple, Microsoft login — verified owner_did' },
    { title: 'Rate Limiting', desc: 'Redis-based per-DID rate limiting with configurable windows' },
    { title: 'Key Rotation', desc: 'version+1, previousAid link, TTL-based expiration' },
    { title: 'Signed Audit Log', desc: 'HMAC-SHA256 on every entry, verifiable via API' },
    { title: 'Anti-Replay', desc: 'UUID nonce + 5 min timestamp window' },
    { title: 'Delegation Chain', desc: 'Max 10 levels, child ⊆ parent scopes, cascade revocation' },
  ];
  return (
    <section className="py-24">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide text-center">Security</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-12 text-center">Built-in protections</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((f) => (
          <div key={f.title} className="bg-page-white rounded-md px-5 py-4 border border-border-ash">
            <p className="font-semibold text-text-graphite text-body mb-1">{f.title}</p>
            <p className="text-text-slate text-caption leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function PackagesSection() {
  const packages = [
    { name: 'agentity-core', lang: 'Rust', type: 'library', icon: Lockers, desc: 'Ed25519 keys, DID, AID, scope matching' },
    { name: 'agentity-sdk-python', lang: 'Python', type: 'library', icon: Cube, desc: 'AgentKeyPair, RequestSigner, LangChain, rotation', pub: 'PyPI' },
    { name: 'agentity-sdk-ts', lang: 'TypeScript', type: 'library', icon: Cube, desc: 'Full parity SDK for Node.js/Next.js', pub: 'npm' },
    { name: 'agentity-registry', lang: 'Python', type: 'service', icon: Cloud, desc: 'FastAPI: register, lookup, revoke, audit, WS', pub: 'PyPI' },
    { name: 'agentity-auth', lang: 'Python', type: 'plugin', icon: SealCheck, desc: 'OIDC: Google, GitHub, Apple, Microsoft', pub: 'PyPI' },
    { name: 'agentity-cli', lang: 'Python', type: 'cli', icon: Terminal, desc: 'create, inspect, verify, sign, manifest', pub: 'PyPI' },
    { name: 'agentity-middleware-python', lang: 'Python', type: 'middleware', icon: Plugs, desc: 'FastAPI automatic token verification', pub: 'PyPI' },
    { name: 'agentity-middleware-express', lang: 'TS', type: 'middleware', icon: PlugsConnected, desc: 'Express automatic token verification', pub: 'npm' },
    { name: 'agentity-mcp', lang: 'Python', type: 'plugin', icon: PuzzlePiece, desc: 'MCP Anthropic protocol plugin', pub: 'PyPI' },
    { name: 'agentity-a2a', lang: 'Python', type: 'plugin', icon: FileCode, desc: 'A2A Google agent-to-agent protocol', pub: 'PyPI' },
    { name: 'agentity-inspector', lang: 'TypeScript', type: 'ui', icon: ChartBar, desc: 'Next.js dashboard with WS live revocations' },
    { name: 'agentity-manifest-gen', lang: 'TypeScript', type: 'cli', icon: FileCode, desc: 'Provider manifest JSON generator', pub: 'npm' },
    { name: 'agentity-evm', lang: 'Python+Sol', type: 'bridge', icon: CoinVertical, desc: 'EVM cross-registry DID bridge' },
  ];
  return (
    <section className="py-24">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide text-center">Packages</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-4 text-center">13 packages, 3 languages</h2>
      <p className="text-text-slate text-caption text-center mb-10 max-w-md mx-auto leading-relaxed">
        Monorepo with Rust core, Python and TypeScript SDKs, middleware for FastAPI and Express,
        CLI tool, protocol plugins, dashboard, and EVM bridge.
      </p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {packages.map((p) => {
          const Icon = p.icon;
          return (
            <div key={p.name} className="bg-page-white rounded-md px-4 py-3 border border-border-ash">
              <div className="flex items-center gap-2 mb-1.5">
                <Icon size={14} className="text-text-fog shrink-0" />
                <p className="font-ibm-plex-mono text-xs text-primary-violet">{p.name}</p>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-caption text-text-fog">{p.lang}</span>
                <span className="text-caption text-text-slate">·</span>
                <span className="text-caption text-text-fog">{p.type}</span>
                {p.pub && (
                  <>
                    <span className="text-caption text-text-slate">·</span>
                    <span className="text-caption text-code-teal">{p.pub}</span>
                  </>
                )}
              </div>
              <p className="text-caption text-text-slate leading-relaxed">{p.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function QuickStart() {
  return (
    <section id="quickstart" className="py-24">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide text-center">Quick Start</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-12 text-center">Install in seconds</h2>
      <div className="max-w-2xl mx-auto space-y-4">
        {[
          { label: 'Python', code: 'pip install agentity-sdk-python agentity-registry agentity-auth agentity-cli agentity-middleware-python agentity-mcp agentity-a2a' },
          { label: 'TypeScript', code: 'pnpm add @agentity/sdk' },
          { label: 'CLI', code: 'python -m agentity_cli create --owner "did:agentity:human:alice" --scope "api:read" --output agent.json' },
          { label: 'Docker', code: 'docker compose up -d' },
        ].map((item) => (
          <div key={item.label} className="bg-page-white rounded-md p-4 border border-border-ash">
            <p className="text-text-fog text-xs mb-1 font-semibold">{item.label}</p>
            <pre className="font-ibm-plex-mono text-sm leading-relaxed text-text-graphite overflow-x-auto"><code>{item.code}</code></pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function Endpoints() {
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
    <section className="py-24 max-w-3xl mx-auto">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide text-center">Registry API</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-4 text-center">Self-hostable</h2>
      <p className="text-text-slate text-caption text-center mb-10 max-w-md mx-auto leading-relaxed">
        The registry is a FastAPI server that tracks agent lifecycle — registration, status, revocation, audit.
        Run it in-memory for development or with PostgreSQL + Redis via Docker Compose.
      </p>
      <div className="overflow-x-auto rounded-lg border border-border-ash">
        <table className="w-full text-caption">
          <thead>
            <tr className="border-b border-border-ash text-text-fog">
              <th className="text-left py-3 px-4 font-semibold font-rubik-variable">Method</th>
              <th className="text-left py-3 px-4 font-semibold font-rubik-variable">Path</th>
              <th className="text-left py-3 px-4 font-semibold font-rubik-variable">Description</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map(([method, path, desc]) => (
              <tr key={path} className="border-b border-border-ash text-text-graphite">
                <td className="py-3 px-4">
                  <span className={`font-ibm-plex-mono text-xs px-2 py-0.5 rounded-sm ${method === 'GET' || method === 'WS' ? 'text-code-teal bg-code-teal/5' : 'text-code-magenta bg-code-magenta/5'}`}>{method}</span>
                </td>
                <td className="py-3 px-4 font-ibm-plex-mono text-xs">{path}</td>
                <td className="py-3 px-4 text-text-slate">{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DocsSection() {
  const docs = [
    { title: 'Getting Started', href: '/docs', desc: 'Install, create identity, sign requests, verify' },
    { title: 'Architecture', file: 'architecture.md', desc: 'Four-layer design, request flow, package roles' },
    { title: 'Security', file: 'security.md', desc: 'Key rotation, anti-replay, delegation, OIDC, threat model' },
    { title: 'Registry API', file: 'registry-api.md', desc: 'All REST endpoints, WebSocket, rate limiting' },
    { title: 'CLI Reference', file: 'cli.md', desc: 'create, inspect, verify, sign, manifest commands' },
    { title: 'Deployment', file: 'deployment.md', desc: 'Docker Compose, env vars, production config' },
    { title: 'Development', file: 'development.md', desc: 'Build/test/lint all 3 languages, CI/CD' },
    { title: 'Protocol Spec', file: '../packages/agentity-spec/SPEC.md', desc: 'RFC: DID method, AID schema, verification rules' },
  ];
  return (
    <section className="py-24">
      <p className="text-text-fog text-caption font-semibold mb-3 uppercase tracking-wide text-center">Documentation</p>
      <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet mb-12 text-center">Guides & reference</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {docs.map((d) => (
          <a key={d.title} href={d.file ? `https://github.com/agenttity/agentity/blob/main/docs/${d.file}` : d.href}
             className="bg-page-white rounded-md px-5 py-4 border border-border-ash hover:border-primary-violet transition-colors group">
            <p className="font-semibold text-text-graphite text-body mb-1 group-hover:text-primary-violet transition-colors">{d.title}</p>
            <p className="text-text-slate text-caption leading-relaxed">{d.desc}</p>
          </a>
        ))}
      </div>
      <div className="text-center mt-8">
        <a href="/docs" className="inline-flex items-center gap-1.5 text-primary-violet text-caption font-rubik-variable font-medium hover:underline">
          <BookOpenText size={14} />
          Browse all documentation
        </a>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 border-t border-border-ash text-center text-caption text-text-slate">
      <p className="mb-2">Apache 2.0 — <a href="https://github.com/agenttity/agentity" className="text-primary-violet hover:underline">agenttity/agentity</a></p>
      <p className="font-ibm-plex-mono text-xs">did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi</p>
    </footer>
  );
}
