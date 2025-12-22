"""
Manual test script to verify authentication endpoints.
Run with: python test_auth_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_registration():
    """Test user registration."""
    print("\n=== Testing Registration ===")
    url = f"{BASE_URL}/register/"
    data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['tokens']
    return None

def test_login():
    """Test user login."""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/login/"
    data = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['tokens']
    return None

def test_current_user(access_token):
    """Test getting current user profile."""
    print("\n=== Testing Current User ===")
    url = f"{BASE_URL}/me/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_logout(refresh_token):
    """Test user logout."""
    print("\n=== Testing Logout ===")
    url = f"{BASE_URL}/logout/"
    data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Starting authentication endpoint tests...")
    print("Make sure the Django server is running on http://localhost:8000")
    
    # Test registration
    tokens = test_registration()
    
    if tokens:
        # Test current user with registration tokens
        test_current_user(tokens['access'])
        
        # Test logout
        test_logout(tokens['refresh'])
    
    # Test login
    tokens = test_login()
    
    if tokens:
        # Test current user with login tokens
        test_current_user(tokens['access'])
    
    print("\n=== Tests Complete ===")
