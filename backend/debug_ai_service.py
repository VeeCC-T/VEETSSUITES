#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')
django.setup()

try:
    from django.conf import settings
    print(f"AI_API_KEY: '{settings.AI_API_KEY}'")
    print(f"AI_API_URL: '{settings.AI_API_URL}'")
    
    from healthee.ai_service import AIService
    print("AIService imported successfully")
    
    service = AIService()
    print("AIService instantiated successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()