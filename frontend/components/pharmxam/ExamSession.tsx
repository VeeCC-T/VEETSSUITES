'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Modal } from '@/components/ui';
import { QuestionCard } from './QuestionCard';
import { ExamAttempt, Question, pharmxamApi, SubmitAnswerData } from '@/lib/pharmxam/api';

interface ExamSessionProps {
  examAttempt: ExamAttempt;
  onExamComplete: (completedAttempt: ExamAttempt) => void;
  onExamExit: () => void;
}

interface QuestionState {
  question: Question;
  selectedAnswer?: string;
  isAnswered: boolean;
  feedback?: {
    isCorrect: boolean;
    correctAnswer: string;
  };
}

/**
 * ExamSession component for taking exams with timer and progress
 * Validates: Requirements 4.2, 4.3
 */
export const ExamSession: React.FC<ExamSessionProps> = ({
  examAttempt,
  onExamComplete,
  onExamExit,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState<QuestionState[]>([]);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  // Initialize questions from exam attempt
  useEffect(() => {
    if (examAttempt.exam_answers) {
      const questionStates: QuestionState[] = examAttempt.exam_answers.map(answer => ({
        question: answer.question,
        selectedAnswer: answer.selected_answer || undefined,
        isAnswered: !!answer.selected_answer,
      }));
      setQuestions(questionStates);
    }
  }, [examAttempt]);

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = useCallback(async (answer: 'A' | 'B' | 'C' | 'D') => {
    if (isSubmitting || currentQuestionIndex >= questions.length) return;

    const currentQuestion = questions[currentQuestionIndex];
    setIsSubmitting(true);

    try {
      const submitData: SubmitAnswerData = {
        question_id: currentQuestion.question.id,
        selected_answer: answer,
      };

      const response = await pharmxamApi.submitAnswer(examAttempt.id, submitData);

      // Update question state with answer and feedback
      setQuestions(prev => {
        const updated = [...prev];
        updated[currentQuestionIndex] = {
          ...updated[currentQuestionIndex],
          selectedAnswer: answer,
          isAnswered: true,
          feedback: {
            isCorrect: response.is_correct,
            correctAnswer: response.correct_answer,
          },
        };
        return updated;
      });

    } catch (error) {
      console.error('Failed to submit answer:', error);
      // You might want to show an error toast here
    } finally {
      setIsSubmitting(false);
    }
  }, [currentQuestionIndex, questions, examAttempt.id, isSubmitting]);

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleCompleteExam = async () => {
    setIsCompleting(true);
    try {
      const completedAttempt = await pharmxamApi.completeExam(examAttempt.id);
      onExamComplete(completedAttempt);
    } catch (error) {
      console.error('Failed to complete exam:', error);
      setIsCompleting(false);
    }
  };

  const answeredCount = questions.filter(q => q.isAnswered).length;
  const progressPercentage = (answeredCount / questions.length) * 100;

  const currentQuestion = questions[currentQuestionIndex];

  if (!currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <div className="p-6 text-center">
            <p className="text-gray-600">Loading exam...</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Exam Header */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div>
                <span className="text-sm text-gray-500">Question</span>
                <p className="font-semibold">
                  {currentQuestionIndex + 1} of {questions.length}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Progress</span>
                <p className="font-semibold">
                  {answeredCount}/{questions.length} answered
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Time Elapsed</span>
                <p className="font-semibold">{formatTime(timeElapsed)}</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowExitModal(true)}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                Exit Exam
              </Button>
              <Button
                onClick={handleCompleteExam}
                disabled={isCompleting}
                className="bg-green-600 hover:bg-green-700"
              >
                {isCompleting ? 'Completing...' : 'Complete Exam'}
              </Button>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Question Navigation */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex flex-wrap gap-2">
            {questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-10 h-10 rounded-lg border-2 font-medium transition-all ${
                  index === currentQuestionIndex
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : questions[index].isAnswered
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Current Question */}
      <QuestionCard
        question={currentQuestion.question}
        selectedAnswer={currentQuestion.selectedAnswer}
        onAnswerSelect={handleAnswerSelect}
        showFeedback={!!currentQuestion.feedback}
        onNext={handleNext}
        onPrevious={handlePrevious}
        canGoNext={currentQuestionIndex < questions.length - 1}
        canGoPrevious={currentQuestionIndex > 0}
      />

      {/* Exit Confirmation Modal */}
      <Modal
        isOpen={showExitModal}
        onClose={() => setShowExitModal(false)}
        title="Exit Exam"
      >
        <div className="p-6">
          <p className="text-gray-600 mb-6">
            Are you sure you want to exit the exam? Your progress will be saved, but you won't be able to resume this attempt.
          </p>
          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowExitModal(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={onExamExit}
              className="bg-red-600 hover:bg-red-700"
            >
              Exit Exam
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};