'use client';

import { useState } from 'react';
import { Card } from '@/components/ui';
import { ConsultationInterface, ConsultationTypeSelector, DisclaimerBanner } from '@/components/healthee';
import { Consultation, CreateConsultationRequest } from '@/lib/healthee/types';
import { healtheeApi } from '@/lib/healthee/api';
import { useAuth } from '@/lib/auth';

export default function HealtheePage() {
  const { user } = useAuth();
  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConsultationSelect = async (request: CreateConsultationRequest) => {
    if (!user) {
      setError('Please log in to start a consultation');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const newConsultation = await healtheeApi.createConsultation(request);
      setConsultation(newConsultation);
    } catch (err) {
      setError('Failed to start consultation. Please try again.');
      console.error('Consultation creation failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConsultationUpdate = (updatedConsultation: Consultation) => {
    setConsultation(updatedConsultation);
  };

  const handleBackToSelection = () => {
    setConsultation(null);
    setError(null);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">HEALTHEE ANYWHERE</h1>
        <p className="text-xl text-gray-600">
          Get professional health guidance anytime, anywhere
        </p>
      </div>

      {/* Medical Disclaimer */}
      <DisclaimerBanner />

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {!user && (
        <Card>
          <div className="p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Login Required</h2>
            <p className="text-gray-600 mb-4">
              Please log in to access health consultations and connect with our AI assistant or licensed pharmacists.
            </p>
            <a 
              href="/auth-demo" 
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go to Login
            </a>
          </div>
        </Card>
      )}

      {user && !consultation && (
        <ConsultationTypeSelector 
          onSelect={handleConsultationSelect}
          isLoading={isLoading}
        />
      )}

      {user && consultation && (
        <Card>
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Consultation #{consultation.id}
              </h2>
              <button
                onClick={handleBackToSelection}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                ← Back to Selection
              </button>
            </div>
            <ConsultationInterface 
              consultation={consultation}
              onConsultationUpdate={handleConsultationUpdate}
            />
          </div>
        </Card>
      )}
    </div>
  );
}