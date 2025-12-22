/**
 * TypeScript types for HUB3660 course management
 */

export interface Instructor {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  instructor_name?: string; // For list view
  instructor?: Instructor; // For detail view
  price: string;
  currency: string;
  enrollment_count: number;
  is_enrolled: boolean;
  enrollment_status?: 'pending' | 'completed' | 'failed' | null;
  is_published?: boolean; // For instructor dashboard
  sessions?: Session[];
  created_at: string;
  updated_at: string;
}

export interface Session {
  id: number;
  title: string;
  course_title: string;
  scheduled_at: string;
  zoom_join_url?: string;
  recording_url?: string;
  is_upcoming: boolean;
  has_recording: boolean;
  created_at: string;
}

export interface Enrollment {
  id: number;
  course: number;
  course_title: string;
  student_name: string;
  payment_status: 'pending' | 'completed' | 'failed';
  payment_id?: string;
  enrolled_at: string;
}

export interface EnrollmentResponse {
  message: string;
  enrollment_id: number;
  course_id?: number;
  course_title?: string;
  amount?: string;
  currency?: string;
  payment_required: boolean;
  payment_metadata?: {
    enrollment_id: number;
    course_id: number;
    course_title: string;
    student_id: number;
    student_email: string;
  };
}

export interface EnrollmentStatus {
  is_enrolled: boolean;
  enrollment_status: 'pending' | 'completed' | 'failed' | null;
  enrolled_at: string | null;
}

export interface Recording {
  session_id: number;
  session_title: string;
  scheduled_at: string;
  has_recording: boolean;
  recording_url?: string;
  expires_in_hours?: number | null;
  storage_type?: 's3' | 'zoom';
}

export interface CourseRecordings {
  course_id: number;
  course_title: string;
  recordings: Recording[];
  total_recordings: number;
}

export interface CourseCreateData {
  title: string;
  description: string;
  price: number;
  currency: string;
  is_published: boolean;
}

export interface SessionCreateData {
  course: number;
  title: string;
  scheduled_at: string;
}