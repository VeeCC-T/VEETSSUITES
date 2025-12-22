import Link from 'next/link';
import { Card } from '@/components/ui';

export default function Home() {
  const subsites = [
    {
      name: 'Portfolio',
      path: '/portfolio',
      description: 'Showcase your professional CV and qualifications',
      icon: '📄',
    },
    {
      name: 'PHARMXAM',
      path: '/pharmxam',
      description: 'Practice pharmacy exam questions and track your progress',
      icon: '💊',
    },
    {
      name: 'HUB3660',
      path: '/hub3660',
      description: 'Learn technology through live courses and sessions',
      icon: '🎓',
    },
    {
      name: 'HEALTHEE',
      path: '/healthee',
      description: 'Get health guidance from AI or consult with pharmacists',
      icon: '🏥',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero section */}
      <header className="text-center mb-16">
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          Welcome to VEETSSUITES
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          A comprehensive platform providing professional services, education, and health consultation
        </p>
      </header>

      {/* Subsites grid */}
      <section aria-labelledby="subsites-heading">
        <h2 id="subsites-heading" className="sr-only">
          Available Subsites
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {subsites.map((subsite) => (
            <Link key={subsite.path} href={subsite.path}>
              <Card 
                className="h-full hover:shadow-xl transition-shadow cursor-pointer"
                ariaLabel={`Navigate to ${subsite.name}`}
              >
                <div className="p-6">
                  <div className="text-4xl mb-4" role="img" aria-label={`${subsite.name} icon`}>
                    {subsite.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {subsite.name}
                  </h3>
                  <p className="text-gray-600">{subsite.description}</p>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA section */}
      <section aria-labelledby="cta-heading">
        <h2 id="cta-heading" className="sr-only">
          Get Started
        </h2>
        <div className="text-center">
          <Card className="bg-blue-50 border-blue-200">
            <div className="p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Ready to get started?
              </h3>
              <p className="text-gray-600 mb-6">
                Create an account to access all features across our platform
              </p>
              <Link
                href="/auth-demo"
                className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-label="Sign up for VEETSSUITES"
              >
                Sign Up Now
              </Link>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
