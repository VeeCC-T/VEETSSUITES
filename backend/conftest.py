"""
Global pytest configuration and fixtures for the VeetsSuites backend.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import factory
from factory.django import DjangoModelFactory
from hypothesis import settings, Verbosity

# Configure Hypothesis settings
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.quiet)
settings.load_profile("default")

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "student"
    is_active = True


class StudentFactory(UserFactory):
    """Factory for creating student users."""
    role = "student"


class InstructorFactory(UserFactory):
    """Factory for creating instructor users."""
    role = "instructor"


class AdminFactory(UserFactory):
    """Factory for creating admin users."""
    role = "admin"
    is_staff = True
    is_superuser = True


@pytest.fixture
def user():
    """Create a basic test user."""
    return UserFactory()


@pytest.fixture
def student():
    """Create a student user."""
    return StudentFactory()


@pytest.fixture
def instructor():
    """Create an instructor user."""
    return InstructorFactory()


@pytest.fixture
def admin():
    """Create an admin user."""
    return AdminFactory()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def api_client():
    """DRF API test client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated with a user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def student_client(api_client, student):
    """API client authenticated as a student."""
    refresh = RefreshToken.for_user(student)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def instructor_client(api_client, instructor):
    """API client authenticated as an instructor."""
    refresh = RefreshToken.for_user(instructor)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin):
    """API client authenticated as an admin."""
    refresh = RefreshToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    This removes the need to mark every test with @pytest.mark.django_db
    """
    pass


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing file uploads."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"


@pytest.fixture
def mock_stripe_session():
    """Mock Stripe checkout session data."""
    return {
        'id': 'cs_test_123456789',
        'url': 'https://checkout.stripe.com/pay/cs_test_123456789',
        'payment_status': 'unpaid',
        'amount_total': 5000,  # $50.00 in cents
        'currency': 'usd',
        'metadata': {
            'course_id': '1',
            'user_id': '1'
        }
    }


@pytest.fixture
def mock_paystack_session():
    """Mock Paystack checkout session data."""
    return {
        'status': True,
        'message': 'Authorization URL created',
        'data': {
            'authorization_url': 'https://checkout.paystack.com/test_123456789',
            'access_code': 'test_123456789',
            'reference': 'ref_123456789'
        }
    }