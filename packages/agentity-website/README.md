# agentity-website

**Agentity Protocol landing page.**
Built with Next.js 15 and Tailwind v4 — deployed at [agentity-website.vercel.app](https://agentity-website.vercel.app).

## Tech

- Next.js 15 (App Router, static export)
- Tailwind v4
- Phosphor Icons
- IBM Plex Mono + Rubik Variable

## Development

```bash
pnpm dev       # Local server
pnpm build     # Static export → out/
```

## Deployment

Automatic via Vercel GitHub integration. The `vercel.json` at repo root sets the root directory:

```json
{
  "rootDirectory": "packages/agentity-website"
}
```

License: Apache 2.0
