"""
Unit tests for authentication endpoints.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTests(TestCase):
    """Test suite for authentication endpoints."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        self.me_url = '/api/auth/me/'
        
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test user can register with valid data."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertEqual(response.data['user']['role'], 'student')
        
        # Verify user was created in database
        user = User.objects.get(email=self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_user_login(self):
        """Test user can login with valid credentials."""
        # Create user first
        User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        
        # Login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_current_user(self):
        """Test authenticated user can get their profile."""
        # Create and login user
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        
        # Get tokens
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['tokens']['access']
        
        # Get current user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
    
    def test_protected_endpoint_requires_authentication(self):
        """Test protected endpoint requires authentication."""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(TestCase):
    """Test suite for role-based permissions."""
    
    def setUp(self):
        """Set up test users with different roles."""
        self.client = APIClient()
        
        self.student = User.objects.create_user(
            email='student@example.com',
            username='student',
            password='TestPass123!',
            first_name='Student',
            last_name='User',
            role='student'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            username='instructor',
            password='TestPass123!',
            first_name='Instructor',
            last_name='User',
            role='instructor'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='TestPass123!',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
    
    def test_user_role_properties(self):
        """Test user role property methods."""
        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_instructor)
        self.assertFalse(self.student.is_admin_user)
        
        self.assertFalse(self.instructor.is_student)
        self.assertTrue(self.instructor.is_instructor)
        self.assertFalse(self.instructor.is_admin_user)
        
        self.assertFalse(self.admin.is_student)
        self.assertFalse(self.admin.is_instructor)
        self.assertTrue(self.admin.is_admin_user)
    
    def test_role_promotion(self):
        """Test user role promotion methods."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        # Default role should be student
        self.assertEqual(user.role, 'student')
        
        # Promote to instructor
        user.promote_to_instructor()
        user.refresh_from_db()
        self.assertEqual(user.role, 'instructor')
        
        # Promote to admin
        user.promote_to_admin()
        user.refresh_from_db()
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
        # Demote to student
        user.demote_to_student()
        user.refresh_from_db()
        self.assertEqual(user.role, 'student')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
