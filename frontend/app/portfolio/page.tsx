'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { generatePortfolioMetadata } from '@/lib/seo';
import { useAuth } from '@/lib/auth';
import { 
  PortfolioUpload, 
  PortfolioDisplay, 
  PortfolioEdit 
} from '@/components/portfolio';
import { portfolioApi, Portfolio } from '@/lib/portfolio/api';

// Note: This would normally be handled by Next.js metadata API in a server component
// For now, we'll handle it client-side
export default function PortfolioPage() {
  const { user, isAuthenticated } = useAuth();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch user's portfolio
  useEffect(() => {
    const fetchPortfolio = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await portfolioApi.getMyPortfolio();
        setPortfolio(data);
      } catch (err: any) {
        if (err.response?.status === 404) {
          // User doesn't have a portfolio yet
          setPortfolio(null);
        } else {
          setError('Failed to load portfolio');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [isAuthenticated]);

  // Handle upload success
  const handleUploadSuccess = (newPortfolio: Portfolio) => {
    setPortfolio(newPortfolio);
    setError(null);
  };

  // Handle upload error
  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  // Handle update success
  const handleUpdateSuccess = (updatedPortfolio: Portfolio) => {
    setPortfolio(updatedPortfolio);
    setIsEditing(false);
    setError(null);
  };

  // Handle update error
  const handleUpdateError = (errorMessage: string) => {
    setError(errorMessage);
  };

  // Handle delete
  const handleDelete = async () => {
    if (!portfolio || !user) return;

    try {
      await portfolioApi.deletePortfolio(user.id);
      setPortfolio(null);
      setShowDeleteConfirm(false);
      setError(null);
    } catch (err: any) {
      setError('Failed to delete portfolio');
      setShowDeleteConfirm(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">Portfolio</h1>
        <Card>
          <div className="p-6 text-center">
            <p className="text-gray-600 mb-4">
              Please log in to manage your portfolio.
            </p>
            <Button onClick={() => window.location.href = '/auth-demo'}>
              Log In
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">Portfolio</h1>
        <div className="animate-pulse">
          <div className="h-64 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">Portfolio</h1>
      
      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg leading-6 font-medium text-gray-900 mt-4">Delete Portfolio</h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Are you sure you want to delete your portfolio? This action cannot be undone.
                </p>
              </div>
              <div className="items-center px-4 py-3">
                <div className="flex space-x-3">
                  <Button
                    variant="danger"
                    onClick={handleDelete}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!portfolio ? (
        // No portfolio - show upload form
        <PortfolioUpload
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
      ) : isEditing ? (
        // Editing mode
        <PortfolioEdit
          portfolio={portfolio}
          onUpdateSuccess={handleUpdateSuccess}
          onUpdateError={handleUpdateError}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        // Display mode
        <PortfolioDisplay
          portfolio={portfolio}
          isOwner={true}
          onEdit={() => setIsEditing(true)}
          onDelete={() => setShowDeleteConfirm(true)}
        />
      )}
    </div>
  );
}
