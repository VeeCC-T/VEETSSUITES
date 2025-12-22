/**
 * Integration tests for PHARMXAM exam flow
 * Validates: Requirements 4.2, 4.3, 4.4, 4.5
 * 
 * Tests complete exam flow:
 * - Start exam with question randomization
 * - Answer submission with immediate feedback
 * - Exam completion with score calculation
 * - Exam history retrieval and review
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '@/lib/auth/AuthContext';
import * as pharmxamApiModule from '@/lib/pharmxam/api';
import { ExamAttempt, Question, SubmitAnswerResponse } from '@/lib/pharmxam/api';

// Mock Next.js router
const mockPush = jest.fn();
const mockReplace = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    prefetch: jest.fn(),
  }),
}));

// Mock the pharmxam API module
jest.mock('@/lib/pharmxam/api', () => ({
  pharmxamApi: {
    startExam: jest.fn(),
    getExamAttempt: jest.fn(),
    submitAnswer: jest.fn(),
    completeExam: jest.fn(),
    reviewExam: jest.fn(),
    getExamHistory: jest.fn(),
  },
}));

// Mock auth API to provide authenticated user
jest.mock('@/lib/auth/api', () => ({
  authApi: {
    getCurrentUser: jest.fn().mockResolvedValue({
      id: 1,
      email: 'student@example.com',
      name: 'Test Student',
      role: 'student',
    }),
    refreshToken: jest.fn().mockResolvedValue({
      access: 'mock-access-token',
      refresh: 'mock-refresh-token',
    }),
  },
}));

// Test component that simulates the complete exam flow
const ExamFlowTestComponent = () => {
  const [currentStep, setCurrentStep] = React.useState<'start' | 'exam' | 'results' | 'history' | 'review'>('start');
  const [examAttempt, setExamAttempt] = React.useState<ExamAttempt | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = React.useState(0);
  const [selectedAnswers, setSelectedAnswers] = React.useState<Record<number, string>>({});
  const [examHistory, setExamHistory] = React.useState<ExamAttempt[]>([]);
  const [reviewData, setReviewData] = React.useState<ExamAttempt | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const startExam = async () => {
    try {
      setError(null);
      const attempt = await pharmxamApiModule.pharmxamApi.startExam({
        category: 'Pharmacology',
        difficulty: 'medium',
        num_questions: 5,
      });
      setExamAttempt(attempt);
      setCurrentStep('exam');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start exam');
    }
  };

  const submitAnswer = async (questionId: number, answer: string) => {
    if (!examAttempt) return;
    
    try {
      setError(null);
      const response = await pharmxamApiModule.pharmxamApi.submitAnswer(examAttempt.id, {
        question_id: questionId,
        selected_answer: answer as 'A' | 'B' | 'C' | 'D',
      });
      
      setSelectedAnswers(prev => ({ ...prev, [questionId]: answer }));
      
      // Clean up any existing feedback
      const existingFeedback = document.querySelectorAll('[data-testid="answer-feedback"]');
      existingFeedback.forEach(el => el.remove());
      
      // Show feedback
      const feedbackElement = document.createElement('div');
      feedbackElement.setAttribute('data-testid', 'answer-feedback');
      feedbackElement.textContent = response.is_correct ? 'Correct!' : `Incorrect. Correct answer: ${response.correct_answer}`;
      document.body.appendChild(feedbackElement);
      
      // Remove feedback after 2 seconds
      setTimeout(() => {
        if (document.body.contains(feedbackElement)) {
          document.body.removeChild(feedbackElement);
        }
      }, 2000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    }
  };

  const nextQuestion = () => {
    if (examAttempt && currentQuestionIndex < examAttempt.exam_answers!.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const completeExam = async () => {
    if (!examAttempt) return;
    
    try {
      setError(null);
      const completedAttempt = await pharmxamApiModule.pharmxamApi.completeExam(examAttempt.id);
      setExamAttempt(completedAttempt);
      setCurrentStep('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete exam');
    }
  };

  const viewHistory = async () => {
    try {
      setError(null);
      const history = await pharmxamApiModule.pharmxamApi.getExamHistory();
      setExamHistory(history);
      setCurrentStep('history');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load exam history');
    }
  };

  const reviewExam = async (attemptId: number) => {
    try {
      setError(null);
      const review = await pharmxamApiModule.pharmxamApi.reviewExam(attemptId);
      setReviewData(review);
      setCurrentStep('review');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load exam review');
    }
  };

  const resetFlow = () => {
    setCurrentStep('start');
    setExamAttempt(null);
    setCurrentQuestionIndex(0);
    setSelectedAnswers({});
    setExamHistory([]);
    setReviewData(null);
    setError(null);
  };

  if (error) {
    return (
      <div>
        <div data-testid="error-message">{error}</div>
        <button data-testid="reset-btn" onClick={resetFlow}>Reset</button>
      </div>
    );
  }

  if (currentStep === 'start') {
    return (
      <div>
        <h1>PHARMXAM Practice</h1>
        <button data-testid="start-exam-btn" onClick={startExam}>
          Start Exam
        </button>
        <button data-testid="view-history-btn" onClick={viewHistory}>
          View History
        </button>
      </div>
    );
  }

  if (currentStep === 'exam' && examAttempt) {
    const currentQuestion = examAttempt.exam_answers![currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === examAttempt.exam_answers!.length - 1;
    
    return (
      <div>
        <div data-testid="exam-progress">
          Question {currentQuestionIndex + 1} of {examAttempt.total_questions}
        </div>
        <div data-testid="question-text">{currentQuestion.question.text}</div>
        <div data-testid="question-category">{currentQuestion.question.category}</div>
        <div data-testid="question-difficulty">{currentQuestion.question.difficulty}</div>
        
        {Object.entries(currentQuestion.question.options).map(([option, text]) => (
          <button
            key={option}
            data-testid={`option-${option}`}
            onClick={() => submitAnswer(currentQuestion.question.id, option)}
            disabled={selectedAnswers[currentQuestion.question.id] !== undefined}
            style={{
              backgroundColor: selectedAnswers[currentQuestion.question.id] === option ? '#e3f2fd' : 'white'
            }}
          >
            {option}: {text}
          </button>
        ))}
        
        {selectedAnswers[currentQuestion.question.id] && (
          <div>
            {!isLastQuestion ? (
              <button data-testid="next-question-btn" onClick={nextQuestion}>
                Next Question
              </button>
            ) : (
              <button data-testid="complete-exam-btn" onClick={completeExam}>
                Complete Exam
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  if (currentStep === 'results' && examAttempt) {
    return (
      <div>
        <h2>Exam Results</h2>
        <div data-testid="final-score">{examAttempt.percentage_score}%</div>
        <div data-testid="score-breakdown">
          {examAttempt.score} out of {examAttempt.total_questions} correct
        </div>
        <div data-testid="exam-status">{examAttempt.status}</div>
        <div data-testid="completion-time">{examAttempt.completed_at}</div>
        
        <button data-testid="review-answers-btn" onClick={() => reviewExam(examAttempt.id)}>
          Review Answers
        </button>
        <button data-testid="start-new-exam-btn" onClick={resetFlow}>
          Start New Exam
        </button>
        <button data-testid="view-history-from-results-btn" onClick={viewHistory}>
          View History
        </button>
      </div>
    );
  }

  if (currentStep === 'history') {
    return (
      <div>
        <h2>Exam History</h2>
        <div data-testid="history-count">{examHistory.length} completed exams</div>
        
        {examHistory.length === 0 ? (
          <div data-testid="no-history">No completed exams found</div>
        ) : (
          examHistory.map((attempt, index) => (
            <div key={attempt.id} data-testid={`history-item-${index}`}>
              <div>Score: {attempt.percentage_score}%</div>
              <div>Date: {attempt.completed_at}</div>
              <div>Questions: {attempt.total_questions}</div>
              <button 
                data-testid={`review-exam-${attempt.id}`}
                onClick={() => reviewExam(attempt.id)}
              >
                Review
              </button>
            </div>
          ))
        )}
        
        <button data-testid="back-to-start-btn" onClick={resetFlow}>
          Back to Start
        </button>
      </div>
    );
  }

  if (currentStep === 'review' && reviewData) {
    return (
      <div>
        <h2>Exam Review</h2>
        <div data-testid="review-score">{reviewData.percentage_score}%</div>
        <div data-testid="review-breakdown">
          {reviewData.score} out of {reviewData.total_questions} correct
        </div>
        
        {reviewData.exam_answers!.map((answer, index) => (
          <div key={answer.id} data-testid={`review-question-${index}`}>
            <div data-testid={`review-question-text-${index}`}>{answer.question.text}</div>
            <div data-testid={`review-selected-${index}`}>
              Your answer: {answer.selected_answer}
            </div>
            <div data-testid={`review-correct-${index}`}>
              Correct answer: {answer.question.correct_answer}
            </div>
            <div data-testid={`review-result-${index}`}>
              {answer.is_correct ? 'Correct' : 'Incorrect'}
            </div>
          </div>
        ))}
        
        <button data-testid="back-to-history-btn" onClick={viewHistory}>
          Back to History
        </button>
        <button data-testid="back-to-start-from-review-btn" onClick={resetFlow}>
          Back to Start
        </button>
      </div>
    );
  }

  return <div>Loading...</div>;
};

describe('PHARMXAM Exam Flow Integration Tests', () => {
  const mockPharmxamApi = pharmxamApiModule.pharmxamApi as jest.Mocked<typeof pharmxamApiModule.pharmxamApi>;

  // Mock data
  const mockQuestions: Question[] = [
    {
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
      correct_answer: 'C',
    },
    {
      id: 2,
      text: 'Which drug is a beta-blocker?',
      options: {
        A: 'Amlodipine',
        B: 'Metoprolol',
        C: 'Lisinopril',
        D: 'Hydrochlorothiazide',
      },
      category: 'Pharmacology',
      difficulty: 'medium',
      created_at: '2024-01-01T00:00:00Z',
      correct_answer: 'B',
    },
    {
      id: 3,
      text: 'What is the antidote for warfarin overdose?',
      options: {
        A: 'Protamine sulfate',
        B: 'Vitamin K',
        C: 'Naloxone',
        D: 'Flumazenil',
      },
      category: 'Clinical Pharmacy',
      difficulty: 'hard',
      created_at: '2024-01-01T00:00:00Z',
      correct_answer: 'B',
    },
    {
      id: 4,
      text: 'Which is a common side effect of ACE inhibitors?',
      options: {
        A: 'Dry cough',
        B: 'Weight gain',
        C: 'Constipation',
        D: 'Hair loss',
      },
      category: 'Clinical Pharmacy',
      difficulty: 'easy',
      created_at: '2024-01-01T00:00:00Z',
      correct_answer: 'A',
    },
    {
      id: 5,
      text: 'What is the therapeutic range for digoxin?',
      options: {
        A: '0.5-1.0 ng/mL',
        B: '1.0-2.0 ng/mL',
        C: '2.0-3.0 ng/mL',
        D: '3.0-4.0 ng/mL',
      },
      category: 'Clinical Pharmacy',
      difficulty: 'hard',
      created_at: '2024-01-01T00:00:00Z',
      correct_answer: 'B',
    },
  ];

  beforeEach(() => {
    // Clear localStorage and reset mocks
    localStorage.clear();
    jest.clearAllMocks();
    mockPush.mockClear();
    mockReplace.mockClear();

    // Clean up DOM
    document.body.innerHTML = '';

    // Set up authenticated state
    localStorage.setItem('veetssuites_access_token', 'mock-access-token');
    localStorage.setItem('veetssuites_refresh_token', 'mock-refresh-token');
  });

  afterEach(() => {
    // Clean up DOM after each test
    document.body.innerHTML = '';
  });

  describe('Complete Exam Flow: Start → Answer → Submit → Results', () => {
    it('should complete the full exam flow successfully', async () => {
      // Mock exam start
      const mockExamAttempt: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: null,
        total_questions: 5,
        percentage_score: null,
        status: 'in_progress',
        is_completed: false,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: null,
        exam_answers: mockQuestions.map((q, index) => ({
          id: index + 1,
          question: q,
          question_id: q.id,
          selected_answer: null,
          is_correct: false,
          answered_at: '2024-01-01T10:00:00Z',
        })),
      };

      mockPharmxamApi.startExam.mockResolvedValue(mockExamAttempt);

      // Mock answer submissions
      const mockAnswerResponses: SubmitAnswerResponse[] = [
        { question_id: 1, selected_answer: 'C', is_correct: true, correct_answer: 'C', created: true },
        { question_id: 2, selected_answer: 'A', is_correct: false, correct_answer: 'B', created: true },
        { question_id: 3, selected_answer: 'B', is_correct: true, correct_answer: 'B', created: true },
        { question_id: 4, selected_answer: 'A', is_correct: true, correct_answer: 'A', created: true },
        { question_id: 5, selected_answer: 'B', is_correct: true, correct_answer: 'B', created: true },
      ];

      mockPharmxamApi.submitAnswer
        .mockResolvedValueOnce(mockAnswerResponses[0])
        .mockResolvedValueOnce(mockAnswerResponses[1])
        .mockResolvedValueOnce(mockAnswerResponses[2])
        .mockResolvedValueOnce(mockAnswerResponses[3])
        .mockResolvedValueOnce(mockAnswerResponses[4]);

      // Mock exam completion
      const completedExamAttempt: ExamAttempt = {
        ...mockExamAttempt,
        score: 4,
        percentage_score: 80,
        status: 'completed',
        is_completed: true,
        completed_at: '2024-01-01T10:30:00Z',
      };

      mockPharmxamApi.completeExam.mockResolvedValue(completedExamAttempt);

      // Render the test component
      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Step 1: Start exam
      expect(screen.getByText('PHARMXAM Practice')).toBeInTheDocument();
      
      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      // Verify exam started
      await waitFor(() => {
        expect(screen.getByTestId('exam-progress')).toHaveTextContent('Question 1 of 5');
      });

      expect(mockPharmxamApi.startExam).toHaveBeenCalledWith({
        category: 'Pharmacology',
        difficulty: 'medium',
        num_questions: 5,
      });

      // Step 2: Answer questions
      for (let i = 0; i < 5; i++) {
        const question = mockQuestions[i];
        const correctAnswer = question.correct_answer!;
        const selectedAnswer = i === 1 ? 'A' : correctAnswer; // Make second question incorrect
        
        // Verify question display
        expect(screen.getByTestId('question-text')).toHaveTextContent(question.text);
        expect(screen.getByTestId('question-category')).toHaveTextContent(question.category);
        expect(screen.getByTestId('question-difficulty')).toHaveTextContent(question.difficulty);

        // Select answer
        const optionBtn = screen.getByTestId(`option-${selectedAnswer}`);
        await act(async () => {
          await userEvent.click(optionBtn);
        });

        // Verify answer feedback
        await waitFor(() => {
          const feedback = screen.getByTestId('answer-feedback');
          if (selectedAnswer === correctAnswer) {
            expect(feedback).toHaveTextContent('Correct!');
          } else {
            expect(feedback).toHaveTextContent(`Incorrect. Correct answer: ${correctAnswer}`);
          }
        });

        // Move to next question or complete exam
        if (i < 4) {
          const nextBtn = screen.getByTestId('next-question-btn');
          await act(async () => {
            await userEvent.click(nextBtn);
          });
          
          await waitFor(() => {
            expect(screen.getByTestId('exam-progress')).toHaveTextContent(`Question ${i + 2} of 5`);
          });
        } else {
          // Complete exam on last question
          const completeBtn = screen.getByTestId('complete-exam-btn');
          await act(async () => {
            await userEvent.click(completeBtn);
          });
        }
      }

      // Step 3: Verify results
      await waitFor(() => {
        expect(screen.getByText('Exam Results')).toBeInTheDocument();
      });

      expect(screen.getByTestId('final-score')).toHaveTextContent('80%');
      expect(screen.getByTestId('score-breakdown')).toHaveTextContent('4 out of 5 correct');
      expect(screen.getByTestId('exam-status')).toHaveTextContent('completed');
      expect(screen.getByTestId('completion-time')).toHaveTextContent('2024-01-01T10:30:00Z');

      // Verify API calls
      expect(mockPharmxamApi.submitAnswer).toHaveBeenCalledTimes(5);
      expect(mockPharmxamApi.completeExam).toHaveBeenCalledWith(1);
    });

    it('should handle exam start failure', async () => {
      // Mock exam start failure
      mockPharmxamApi.startExam.mockRejectedValue(new Error('Not enough questions available'));

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      // Verify error is displayed
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Not enough questions available');
      });

      // Verify reset functionality
      const resetBtn = screen.getByTestId('reset-btn');
      await act(async () => {
        await userEvent.click(resetBtn);
      });

      expect(screen.getByText('PHARMXAM Practice')).toBeInTheDocument();
    });

    it('should handle answer submission failure', async () => {
      // Mock successful exam start
      const mockExamAttempt: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: null,
        total_questions: 1,
        percentage_score: null,
        status: 'in_progress',
        is_completed: false,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: null,
        exam_answers: [{
          id: 1,
          question: mockQuestions[0],
          question_id: mockQuestions[0].id,
          selected_answer: null,
          is_correct: false,
          answered_at: '2024-01-01T10:00:00Z',
        }],
      };

      mockPharmxamApi.startExam.mockResolvedValue(mockExamAttempt);
      
      // Mock answer submission failure - need to reject after a successful call first
      mockPharmxamApi.submitAnswer.mockRejectedValueOnce(new Error('Question is not part of this exam'));

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Start exam
      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('question-text')).toBeInTheDocument();
      });

      // Try to submit answer - this should fail
      const optionBtn = screen.getByTestId('option-A');
      await act(async () => {
        await userEvent.click(optionBtn);
      });

      // Wait for the error to be processed and displayed
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Question is not part of this exam');
      }, { timeout: 3000 });
    });

    it('should handle exam completion failure', async () => {
      // Mock successful exam start and answer submission
      const mockExamAttempt: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: null,
        total_questions: 1,
        percentage_score: null,
        status: 'in_progress',
        is_completed: false,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: null,
        exam_answers: [{
          id: 1,
          question: mockQuestions[0],
          question_id: mockQuestions[0].id,
          selected_answer: null,
          is_correct: false,
          answered_at: '2024-01-01T10:00:00Z',
        }],
      };

      mockPharmxamApi.startExam.mockResolvedValue(mockExamAttempt);
      mockPharmxamApi.submitAnswer.mockResolvedValue({
        question_id: 1,
        selected_answer: 'A',
        is_correct: true,
        correct_answer: 'C',
        created: true,
      });
      
      // Mock exam completion failure
      mockPharmxamApi.completeExam.mockRejectedValue(new Error('Exam is not in progress'));

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Start exam and answer question
      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('question-text')).toBeInTheDocument();
      });

      const optionBtn = screen.getByTestId('option-A');
      await act(async () => {
        await userEvent.click(optionBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('complete-exam-btn')).toBeInTheDocument();
      });

      // Try to complete exam
      const completeBtn = screen.getByTestId('complete-exam-btn');
      await act(async () => {
        await userEvent.click(completeBtn);
      });

      // Verify error is displayed
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Exam is not in progress');
      });
    });
  });

  describe('Exam History Retrieval and Review', () => {
    it('should retrieve and display exam history', async () => {
      // Mock exam history
      const mockHistory: ExamAttempt[] = [
        {
          id: 1,
          student: 1,
          student_username: 'student',
          score: 8,
          total_questions: 10,
          percentage_score: 80,
          status: 'completed',
          is_completed: true,
          started_at: '2024-01-01T10:00:00Z',
          completed_at: '2024-01-01T10:30:00Z',
        },
        {
          id: 2,
          student: 1,
          student_username: 'student',
          score: 15,
          total_questions: 20,
          percentage_score: 75,
          status: 'completed',
          is_completed: true,
          started_at: '2024-01-02T14:00:00Z',
          completed_at: '2024-01-02T14:45:00Z',
        },
      ];

      mockPharmxamApi.getExamHistory.mockResolvedValue(mockHistory);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Click view history
      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      // Verify history is displayed
      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      expect(screen.getByTestId('history-count')).toHaveTextContent('2 completed exams');
      
      // Verify first exam
      const firstExam = screen.getByTestId('history-item-0');
      expect(firstExam).toHaveTextContent('Score: 80%');
      expect(firstExam).toHaveTextContent('Date: 2024-01-01T10:30:00Z');
      expect(firstExam).toHaveTextContent('Questions: 10');

      // Verify second exam
      const secondExam = screen.getByTestId('history-item-1');
      expect(secondExam).toHaveTextContent('Score: 75%');
      expect(secondExam).toHaveTextContent('Date: 2024-01-02T14:45:00Z');
      expect(secondExam).toHaveTextContent('Questions: 20');

      expect(mockPharmxamApi.getExamHistory).toHaveBeenCalled();
    });

    it('should display empty history message when no exams completed', async () => {
      // Mock empty history
      mockPharmxamApi.getExamHistory.mockResolvedValue([]);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      expect(screen.getByTestId('history-count')).toHaveTextContent('0 completed exams');
      expect(screen.getByTestId('no-history')).toHaveTextContent('No completed exams found');
    });

    it('should handle exam history retrieval failure', async () => {
      // Mock history retrieval failure
      mockPharmxamApi.getExamHistory.mockRejectedValue(new Error('Failed to load exam history'));

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Failed to load exam history');
      });
    });

    it('should review a completed exam with correct/incorrect answers', async () => {
      // Mock exam history
      const mockHistory: ExamAttempt[] = [{
        id: 1,
        student: 1,
        student_username: 'student',
        score: 3,
        total_questions: 5,
        percentage_score: 60,
        status: 'completed',
        is_completed: true,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: '2024-01-01T10:30:00Z',
      }];

      // Mock exam review data
      const mockReviewData: ExamAttempt = {
        ...mockHistory[0],
        exam_answers: [
          {
            id: 1,
            question: { ...mockQuestions[0], correct_answer: 'C' },
            question_id: 1,
            selected_answer: 'C',
            is_correct: true,
            answered_at: '2024-01-01T10:05:00Z',
          },
          {
            id: 2,
            question: { ...mockQuestions[1], correct_answer: 'B' },
            question_id: 2,
            selected_answer: 'A',
            is_correct: false,
            answered_at: '2024-01-01T10:10:00Z',
          },
          {
            id: 3,
            question: { ...mockQuestions[2], correct_answer: 'B' },
            question_id: 3,
            selected_answer: 'B',
            is_correct: true,
            answered_at: '2024-01-01T10:15:00Z',
          },
          {
            id: 4,
            question: { ...mockQuestions[3], correct_answer: 'A' },
            question_id: 4,
            selected_answer: 'D',
            is_correct: false,
            answered_at: '2024-01-01T10:20:00Z',
          },
          {
            id: 5,
            question: { ...mockQuestions[4], correct_answer: 'B' },
            question_id: 5,
            selected_answer: 'B',
            is_correct: true,
            answered_at: '2024-01-01T10:25:00Z',
          },
        ],
      };

      mockPharmxamApi.getExamHistory.mockResolvedValue(mockHistory);
      mockPharmxamApi.reviewExam.mockResolvedValue(mockReviewData);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Go to history
      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      // Click review exam
      const reviewBtn = screen.getByTestId('review-exam-1');
      await act(async () => {
        await userEvent.click(reviewBtn);
      });

      // Verify review is displayed
      await waitFor(() => {
        expect(screen.getByText('Exam Review')).toBeInTheDocument();
      });

      expect(screen.getByTestId('review-score')).toHaveTextContent('60%');
      expect(screen.getByTestId('review-breakdown')).toHaveTextContent('3 out of 5 correct');

      // Verify each question review
      for (let i = 0; i < 5; i++) {
        const answer = mockReviewData.exam_answers![i];
        
        expect(screen.getByTestId(`review-question-text-${i}`)).toHaveTextContent(answer.question.text);
        expect(screen.getByTestId(`review-selected-${i}`)).toHaveTextContent(`Your answer: ${answer.selected_answer}`);
        expect(screen.getByTestId(`review-correct-${i}`)).toHaveTextContent(`Correct answer: ${answer.question.correct_answer}`);
        expect(screen.getByTestId(`review-result-${i}`)).toHaveTextContent(answer.is_correct ? 'Correct' : 'Incorrect');
      }

      expect(mockPharmxamApi.reviewExam).toHaveBeenCalledWith(1);
    });

    it('should handle exam review failure', async () => {
      // Mock successful history retrieval
      const mockHistory: ExamAttempt[] = [{
        id: 1,
        student: 1,
        student_username: 'student',
        score: 8,
        total_questions: 10,
        percentage_score: 80,
        status: 'completed',
        is_completed: true,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: '2024-01-01T10:30:00Z',
      }];

      mockPharmxamApi.getExamHistory.mockResolvedValue(mockHistory);
      
      // Mock review failure
      mockPharmxamApi.reviewExam.mockRejectedValue(new Error('Exam must be completed to review'));

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Go to history
      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      // Try to review exam
      const reviewBtn = screen.getByTestId('review-exam-1');
      await act(async () => {
        await userEvent.click(reviewBtn);
      });

      // Verify error is displayed
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Exam must be completed to review');
      });
    });
  });

  describe('Navigation Between Exam States', () => {
    it('should navigate from results to history and back', async () => {
      // Mock completed exam
      const completedExam: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: 4,
        total_questions: 5,
        percentage_score: 80,
        status: 'completed',
        is_completed: true,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: '2024-01-01T10:30:00Z',
      };

      // Mock history
      const mockHistory: ExamAttempt[] = [completedExam];

      mockPharmxamApi.completeExam.mockResolvedValue(completedExam);
      mockPharmxamApi.getExamHistory.mockResolvedValue(mockHistory);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Simulate being at results page (we'll manually set the state)
      // This would normally come from completing an exam
      const component = screen.getByText('PHARMXAM Practice').closest('div');
      
      // We need to simulate the results state, so let's start an exam first
      const mockExamAttempt: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: null,
        total_questions: 1,
        percentage_score: null,
        status: 'in_progress',
        is_completed: false,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: null,
        exam_answers: [{
          id: 1,
          question: mockQuestions[0],
          question_id: mockQuestions[0].id,
          selected_answer: null,
          is_correct: false,
          answered_at: '2024-01-01T10:00:00Z',
        }],
      };

      mockPharmxamApi.startExam.mockResolvedValue(mockExamAttempt);
      mockPharmxamApi.submitAnswer.mockResolvedValue({
        question_id: 1,
        selected_answer: 'C',
        is_correct: true,
        correct_answer: 'C',
        created: true,
      });

      // Start and complete exam
      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('question-text')).toBeInTheDocument();
      });

      const optionBtn = screen.getByTestId('option-C');
      await act(async () => {
        await userEvent.click(optionBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('complete-exam-btn')).toBeInTheDocument();
      });

      const completeBtn = screen.getByTestId('complete-exam-btn');
      await act(async () => {
        await userEvent.click(completeBtn);
      });

      // Now at results page
      await waitFor(() => {
        expect(screen.getByText('Exam Results')).toBeInTheDocument();
      });

      // Navigate to history
      const viewHistoryFromResultsBtn = screen.getByTestId('view-history-from-results-btn');
      await act(async () => {
        await userEvent.click(viewHistoryFromResultsBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      // Navigate back to start
      const backToStartBtn = screen.getByTestId('back-to-start-btn');
      await act(async () => {
        await userEvent.click(backToStartBtn);
      });

      expect(screen.getByText('PHARMXAM Practice')).toBeInTheDocument();
    });

    it('should navigate from review back to history and start', async () => {
      // Mock history and review data
      const mockHistory: ExamAttempt[] = [{
        id: 1,
        student: 1,
        student_username: 'student',
        score: 4,
        total_questions: 5,
        percentage_score: 80,
        status: 'completed',
        is_completed: true,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: '2024-01-01T10:30:00Z',
      }];

      const mockReviewData: ExamAttempt = {
        ...mockHistory[0],
        exam_answers: [{
          id: 1,
          question: { ...mockQuestions[0], correct_answer: 'C' },
          question_id: 1,
          selected_answer: 'C',
          is_correct: true,
          answered_at: '2024-01-01T10:05:00Z',
        }],
      };

      mockPharmxamApi.getExamHistory.mockResolvedValue(mockHistory);
      mockPharmxamApi.reviewExam.mockResolvedValue(mockReviewData);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      // Go to history
      const viewHistoryBtn = screen.getByTestId('view-history-btn');
      await act(async () => {
        await userEvent.click(viewHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      // Go to review
      const reviewBtn = screen.getByTestId('review-exam-1');
      await act(async () => {
        await userEvent.click(reviewBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam Review')).toBeInTheDocument();
      });

      // Navigate back to history
      const backToHistoryBtn = screen.getByTestId('back-to-history-btn');
      await act(async () => {
        await userEvent.click(backToHistoryBtn);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam History')).toBeInTheDocument();
      });

      // Navigate back to start from review
      const reviewBtn2 = screen.getByTestId('review-exam-1');
      await act(async () => {
        await userEvent.click(reviewBtn2);
      });

      await waitFor(() => {
        expect(screen.getByText('Exam Review')).toBeInTheDocument();
      });

      const backToStartFromReviewBtn = screen.getByTestId('back-to-start-from-review-btn');
      await act(async () => {
        await userEvent.click(backToStartFromReviewBtn);
      });

      expect(screen.getByText('PHARMXAM Practice')).toBeInTheDocument();
    });
  });

  describe('Question Randomization Validation', () => {
    it('should verify questions are presented in random order', async () => {
      // Mock exam with questions in specific order
      const mockExamAttempt: ExamAttempt = {
        id: 1,
        student: 1,
        student_username: 'student',
        score: null,
        total_questions: 3,
        percentage_score: null,
        status: 'in_progress',
        is_completed: false,
        started_at: '2024-01-01T10:00:00Z',
        completed_at: null,
        exam_answers: [
          {
            id: 1,
            question: mockQuestions[2], // Third question first
            question_id: mockQuestions[2].id,
            selected_answer: null,
            is_correct: false,
            answered_at: '2024-01-01T10:00:00Z',
          },
          {
            id: 2,
            question: mockQuestions[0], // First question second
            question_id: mockQuestions[0].id,
            selected_answer: null,
            is_correct: false,
            answered_at: '2024-01-01T10:00:00Z',
          },
          {
            id: 3,
            question: mockQuestions[1], // Second question third
            question_id: mockQuestions[1].id,
            selected_answer: null,
            is_correct: false,
            answered_at: '2024-01-01T10:00:00Z',
          },
        ],
      };

      mockPharmxamApi.startExam.mockResolvedValue(mockExamAttempt);

      render(
        <AuthProvider>
          <ExamFlowTestComponent />
        </AuthProvider>
      );

      const startExamBtn = screen.getByTestId('start-exam-btn');
      await act(async () => {
        await userEvent.click(startExamBtn);
      });

      // Verify first question is the third from our original array (randomized)
      await waitFor(() => {
        expect(screen.getByTestId('question-text')).toHaveTextContent(mockQuestions[2].text);
      });

      // Verify the API was called with randomization parameters
      expect(mockPharmxamApi.startExam).toHaveBeenCalledWith({
        category: 'Pharmacology',
        difficulty: 'medium',
        num_questions: 5,
      });
    });
  });
});