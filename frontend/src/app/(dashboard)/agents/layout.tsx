import { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Agent Conversation | Otto',
  description: 'Interactive agent conversation powered by Ottolabs',
  openGraph: {
    title: 'Agent Conversation | Otto',
    description: 'Interactive agent conversation powered by Ottolabs',
    type: 'website',
  },
};

export default async function AgentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
