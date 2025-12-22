export interface Consultation {
  id: number;
  consultation_type: 'ai' | 'human';
  status: 'active' | 'waiting' | 'completed';
  pharmacist?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
  completed_at?: string;
}

export interface ConsultationMessage {
  id: number;
  consultation: number;
  sender: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  message: string;
  is_ai_response: boolean;
  created_at: string;
}

export interface CreateConsultationRequest {
  consultation_type: 'ai' | 'human';
}

export interface SendMessageRequest {
  message: string;
}

export interface PharmacistQueueItem {
  id: number;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
  message_count: number;
}