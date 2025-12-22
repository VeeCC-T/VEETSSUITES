#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')
django.setup()

# Test minimal class definition
try:
    from django.conf import settings
    print(f"Settings loaded: {hasattr(settings, 'AI_API_KEY')}")
    
    # Define a minimal class
    class TestAIService:
        def __init__(self):
            self.api_key = getattr(settings, 'AI_API_KEY', '')
            print(f"API key: '{self.api_key}'")
    
    # Test instantiation
    service = TestAIService()
    print("Minimal class works")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()