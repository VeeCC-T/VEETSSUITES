"""
AI Service for HEALTHEE consultation system.
Handles AI chatbot integration with error handling, fallbacks, and caching.
"""

import requests
import json
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import hashlib

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIService:
    """Service class for handling AI chatbot interactions"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'AI_API_KEY', '')
        self.api_url = getattr(settings, 'AI_API_URL', '') or "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.temperature = 0.7
        self.timeout = 30
        self.cache_timeout = 3600
        self.enable_cache = True
        
        self.system_prompt = """You are HEALTHEE, an AI health consultation assistant for a pharmacy platform. 

IMPORTANT DISCLAIMERS AND GUIDELINES:
- You are NOT a replacement for professional medical advice
- Always remind users to consult with a healthcare provider for serious concerns
- You can provide general health information and medication guidance
- Focus on pharmacy-related questions, medication interactions, and general wellness
- Be helpful but cautious with medical advice

Your responses should be:
- Informative but not diagnostic
- Encouraging users to seek professional help when needed
- Focused on medication safety and general health guidance
- Clear about your limitations as an AI assistant

Always end serious health discussions with: "Please consult with a healthcare provider or pharmacist for personalized medical advice."
"""

    def _generate_cache_key(self, message: str, conversation_context: str = "") -> str:
        """Generate a cache key for the message and context"""
        content = f"{message}:{conversation_context}"
        return f"ai_response:{hashlib.md5(content.encode()).hexdigest()}"

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available"""
        if not self.enable_cache:
            return None
        
        try:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key[:20]}...")
                return cached
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None

    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache the AI response"""
        if not self.enable_cache:
            return
        
        try:
            cache.set(cache_key, response, self.cache_timeout)
            logger.info(f"Cached response for key: {cache_key[:20]}...")
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

    def _build_conversation_context(self, messages: list) -> str:
        """Build conversation context from recent messages"""
        if not messages:
            return ""
        
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        
        context_parts = []
        for msg in recent_messages:
            if msg.is_ai_response:
                context_parts.append(f"Assistant: {msg.message}")
            else:
                context_parts.append(f"User: {msg.message}")
        
        return "\n".join(context_parts)

    def _prepare_openai_payload(self, message: str, conversation_context: str = "") -> Dict:
        """Prepare the payload for OpenAI API"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if conversation_context:
            messages.append({
                "role": "user", 
                "content": f"Previous conversation:\n{conversation_context}\n\nCurrent question: {message}"
            })
        else:
            messages.append({"role": "user", "content": message})
        
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

    def _call_openai_api(self, payload: Dict) -> Tuple[str, bool]:
        """Call OpenAI API and return response"""
        if not self.api_key:
            raise AIServiceError("AI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info("Calling OpenAI API...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content'].strip()
                logger.info("OpenAI API call successful")
                return ai_response, True
            
            elif response.status_code == 429:
                logger.warning("OpenAI API rate limit exceeded")
                raise AIServiceError("AI service is currently busy. Please try again in a moment.")
            
            elif response.status_code == 401:
                logger.error("OpenAI API authentication failed")
                raise AIServiceError("AI service authentication error")
            
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise AIServiceError(f"AI service error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("OpenAI API timeout")
            raise AIServiceError("AI service timeout. Please try again.")
        
        except requests.exceptions.ConnectionError:
            logger.error("OpenAI API connection error")
            raise AIServiceError("AI service connection error. Please try again.")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request error: {e}")
            raise AIServiceError("AI service request error. Please try again.")

    def _get_fallback_response(self, message: str) -> str:
        """Generate a fallback response when AI service is unavailable"""
        message_lower = message.lower()
        
        fallback_responses = {
            'headache': "For headaches, you might consider over-the-counter pain relievers like acetaminophen or ibuprofen. However, if headaches are frequent or severe, please consult with a healthcare provider.",
            'fever': "For fever, you can use acetaminophen or ibuprofen as directed on the package. Stay hydrated and rest. If fever is high (over 103F) or persistent, seek medical attention.",
            'cold': "For cold symptoms, rest, stay hydrated, and consider over-the-counter medications for symptom relief. If symptoms worsen or persist beyond 7-10 days, consult a healthcare provider.",
            'cough': "For coughs, try staying hydrated, using a humidifier, or throat lozenges. Over-the-counter cough medications may help. Persistent coughs should be evaluated by a healthcare provider.",
            'medication': "For medication questions, it's best to consult with a pharmacist or your healthcare provider who can review your specific medications and health conditions.",
            'interaction': "Drug interactions can be serious. Please consult with a pharmacist or your healthcare provider to review all your medications and supplements.",
            'dosage': "Medication dosages should always be determined by your healthcare provider or pharmacist based on your specific condition and health status.",
        }
        
        for keyword, response in fallback_responses.items():
            if keyword in message_lower:
                return f"{response}\n\nNote: I'm currently experiencing technical difficulties. Please consult with a healthcare provider or pharmacist for personalized medical advice."
        
        return """I'm currently experiencing technical difficulties and cannot provide a detailed response. 

For health and medication questions, I recommend:
- Consulting with a pharmacist at your local pharmacy
- Speaking with your healthcare provider
- Calling a nurse hotline if available in your area
- Seeking immediate medical attention for urgent concerns

Please consult with a healthcare provider or pharmacist for personalized medical advice."""

    def get_ai_response(self, message: str, conversation_messages: list = None) -> Dict[str, any]:
        """Get AI response for a health consultation message"""
        if not message or not message.strip():
            return {
                'response': "I didn't receive a message. Could you please ask your health question?",
                'success': True,
                'cached': False,
                'error': None
            }
        
        try:
            conversation_context = ""
            if conversation_messages:
                conversation_context = self._build_conversation_context(conversation_messages)
            
            cache_key = self._generate_cache_key(message, conversation_context)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                return {
                    'response': cached_response,
                    'success': True,
                    'cached': True,
                    'error': None
                }
            
            payload = self._prepare_openai_payload(message, conversation_context)
            ai_response, success = self._call_openai_api(payload)
            
            if success:
                self._cache_response(cache_key, ai_response)
                
                return {
                    'response': ai_response,
                    'success': True,
                    'cached': False,
                    'error': None
                }
            
        except AIServiceError as e:
            logger.warning(f"AI service error: {e}")
            fallback_response = self._get_fallback_response(message)
            
            return {
                'response': fallback_response,
                'success': False,
                'cached': False,
                'error': str(e)
            }
        
        except Exception as e:
            logger.error(f"Unexpected AI service error: {e}")
            fallback_response = self._get_fallback_response(message)
            
            return {
                'response': fallback_response,
                'success': False,
                'cached': False,
                'error': "Unexpected error occurred"
            }

    def health_check(self) -> Dict[str, any]:
        """Check if the AI service is available and working"""
        if not self.api_key:
            return {
                'available': False,
                'response_time': None,
                'error': 'AI API key not configured'
            }
        
        try:
            start_time = timezone.now()
            
            test_payload = self._prepare_openai_payload("Hello, are you working?")
            response, success = self._call_openai_api(test_payload)
            
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                'available': success,
                'response_time': response_time,
                'error': None if success else 'API call failed'
            }
            
        except Exception as e:
            return {
                'available': False,
                'response_time': None,
                'error': str(e)
            }


# Global AI service instance
ai_service = AIService()
