import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'API Keys | Otto',
  description: 'Manage your API keys for programmatic access to Otto',
  openGraph: {
    title: 'API Keys | Otto',
    description: 'Manage your API keys for programmatic access to Otto',
    type: 'website',
  },
};

export default async function APIKeysLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
