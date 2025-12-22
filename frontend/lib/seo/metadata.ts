import { Metadata } from 'next';

export interface SEOConfig {
  title?: string;
  description?: string;
  keywords?: string[];
  ogImage?: string;
  ogType?: 'website' | 'article' | 'profile';
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
  canonical?: string;
  noindex?: boolean;
}

const DEFAULT_TITLE = 'VEETSSUITES';
const DEFAULT_DESCRIPTION = 'Multi-subsite platform for education and professional services';
const DEFAULT_KEYWORDS = ['education', 'pharmacy', 'health consultation', 'online courses', 'portfolio'];
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://veetssuites.com';

/**
 * Generate Next.js Metadata object for SEO
 * Implements dynamic title and description generation with Open Graph and Twitter Card support
 */
export function generateMetadata(config: SEOConfig = {}): Metadata {
  const {
    title = DEFAULT_TITLE,
    description = DEFAULT_DESCRIPTION,
    keywords = DEFAULT_KEYWORDS,
    ogImage = '/og-image.png',
    ogType = 'website',
    twitterCard = 'summary_large_image',
    canonical,
    noindex = false,
  } = config;

  const fullTitle = title === DEFAULT_TITLE ? title : `${title} | ${DEFAULT_TITLE}`;
  const canonicalUrl = canonical || SITE_URL;
  const fullOgImage = ogImage.startsWith('http') ? ogImage : `${SITE_URL}${ogImage}`;

  const metadata: Metadata = {
    title: fullTitle,
    description,
    keywords: keywords.join(', '),
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title: fullTitle,
      description,
      type: ogType,
      url: canonicalUrl,
      images: [
        {
          url: fullOgImage,
          width: 1200,
          height: 630,
          alt: fullTitle,
        },
      ],
      siteName: 'VEETSSUITES',
    },
    twitter: {
      card: twitterCard,
      title: fullTitle,
      description,
      images: [fullOgImage],
    },
  };

  if (noindex) {
    metadata.robots = {
      index: false,
      follow: false,
    };
  }

  return metadata;
}

/**
 * Generate metadata for Portfolio subsite
 */
export function generatePortfolioMetadata(userName?: string): Metadata {
  return generateMetadata({
    title: userName ? `${userName}'s Portfolio` : 'Portfolio',
    description: 'Professional CV showcase and qualifications display',
    keywords: ['portfolio', 'CV', 'resume', 'professional profile', ...DEFAULT_KEYWORDS],
    ogType: userName ? 'profile' : 'website',
  });
}

/**
 * Generate metadata for PHARMXAM subsite
 */
export function generatePharmxamMetadata(): Metadata {
  return generateMetadata({
    title: 'PHARMXAM',
    description: 'Practice pharmacy exam questions and track your progress with our comprehensive MCQ system',
    keywords: ['pharmacy exam', 'MCQ', 'exam preparation', 'pharmacy questions', ...DEFAULT_KEYWORDS],
  });
}

/**
 * Generate metadata for HUB3660 subsite
 */
export function generateHub3660Metadata(courseName?: string): Metadata {
  return generateMetadata({
    title: courseName ? `${courseName} - HUB3660` : 'HUB3660',
    description: 'Learn technology through live courses and interactive sessions with expert instructors',
    keywords: ['online courses', 'technology education', 'live sessions', 'programming', ...DEFAULT_KEYWORDS],
  });
}

/**
 * Generate metadata for HEALTHEE subsite
 */
export function generateHealtheeMetadata(): Metadata {
  return generateMetadata({
    title: 'HEALTHEE ANYWHERE',
    description: 'Get health guidance from AI chatbot or consult with licensed pharmacists',
    keywords: ['health consultation', 'pharmacist', 'AI health', 'medical guidance', ...DEFAULT_KEYWORDS],
  });
}
