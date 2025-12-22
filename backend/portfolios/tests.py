"""
Tests for Portfolio API endpoints.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import Portfolio
import io
from PyPDF2 import PdfWriter


class PortfolioAPITestCase(TestCase):
    """Test cases for Portfolio API endpoints"""

    def setUp(self):
        """Set up test client and test user"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create another user for testing access control
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )

    def create_test_pdf(self, content="Test CV Content"):
        """Create a simple test PDF file"""
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        
        pdf_buffer = io.BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)
        
        return SimpleUploadedFile(
            "test_cv.pdf",
            pdf_buffer.read(),
            content_type="application/pdf"
        )

    def test_upload_portfolio_authenticated(self):
        """Test uploading a portfolio when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        pdf_file = self.create_test_pdf()
        
        response = self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Portfolio.objects.filter(user=self.user).exists())
        
        portfolio = Portfolio.objects.get(user=self.user)
        self.assertTrue(portfolio.is_public)
        self.assertIsNotNone(portfolio.cv_file)

    def test_upload_portfolio_unauthenticated(self):
        """Test uploading a portfolio without authentication fails"""
        pdf_file = self.create_test_pdf()
        
        response = self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_duplicate_portfolio(self):
        """Test that uploading a second portfolio fails"""
        self.client.force_authenticate(user=self.user)
        
        # Create first portfolio
        pdf_file1 = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file1,
                'is_public': True
            },
            format='multipart'
        )
        
        # Try to create second portfolio
        pdf_file2 = self.create_test_pdf()
        response = self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file2,
                'is_public': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_public_portfolio(self):
        """Test retrieving a public portfolio without authentication"""
        # Create a public portfolio
        self.client.force_authenticate(user=self.user)
        pdf_file = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': True
            },
            format='multipart'
        )
        
        # Logout and try to access
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/portfolio/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_private_portfolio_unauthorized(self):
        """Test that accessing a private portfolio without auth fails"""
        # Create a private portfolio
        self.client.force_authenticate(user=self.user)
        pdf_file = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': False
            },
            format='multipart'
        )
        
        # Logout and try to access
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/portfolio/{self.user.id}/')
        
        # Should return 401 (unauthenticated) or 403 (forbidden)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_portfolio(self):
        """Test updating an existing portfolio"""
        # Create portfolio
        self.client.force_authenticate(user=self.user)
        pdf_file1 = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file1,
                'is_public': False
            },
            format='multipart'
        )
        
        # Update portfolio
        pdf_file2 = self.create_test_pdf("Updated CV Content")
        response = self.client.put(
            f'/api/portfolio/{self.user.id}/update/',
            {
                'cv_file': pdf_file2,
                'is_public': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        portfolio = Portfolio.objects.get(user=self.user)
        self.assertTrue(portfolio.is_public)

    def test_update_portfolio_unauthorized(self):
        """Test that updating another user's portfolio fails"""
        # Create portfolio for user
        self.client.force_authenticate(user=self.user)
        pdf_file = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': False
            },
            format='multipart'
        )
        
        # Try to update as other user
        self.client.force_authenticate(user=self.other_user)
        pdf_file2 = self.create_test_pdf()
        response = self.client.put(
            f'/api/portfolio/{self.user.id}/update/',
            {
                'cv_file': pdf_file2,
                'is_public': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_portfolio(self):
        """Test deleting a portfolio"""
        # Create portfolio
        self.client.force_authenticate(user=self.user)
        pdf_file = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': False
            },
            format='multipart'
        )
        
        # Delete portfolio
        response = self.client.delete(f'/api/portfolio/{self.user.id}/delete/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Portfolio.objects.filter(user=self.user).exists())

    def test_get_my_portfolio(self):
        """Test getting authenticated user's portfolio"""
        # Create portfolio
        self.client.force_authenticate(user=self.user)
        pdf_file = self.create_test_pdf()
        self.client.post(
            '/api/portfolio/upload/',
            {
                'cv_file': pdf_file,
                'is_public': False
            },
            format='multipart'
        )
        
        # Get my portfolio
        response = self.client.get('/api/portfolio/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], self.user.email)
