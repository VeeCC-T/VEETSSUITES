'use client';

import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { portfolioApi, Portfolio, PortfolioUpdateData } from '@/lib/portfolio/api';

interface PortfolioEditProps {
  portfolio: Portfolio;
  onUpdateSuccess?: (portfolio: Portfolio) => void;
  onUpdateError?: (error: string) => void;
  onCancel?: () => void;
}

export function PortfolioEdit({ 
  portfolio, 
  onUpdateSuccess, 
  onUpdateError, 
  onCancel 
}: PortfolioEditProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateProgress, setUpdateProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isPublic, setIsPublic] = useState(portfolio.is_public);
  const [error, setError] = useState<string | null>(null);

  // File validation
  const validateFile = useCallback((file: File): string | null => {
    // Check file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'File type not supported. Please upload a PDF file.';
    }

    // Check file size (10MB = 10 * 1024 * 1024 bytes)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      return 'File size exceeds maximum allowed size of 10MB.';
    }

    return null;
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      setSelectedFile(null);
      return;
    }

    setError(null);
    setSelectedFile(file);
  }, [validateFile]);

  // Handle drag events
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // Handle file input change
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // Handle update
  const handleUpdate = useCallback(async () => {
    // Check if anything changed
    if (!selectedFile && isPublic === portfolio.is_public) {
      setError('No changes to save.');
      return;
    }

    setIsUpdating(true);
    setUpdateProgress(0);
    setError(null);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUpdateProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const updateData: PortfolioUpdateData = {
        is_public: isPublic,
      };

      if (selectedFile) {
        updateData.cv_file = selectedFile;
      }

      const updatedPortfolio = await portfolioApi.updatePortfolio(portfolio.user.id, updateData);

      clearInterval(progressInterval);
      setUpdateProgress(100);

      // Reset form
      setSelectedFile(null);
      
      if (onUpdateSuccess) {
        onUpdateSuccess(updatedPortfolio);
      }
    } catch (err: any) {
      setUpdateProgress(0);
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.cv_file?.[0] || 
                          'Update failed. Please try again.';
      setError(errorMessage);
      
      if (onUpdateError) {
        onUpdateError(errorMessage);
      }
    } finally {
      setIsUpdating(false);
    }
  }, [selectedFile, isPublic, portfolio, onUpdateSuccess, onUpdateError]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card>
      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Edit Portfolio</h2>
        
        {/* Current CV Info */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Current CV</h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                Uploaded: {new Date(portfolio.updated_at).toLocaleDateString()}
              </p>
              <p className="text-xs text-gray-500">
                Status: {portfolio.is_public ? 'Public' : 'Private'}
              </p>
            </div>
            {portfolio.cv_file_url && (
              <Button
                variant="secondary"
                onClick={() => portfolio.cv_file_url && window.open(portfolio.cv_file_url, '_blank')}
              >
                View Current
              </Button>
            )}
          </div>
        </div>
        
        {/* New CV Upload */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-900 mb-2">
            Upload New CV (Optional)
          </h3>
          <div
            className={`
              border-2 border-dashed rounded-lg p-6 text-center transition-colors
              ${isDragging 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
              }
              ${isUpdating ? 'pointer-events-none opacity-50' : ''}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {selectedFile ? (
              <div className="space-y-2">
                <div className="text-green-600">
                  <svg className="mx-auto h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                <Button
                  variant="secondary"
                  onClick={() => setSelectedFile(null)}
                  disabled={isUpdating}
                >
                  Remove
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-gray-400">
                  <svg className="mx-auto h-8 w-8" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium text-blue-600 hover:text-blue-500 cursor-pointer">
                      Click to upload new CV
                    </span>
                    {' '}or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PDF files only, up to 10MB</p>
                </div>
              </div>
            )}
            
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileInputChange}
              className="hidden"
              id="cv-file-input-edit"
              disabled={isUpdating}
            />
            
            {!selectedFile && (
              <label
                htmlFor="cv-file-input-edit"
                className="absolute inset-0 cursor-pointer"
                aria-label="Upload new CV file"
              />
            )}
          </div>
        </div>

        {/* Update Progress */}
        {isUpdating && (
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Updating...</span>
              <span>{updateProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${updateProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
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

        {/* Privacy Setting */}
        <div className="mb-6 flex items-center">
          <input
            id="is-public-edit"
            type="checkbox"
            checked={isPublic}
            onChange={(e) => setIsPublic(e.target.checked)}
            disabled={isUpdating}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is-public-edit" className="ml-2 block text-sm text-gray-900">
            Make portfolio publicly accessible
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <Button
            onClick={handleUpdate}
            disabled={isUpdating}
            loading={isUpdating}
            className="flex-1"
          >
            {isUpdating ? 'Updating...' : 'Save Changes'}
          </Button>
          
          {onCancel && (
            <Button
              variant="secondary"
              onClick={onCancel}
              disabled={isUpdating}
              className="flex-1"
            >
              Cancel
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}