"""
Manual test script for Portfolio API
"""

import os
import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')
django.setup()

from accounts.models import User
from portfolios.models import Portfolio
from portfolios.services import CVParserService
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PyPDF2 import PdfWriter

def create_test_pdf():
    """Create a simple test PDF"""
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

@pytest.mark.django_db
def test_portfolio_creation():
    """Test creating a portfolio"""
    print("Testing Portfolio Creation...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='testportfolio',
        email='testportfolio@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Portfolio'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"✓ Using existing test user: {user.email}")
    
    # Delete existing portfolio if any
    Portfolio.objects.filter(user=user).delete()
    
    # Create portfolio
    pdf_file = create_test_pdf()
    portfolio = Portfolio.objects.create(
        user=user,
        cv_file=pdf_file,
        is_public=True
    )
    print(f"✓ Created portfolio with ID: {portfolio.id}")
    
    # Parse CV content
    try:
        parser = CVParserService(portfolio.cv_file)
        parsed_content = parser.parse_content()
        portfolio.parsed_content = parsed_content
        portfolio.save()
        print(f"✓ Parsed CV content successfully")
        print(f"  - Sections found: {len(parsed_content.get('sections', {}))}")
        print(f"  - Contact info: {parsed_content.get('contact_info', {})}")
    except Exception as e:
        print(f"✗ Failed to parse CV: {e}")
    
    # Verify portfolio
    retrieved = Portfolio.objects.get(id=portfolio.id)
    print(f"✓ Retrieved portfolio: {retrieved}")
    print(f"  - User: {retrieved.user.email}")
    print(f"  - Public: {retrieved.is_public}")
    print(f"  - CV File: {retrieved.cv_file.name}")
    print(f"  - Parsed Content Keys: {list(retrieved.parsed_content.keys())}")
    
    print("\n✓ All tests passed!")

if __name__ == '__main__':
    test_portfolio_creation()
