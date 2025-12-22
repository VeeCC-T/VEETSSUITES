'use client';

import React, { useState } from 'react';
import { authApi } from '@/lib/auth';
import { Button } from '@/components/ui';
import { useToast } from '@/components/ui';

interface PasswordResetFormProps {
  onSuccess?: () => void;
}

/**
 * PasswordResetForm component for initiating password reset
 * Validates: Requirements 1.3
 */
export const PasswordResetForm: React.FC<PasswordResetFormProps> = ({ onSuccess }) => {
  const { addToast } = useToast();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string }>({});

  const validateForm = (): boolean => {
    const newErrors: { email?: string } = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await authApi.requestPasswordReset(email);
      addToast('Password reset link sent to your email', 'success');
      onSuccess?.();
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to send reset link. Please try again.';
      addToast(message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.email ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="your@email.com"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.email}
          </p>
        )}
        <p className="mt-2 text-sm text-gray-600">
          We&apos;ll send you a link to reset your password.
        </p>
      </div>

      <Button type="submit" loading={isLoading} className="w-full">
        {isLoading ? 'Sending...' : 'Send Reset Link'}
      </Button>
    </form>
  );
};
