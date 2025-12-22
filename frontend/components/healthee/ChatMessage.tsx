'use client';

import { ConsultationMessage } from '@/lib/healthee/types';

interface ChatMessageProps {
  message: ConsultationMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAI = message.is_ai_response;
  const isUser = !isAI && message.sender;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : isAI 
            ? 'bg-gray-100 text-gray-900 border'
            : 'bg-green-100 text-green-900 border border-green-200'
      }`}>
        {/* Sender info */}
        {!isUser && (
          <div className="text-xs font-semibold mb-1 text-gray-600">
            {isAI ? 'AI Assistant' : `${message.sender.first_name} ${message.sender.last_name}`}
          </div>
        )}
        
        {/* Message content */}
        <div className="text-sm whitespace-pre-wrap">
          {message.message}
        </div>
        
        {/* Timestamp */}
        <div className={`text-xs mt-1 ${
          isUser ? 'text-blue-100' : 'text-gray-500'
        }`}>
          {new Date(message.created_at).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
}