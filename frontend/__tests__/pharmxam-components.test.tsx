/**
 * Tests for PHARMXAM components
 * Validates: Requirements 4.2, 4.3, 4.4, 4.5
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ExamList, QuestionCard, ExamResults } from '@/components/pharmxam';
import { ExamAttempt, Question } from '@/lib/pharmxam/api';

// Mock the pharmxam API
jest.mock('@/lib/pharmxam/api', () => ({
  pharmxamApi: {
    startExam: jest.fn(),
    getExamHistory: jest.fn(),
  },
}));

describe('PHARMXAM Components', () => {
  describe('ExamList', () => {
    it('renders exam configuration options', () => {
      const mockOnStartExam = jest.fn();
      
      render(<ExamList onStartExam={mockOnStartExam} />);
      
      expect(screen.getByText('PHARMXAM Practice')).toBeInTheDocument();
      expect(screen.getByText('Configure Your Exam')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Difficulty')).toBeInTheDocument();
      expect(screen.getByText('Number of Questions')).toBeInTheDocument();
    });

    it('displays quick start options', () => {
      const mockOnStartExam = jest.fn();
      
      render(<ExamList onStartExam={mockOnStartExam} />);
      
      expect(screen.getByText('Quick Practice')).toBeInTheDocument();
      expect(screen.getByText('Pharmacology Focus')).toBeInTheDocument();
      expect(screen.getByText('Challenge Mode')).toBeInTheDocument();
    });
  });

  describe('QuestionCard', () => {
    const mockQuestion: Question = {
      id: 1,
      text: 'What is the mechanism of action of aspirin?',
      options: {
        A: 'COX-1 inhibition',
        B: 'COX-2 inhibition',
        C: 'Both COX-1 and COX-2 inhibition',
        D: 'Prostaglandin synthesis',
      },
      category: 'Pharmacology',
      difficulty: 'medium',
      created_at: '2024-01-01T00:00:00Z',
    };

    it('renders question text and options', () => {
      const mockOnAnswerSelect = jest.fn();
      
      render(
        <QuestionCard
          question={mockQuestion}
          onAnswerSelect={mockOnAnswerSelect}
        />
      );
      
      expect(screen.getByText('What is the mechanism of action of aspirin?')).toBeInTheDocument();
      expect(screen.getByText('COX-1 inhibition')).toBeInTheDocument();
      expect(screen.getByText('COX-2 inhibition')).toBeInTheDocument();
      expect(screen.getByText('Both COX-1 and COX-2 inhibition')).toBeInTheDocument();
      expect(screen.getByText('Prostaglandin synthesis')).toBeInTheDocument();
    });

    it('displays category and difficulty', () => {
      const mockOnAnswerSelect = jest.fn();
      
      render(
        <QuestionCard
          question={mockQuestion}
          onAnswerSelect={mockOnAnswerSelect}
        />
      );
      
      expect(screen.getByText('Pharmacology • medium')).toBeInTheDocument();
    });
  });

  describe('ExamResults', () => {
    const mockExamAttempt: ExamAttempt = {
      id: 1,
      student: 1,
      student_username: 'testuser',
      score: 16,
      total_questions: 20,
      percentage_score: 80,
      status: 'completed',
      is_completed: true,
      started_at: '2024-01-01T10:00:00Z',
      completed_at: '2024-01-01T10:30:00Z',
      exam_answers: [
        {
          id: 1,
          question: {
            id: 1,
            text: 'Test question',
            options: { A: 'Option A', B: 'Option B', C: 'Option C', D: 'Option D' },
            category: 'Pharmacology',
            difficulty: 'medium',
            created_at: '2024-01-01T00:00:00Z',
            correct_answer: 'A',
          },
          question_id: 1,
          selected_answer: 'A',
          is_correct: true,
          answered_at: '2024-01-01T10:05:00Z',
        },
      ],
    };

    it('displays overall score and percentage', () => {
      const mockProps = {
        onReviewExam: jest.fn(),
        onStartNewExam: jest.fn(),
        onViewHistory: jest.fn(),
      };
      
      render(<ExamResults examAttempt={mockExamAttempt} {...mockProps} />);
      
      expect(screen.getByText('80%')).toBeInTheDocument();
      expect(screen.getByText('16 out of 20 correct')).toBeInTheDocument();
    });

    it('displays action buttons', () => {
      const mockProps = {
        onReviewExam: jest.fn(),
        onStartNewExam: jest.fn(),
        onViewHistory: jest.fn(),
      };
      
      render(<ExamResults examAttempt={mockExamAttempt} {...mockProps} />);
      
      expect(screen.getByText('Review Answers')).toBeInTheDocument();
      expect(screen.getByText('Take Another Exam')).toBeInTheDocument();
      expect(screen.getByText('View History')).toBeInTheDocument();
    });
  });
});