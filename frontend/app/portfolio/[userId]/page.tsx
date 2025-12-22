'use client';

import React from 'react';
import { PortfolioPublicView } from '@/components/portfolio';

interface PublicPortfolioPageProps {
  params: {
    userId: string;
  };
}

export default function PublicPortfolioPage({ params }: PublicPortfolioPageProps) {
  const userId = parseInt(params.userId, 10);

  if (isNaN(userId)) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Portfolio URL</h1>
          <p className="text-gray-600">The portfolio URL you're looking for is not valid.</p>
        </div>
      </div>
    );
  }

  return <PortfolioPublicView userId={userId} />;
}