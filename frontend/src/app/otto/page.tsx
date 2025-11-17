import { Metadata } from 'next';
import Link from 'next/link';
import { ArrowRight, Github } from 'lucide-react';
import Image from 'next/image';

export const metadata: Metadata = {
  title: 'Otto | Otto Agent - Open Source AI Orchestrator',
  description: 'Otto is a powerful open source AI assistant/Generalist AI worker & AI Agent Orchestrator to help you realize your dream.',
  keywords: [
    'Otto',
    'Ottolabs',
    'Otto AI',
    'Otto Assistant',
    'Otto.lk',
    'where is Otto',
    'Otto Agent',
    'AI assistant',
    'open source AI',
    'generalist AI worker',
    'AI Orchestrator',
    'AI worker',
    'autonomous AI',
  ],
  openGraph: {
    title: 'Otto',
    description: 'AI Agent Orchestrator',
    type: 'website',
    url: 'https://app.otto.lk',
    siteName: 'Otto App',
    images: [
      {
        url: '/banner.png',
        width: 1200,
        height: 630,
        alt: 'Otto',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Otto',
    description: 'Otto - open source AI Agent Orchestrator.',
    images: ['/banner.png'],
  },
  alternates: {
    canonical: 'https://app.otto.lk/',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function SunaPage() {
  return (
    <>
      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'Otto',
            alternateName: ['Otto', 'Ottolabs', 'Otto AI'],
            url: 'https://app.otto.lk',
            logo: 'https://app.otto.lk/favicon.png',
            sameAs: [
              'https://github.com/OttolabsAI',
              'https://x.com/OttolabsAI',
              'https://linkedin.com/company/ottolabs',
            ],
            description:
              'Otto is an open source generalist AI Agent Orchestrator that helps you accomplish real-world tasks through natural conversation.',
          }),
        }}
      />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            itemListElement: [
              {
                '@type': 'ListItem',
                position: 1,
                name: 'Home',
                item: 'https://app.otto.lk',
              },
              {
                '@type': 'ListItem',
                position: 2,
                name: 'Otto',
                item: 'https://app.otto.lk',
              },
            ],
          }),
        }}
      />

      <main className="w-full relative overflow-hidden bg-background">
        <div className="relative flex flex-col items-center w-full px-4 sm:px-6">
          {/* Hero Section with Logo */}
          <div className="relative z-10 pt-16 sm:pt-24 md:pt-32 mx-auto h-full w-full max-w-6xl flex flex-col items-center justify-center">
            <div className="flex flex-col items-center justify-center gap-3 sm:gap-4 pt-8 sm:pt-20 max-w-4xl mx-auto pb-10">
              {/* Otto Symbol with grain texture */}
              <div className="relative mb-8 sm:mb-12" style={{ width: '80px', height: '80px' }}>
                <Image
                  src="/kortix-symbol.svg"
                  alt="Otto"
                  fill
                  className="object-contain dark:invert"
                  priority
                  style={{ mixBlendMode: 'normal' }}
                />
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: 'url(/grain-texture.png)',
                    backgroundSize: '100px 100px',
                    backgroundRepeat: 'repeat',
                    mixBlendMode: 'multiply',
                    opacity: 0.6,
                    maskImage: 'url(/kortix-symbol.svg)',
                    WebkitMaskImage: 'url(/kortix-symbol.svg)',
                    maskSize: 'contain',
                    WebkitMaskSize: 'contain',
                    maskRepeat: 'no-repeat',
                    WebkitMaskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    WebkitMaskPosition: 'center',
                  }}
                />
              </div>

              {/* Main Heading */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-medium tracking-tighter text-balance text-center">
                Otto
              </h1>

              {/* Subheading */}
              <p className="text-lg md:text-xl text-muted-foreground font-medium text-center tracking-tight max-w-2xl pt-2">
                Same powerful open source AI worker. New name.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 w-full max-w-3xl mx-auto px-2 sm:px-0 pb-16">
              <Link
                href="/"
                className="flex h-12 items-center justify-center w-full sm:w-auto px-8 text-center rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-sm font-medium"
              >
                Go to Otto
                <ArrowRight className="ml-2 size-4" />
              </Link>
              <a
                href="https://github.com/OttolabsAI/otto"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-12 items-center justify-center w-full sm:w-auto px-8 text-center rounded-full border border-border bg-background hover:bg-accent/50 transition-all font-medium"
              >
                <Github className="mr-2 size-4" />
                View on GitHub
              </a>
            </div>
          </div>

          {/* Content Sections */}
          <div className="relative z-10 w-full max-w-4xl mx-auto pb-20 sm:pb-32">
            <div className="space-y-20 sm:space-y-32 text-center">
              {/* What Changed */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  What changed?
                </h2>
                <div className="space-y-3 text-base md:text-lg text-muted-foreground font-medium">
                  <p>Our domain is now Otto.lk</p>
                </div>
              </div>

              {/* Divider */}
              <div className="w-12 h-px bg-border mx-auto" />

              {/* What Stayed */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  What stayed the same?
                </h2>
                <div className="space-y-3 text-base md:text-lg text-muted-foreground font-medium">
                  <p>Fully open source (Apache 2.0)</p>
                  <p>Same powerful AI capabilities</p>
                  <p>All your existing agents and workflows</p>
                </div>
              </div>

              {/* Divider */}
              <div className="w-12 h-px bg-border mx-auto" />

              {/* GitHub */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  Where to find us?
                </h2>
                <p className="text-base md:text-lg text-muted-foreground font-medium">
                  Our GitHub remains at github.com/OttolabsAI
                </p>
              </div>
            </div>
          </div>

          {/* Footer Wordmark Section */}
          <div className="relative w-full mx-auto overflow-hidden pb-20 sm:pb-32">
            <div className="relative w-full max-w-5xl mx-auto aspect-[1150/344] px-8 md:px-16">
              <div className="relative w-full h-full" style={{ isolation: 'isolate' }}>
                <Image
                  src="/wordmark.svg"
                  alt="Otto"
                  fill
                  className="object-contain dark:invert opacity-10"
                  priority
                  style={{ mixBlendMode: 'normal' }}
                />
                {/* Grain texture overlay */}
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: 'url(/grain-texture.png)',
                    backgroundSize: '100px 100px',
                    backgroundRepeat: 'repeat',
                    mixBlendMode: 'multiply',
                    opacity: 0.6,
                    maskImage: 'url(/wordmark.svg)',
                    WebkitMaskImage: 'url(/wordmark.svg)',
                    maskSize: 'contain',
                    WebkitMaskSize: 'contain',
                    maskRepeat: 'no-repeat',
                    WebkitMaskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    WebkitMaskPosition: 'center',
                  }}
                />
              </div>
            </div>
          </div>

          {/* SEO Footer Text */}
          <div className="relative z-10 text-center max-w-2xl mx-auto pb-20 pt-12 border-t border-border/50">
            <p className="text-sm text-muted-foreground/60 leading-relaxed font-medium">
              Looking for Otto? You've found us. Otto is the next evolution of Agents — An AI assistant and generalist AI worker, to help you realize your vision.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
