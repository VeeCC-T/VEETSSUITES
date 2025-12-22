"""
Property-based tests for HEALTHEE consultation system.
Tests Properties 37-41 from the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from .models import Consultation, ConsultationMessage
from .ai_service import ai_service

User = get_user_model()


class ConsultationPropertyTests(TestCase):
    """Property-based tests for consultation system"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    # Feature: veetssuites-platform, Property 37: Consultation initiation presents options
    @given(
        consultation_type=st.sampled_from(['ai', 'human'])
    )
    @settings(max_examples=100)
    def test_consultation_initiation_presents_options(self, consultation_type):
        """
        For any consultation type (ai or human), when initiated, 
        the system should create a consultation with the specified type.
        """
        response = self.client.post('/api/healthee/consultations/', {
            'consultation_type': consultation_type
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['consultation_type'] == consultation_type
        
        # Verify consultation was created in database
        consultation = Consultation.objects.get(id=response.data['id'])
        assert consultation.consultation_type == consultation_type
        assert consultation.user == self.user
        
        # AI consultations should be active, human should be waiting
        if consultation_type == 'ai':
            assert consultation.status == 'active'
        else:
            assert consultation.status == 'waiting'

    # Feature: veetssuites-platform, Property 38: AI messages forwarded and returned
    @given(
        message_text=st.text(min_size=1, max_size=500).filter(lambda x: x.strip())
    )
    @settings(max_examples=100)
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_ai_messages_forwarded_and_returned(self, mock_ai_response, message_text):
        """
        For any message sent to AI chatbot, the system should forward it to AI API 
        and return the AI's response to the user.
        """
        # Create AI consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='ai'
        )
        
        # Mock AI response
        ai_response_text = f"AI response to: {message_text[:50]}..."
        mock_ai_response.return_value = {
            'response': ai_response_text,
            'success': True,
            'cached': False,
            'error': None
        }
        
        # Send message
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/send-message/',
            {'message': message_text}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify user message was created
        assert response.data['user_message']['message'] == message_text
        assert response.data['user_message']['is_ai_response'] is False
        
        # Verify AI response was created and returned
        assert response.data['ai_response'] is not None
        assert response.data['ai_response']['is_ai_response'] is True
        assert response.data['ai_response']['message'] == ai_response_text
        
        # Verify AI service was called with the message
        mock_ai_response.assert_called_once()
        call_args = mock_ai_response.call_args
        assert call_args[1]['message'] == message_text
        
        # Verify both messages exist in database
        messages = ConsultationMessage.objects.filter(consultation=consultation)
        assert messages.count() == 2
        
        user_msg = messages.filter(is_ai_response=False).first()
        ai_msg = messages.filter(is_ai_response=True).first()
        
        assert user_msg.message == message_text
        assert ai_msg.message == ai_response_text

    # Feature: veetssuites-platform, Property 39: Human consultation creates requests
    @given(
        message_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    @settings(max_examples=100)
    def test_human_consultation_creates_requests(self, message_text):
        """
        For any human pharmacist consultation request, the system should create 
        a consultation record with status "waiting".
        """
        # Create human consultation
        response = self.client.post('/api/healthee/consultations/', {
            'consultation_type': 'human'
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        consultation_id = response.data['id']
        
        # Verify consultation is in waiting status
        consultation = Consultation.objects.get(id=consultation_id)
        assert consultation.status == 'waiting'
        assert consultation.consultation_type == 'human'
        assert consultation.pharmacist is None
        
        # Send a message to the human consultation
        message_response = self.client.post(
            f'/api/healthee/consultations/{consultation_id}/send-message/',
            {'message': message_text}
        )
        
        assert message_response.status_code == status.HTTP_201_CREATED
        
        # Verify no AI response is generated for human consultations
        assert message_response.data['ai_response'] is None
        
        # Verify message was stored
        assert message_response.data['user_message']['message'] == message_text
        
        # Consultation should still be waiting for pharmacist
        consultation.refresh_from_db()
        assert consultation.status == 'waiting'

    # Feature: veetssuites-platform, Property 41: Consultation history is stored
    @given(
        messages=st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=1,
            max_size=10
        ),
        consultation_type=st.sampled_from(['ai', 'human'])
    )
    @settings(max_examples=100)
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_consultation_history_is_stored(self, mock_ai_response, messages, consultation_type):
        """
        For any completed consultation, all messages should be stored 
        and retrievable by the user for future reference.
        """
        # Create consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type=consultation_type
        )
        
        # Mock AI responses if needed
        if consultation_type == 'ai':
            mock_ai_response.return_value = {
                'response': 'AI response',
                'success': True,
                'cached': False,
                'error': None
            }
        
        # Send all messages
        for message_text in messages:
            response = self.client.post(
                f'/api/healthee/consultations/{consultation.id}/send-message/',
                {'message': message_text}
            )
            assert response.status_code == status.HTTP_201_CREATED
        
        # Complete the consultation
        complete_response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/complete/'
        )
        assert complete_response.status_code == status.HTTP_200_OK
        
        # Retrieve consultation history
        history_response = self.client.get(
            f'/api/healthee/consultations/{consultation.id}/messages/'
        )
        assert history_response.status_code == status.HTTP_200_OK
        
        # Verify all user messages are stored and retrievable
        stored_messages = history_response.data
        user_messages = [msg for msg in stored_messages if not msg['is_ai_response']]
        
        assert len(user_messages) >= len(messages)
        
        # Verify each original message is stored
        stored_message_texts = [msg['message'] for msg in user_messages if msg['message'] in messages]
        assert len(stored_message_texts) == len(messages)
        
        # Verify consultation is marked as completed
        consultation.refresh_from_db()
        assert consultation.status == 'completed'
        assert consultation.completed_at is not None
        
        # Verify messages are still accessible after completion
        final_check = self.client.get(
            f'/api/healthee/consultations/{consultation.id}/messages/'
        )
        assert final_check.status_code == status.HTTP_200_OK
        assert len(final_check.data) == len(stored_messages)

    # Feature: veetssuites-platform, Property 38: AI error handling with fallbacks
    @given(
        message_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        error_type=st.sampled_from(['timeout', 'api_error', 'rate_limit', 'connection_error'])
    )
    @settings(max_examples=100)
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_ai_error_handling_with_fallbacks(self, mock_ai_response, message_text, error_type):
        """
        For any AI service error, the system should provide a fallback response 
        and not fail the user's request.
        """
        # Create AI consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='ai'
        )
        
        # Mock different types of AI service errors
        if error_type == 'timeout':
            mock_ai_response.return_value = {
                'response': 'AI service timeout fallback message',
                'success': False,
                'cached': False,
                'error': 'Request timeout'
            }
        elif error_type == 'api_error':
            mock_ai_response.side_effect = Exception("API Error")
        elif error_type == 'rate_limit':
            mock_ai_response.return_value = {
                'response': 'AI service busy fallback message',
                'success': False,
                'cached': False,
                'error': 'Rate limit exceeded'
            }
        else:  # connection_error
            mock_ai_response.side_effect = ConnectionError("Connection failed")
        
        # Send message
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/send-message/',
            {'message': message_text}
        )
        
        # Request should still succeed despite AI error
        assert response.status_code == status.HTTP_201_CREATED
        
        # User message should be stored
        assert response.data['user_message']['message'] == message_text
        assert response.data['user_message']['is_ai_response'] is False
        
        # AI response should be provided (fallback)
        assert response.data['ai_response'] is not None
        assert response.data['ai_response']['is_ai_response'] is True
        
        # Fallback message should indicate technical difficulties
        ai_message = response.data['ai_response']['message']
        assert 'technical difficulties' in ai_message.lower() or 'unavailable' in ai_message.lower()
        
        # Error metadata should indicate failure
        if 'ai_metadata' in response.data:
            assert response.data['ai_metadata']['success'] is False

    # Feature: veetssuites-platform, Property 37: Request pharmacist transition
    @given(
        initial_messages=st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=100)
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_request_pharmacist_transition(self, mock_ai_response, initial_messages):
        """
        For any AI consultation, users should be able to request human pharmacist 
        assistance, transitioning the consultation type and status.
        """
        # Create AI consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='ai'
        )
        
        # Mock AI responses
        mock_ai_response.return_value = {
            'response': 'AI response',
            'success': True,
            'cached': False,
            'error': None
        }
        
        # Send some initial messages
        for message in initial_messages:
            self.client.post(
                f'/api/healthee/consultations/{consultation.id}/send-message/',
                {'message': message}
            )
        
        # Request pharmacist
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/request-pharmacist/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify consultation type and status changed
        consultation.refresh_from_db()
        assert consultation.consultation_type == 'human'
        assert consultation.status == 'waiting'
        assert consultation.pharmacist is None
        
        # Verify system message was added
        messages = ConsultationMessage.objects.filter(consultation=consultation)
        system_messages = [msg for msg in messages if 'pharmacist assistance' in msg.message]
        assert len(system_messages) >= 1
        
        # Verify response contains updated consultation data
        assert response.data['consultation_type'] == 'human'
        assert response.data['status'] == 'waiting'

    # Feature: veetssuites-platform, Property 39: Pharmacist queue functionality
    @given(
        num_consultations=st.integers(min_value=1, max_value=5),
        consultation_messages=st.lists(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=50)
    def test_pharmacist_queue_functionality(self, num_consultations, consultation_messages):
        """
        For any number of human consultations waiting, pharmacists should be able 
        to see them in a queue and accept them.
        """
        # Create pharmacist user
        pharmacist = User.objects.create_user(
            email='pharmacist@example.com',
            password='testpass123',
            role='pharmacist'
        )
        pharmacist_client = APIClient()
        pharmacist_client.force_authenticate(user=pharmacist)
        
        # Create multiple users and consultations
        consultations = []
        for i in range(num_consultations):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123'
            )
            consultation = Consultation.objects.create(
                user=user,
                consultation_type='human',
                status='waiting'
            )
            
            # Add some messages to each consultation
            for msg_text in consultation_messages:
                ConsultationMessage.objects.create(
                    consultation=consultation,
                    sender=user,
                    message=f"{msg_text} from user {i}",
                    is_ai_response=False
                )
            
            consultations.append(consultation)
        
        # Check pharmacist queue
        queue_response = pharmacist_client.get('/api/healthee/pharmacist/queue/')
        assert queue_response.status_code == status.HTTP_200_OK
        
        # Verify all waiting consultations are in queue
        queue_data = queue_response.data
        assert len(queue_data) == num_consultations
        
        # Verify queue contains expected data
        for consultation_data in queue_data:
            assert consultation_data['id'] in [c.id for c in consultations]
            assert 'user_email' in consultation_data
            assert 'waiting_time' in consultation_data
            assert 'latest_message' in consultation_data
        
        # Accept one consultation
        if consultations:
            consultation_to_accept = consultations[0]
            accept_response = pharmacist_client.post(
                f'/api/healthee/pharmacist/accept/{consultation_to_accept.id}/'
            )
            assert accept_response.status_code == status.HTTP_200_OK
            
            # Verify consultation was assigned and status changed
            consultation_to_accept.refresh_from_db()
            assert consultation_to_accept.pharmacist == pharmacist
            assert consultation_to_accept.status == 'active'
            
            # Verify queue is updated (one less consultation)
            updated_queue = pharmacist_client.get('/api/healthee/pharmacist/queue/')
            assert len(updated_queue.data) == num_consultations - 1