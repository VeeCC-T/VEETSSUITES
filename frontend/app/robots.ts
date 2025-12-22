import { MetadataRoute } from 'next';

/**
 * Generate robots.txt for search engine crawling rules
 */
export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://veetssuites.com';

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/auth-demo/'], // Disallow API routes and demo pages
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
