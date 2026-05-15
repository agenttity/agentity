import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agentity — Identity for AI Agents',
  description: 'Open source cryptographic identity protocol for AI agents. DID, signed AID, scopes, OIDC, delegation chains.',
  openGraph: {
    title: 'Agentity — Identity for AI Agents',
    description: 'Open source cryptographic identity protocol for AI agents.',
    url: 'https://agentity.dev',
    siteName: 'Agentity',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="antialiased">
      <body className="bg-zinc-950 text-zinc-100 font-sans">{children}</body>
    </html>
  );
}
