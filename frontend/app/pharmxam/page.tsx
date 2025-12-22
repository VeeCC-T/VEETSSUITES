'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { ProtectedRoute } from '@/components/auth';
import {
  ExamList,
  ExamSession,
  ExamResults,
  ExamHistory,
  ExamReview,
} from '@/components/pharmxam';
import { ExamAttempt, pharmxamApi } from '@/lib/pharmxam/api';
import { ExamConfig } from '@/lib/pharmxam/types';

type ViewMode = 'list' | 'session' | 'results' | 'history' | 'review';

interface PharmxamState {
  view: ViewMode;
  currentExamAttempt?: ExamAttempt;
  reviewAttemptId?: number;
  isLoading: boolean;
  error?: string;
}

/**
 * PHARMXAM main page component
 * Validates: Requirements 4.2, 4.3, 4.4, 4.5
 */
function PharmxamPageContent() {
  const { user } = useAuth();
  const [state, setState] = useState<PharmxamState>({
    view: 'list',
    isLoading: false,
  });

  const handleStartExam = async (config: ExamConfig) => {
    setState(prev => ({ ...prev, isLoading: true, error: undefined }));
    
    try {
      const examAttempt = await pharmxamApi.startExam({
        category: config.category,
        difficulty: config.difficulty,
        num_questions: config.numQuestions,
      });
      
      setState(prev => ({
        ...prev,
        view: 'session',
        currentExamAttempt: examAttempt,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Failed to start exam:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to start exam. Please try again.',
        isLoading: false,
      }));
    }
  };

  const handleExamComplete = (completedAttempt: ExamAttempt) => {
    setState(prev => ({
      ...prev,
      view: 'results',
      currentExamAttempt: completedAttempt,
    }));
  };

  const handleExamExit = () => {
    setState(prev => ({
      ...prev,
      view: 'list',
      currentExamAttempt: undefined,
    }));
  };

  const handleReviewExam = (attemptId?: number) => {
    const reviewId = attemptId || state.currentExamAttempt?.id;
    if (reviewId) {
      setState(prev => ({
        ...prev,
        view: 'review',
        reviewAttemptId: reviewId,
      }));
    }
  };

  const handleViewHistory = () => {
    setState(prev => ({
      ...prev,
      view: 'history',
    }));
  };

  const handleBackToList = () => {
    setState(prev => ({
      ...prev,
      view: 'list',
      currentExamAttempt: undefined,
      reviewAttemptId: undefined,
      error: undefined,
    }));
  };

  const renderCurrentView = () => {
    switch (state.view) {
      case 'session':
        if (!state.currentExamAttempt) {
          return <div>No active exam session</div>;
        }
        return (
          <ExamSession
            examAttempt={state.currentExamAttempt}
            onExamComplete={handleExamComplete}
            onExamExit={handleExamExit}
          />
        );

      case 'results':
        if (!state.currentExamAttempt) {
          return <div>No exam results available</div>;
        }
        return (
          <ExamResults
            examAttempt={state.currentExamAttempt}
            onReviewExam={() => handleReviewExam()}
            onStartNewExam={handleBackToList}
            onViewHistory={handleViewHistory}
          />
        );

      case 'history':
        return (
          <ExamHistory
            onReviewExam={handleReviewExam}
            onStartNewExam={handleBackToList}
          />
        );

      case 'review':
        if (!state.reviewAttemptId) {
          return <div>No exam to review</div>;
        }
        return (
          <ExamReview
            attemptId={state.reviewAttemptId}
            onBack={() => setState(prev => ({ ...prev, view: 'history' }))}
          />
        );

      case 'list':
      default:
        return (
          <ExamList
            onStartExam={handleStartExam}
            isLoading={state.isLoading}
          />
        );
    }
  };

  if (state.error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{state.error}</p>
          <button
            onClick={handleBackToList}
            className="mt-2 text-red-600 hover:text-red-800 underline"
          >
            Go back to exam list
          </button>
        </div>
      </div>
    );
  }

  return renderCurrentView();
}

export default function PharmxamPage() {
  return (
    <ProtectedRoute>
      <PharmxamPageContent />
    </ProtectedRoute>
  );
}
