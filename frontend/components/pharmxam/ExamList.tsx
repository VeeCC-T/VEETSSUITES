'use client';

import React, { useState } from 'react';
import { Card, Button } from '@/components/ui';
import { ExamConfig } from '@/lib/pharmxam/types';

interface ExamListProps {
  onStartExam: (config: ExamConfig) => void;
  isLoading?: boolean;
}

/**
 * ExamList component showing available exam configurations
 * Validates: Requirements 4.2
 */
export const ExamList: React.FC<ExamListProps> = ({ onStartExam, isLoading = false }) => {
  const [selectedConfig, setSelectedConfig] = useState<ExamConfig>({
    numQuestions: 20,
  });

  const categories = [
    'All Categories',
    'Pharmacology',
    'Clinical Pharmacy',
    'Pharmaceutical Chemistry',
    'Pharmaceutics',
    'Pharmacognosy',
    'Pharmacy Practice',
  ];

  const difficulties = [
    { value: undefined, label: 'All Difficulties' },
    { value: 'easy' as const, label: 'Easy' },
    { value: 'medium' as const, label: 'Medium' },
    { value: 'hard' as const, label: 'Hard' },
  ];

  const questionCounts = [10, 20, 30, 50];

  const handleStartExam = () => {
    const config: ExamConfig = {
      ...selectedConfig,
      category: selectedConfig.category === 'All Categories' ? undefined : selectedConfig.category,
    };
    onStartExam(config);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">PHARMXAM Practice</h1>
        <p className="text-gray-600">
          Test your pharmacy knowledge with our comprehensive question bank
        </p>
      </div>

      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Configure Your Exam</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Category Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={selectedConfig.category || 'All Categories'}
                onChange={(e) => setSelectedConfig({
                  ...selectedConfig,
                  category: e.target.value === 'All Categories' ? undefined : e.target.value
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty
              </label>
              <select
                value={selectedConfig.difficulty || ''}
                onChange={(e) => setSelectedConfig({
                  ...selectedConfig,
                  difficulty: e.target.value as 'easy' | 'medium' | 'hard' | undefined
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {difficulties.map((difficulty) => (
                  <option key={difficulty.label} value={difficulty.value || ''}>
                    {difficulty.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Number of Questions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions
              </label>
              <select
                value={selectedConfig.numQuestions}
                onChange={(e) => setSelectedConfig({
                  ...selectedConfig,
                  numQuestions: parseInt(e.target.value)
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {questionCounts.map((count) => (
                  <option key={count} value={count}>
                    {count} questions
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-8 text-center">
            <Button
              onClick={handleStartExam}
              disabled={isLoading}
              className="px-8 py-3 text-lg"
            >
              {isLoading ? 'Starting Exam...' : 'Start Practice Exam'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Quick Start Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="p-4 text-center">
            <h3 className="font-semibold text-gray-900 mb-2">Quick Practice</h3>
            <p className="text-sm text-gray-600 mb-4">
              20 random questions from all categories
            </p>
            <Button
              variant="outline"
              onClick={() => onStartExam({ numQuestions: 20 })}
              disabled={isLoading}
              className="w-full"
            >
              Start Now
            </Button>
          </div>
        </Card>

        <Card>
          <div className="p-4 text-center">
            <h3 className="font-semibold text-gray-900 mb-2">Pharmacology Focus</h3>
            <p className="text-sm text-gray-600 mb-4">
              30 pharmacology questions
            </p>
            <Button
              variant="outline"
              onClick={() => onStartExam({ 
                category: 'Pharmacology', 
                numQuestions: 30 
              })}
              disabled={isLoading}
              className="w-full"
            >
              Start Now
            </Button>
          </div>
        </Card>

        <Card>
          <div className="p-4 text-center">
            <h3 className="font-semibold text-gray-900 mb-2">Challenge Mode</h3>
            <p className="text-sm text-gray-600 mb-4">
              50 hard questions
            </p>
            <Button
              variant="outline"
              onClick={() => onStartExam({ 
                difficulty: 'hard', 
                numQuestions: 50 
              })}
              disabled={isLoading}
              className="w-full"
            >
              Start Now
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};