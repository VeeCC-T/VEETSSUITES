'use client';

import { useState, useEffect, useRef } from 'react';
import { Button, Card } from '@/components/ui';
import { Consultation, ConsultationMessage } from '@/lib/healthee/types';
import { healtheeApi } from '@/lib/healthee/api';
import { ChatMessage } from './ChatMessage';

interface ConsultationInterfaceProps {
  consultation: Consultation;
  onConsultationUpdate?: (consultation: Consultation) => void;
}

export function ConsultationInterface({ consultation, onConsultationUpdate }: ConsultationInterfaceProps) {
  const [messages, setMessages] = useState<ConsultationMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    loadMessages();
  }, [consultation.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Poll for new messages every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (consultation.status === 'active') {
        loadMessages();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [consultation.id, consultation.status]);

  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const messagesData = await healtheeApi.getMessages(consultation.id);
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    try {
      setIsSending(true);
      const message = await healtheeApi.sendMessage(consultation.id, {
        message: newMessage.trim()
      });
      
      setMessages(prev => [...prev, message]);
      setNewMessage('');
      
      // Reload messages after a short delay to get AI response
      if (consultation.consultation_type === 'ai') {
        setTimeout(() => {
          loadMessages();
        }, 1000);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleRequestPharmacist = async () => {
    try {
      await healtheeApi.requestPharmacist(consultation.id);
      // Reload consultation to get updated status
      const updatedConsultation = await healtheeApi.getConsultation(consultation.id);
      onConsultationUpdate?.(updatedConsultation);
    } catch (error) {
      console.error('Failed to request pharmacist:', error);
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      {/* Header */}
      <div className="bg-blue-50 p-4 border-b">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-900">
              {consultation.consultation_type === 'ai' ? 'AI Health Assistant' : 'Pharmacist Consultation'}
            </h3>
            <p className="text-sm text-gray-600">
              Status: <span className="capitalize">{consultation.status}</span>
              {consultation.pharmacist && (
                <span className="ml-2">
                  with {consultation.pharmacist.first_name} {consultation.pharmacist.last_name}
                </span>
              )}
            </p>
          </div>
          
          {consultation.consultation_type === 'ai' && consultation.status === 'active' && (
            <Button
              onClick={handleRequestPharmacist}
              variant="outline"
              size="sm"
            >
              Request Human Pharmacist
            </Button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading && messages.length === 0 ? (
          <div className="text-center text-gray-500">Loading messages...</div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Message Input */}
      {consultation.status === 'active' && (
        <form onSubmit={handleSendMessage} className="p-4 border-t bg-gray-50">
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSending}
            />
            <Button
              type="submit"
              disabled={!newMessage.trim() || isSending}
              loading={isSending}
            >
              Send
            </Button>
          </div>
        </form>
      )}

      {consultation.status === 'waiting' && (
        <div className="p-4 border-t bg-yellow-50">
          <p className="text-center text-yellow-800">
            Waiting for a pharmacist to join the consultation...
          </p>
        </div>
      )}

      {consultation.status === 'completed' && (
        <div className="p-4 border-t bg-green-50">
          <p className="text-center text-green-800">
            This consultation has been completed.
          </p>
        </div>
      )}
    </div>
  );
}