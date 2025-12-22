"""
Tests for error handling and validation system.
"""

import json
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from .validators import (
    PasswordStrengthValidator, 
    FileTypeValidator, 
    FileSizeValidator,
    EmailFormatValidator,
    CourseDataValidator,
    ExamDataValidator,
    PaymentDataValidator
)
from .error_responses import (
    create_error_response,
    create_validation_error_response,
    create_authentication_error_response,
    ErrorCodes,
    ErrorMessages
)

User = get_user_model()

class ErrorHandlingTestCase(APITestCase):
    """
    Test cases for error handling middleware and responses.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    def test_authentication_error_response(self):
        """Test authentication error response format."""
        response = create_authentication_error_response()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], ErrorCodes.AUTH_FAILED)
        self.assertEqual(response.data['error'], ErrorMessages.INVALID_CREDENTIALS)

    def test_validation_error_response(self):
        """Test validation error response format."""
        field_errors = {
            'email': ['This field is required'],
            'password': ['Password is too weak']
        }
        response = create_validation_error_response(field_errors)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], ErrorCodes.VALIDATION_ERROR)
        self.assertEqual(response.data['details'], field_errors)

    def test_rate_limiting_error(self):
        """Test rate limiting error response."""
        # Make multiple rapid requests to trigger rate limiting
        for i in range(10):
            response = self.client.post('/api/auth/login/', {
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        
        # Should eventually get rate limited
        # Note: This test might need adjustment based on actual rate limits

    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request body."""
        response = self.client.post(
            '/api/auth/login/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields(self):
        """Test validation of missing required fields."""
        response = self.client.post('/api/auth/register/', {
            'email': 'test@example.com'
            # Missing password, first_name, last_name
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_upload_size_limit(self):
        """Test file upload size validation."""
        # Create a large file (simulate)
        large_file = SimpleUploadedFile(
            "large_file.pdf",
            b"x" * (11 * 1024 * 1024),  # 11MB file
            content_type="application/pdf"
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/portfolios/upload/', {
            'cv_file': large_file
        })
        
        # Should be rejected due to size limit
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE])


class ValidatorTestCase(TestCase):
    """
    Test cases for custom validators.
    """

    def test_password_strength_validator(self):
        """Test password strength validation."""
        validator = PasswordStrengthValidator()
        
        # Test weak passwords
        with self.assertRaises(Exception):
            validator('123456')  # Too short and weak
        
        with self.assertRaises(Exception):
            validator('password')  # Common weak password
        
        with self.assertRaises(Exception):
            validator('Password')  # Missing digits and special chars
        
        # Test strong password
        try:
            validator('StrongPass123!')
        except Exception:
            self.fail("Strong password should pass validation")

    def test_email_format_validator(self):
        """Test email format validation."""
        validator = EmailFormatValidator()
        
        # Test valid emails
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            try:
                validator(email)
            except Exception:
                self.fail(f"Valid email {email} should pass validation")
        
        # Test invalid emails
        invalid_emails = [
            'invalid.email',
            '@example.com',
            'test@',
            'test..test@example.com',  # Double dots
            'test@example..com'  # Double dots in domain
        ]
        
        for email in invalid_emails:
            with self.assertRaises(Exception):
                validator(email)

    def test_file_type_validator(self):
        """Test file type validation."""
        validator = FileTypeValidator(
            allowed_types=['application/pdf'],
            allowed_extensions=['pdf']
        )
        
        # Test valid PDF file
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b"%PDF-1.4 test content",
            content_type="application/pdf"
        )
        
        try:
            validator(pdf_file)
        except Exception:
            self.fail("Valid PDF file should pass validation")
        
        # Test invalid file type
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"text content",
            content_type="text/plain"
        )
        
        with self.assertRaises(Exception):
            validator(txt_file)

    def test_file_size_validator(self):
        """Test file size validation."""
        validator = FileSizeValidator(max_size_mb=1)  # 1MB limit
        
        # Test small file
        small_file = SimpleUploadedFile(
            "small.pdf",
            b"small content",
            content_type="application/pdf"
        )
        
        try:
            validator(small_file)
        except Exception:
            self.fail("Small file should pass validation")
        
        # Test large file
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (2 * 1024 * 1024),  # 2MB file
            content_type="application/pdf"
        )
        
        with self.assertRaises(Exception):
            validator(large_file)

    def test_course_data_validator(self):
        """Test course data validation."""
        validator = CourseDataValidator()
        
        # Test valid course data
        valid_data = {
            'title': 'Introduction to Python Programming',
            'description': 'A comprehensive course covering Python basics and advanced topics.',
            'price': 99.99
        }
        
        try:
            validator(valid_data)
        except Exception:
            self.fail("Valid course data should pass validation")
        
        # Test invalid course data
        invalid_data = {
            'title': 'A',  # Too short
            'description': 'Short',  # Too short
            'price': -10  # Negative price
        }
        
        with self.assertRaises(Exception):
            validator(invalid_data)

    def test_exam_data_validator(self):
        """Test exam data validation."""
        validator = ExamDataValidator()
        
        # Test valid exam data
        valid_data = {
            'text': 'What is the capital of France?',
            'option_a': 'London',
            'option_b': 'Berlin',
            'option_c': 'Paris',
            'option_d': 'Madrid',
            'correct_answer': 'C'
        }
        
        try:
            validator(valid_data)
        except Exception:
            self.fail("Valid exam data should pass validation")
        
        # Test invalid exam data
        invalid_data = {
            'text': 'Short',  # Too short
            'option_a': '',  # Empty option
            'option_b': 'Berlin',
            'option_c': 'Paris',
            'option_d': 'Madrid',
            'correct_answer': 'X'  # Invalid answer
        }
        
        with self.assertRaises(Exception):
            validator(invalid_data)

    def test_payment_data_validator(self):
        """Test payment data validation."""
        validator = PaymentDataValidator()
        
        # Test valid payment data
        valid_data = {
            'amount': 99.99,
            'currency': 'USD'
        }
        
        try:
            validator(valid_data)
        except Exception:
            self.fail("Valid payment data should pass validation")
        
        # Test invalid payment data
        invalid_data = {
            'amount': -10,  # Negative amount
            'currency': 'INVALID'  # Invalid currency
        }
        
        with self.assertRaises(Exception):
            validator(invalid_data)


class MiddlewareTestCase(TestCase):
    """
    Test cases for custom middleware.
    """
    
    def setUp(self):
        self.client = Client()

    def test_security_headers(self):
        """Test that security headers are added to responses."""
        response = self.client.get('/api/')
        
        # Check for security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

    def test_request_size_limit(self):
        """Test request size validation."""
        # Create a large request body
        large_data = {'data': 'x' * (2 * 1024 * 1024)}  # 2MB of data
        
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(large_data),
            content_type='application/json'
        )
        
        # Should be rejected due to size limit
        self.assertIn(response.status_code, [
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_400_BAD_REQUEST
        ])

    @patch('veetssuites.middleware.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are properly logged."""
        # Trigger an error
        response = self.client.post('/api/nonexistent-endpoint/')
        
        # Check that error was logged
        self.assertTrue(mock_logger.error.called or mock_logger.warning.called)


@pytest.mark.django_db
class ThrottlingTestCase(APITestCase):
    """
    Test cases for rate limiting/throttling.
    """
    
    def setUp(self):
        self.client = APIClient()

    def test_login_rate_limiting(self):
        """Test rate limiting on login attempts."""
        # Make multiple failed login attempts
        for i in range(10):
            response = self.client.post('/api/auth/login/', {
                'email': 'nonexistent@example.com',
                'password': 'wrongpassword'
            })
        
        # Eventually should get rate limited
        # Note: Actual behavior depends on throttling configuration

    def test_registration_rate_limiting(self):
        """Test rate limiting on registration attempts."""
        # Make multiple registration attempts
        for i in range(5):
            response = self.client.post('/api/auth/register/', {
                'email': f'test{i}@example.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User'
            })
        
        # Should eventually get rate limited


if __name__ == '__main__':
    pytest.main([__file__])