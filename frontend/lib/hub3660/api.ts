/**
 * API client for HUB3660 course management
 */

import axios from 'axios';
import { getAuthToken } from '@/lib/auth';
import type {
  Course,
  Enrollment,
  EnrollmentResponse,
  EnrollmentStatus,
  Session,
  Recording,
  CourseRecordings,
  CourseCreateData,
  SessionCreateData
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/hub3660`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const hub3660Api = {
  // Course management
  async getCourses(): Promise<Course[]> {
    const response = await apiClient.get('/courses/');
    return response.data;
  },

  async getCourse(courseId: number): Promise<Course> {
    const response = await apiClient.get(`/courses/${courseId}/`);
    return response.data;
  },

  async createCourse(courseData: CourseCreateData): Promise<Course> {
    const response = await apiClient.post('/courses/', courseData);
    return response.data;
  },

  async updateCourse(courseId: number, courseData: Partial<CourseCreateData>): Promise<Course> {
    const response = await apiClient.put(`/courses/${courseId}/edit/`, courseData);
    return response.data;
  },

  async getInstructorCourses(): Promise<Course[]> {
    const response = await apiClient.get('/instructor/courses/');
    return response.data;
  },

  // Enrollment management
  async enrollInCourse(courseId: number): Promise<EnrollmentResponse> {
    const response = await apiClient.post(`/courses/${courseId}/enroll/`);
    return response.data;
  },

  async getStudentEnrollments(): Promise<Enrollment[]> {
    const response = await apiClient.get('/student/enrollments/');
    return response.data;
  },

  async checkEnrollmentStatus(courseId: number): Promise<EnrollmentStatus> {
    const response = await apiClient.get(`/courses/${courseId}/enrollment-status/`);
    return response.data;
  },

  // Session management
  async getCourseSessions(courseId: number): Promise<Session[]> {
    const response = await apiClient.get(`/courses/${courseId}/sessions/`);
    return response.data;
  },

  async createSession(sessionData: SessionCreateData): Promise<Session> {
    const response = await apiClient.post('/sessions/', sessionData);
    return response.data;
  },

  async registerForSession(sessionId: number): Promise<{ message: string; session_title: string; scheduled_at: string }> {
    const response = await apiClient.post(`/sessions/${sessionId}/register/`);
    return response.data;
  },

  // Recording access
  async getSessionRecording(sessionId: number): Promise<{
    recording_url: string;
    session_title: string;
    course_title: string;
    expires_in_hours: number | null;
    storage_type: 's3' | 'zoom';
  }> {
    const response = await apiClient.get(`/sessions/${sessionId}/recording/`);
    return response.data;
  },

  async getCourseRecordings(courseId: number): Promise<CourseRecordings> {
    const response = await apiClient.get(`/courses/${courseId}/recordings/`);
    return response.data;
  },
};

export default hub3660Api;