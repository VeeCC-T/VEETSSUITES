#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')
django.setup()

try:
    # Try to execute the ai_service.py file manually
    with open('healthee/ai_service.py', 'r') as f:
        content = f.read()
    
    # Execute the content
    exec(content)
    
    print("File executed successfully")
    print(f"AIService class defined: {'AIService' in locals()}")
    
    if 'AIService' in locals():
        service = locals()['AIService']()
        print("AIService instantiated successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()