'use client';

import React, { useState, useEffect } from 'react';
import { Card, Button, Modal } from '@/components/ui';
import { useAuth } from '@/lib/auth';
import { hub3660Api, type Course, type EnrollmentResponse } from '@/lib/hub3660';

interface PaymentProvider {
  provider: string;
  country_code: string;
  currency: string;
  is_configured: boolean;
  config: Record<string, any>;
}

interface PaymentSession {
  transaction_id: number;
  provider: string;
  amount: number;
  currency: string;
  session_url: string | null;
  session_id: string | null;
}

interface EnrollmentCheckoutProps {
  course: Course;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (course: Course) => void;
  onError: (error: string) => void;
}

export default function EnrollmentCheckout({
  course,
  isOpen,
  onClose,
  onSuccess,
  onError
}: EnrollmentCheckoutProps) {
  const [step, setStep] = useState<'confirm' | 'payment' | 'processing' | 'success' | 'error'>('confirm');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enrollmentResponse, setEnrollmentResponse] = useState<EnrollmentResponse | null>(null);
  const [paymentProvider, setPaymentProvider] = useState<PaymentProvider | null>(null);
  const [paymentSession, setPaymentSession] = useState<PaymentSession | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const { user } = useAuth();

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setStep('confirm');
      setError(null);
      setEnrollmentResponse(null);
      setPaymentProvider(null);
      setPaymentSession(null);
      setRetryCount(0);
    }
  }, [isOpen]);

  // Check payment status periodically when processing
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (step === 'processing' && paymentSession) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`/api/payments/status/${paymentSession.transaction_id}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          });
          
          if (response.ok) {
            const data = await response.json();
            
            if (data.status === 'completed') {
              setStep('success');
              setTimeout(() => {
                onSuccess(course);
                onClose();
              }, 2000);
            } else if (data.status === 'failed') {
              setStep('error');
              setError('Payment failed. Please try again.');
            }
          }
        } catch (err) {
          console.error('Error checking payment status:', err);
        }
      }, 2000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [step, paymentSession, course, onSuccess, onClose]);

  const formatPrice = (price: string, currency: string) => {
    const numPrice = parseFloat(price);
    if (numPrice === 0) {
      return 'Free';
    }
    return `${currency} ${numPrice.toFixed(2)}`;
  };

  const handleEnrollment = async () => {
    if (!user) {
      setError('Please log in to enroll in courses.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Initiate enrollment
      const response = await hub3660Api.enrollInCourse(course.id);
      setEnrollmentResponse(response);
      
      if (!response.payment_required) {
        // Free course - enrollment complete
        setStep('success');
        setTimeout(() => {
          onSuccess(course);
          onClose();
        }, 2000);
        return;
      }
      
      // Paid course - proceed to payment
      await setupPayment(response);
      
    } catch (err: any) {
      console.error('Enrollment failed:', err);
      const errorMessage = err.response?.data?.message || 'Failed to enroll in course. Please try again.';
      setError(errorMessage);
      onError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const setupPayment = async (enrollmentData: EnrollmentResponse) => {
    try {
      setLoading(true);
      
      // Get payment provider routing
      const providerResponse = await fetch('/api/payments/provider-routing/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          currency: course.currency,
        }),
      });
      
      if (!providerResponse.ok) {
        throw new Error('Failed to determine payment provider');
      }
      
      const providerData = await providerResponse.json();
      setPaymentProvider(providerData);
      
      if (!providerData.is_configured) {
        throw new Error(`Payment provider ${providerData.provider} is not configured`);
      }
      
      // Create payment session
      const sessionResponse = await fetch('/api/payments/create-checkout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          amount: parseFloat(course.price),
          currency: course.currency,
          success_url: `${window.location.origin}/hub3660/enrollment-success?course_id=${course.id}`,
          cancel_url: `${window.location.origin}/hub3660/enrollment-cancelled?course_id=${course.id}`,
          metadata: enrollmentData.payment_metadata,
        }),
      });
      
      if (!sessionResponse.ok) {
        throw new Error('Failed to create payment session');
      }
      
      const sessionData = await sessionResponse.json();
      setPaymentSession(sessionData);
      
      setStep('payment');
      
    } catch (err: any) {
      console.error('Payment setup failed:', err);
      setError(err.message || 'Failed to setup payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentRedirect = () => {
    if (paymentSession?.session_url) {
      setStep('processing');
      window.location.href = paymentSession.session_url;
    } else {
      setError('Payment session not available. Please try again.');
    }
  };

  const handleRetry = () => {
    if (retryCount < 2) {
      setRetryCount(prev => prev + 1);
      setError(null);
      setStep('confirm');
    } else {
      setError('Maximum retry attempts reached. Please try again later.');
    }
  };

  const renderConfirmStep = () => (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Confirm Enrollment
      </h3>
      
      <div className="mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">{course.title}</h4>
          <p className="text-sm text-gray-600 mb-3">{course.description}</p>
          
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Course Price:</span>
            <span className="font-bold text-lg text-blue-600">
              {formatPrice(course.price, course.currency)}
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      <div className="flex gap-3">
        <Button
          onClick={onClose}
          variant="secondary"
          className="flex-1"
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleEnrollment}
          className="flex-1"
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Confirm Enrollment'}
        </Button>
      </div>
    </div>
  );

  const renderPaymentStep = () => (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Complete Payment
      </h3>
      
      <div className="mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-blue-800 text-sm">
              You will be redirected to {paymentProvider?.provider} to complete your payment securely.
            </p>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">Course:</span>
            <span className="font-medium">{course.title}</span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">Amount:</span>
            <span className="font-bold text-lg">
              {formatPrice(course.price, course.currency)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Payment Provider:</span>
            <span className="font-medium capitalize">{paymentProvider?.provider}</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
          {retryCount < 2 && (
            <Button
              onClick={handleRetry}
              variant="secondary"
              size="sm"
              className="mt-2"
            >
              Try Again
            </Button>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <Button
          onClick={onClose}
          variant="secondary"
          className="flex-1"
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          onClick={handlePaymentRedirect}
          className="flex-1"
          disabled={loading || !paymentSession?.session_url}
        >
          {loading ? 'Setting up...' : 'Proceed to Payment'}
        </Button>
      </div>
    </div>
  );

  const renderProcessingStep = () => (
    <div className="p-6 text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Processing Payment
      </h3>
      <p className="text-gray-600">
        Please wait while we confirm your payment...
      </p>
    </div>
  );

  const renderSuccessStep = () => (
    <div className="p-6 text-center">
      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Enrollment Successful!
      </h3>
      <p className="text-gray-600">
        You have successfully enrolled in {course.title}. Redirecting to course content...
      </p>
    </div>
  );

  const renderErrorStep = () => (
    <div className="p-6 text-center">
      <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Enrollment Failed
      </h3>
      <p className="text-gray-600 mb-4">
        {error || 'Something went wrong during enrollment. Please try again.'}
      </p>
      
      <div className="flex gap-3">
        <Button
          onClick={onClose}
          variant="secondary"
          className="flex-1"
        >
          Close
        </Button>
        {retryCount < 2 && (
          <Button
            onClick={handleRetry}
            className="flex-1"
          >
            Try Again
          </Button>
        )}
      </div>
    </div>
  );

  const getStepContent = () => {
    switch (step) {
      case 'confirm':
        return renderConfirmStep();
      case 'payment':
        return renderPaymentStep();
      case 'processing':
        return renderProcessingStep();
      case 'success':
        return renderSuccessStep();
      case 'error':
        return renderErrorStep();
      default:
        return renderConfirmStep();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Course Enrollment"
    >
      {getStepContent()}
    </Modal>
  );
}