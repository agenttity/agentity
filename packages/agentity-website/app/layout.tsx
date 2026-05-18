import type { Metadata } from 'next';
import { GoogleAnalytics } from '@next/third-parties/google';
import './globals.css';

const GA_ID = 'G-WKVSFZQEXZ';

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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Rubik:ital,wght@0,300..900;1,300..900&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-page-white text-text-graphite">
        {children}
        <GoogleAnalytics gaId={GA_ID} />
      </body>
    </html>
  );
}
