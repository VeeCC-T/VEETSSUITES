'use client';

import React from 'react';
import { Card, Button } from '@/components/ui';
import { ExamAttempt } from '@/lib/pharmxam/api';

interface ExamResultsProps {
  examAttempt: ExamAttempt;
  onReviewExam: () => void;
  onStartNewExam: () => void;
  onViewHistory: () => void;
}

interface CategoryStats {
  category: string;
  correct: number;
  total: number;
  percentage: number;
}

interface DifficultyStats {
  difficulty: string;
  correct: number;
  total: number;
  percentage: number;
}

/**
 * ExamResults component with score display and performance breakdown
 * Validates: Requirements 4.4
 */
export const ExamResults: React.FC<ExamResultsProps> = ({
  examAttempt,
  onReviewExam,
  onStartNewExam,
  onViewHistory,
}) => {
  // Calculate category breakdown
  const categoryStats: CategoryStats[] = React.useMemo(() => {
    if (!examAttempt.exam_answers) return [];

    const categoryMap = new Map<string, { correct: number; total: number }>();

    examAttempt.exam_answers.forEach(answer => {
      const category = answer.question.category;
      const current = categoryMap.get(category) || { correct: 0, total: 0 };
      
      categoryMap.set(category, {
        correct: current.correct + (answer.is_correct ? 1 : 0),
        total: current.total + 1,
      });
    });

    return Array.from(categoryMap.entries()).map(([category, stats]) => ({
      category,
      correct: stats.correct,
      total: stats.total,
      percentage: Math.round((stats.correct / stats.total) * 100),
    })).sort((a, b) => b.percentage - a.percentage);
  }, [examAttempt.exam_answers]);

  // Calculate difficulty breakdown
  const difficultyStats: DifficultyStats[] = React.useMemo(() => {
    if (!examAttempt.exam_answers) return [];

    const difficultyMap = new Map<string, { correct: number; total: number }>();

    examAttempt.exam_answers.forEach(answer => {
      const difficulty = answer.question.difficulty;
      const current = difficultyMap.get(difficulty) || { correct: 0, total: 0 };
      
      difficultyMap.set(difficulty, {
        correct: current.correct + (answer.is_correct ? 1 : 0),
        total: current.total + 1,
      });
    });

    const difficultyOrder = ['easy', 'medium', 'hard'];
    return difficultyOrder
      .filter(difficulty => difficultyMap.has(difficulty))
      .map(difficulty => {
        const stats = difficultyMap.get(difficulty)!;
        return {
          difficulty: difficulty.charAt(0).toUpperCase() + difficulty.slice(1),
          correct: stats.correct,
          total: stats.total,
          percentage: Math.round((stats.correct / stats.total) * 100),
        };
      });
  }, [examAttempt.exam_answers]);

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-50 border-green-200';
    if (percentage >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
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

  const overallPercentage = examAttempt.percentage_score || 0;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Exam Results</h1>
        <p className="text-gray-600">
          Completed on {examAttempt.completed_at ? formatDate(examAttempt.completed_at) : 'Unknown'}
        </p>
      </div>

      {/* Overall Score */}
      <Card className={`border-2 ${getScoreBgColor(overallPercentage)}`}>
        <div className="p-8 text-center">
          <div className={`text-6xl font-bold mb-2 ${getScoreColor(overallPercentage)}`}>
            {overallPercentage}%
          </div>
          <div className="text-xl text-gray-700 mb-4">
            {examAttempt.score} out of {examAttempt.total_questions} correct
          </div>
          <div className="text-lg font-medium">
            {overallPercentage >= 80 ? '🎉 Excellent!' : 
             overallPercentage >= 60 ? '👍 Good job!' : 
             '📚 Keep studying!'}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Performance by Category
            </h2>
            <div className="space-y-4">
              {categoryStats.map((stat) => (
                <div key={stat.category} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {stat.category}
                      </span>
                      <span className="text-sm text-gray-500">
                        {stat.correct}/{stat.total}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          stat.percentage >= 80 ? 'bg-green-500' :
                          stat.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${stat.percentage}%` }}
                      />
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <span className={`text-sm font-semibold ${getScoreColor(stat.percentage)}`}>
                      {stat.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Difficulty Breakdown */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Performance by Difficulty
            </h2>
            <div className="space-y-4">
              {difficultyStats.map((stat) => (
                <div key={stat.difficulty} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {stat.difficulty}
                      </span>
                      <span className="text-sm text-gray-500">
                        {stat.correct}/{stat.total}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          stat.percentage >= 80 ? 'bg-green-500' :
                          stat.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${stat.percentage}%` }}
                      />
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <span className={`text-sm font-semibold ${getScoreColor(stat.percentage)}`}>
                      {stat.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button
          onClick={onReviewExam}
          variant="outline"
          className="px-6 py-3"
        >
          Review Answers
        </Button>
        <Button
          onClick={onStartNewExam}
          className="px-6 py-3"
        >
          Take Another Exam
        </Button>
        <Button
          onClick={onViewHistory}
          variant="outline"
          className="px-6 py-3"
        >
          View History
        </Button>
      </div>

      {/* Study Recommendations */}
      {overallPercentage < 80 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              📚 Study Recommendations
            </h2>
            <div className="space-y-2">
              {categoryStats
                .filter(stat => stat.percentage < 70)
                .slice(0, 3)
                .map(stat => (
                  <p key={stat.category} className="text-gray-700">
                    • Focus on <strong>{stat.category}</strong> - you scored {stat.percentage}% ({stat.correct}/{stat.total})
                  </p>
                ))}
              {categoryStats.filter(stat => stat.percentage < 70).length === 0 && (
                <p className="text-gray-700">
                  • Great job! Continue practicing to maintain your performance.
                </p>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};