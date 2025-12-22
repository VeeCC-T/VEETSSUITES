"""
Test AI Service with imports
"""

import requests
import json
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib


class AIService:
    """Test AI service class"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'AI_API_KEY', '')
        print("AIService initialized successfully")


# Global instance
ai_service = AIService()