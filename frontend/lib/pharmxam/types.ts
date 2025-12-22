export interface ExamConfig {
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  numQuestions: number;
}

export interface ExamSession {
  attemptId: number;
  currentQuestionIndex: number;
  questions: Array<{
    id: number;
    text: string;
    options: Record<string, string>;
    selectedAnswer?: string;
    isAnswered: boolean;
  }>;
  timeStarted: Date;
  timeRemaining?: number; // in seconds
}

export interface ExamResults {
  score: number;
  totalQuestions: number;
  percentage: number;
  categoryBreakdown: Record<string, {
    correct: number;
    total: number;
    percentage: number;
  }>;
  difficultyBreakdown: Record<string, {
    correct: number;
    total: number;
    percentage: number;
  }>;
}