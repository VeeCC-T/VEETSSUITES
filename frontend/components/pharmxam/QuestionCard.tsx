'use client';

import React from 'react';
import { Card, Button } from '@/components/ui';
import { Question } from '@/lib/pharmxam/api';

interface QuestionCardProps {
  question: Question;
  selectedAnswer?: string;
  onAnswerSelect: (answer: 'A' | 'B' | 'C' | 'D') => void;
  showFeedback?: boolean;
  isReviewMode?: boolean;
  onNext?: () => void;
  onPrevious?: () => void;
  canGoNext?: boolean;
  canGoPrevious?: boolean;
}

/**
 * QuestionCard component for displaying individual MCQ questions
 * Validates: Requirements 4.3
 */
export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  selectedAnswer,
  onAnswerSelect,
  showFeedback = false,
  isReviewMode = false,
  onNext,
  onPrevious,
  canGoNext = false,
  canGoPrevious = false,
}) => {
  const options = ['A', 'B', 'C', 'D'] as const;

  const getOptionClassName = (option: string) => {
    const baseClasses = "w-full text-left p-4 border-2 rounded-lg transition-all duration-200 hover:bg-gray-50";
    
    if (!selectedAnswer) {
      return `${baseClasses} border-gray-200 hover:border-gray-300`;
    }

    if (selectedAnswer === option) {
      if (showFeedback && question.correct_answer) {
        // Show correct/incorrect feedback
        if (option === question.correct_answer) {
          return `${baseClasses} border-green-500 bg-green-50 text-green-800`;
        } else {
          return `${baseClasses} border-red-500 bg-red-50 text-red-800`;
        }
      } else {
        // Just show selected state
        return `${baseClasses} border-blue-500 bg-blue-50 text-blue-800`;
      }
    }

    if (showFeedback && question.correct_answer && option === question.correct_answer) {
      // Show correct answer even if not selected
      return `${baseClasses} border-green-500 bg-green-50 text-green-800`;
    }

    return `${baseClasses} border-gray-200`;
  };

  const getOptionIcon = (option: string) => {
    if (!selectedAnswer || !showFeedback || !question.correct_answer) {
      return null;
    }

    if (selectedAnswer === option) {
      if (option === question.correct_answer) {
        return <span className="text-green-600 font-bold">✓</span>;
      } else {
        return <span className="text-red-600 font-bold">✗</span>;
      }
    }

    if (option === question.correct_answer) {
      return <span className="text-green-600 font-bold">✓</span>;
    }

    return null;
  };

  return (
    <Card>
      <div className="p-6">
        {/* Question Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-500">
              {question.category} • {question.difficulty}
            </span>
            {showFeedback && question.correct_answer && (
              <span className={`text-sm font-medium px-2 py-1 rounded ${
                selectedAnswer === question.correct_answer 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {selectedAnswer === question.correct_answer ? 'Correct' : 'Incorrect'}
              </span>
            )}
          </div>
          <h3 className="text-lg font-medium text-gray-900 leading-relaxed">
            {question.text}
          </h3>
        </div>

        {/* Answer Options */}
        <div className="space-y-3 mb-6">
          {options.map((option) => (
            <button
              key={option}
              onClick={() => !isReviewMode && onAnswerSelect(option)}
              disabled={isReviewMode}
              className={getOptionClassName(option)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start space-x-3">
                  <span className="font-semibold text-gray-700 mt-0.5">
                    {option}.
                  </span>
                  <span className="flex-1">
                    {question.options[option]}
                  </span>
                </div>
                {getOptionIcon(option)}
              </div>
            </button>
          ))}
        </div>

        {/* Navigation Buttons */}
        {(onPrevious || onNext) && (
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={onPrevious}
              disabled={!canGoPrevious}
              className={!canGoPrevious ? 'invisible' : ''}
            >
              Previous
            </Button>
            <Button
              onClick={onNext}
              disabled={!canGoNext}
              className={!canGoNext ? 'invisible' : ''}
            >
              Next
            </Button>
          </div>
        )}

        {/* Feedback Message */}
        {showFeedback && question.correct_answer && (
          <div className={`mt-4 p-3 rounded-lg ${
            selectedAnswer === question.correct_answer
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}>
            <p className={`text-sm ${
              selectedAnswer === question.correct_answer
                ? 'text-green-800'
                : 'text-red-800'
            }`}>
              {selectedAnswer === question.correct_answer
                ? 'Correct! Well done.'
                : `Incorrect. The correct answer is ${question.correct_answer}.`
              }
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};