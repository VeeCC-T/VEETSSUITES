'use client';

import React, { useState, useEffect } from 'react';
import { Card, Button } from '@/components/ui';
import { QuestionCard } from './QuestionCard';
import { ExamAttempt, pharmxamApi } from '@/lib/pharmxam/api';

interface ExamReviewProps {
  attemptId: number;
  onBack: () => void;
}

/**
 * ExamReview component for reviewing completed exams with correct/incorrect answers
 * Validates: Requirements 4.5
 */
export const ExamReview: React.FC<ExamReviewProps> = ({
  attemptId,
  onBack,
}) => {
  const [examAttempt, setExamAttempt] = useState<ExamAttempt | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'correct' | 'incorrect'>('all');

  useEffect(() => {
    loadExamReview();
  }, [attemptId]);

  const loadExamReview = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const attempt = await pharmxamApi.reviewExam(attemptId);
      setExamAttempt(attempt);
    } catch (err) {
      setError('Failed to load exam review');
      console.error('Failed to load exam review:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-gray-600">Loading exam review...</p>
          </div>
        </Card>
      </div>
    );
  }

  if (error || !examAttempt) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-red-600 mb-4">{error || 'Exam not found'}</p>
            <Button onClick={onBack}>Go Back</Button>
          </div>
        </Card>
      </div>
    );
  }

  const answers = examAttempt.exam_answers || [];
  
  // Filter questions based on filter type
  const filteredAnswers = answers.filter(answer => {
    if (filterType === 'correct') return answer.is_correct;
    if (filterType === 'incorrect') return !answer.is_correct;
    return true;
  });

  const currentAnswer = filteredAnswers[currentQuestionIndex];

  if (!currentAnswer) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-gray-600">No questions match the current filter.</p>
            <Button onClick={() => setFilterType('all')} className="mt-4">
              Show All Questions
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const correctCount = answers.filter(a => a.is_correct).length;
  const incorrectCount = answers.length - correctCount;

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <Card className="mb-6">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Exam Review #{examAttempt.id}
              </h1>
              <p className="text-gray-600">
                Completed on {examAttempt.completed_at ? formatDate(examAttempt.completed_at) : 'Unknown'}
              </p>
            </div>
            <Button variant="outline" onClick={onBack}>
              Back to History
            </Button>
          </div>

          {/* Score Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {examAttempt.percentage_score || 0}%
              </div>
              <div className="text-sm text-gray-600">Overall Score</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {correctCount}
              </div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {incorrectCount}
              </div>
              <div className="text-sm text-gray-600">Incorrect</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-600">
                {examAttempt.total_questions}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>

          {/* Filter Controls */}
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setFilterType('all');
                  setCurrentQuestionIndex(0);
                }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                All ({answers.length})
              </button>
              <button
                onClick={() => {
                  setFilterType('correct');
                  setCurrentQuestionIndex(0);
                }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filterType === 'correct'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Correct ({correctCount})
              </button>
              <button
                onClick={() => {
                  setFilterType('incorrect');
                  setCurrentQuestionIndex(0);
                }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filterType === 'incorrect'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Incorrect ({incorrectCount})
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Question Navigation */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-gray-700">
              Question {currentQuestionIndex + 1} of {filteredAnswers.length}
              {filterType !== 'all' && ` (${filterType})`}
            </span>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentQuestionIndex(Math.min(filteredAnswers.length - 1, currentQuestionIndex + 1))}
                disabled={currentQuestionIndex === filteredAnswers.length - 1}
              >
                Next
              </Button>
            </div>
          </div>

          {/* Question Grid Navigation */}
          <div className="flex flex-wrap gap-2">
            {filteredAnswers.map((answer, index) => (
              <button
                key={answer.id}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-10 h-10 rounded-lg border-2 font-medium transition-all ${
                  index === currentQuestionIndex
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : answer.is_correct
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-red-500 bg-red-50 text-red-700'
                }`}
                title={answer.is_correct ? 'Correct' : 'Incorrect'}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Current Question */}
      <QuestionCard
        question={{
          ...currentAnswer.question,
          correct_answer: currentAnswer.question.correct_answer,
        }}
        selectedAnswer={currentAnswer.selected_answer || undefined}
        onAnswerSelect={() => {}} // No-op in review mode
        showFeedback={true}
        isReviewMode={true}
      />

      {/* Additional Question Info */}
      <Card className="mt-6">
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Category:</span>
              <span className="ml-2 text-gray-600">{currentAnswer.question.category}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Difficulty:</span>
              <span className="ml-2 text-gray-600 capitalize">{currentAnswer.question.difficulty}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Your Answer:</span>
              <span className={`ml-2 font-medium ${
                currentAnswer.is_correct ? 'text-green-600' : 'text-red-600'
              }`}>
                {currentAnswer.selected_answer || 'Not answered'} 
                {currentAnswer.is_correct ? ' ✓' : ' ✗'}
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};