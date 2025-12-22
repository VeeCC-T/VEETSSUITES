import axios from 'axios';
import { tokenStorage } from '@/lib/auth/storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Question {
  id: number;
  text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  created_at: string;
  correct_answer?: string; // Only available in review mode
}

export interface ExamAnswer {
  id: number;
  question: Question;
  question_id: number;
  selected_answer: string | null;
  is_correct: boolean;
  answered_at: string;
}

export interface ExamAttempt {
  id: number;
  student: number;
  student_username: string;
  score: number | null;
  total_questions: number;
  percentage_score: number | null;
  status: 'in_progress' | 'completed' | 'abandoned';
  is_completed: boolean;
  started_at: string;
  completed_at: string | null;
  exam_answers?: ExamAnswer[];
}

export interface StartExamData {
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  num_questions?: number;
}

export interface SubmitAnswerData {
  question_id: number;
  selected_answer: 'A' | 'B' | 'C' | 'D';
}

export interface SubmitAnswerResponse {
  question_id: number;
  selected_answer: string;
  is_correct: boolean;
  correct_answer: string;
  created: boolean;
}

/**
 * PHARMXAM API functions
 * Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
 */
export const pharmxamApi = {
  async getQuestions(params?: { category?: string; difficulty?: string }): Promise<Question[]> {
    const response = await api.get('/api/exams/questions/', { params });
    return response.data.results || response.data;
  },

  async startExam(data: StartExamData): Promise<ExamAttempt> {
    const response = await api.post('/api/exams/attempts/start_exam/', data);
    return response.data;
  },

  async getExamAttempt(attemptId: number): Promise<ExamAttempt> {
    const response = await api.get(`/api/exams/attempts/${attemptId}/`);
    return response.data;
  },

  async submitAnswer(attemptId: number, data: SubmitAnswerData): Promise<SubmitAnswerResponse> {
    const response = await api.post(`/api/exams/attempts/${attemptId}/submit_answer/`, data);
    return response.data;
  },

  async completeExam(attemptId: number): Promise<ExamAttempt> {
    const response = await api.post(`/api/exams/attempts/${attemptId}/complete_exam/`);
    return response.data;
  },

  async reviewExam(attemptId: number): Promise<ExamAttempt> {
    const response = await api.get(`/api/exams/attempts/${attemptId}/review/`);
    return response.data;
  },

  async getExamHistory(): Promise<ExamAttempt[]> {
    const response = await api.get('/api/exams/attempts/history/');
    return response.data;
  },

  async getExamAttempts(): Promise<ExamAttempt[]> {
    const response = await api.get('/api/exams/attempts/');
    return response.data.results || response.data;
  },
};