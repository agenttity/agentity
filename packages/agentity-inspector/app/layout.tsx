import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Agentity Inspector',
  description: 'AI Agent Identity Dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
