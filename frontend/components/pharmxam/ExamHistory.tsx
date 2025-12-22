'use client';

import React, { useState, useEffect } from 'react';
import { Card, Button } from '@/components/ui';
import { ExamAttempt, pharmxamApi } from '@/lib/pharmxam/api';

interface ExamHistoryProps {
  onReviewExam: (attemptId: number) => void;
  onStartNewExam: () => void;
}

/**
 * ExamHistory component showing past exam attempts
 * Validates: Requirements 4.5
 */
export const ExamHistory: React.FC<ExamHistoryProps> = ({
  onReviewExam,
  onStartNewExam,
}) => {
  const [examHistory, setExamHistory] = useState<ExamAttempt[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExamHistory();
  }, []);

  const loadExamHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const history = await pharmxamApi.getExamHistory();
      setExamHistory(history);
    } catch (err) {
      setError('Failed to load exam history');
      console.error('Failed to load exam history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-100 text-green-800';
    if (percentage >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const calculateAverageScore = () => {
    if (examHistory.length === 0) return 0;
    const total = examHistory.reduce((sum, attempt) => sum + (attempt.percentage_score || 0), 0);
    return Math.round(total / examHistory.length);
  };

  const getBestScore = () => {
    if (examHistory.length === 0) return 0;
    return Math.max(...examHistory.map(attempt => attempt.percentage_score || 0));
  };

  const getRecentTrend = () => {
    if (examHistory.length < 2) return null;
    
    const recent = examHistory.slice(0, 3);
    const older = examHistory.slice(3, 6);
    
    if (older.length === 0) return null;
    
    const recentAvg = recent.reduce((sum, attempt) => sum + (attempt.percentage_score || 0), 0) / recent.length;
    const olderAvg = older.reduce((sum, attempt) => sum + (attempt.percentage_score || 0), 0) / older.length;
    
    const diff = recentAvg - olderAvg;
    
    if (Math.abs(diff) < 5) return 'stable';
    return diff > 0 ? 'improving' : 'declining';
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-gray-600">Loading exam history...</p>
          </div>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadExamHistory}>Try Again</Button>
          </div>
        </Card>
      </div>
    );
  }

  const averageScore = calculateAverageScore();
  const bestScore = getBestScore();
  const trend = getRecentTrend();

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Exam History</h1>
        <p className="text-gray-600">
          Track your progress and review past performance
        </p>
      </div>

      {examHistory.length === 0 ? (
        <Card>
          <div className="p-8 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              No Exams Completed Yet
            </h2>
            <p className="text-gray-600 mb-6">
              Start your first practice exam to begin tracking your progress.
            </p>
            <Button onClick={onStartNewExam} className="px-6 py-3">
              Start Your First Exam
            </Button>
          </div>
        </Card>
      ) : (
        <>
          {/* Statistics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {examHistory.length}
                </div>
                <div className="text-gray-600">Total Exams</div>
              </div>
            </Card>
            
            <Card>
              <div className="p-6 text-center">
                <div className={`text-3xl font-bold mb-2 ${getScoreColor(averageScore)}`}>
                  {averageScore}%
                </div>
                <div className="text-gray-600">Average Score</div>
              </div>
            </Card>
            
            <Card>
              <div className="p-6 text-center">
                <div className={`text-3xl font-bold mb-2 ${getScoreColor(bestScore)}`}>
                  {bestScore}%
                </div>
                <div className="text-gray-600">Best Score</div>
                {trend && (
                  <div className={`text-sm mt-1 ${
                    trend === 'improving' ? 'text-green-600' :
                    trend === 'declining' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {trend === 'improving' ? '📈 Improving' :
                     trend === 'declining' ? '📉 Needs focus' : '➡️ Stable'}
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Exam History List */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  Recent Exams
                </h2>
                <Button onClick={onStartNewExam}>
                  Start New Exam
                </Button>
              </div>

              <div className="space-y-4">
                {examHistory.map((attempt) => (
                  <div
                    key={attempt.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <div>
                            <div className="font-medium text-gray-900">
                              Exam #{attempt.id}
                            </div>
                            <div className="text-sm text-gray-500">
                              {attempt.completed_at ? formatDate(attempt.completed_at) : 'In Progress'}
                            </div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-sm text-gray-500">Score</div>
                            <div className={`font-semibold ${getScoreColor(attempt.percentage_score || 0)}`}>
                              {attempt.score}/{attempt.total_questions}
                            </div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-sm text-gray-500">Percentage</div>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              getScoreBadgeColor(attempt.percentage_score || 0)
                            }`}>
                              {attempt.percentage_score || 0}%
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onReviewExam(attempt.id)}
                        >
                          Review
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {examHistory.length > 10 && (
                <div className="mt-6 text-center">
                  <Button variant="outline">
                    Load More
                  </Button>
                </div>
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  );
};