"""
Simple AI Service for testing
"""

from django.conf import settings


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIService:
    """Simple AI service class"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'AI_API_KEY', '')
        self.api_url = getattr(settings, 'AI_API_URL', '') or "https://api.openai.com/v1/chat/completions"
    
    def get_ai_response(self, message: str, conversation_messages: list = None):
        """Simple response method"""
        return {
            'response': f"Echo: {message}",
            'success': True,
            'cached': False,
            'error': None
        }


# Global instance
ai_service = AIService()