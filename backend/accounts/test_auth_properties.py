"""
Property-based tests for authentication system.
Tests Properties 2, 3, and 5 from requirements.
"""
import pytest
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
import json

User = get_user_model()


class AuthenticationPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @given(
        email=st.emails(),
        password=st.text(min_size=8, max_size=50).filter(lambda x: any(c.isdigit() for c in x) and any(c.isalpha() for c in x))
    )
    def test_property_2_valid_credentials_return_tokens(self, email, password):
        """Property 2: Valid credentials return tokens"""
        # Create user
        username = email.split('@')[0]  # Use email prefix as username
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Login with valid credentials
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': email,
            'password': password
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertTrue(len(data['access']) > 0)
        self.assertTrue(len(data['refresh']) > 0)

    @given(email=st.emails())
    def test_property_3_password_reset_sends_secure_links(self, email):
        """Property 3: Password reset sends secure links"""
        # Create user
        user = User.objects.create_user(email=email, password='testpass123')
        
        # Clear mail outbox
        mail.outbox = []
        
        # Request password reset
        response = self.client.post(reverse('password_reset_request'), {
            'email': email
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email contains secure reset link
        email_body = mail.outbox[0].body
        self.assertIn('reset', email_body.lower())
        self.assertIn('token', email_body.lower())

    @given(
        email=st.emails(),
        password=st.text(min_size=8, max_size=50).filter(lambda x: any(c.isdigit() for c in x) and any(c.isalpha() for c in x))
    )
    def test_property_5_logout_invalidates_tokens(self, email, password):
        """Property 5: Logout invalidates tokens"""
        # Create user and get tokens
        user = User.objects.create_user(email=email, password=password)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, 200)
        
        # Logout (blacklist token)
        response = self.client.post(reverse('logout'), {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, 200)
        
        # Try to use token again - should fail
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, 401)