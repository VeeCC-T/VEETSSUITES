"""
Tests for AI service integration in HEALTHEE consultation system.
"""

import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Consultation, ConsultationMessage
from .ai_service import AIService, AIServiceError, ai_service

User = get_user_model()


class AIServiceTest(TestCase):
    """Test AI service functionality"""
    
    def setUp(self):
        self.ai_service = AIService()
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        message = "What is aspirin used for?"
        context = "User: Hello\nAssistant: Hi there!"
        
        key1 = self.ai_service._generate_cache_key(message, context)
        key2 = self.ai_service._generate_cache_key(message, context)
        key3 = self.ai_service._generate_cache_key(message, "different context")
        
        # Same inputs should generate same key
        self.assertEqual(key1, key2)
        # Different inputs should generate different keys
        self.assertNotEqual(key1, key3)
        # Key should start with prefix
        self.assertTrue(key1.startswith("ai_response:"))
    
    def test_build_conversation_context(self):
        """Test conversation context building"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        consultation = Consultation.objects.create(
            user=user,
            consultation_type='ai'
        )
        
        # Create some messages
        msg1 = ConsultationMessage.objects.create(
            consultation=consultation,
            sender=user,
            message="Hello",
            is_ai_response=False
        )
        
        msg2 = ConsultationMessage.objects.create(
            consultation=consultation,
            sender=user,
            message="Hi there! How can I help you?",
            is_ai_response=True
        )
        
        msg3 = ConsultationMessage.objects.create(
            consultation=consultation,
            sender=user,
            message="What is aspirin?",
            is_ai_response=False
        )
        
        messages = [msg1, msg2, msg3]
        context = self.ai_service._build_conversation_context(messages)
        
        expected_context = "User: Hello\nAssistant: Hi there! How can I help you?\nUser: What is aspirin?"
        self.assertEqual(context, expected_context)
    
    def test_fallback_response_keyword_matching(self):
        """Test fallback response keyword matching"""
        # Test headache keyword
        response = self.ai_service._get_fallback_response("I have a headache")
        self.assertIn("acetaminophen", response.lower())
        self.assertIn("healthcare provider", response.lower())
        
        # Test medication keyword
        response = self.ai_service._get_fallback_response("medication question")
        self.assertIn("pharmacist", response.lower())
        
        # Test unknown keyword
        response = self.ai_service._get_fallback_response("random question")
        self.assertIn("technical difficulties", response.lower())
    
    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        result = self.ai_service.get_ai_response("")
        self.assertTrue(result['success'])
        self.assertIn("didn't receive a message", result['response'])
        
        result = self.ai_service.get_ai_response("   ")
        self.assertTrue(result['success'])
        self.assertIn("didn't receive a message", result['response'])
    
    @patch('healthee.ai_service.requests.post')
    def test_openai_api_success(self, mock_post):
        """Test successful OpenAI API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Aspirin is a pain reliever and anti-inflammatory medication.'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Mock settings
        with patch('healthee.ai_service.settings.AI_API_KEY', 'test-key'):
            result = self.ai_service.get_ai_response("What is aspirin?")
        
        self.assertTrue(result['success'])
        self.assertIn('Aspirin', result['response'])
        self.assertFalse(result['cached'])
        self.assertIsNone(result['error'])
    
    @patch('healthee.ai_service.requests.post')
    def test_openai_api_rate_limit(self, mock_post):
        """Test OpenAI API rate limit handling"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        with patch('healthee.ai_service.settings.AI_API_KEY', 'test-key'):
            result = self.ai_service.get_ai_response("What is aspirin?")
        
        self.assertFalse(result['success'])
        self.assertIn('technical difficulties', result['response'])
        self.assertIsNotNone(result['error'])
    
    def test_health_check_no_api_key(self):
        """Test health check without API key"""
        with patch('healthee.ai_service.settings.AI_API_KEY', ''):
            result = self.ai_service.health_check()
        
        self.assertFalse(result['available'])
        self.assertIn('not configured', result['error'])


class AIIntegrationAPITest(TestCase):
    """Test AI integration in API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_ai_consultation_creation(self):
        """Test creating an AI consultation"""
        response = self.client.post('/api/healthee/consultations/', {
            'consultation_type': 'ai'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['consultation_type'], 'ai')
        self.assertEqual(response.data['status'], 'active')
    
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_send_message_ai_response(self, mock_ai_response):
        """Test sending message and getting AI response"""
        # Create AI consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='ai'
        )
        
        # Mock AI response
        mock_ai_response.return_value = {
            'response': 'Aspirin is a pain reliever commonly used for headaches.',
            'success': True,
            'cached': False,
            'error': None
        }
        
        # Send message
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/send-message/',
            {'message': 'What is aspirin used for?'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_message', response.data)
        self.assertIn('ai_response', response.data)
        self.assertIn('ai_metadata', response.data)
        
        # Check AI response was created
        self.assertEqual(response.data['ai_response']['is_ai_response'], True)
        self.assertIn('Aspirin', response.data['ai_response']['message'])
        
        # Check metadata
        self.assertTrue(response.data['ai_metadata']['success'])
        self.assertFalse(response.data['ai_metadata']['cached'])
    
    @patch('healthee.ai_service.ai_service.get_ai_response')
    def test_send_message_ai_error_fallback(self, mock_ai_response):
        """Test AI error handling with fallback"""
        # Create AI consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='ai'
        )
        
        # Mock AI service error
        mock_ai_response.side_effect = Exception("API Error")
        
        # Send message
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/send-message/',
            {'message': 'What is aspirin used for?'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_message', response.data)
        self.assertIn('ai_response', response.data)
        
        # Check fallback response was created
        self.assertEqual(response.data['ai_response']['is_ai_response'], True)
        self.assertIn('technical difficulties', response.data['ai_response']['message'])
        
        # Check error metadata
        self.assertFalse(response.data['ai_metadata']['success'])
    
    def test_send_message_human_consultation_no_ai(self):
        """Test that human consultations don't trigger AI responses"""
        # Create human consultation
        consultation = Consultation.objects.create(
            user=self.user,
            consultation_type='human'
        )
        
        # Send message
        response = self.client.post(
            f'/api/healthee/consultations/{consultation.id}/send-message/',
            {'message': 'Hello, I need help'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_message', response.data)
        self.assertIsNone(response.data['ai_response'])
    
    @patch('healthee.ai_service.ai_service.health_check')
    def test_ai_health_check_endpoint(self, mock_health_check):
        """Test AI health check endpoint"""
        # Mock health check response
        mock_health_check.return_value = {
            'available': True,
            'response_time': 0.5,
            'error': None
        }
        
        response = self.client.get('/api/healthee/ai/health-check/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ai_service', response.data)
        self.assertIn('timestamp', response.data)
        self.assertTrue(response.data['ai_service']['available'])
    
    @patch('healthee.ai_service.ai_service.health_check')
    def test_ai_health_check_error(self, mock_health_check):
        """Test AI health check with error"""
        # Mock health check error
        mock_health_check.side_effect = Exception("Service unavailable")
        
        response = self.client.get('/api/healthee/ai/health-check/')
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(response.data['ai_service']['available'])
        self.assertIn('Service unavailable', response.data['ai_service']['error'])