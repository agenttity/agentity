export default function DocsPage() {
  return (
    <main className="max-w-4xl mx-auto px-6">
      <DocsNav />
      <DocsHero />
      <DocSection title="Getting Started" file="getting-started.md">
        <p>Install the SDK, create an agent identity, sign and verify HTTP requests, or use the middleware for automatic verification.</p>
        <CodeBlock code={`# Python
pip install agentity-sdk-python agentity-registry agentity-auth

# TypeScript
pnpm add @agentity/sdk`} lang="bash" />
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/getting-started.md" className="text-primary-violet hover:underline">Read the full guide →</a></p>
      </DocSection>

      <DocSection title="Architecture" file="architecture.md">
        <p>Four-layer design: Core (Rust) → SDKs (Python/TS) → Middleware → Service Layer (Registry).</p>
        <p className="mt-2">Each agent carries a self-signed <code className="text-code-magenta text-xs">did:agentity</code> identity document with Ed25519 keys and scope declarations.</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/architecture.md" className="text-primary-violet hover:underline">Read the architecture docs →</a></p>
      </DocSection>

      <DocSection title="Security" file="security.md">
        <p>Six defense layers: Ed25519 signatures, anti-replay (nonce + timestamp), key rotation (version+1), delegation chains (max 10), OIDC owner verification, rate limiting.</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/security.md" className="text-primary-violet hover:underline">Read the security docs →</a></p>
      </DocSection>

      <DocSection title="Registry API" file="registry-api.md">
        <p>Full reference for the FastAPI registry — register, lookup, revoke, audit log, WebSocket events, OIDC endpoints, rate limiting headers.</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/registry-api.md" className="text-primary-violet hover:underline">Read the API reference →</a></p>
      </DocSection>

      <DocSection title="CLI" file="cli.md">
        <p>The <code className="text-code-magenta text-xs">agentity</code> CLI supports five commands: <code className="text-code-rose text-xs">create</code>, <code className="text-code-rose text-xs">inspect</code>, <code className="text-code-rose text-xs">verify</code>, <code className="text-code-rose text-xs">sign</code>, <code className="text-code-rose text-xs">manifest</code>.</p>
        <CodeBlock code={`agentity create --owner "did:agentity:human:alice" --scope "api:read" --output agent.json
agentity inspect agent.json
agentity sign --key agent.json --url https://api.example.com/data`} lang="bash" />
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/cli.md" className="text-primary-violet hover:underline">Read the CLI reference →</a></p>
      </DocSection>

      <DocSection title="Deployment" file="deployment.md">
        <p>Docker Compose setup for production: Registry + PostgreSQL + Redis. Environment variable reference for OIDC, EVM, and store configuration.</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/deployment.md" className="text-primary-violet hover:underline">Read the deployment guide →</a></p>
      </DocSection>

      <DocSection title="Development" file="development.md">
        <p>Set up the monorepo for all three languages. Build, test, and lint commands for Rust (17 tests), Python (43 tests), and TypeScript (19 tests).</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/docs/development.md" className="text-primary-violet hover:underline">Read the dev guide →</a></p>
      </DocSection>

      <DocSection title="Protocol Specification" file="../packages/agentity-spec/SPEC.md">
        <p>Formal RFC for the <code className="text-code-magenta text-xs">did:agentity</code> method — AID schema, delegation rules, provider manifest format, HTTP headers, verification rules.</p>
        <p className="mt-4"><a href="https://github.com/agenttity/agentity/blob/main/packages/agentity-spec/SPEC.md" className="text-primary-violet hover:underline">Read the spec →</a></p>
      </DocSection>

      <DocSection title="Package READMEs" file="">
        <div className="grid sm:grid-cols-2 gap-3">
          {([
            ['agentity-core', 'Rust', 'Core crypto library', 'agentity-core'],
            ['agentity-sdk-python', 'Python', 'SDK with LangChain integration', 'agentity-sdk-python'],
            ['agentity-sdk-ts', 'TypeScript', 'SDK for Node.js/Next.js', 'agentity-sdk-ts'],
            ['agentity-registry', 'Python', 'FastAPI REST registry', 'agentity-registry'],
            ['agentity-auth', 'Python', 'OIDC authentication plugin', 'agentity-auth'],
            ['agentity-cli', 'Python', 'Command-line interface', 'agentity-cli'],
            ['agentity-middleware-python', 'Python', 'FastAPI middleware', 'agentity-middleware/python'],
            ['agentity-middleware-express', 'TypeScript', 'Express middleware', 'agentity-middleware/typescript'],
            ['agentity-mcp', 'Python', 'MCP protocol plugin', 'agentity-mcp'],
            ['agentity-a2a', 'Python', 'A2A protocol plugin', 'agentity-a2a'],
            ['agentity-inspector', 'TypeScript', 'Next.js dashboard', 'agentity-inspector'],
            ['agentity-manifest-gen', 'TypeScript', 'Manifest generator CLI', 'agentity-manifest-gen'],
            ['agentity-evm', 'Python+Sol', 'EVM cross-registry bridge', 'agentity-evm'],
          ] as const).map(([name, lang, desc, dir]) => (
            <a key={name} href={`https://github.com/agenttity/agentity/blob/main/packages/${dir}/README.md`}
               className="bg-page-white rounded-md p-4 border border-border-ash hover:border-primary-violet transition-colors">
              <p className="font-ibm-plex-mono text-xs text-primary-violet mb-1">{name}</p>
              <p className="text-caption text-text-fog mb-1">{lang}</p>
              <p className="text-caption text-text-slate">{desc}</p>
            </a>
          ))}
        </div>
      </DocSection>

      <DocsFooter />
    </main>
  );
}

function DocsNav() {
  return (
    <nav className="flex items-center justify-between py-4 border-b border-border-ash">
      <a href="/" className="font-ibm-plex-mono text-sm font-semibold text-text-jet hover:text-primary-violet transition-colors">Agentity</a>
      <span className="font-ibm-plex-mono text-xs text-text-fog">Documentation</span>
    </nav>
  );
}

function DocsHero() {
  return (
    <section className="py-24 text-center">
      <h1 className="font-ibm-plex-mono font-semibold text-4xl text-text-jet mb-4">Documentation</h1>
      <p className="text-text-graphite text-body max-w-lg mx-auto leading-relaxed">
        Everything you need to integrate, deploy, and extend the Agentity Protocol.
      </p>
    </section>
  );
}

function DocSection({ title, file, children }: { title: string; file: string; children: React.ReactNode }) {
  return (
    <section className="py-12 border-t border-border-ash">
      <div className="flex items-center gap-3 mb-4">
        <h2 className="font-ibm-plex-mono font-semibold text-heading text-text-jet">{title}</h2>
        {file && <span className="font-ibm-plex-mono text-xs text-text-fog bg-border-ash/50 px-2 py-0.5 rounded-sm">{file}</span>}
      </div>
      <div className="text-text-graphite text-body leading-relaxed max-w-2xl">
        {children}
      </div>
    </section>
  );
}

function CodeBlock({ code, lang }: { code: string; lang?: string }) {
  return (
    <div className="bg-page-white rounded-md border border-border-ash mt-4">
      {lang && <div className="px-4 pt-3 pb-1 text-xs text-text-fog font-ibm-plex-mono">{lang}</div>}
      <pre className="p-4 text-sm leading-relaxed overflow-x-auto font-ibm-plex-mono"><code>{code}</code></pre>
    </div>
  );
}

function DocsFooter() {
  return (
    <footer className="py-12 border-t border-border-ash text-center text-caption text-text-slate">
      <p className="mb-2">Apache 2.0 — <a href="https://github.com/agenttity/agentity" className="text-primary-violet hover:underline">agenttity/agentity</a></p>
      <a href="/" className="text-primary-violet hover:underline">← Back to home</a>
    </footer>
  );
}
