"""
Property-based tests for HUB3660 recording access control functionality.

These tests use Hypothesis to verify correctness properties for recording
storage and access control, ensuring proper enrollment verification and
time-limited URL generation.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from hub3660.models import Course, Enrollment, Session

User = get_user_model()


# Custom strategies for generating valid data
@st.composite
def valid_course_title(draw):
    """Generate valid course titles."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_',
        min_size=5,
        max_size=100
    ))


@st.composite
def valid_course_description(draw):
    """Generate valid course descriptions."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-_\n',
        min_size=10,
        max_size=500
    ))


@st.composite
def valid_price(draw):
    """Generate valid course prices."""
    return draw(st.decimals(
        min_value=Decimal('0.00'),
        max_value=Decimal('999.99'),
        places=2
    ))


@st.composite
def valid_currency(draw):
    """Generate valid currency codes."""
    return draw(st.sampled_from(['USD', 'NGN', 'EUR', 'GBP']))


@st.composite
def valid_username(draw):
    """Generate valid usernames."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyz0123456789',
        min_size=5,
        max_size=15
    ))


@st.composite
def valid_name(draw):
    """Generate valid first/last names."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyz',
        min_size=2,
        max_size=15
    ))


@st.composite
def valid_password(draw):
    """Generate valid passwords."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#',
        min_size=8,
        max_size=20
    ))


@st.composite
def valid_session_title(draw):
    """Generate valid session titles."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_',
        min_size=5,
        max_size=100
    ))


@st.composite
def future_datetime(draw):
    """Generate future datetime for session scheduling."""
    now = timezone.now()
    min_time = now + timedelta(hours=1)
    max_time = now + timedelta(days=30)
    
    time_diff = (max_time - min_time).total_seconds()
    random_seconds = draw(st.integers(min_value=0, max_value=int(time_diff)))
    
    return min_time + timedelta(seconds=random_seconds)


@pytest.mark.django_db
class TestRecordingAccessProperties:
    """Property-based tests for recording access control functionality."""
    
    # Feature: veetssuites-platform, Property 33: Recording URLs stored with permissions
    @given(
        instructor_username=valid_username(),
        student_username=valid_username(),
        password=valid_password(),
        instructor_first_name=valid_name(),
        instructor_last_name=valid_name(),
        student_first_name=valid_name(),
        student_last_name=valid_name(),
        course_title=valid_course_title(),
        course_description=valid_course_description(),
        course_price=valid_price(),
        course_currency=valid_currency(),
        session_title=valid_session_title(),
        scheduled_at=future_datetime()
    )
    @settings(max_examples=10, deadline=20000, suppress_health_check=[HealthCheck.too_slow])
    def test_recording_urls_stored_with_permissions(
        self, instructor_username, student_username, password, instructor_first_name,
        instructor_last_name, student_first_name, student_last_name, course_title,
        course_description, course_price, course_currency, session_title, scheduled_at
    ):
        """
        Property 33: Recording URLs stored with permissions
        
        For any recording uploaded to S3, the system should store the S3 URL along with
        a reference to the course, enabling enrollment-based access control.
        
        Validates: Requirements 8.1
        """
        # Ensure usernames are different
        if instructor_username == student_username:
            student_username = f"{student_username}_student"
            instructor_username = f"{instructor_username}_instructor"
        
        # Generate unique emails
        instructor_email = f"{instructor_username}@test.com"
        student_email = f"{student_username}@test.com"
        
        # Clean up any existing data
        User.objects.filter(email__in=[instructor_email, student_email]).delete()
        User.objects.filter(username__in=[instructor_username, student_username]).delete()
        Course.objects.filter(title=course_title).delete()
        Session.objects.filter(title=session_title).delete()
        
        try:
            # Create instructor and student users
            instructor = User.objects.create_user(
                email=instructor_email,
                username=instructor_username,
                password=password,
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                role='instructor'
            )
            
            student = User.objects.create_user(
                email=student_email,
                username=student_username,
                password=password,
                first_name=student_first_name,
                last_name=student_last_name,
                role='student'
            )
            
            # Create course
            course = Course.objects.create(
                title=course_title,
                description=course_description,
                instructor=instructor,
                price=course_price,
                currency=course_currency,
                is_published=True
            )
            
            # Create session
            session = Session.objects.create(
                course=course,
                title=session_title,
                scheduled_at=scheduled_at
            )
            
            # Test the core property: recording storage should maintain course association
            # Simulate storing a recording with S3 key
            s3_key = f"recordings/course_{course.id}/session_{session.id}_test.mp4"
            session.s3_recording_key = s3_key
            session.save()
            
            # CRITICAL: Recording should be associated with the course through the session
            session.refresh_from_db()
            assert session.s3_recording_key == s3_key, \
                f"Session should have S3 key '{s3_key}', but has '{session.s3_recording_key}'"
            
            assert session.course == course, \
                f"Session should be associated with course {course}, but is associated with {session.course}"
            
            # Verify the S3 key contains course information for access control
            assert f"course_{course.id}" in session.s3_recording_key, \
                f"S3 key should contain course ID for access control: {session.s3_recording_key}"
            
            assert f"session_{session.id}" in session.s3_recording_key, \
                f"S3 key should contain session ID for organization: {session.s3_recording_key}"
            
            # Verify session reports having a recording
            assert session.has_recording, \
                "Session with S3 recording key should report having a recording"
            
        finally:
            # Clean up
            Session.objects.filter(title__startswith=session_title).delete()
            Course.objects.filter(title__startswith=course_title).delete()
            User.objects.filter(email__in=[instructor_email, student_email]).delete()
            User.objects.filter(username__in=[instructor_username, student_username]).delete()
    
    # Feature: veetssuites-platform, Property 34: Recording access requires enrollment
    @given(
        instructor_username=valid_username(),
        student_username=valid_username(),
        unenrolled_username=valid_username(),
        password=valid_password(),
        instructor_first_name=valid_name(),
        instructor_last_name=valid_name(),
        student_first_name=valid_name(),
        student_last_name=valid_name(),
        unenrolled_first_name=valid_name(),
        unenrolled_last_name=valid_name(),
        course_title=valid_course_title(),
        course_description=valid_course_description(),
        course_price=valid_price(),
        course_currency=valid_currency(),
        session_title=valid_session_title(),
        scheduled_at=future_datetime()
    )
    @settings(max_examples=10, deadline=25000, suppress_health_check=[HealthCheck.too_slow])
    def test_recording_access_requires_enrollment(
        self, instructor_username, student_username, unenrolled_username, password,
        instructor_first_name, instructor_last_name, student_first_name, student_last_name,
        unenrolled_first_name, unenrolled_last_name, course_title, course_description,
        course_price, course_currency, session_title, scheduled_at
    ):
        """
        Property 34: Recording access requires enrollment
        
        For any recording request, the system should verify the requesting user is
        enrolled in the associated course before generating an access URL.
        
        Validates: Requirements 8.2
        """
        # Ensure usernames are different
        usernames = [instructor_username, student_username, unenrolled_username]
        if len(set(usernames)) != 3:
            instructor_username = f"{instructor_username}_instructor"
            student_username = f"{student_username}_student"
            unenrolled_username = f"{unenrolled_username}_unenrolled"
        
        # Generate unique emails
        instructor_email = f"{instructor_username}@test.com"
        student_email = f"{student_username}@test.com"
        unenrolled_email = f"{unenrolled_username}@test.com"
        
        # Clean up any existing data
        User.objects.filter(email__in=[instructor_email, student_email, unenrolled_email]).delete()
        User.objects.filter(username__in=[instructor_username, student_username, unenrolled_username]).delete()
        Course.objects.filter(title=course_title).delete()
        Session.objects.filter(title=session_title).delete()
        
        try:
            # Create users
            instructor = User.objects.create_user(
                email=instructor_email,
                username=instructor_username,
                password=password,
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                role='instructor'
            )
            
            enrolled_student = User.objects.create_user(
                email=student_email,
                username=student_username,
                password=password,
                first_name=student_first_name,
                last_name=student_last_name,
                role='student'
            )
            
            unenrolled_student = User.objects.create_user(
                email=unenrolled_email,
                username=unenrolled_username,
                password=password,
                first_name=unenrolled_first_name,
                last_name=unenrolled_last_name,
                role='student'
            )
            
            # Create course
            course = Course.objects.create(
                title=course_title,
                description=course_description,
                instructor=instructor,
                price=course_price,
                currency=course_currency,
                is_published=True
            )
            
            # Create session with recording
            session = Session.objects.create(
                course=course,
                title=session_title,
                scheduled_at=scheduled_at,
                s3_recording_key=f"recordings/course_{course.id}/session_test.mp4"
            )
            
            # Enroll one student
            enrollment = Enrollment.objects.create(
                student=enrolled_student,
                course=course,
                payment_status='completed'
            )
            
            # Test API clients
            enrolled_client = APIClient()
            unenrolled_client = APIClient()
            
            # Get tokens
            enrolled_refresh = RefreshToken.for_user(enrolled_student)
            enrolled_token = str(enrolled_refresh.access_token)
            
            unenrolled_refresh = RefreshToken.for_user(unenrolled_student)
            unenrolled_token = str(unenrolled_refresh.access_token)
            
            # Test the core property: enrollment verification for recording access
            
            # Test 1: Unenrolled student should be denied access
            response = unenrolled_client.get(
                f'/api/hub3660/sessions/{session.id}/recording/',
                HTTP_AUTHORIZATION=f'Bearer {unenrolled_token}'
            )
            
            assert response.status_code == 403, \
                f"Unenrolled student should be denied access, got {response.status_code}: {response.data}"
            
            assert 'error' in response.data, \
                "Forbidden response should include error message"
            
            assert 'enrolled' in response.data['error'].lower(), \
                f"Error message should mention enrollment requirement: {response.data['error']}"
            
        finally:
            # Clean up
            Enrollment.objects.filter(course__title=course_title).delete()
            Session.objects.filter(title=session_title).delete()
            Course.objects.filter(title=course_title).delete()
            User.objects.filter(email__in=[instructor_email, student_email, unenrolled_email]).delete()
            User.objects.filter(username__in=[instructor_username, student_username, unenrolled_username]).delete()
    
    # Feature: veetssuites-platform, Property 35: Unenrolled users denied recording access
    @given(
        instructor_username=valid_username(),
        unenrolled_username=valid_username(),
        password=valid_password(),
        instructor_first_name=valid_name(),
        instructor_last_name=valid_name(),
        unenrolled_first_name=valid_name(),
        unenrolled_last_name=valid_name(),
        course_title=valid_course_title(),
        course_description=valid_course_description(),
        course_price=valid_price(),
        course_currency=valid_currency(),
        session_title=valid_session_title(),
        scheduled_at=future_datetime()
    )
    @settings(max_examples=10, deadline=20000, suppress_health_check=[HealthCheck.too_slow])
    def test_unenrolled_users_denied_recording_access(
        self, instructor_username, unenrolled_username, password, instructor_first_name,
        instructor_last_name, unenrolled_first_name, unenrolled_last_name, course_title,
        course_description, course_price, course_currency, session_title, scheduled_at
    ):
        """
        Property 35: Unenrolled users denied recording access
        
        For any user not enrolled in a course, when attempting to access a recording
        from that course, the system should return a 403 error.
        
        Validates: Requirements 8.3
        """
        # Ensure usernames are different
        if instructor_username == unenrolled_username:
            instructor_username = f"{instructor_username}_instructor"
            unenrolled_username = f"{unenrolled_username}_unenrolled"
        
        # Generate unique emails
        instructor_email = f"{instructor_username}@test.com"
        unenrolled_email = f"{unenrolled_username}@test.com"
        
        # Clean up any existing data
        User.objects.filter(email__in=[instructor_email, unenrolled_email]).delete()
        User.objects.filter(username__in=[instructor_username, unenrolled_username]).delete()
        Course.objects.filter(title=course_title).delete()
        Session.objects.filter(title=session_title).delete()
        
        try:
            # Create users
            instructor = User.objects.create_user(
                email=instructor_email,
                username=instructor_username,
                password=password,
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                role='instructor'
            )
            
            unenrolled_user = User.objects.create_user(
                email=unenrolled_email,
                username=unenrolled_username,
                password=password,
                first_name=unenrolled_first_name,
                last_name=unenrolled_last_name,
                role='student'
            )
            
            # Create course
            course = Course.objects.create(
                title=course_title,
                description=course_description,
                instructor=instructor,
                price=course_price,
                currency=course_currency,
                is_published=True
            )
            
            # Create session with recording
            session = Session.objects.create(
                course=course,
                title=session_title,
                scheduled_at=scheduled_at,
                s3_recording_key=f"recordings/course_{course.id}/session_test.mp4"
            )
            
            # Test API client for unenrolled user
            client = APIClient()
            refresh = RefreshToken.for_user(unenrolled_user)
            token = str(refresh.access_token)
            
            # Test the core property: unenrolled users should be denied access
            
            # Test 1: Direct session recording access should be denied
            response = client.get(
                f'/api/hub3660/sessions/{session.id}/recording/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            assert response.status_code == 403, \
                f"Unenrolled user should be denied recording access, got {response.status_code}: {response.data}"
            
            assert 'error' in response.data, \
                "Forbidden response should include error message"
            
            error_message = response.data['error'].lower()
            assert 'enrolled' in error_message or 'enroll' in error_message, \
                f"Error message should mention enrollment requirement: {response.data['error']}"
            
            # Test 2: Course recordings access should be denied
            response = client.get(
                f'/api/hub3660/courses/{course.id}/recordings/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            assert response.status_code == 403, \
                f"Unenrolled user should be denied course recordings access, got {response.status_code}: {response.data}"
            
            assert 'error' in response.data, \
                "Forbidden response should include error message"
            
        finally:
            # Clean up
            Session.objects.filter(title=session_title).delete()
            Course.objects.filter(title=course_title).delete()
            User.objects.filter(email__in=[instructor_email, unenrolled_email]).delete()
            User.objects.filter(username__in=[instructor_username, unenrolled_username]).delete()
    
    # Feature: veetssuites-platform, Property 36: Recording URLs are time-limited
    @given(
        instructor_username=valid_username(),
        student_username=valid_username(),
        password=valid_password(),
        instructor_first_name=valid_name(),
        instructor_last_name=valid_name(),
        student_first_name=valid_name(),
        student_last_name=valid_name(),
        course_title=valid_course_title(),
        course_description=valid_course_description(),
        course_price=valid_price(),
        course_currency=valid_currency(),
        session_title=valid_session_title(),
        scheduled_at=future_datetime()
    )
    @settings(max_examples=10, deadline=20000, suppress_health_check=[HealthCheck.too_slow])
    def test_recording_urls_are_time_limited(
        self, instructor_username, student_username, password, instructor_first_name,
        instructor_last_name, student_first_name, student_last_name, course_title,
        course_description, course_price, course_currency, session_title, scheduled_at
    ):
        """
        Property 36: Recording URLs are time-limited
        
        For any authorized recording access, the generated signed URL should include
        an expiration timestamp set to 24 hours from generation time.
        
        Validates: Requirements 8.4
        """
        # Ensure usernames are different
        if instructor_username == student_username:
            student_username = f"{student_username}_student"
            instructor_username = f"{instructor_username}_instructor"
        
        # Generate unique emails
        instructor_email = f"{instructor_username}@test.com"
        student_email = f"{student_username}@test.com"
        
        # Clean up any existing data
        User.objects.filter(email__in=[instructor_email, student_email]).delete()
        User.objects.filter(username__in=[instructor_username, student_username]).delete()
        Course.objects.filter(title=course_title).delete()
        Session.objects.filter(title=session_title).delete()
        
        try:
            # Create users
            instructor = User.objects.create_user(
                email=instructor_email,
                username=instructor_username,
                password=password,
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                role='instructor'
            )
            
            student = User.objects.create_user(
                email=student_email,
                username=student_username,
                password=password,
                first_name=student_first_name,
                last_name=student_last_name,
                role='student'
            )
            
            # Create course
            course = Course.objects.create(
                title=course_title,
                description=course_description,
                instructor=instructor,
                price=course_price,
                currency=course_currency,
                is_published=True
            )
            
            # Create session with S3 recording
            session = Session.objects.create(
                course=course,
                title=session_title,
                scheduled_at=scheduled_at,
                s3_recording_key=f"recordings/course_{course.id}/session_test.mp4"
            )
            
            # Enroll student
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                payment_status='completed'
            )
            
            # Test API client
            client = APIClient()
            refresh = RefreshToken.for_user(student)
            token = str(refresh.access_token)
            
            # Test the core property: signed URLs should have time limits
            
            # Mock the storage service to test URL generation without actual S3
            mock_signed_url = "https://test-bucket.s3.amazonaws.com/recordings/course_1/session_test.mp4?X-Amz-Expires=86400&X-Amz-Signature=test"
            
            with patch('hub3660.storage.recording_storage.generate_signed_url', return_value=mock_signed_url) as mock_generate:
                response = client.get(
                    f'/api/hub3660/sessions/{session.id}/recording/',
                    HTTP_AUTHORIZATION=f'Bearer {token}'
                )
                
                # Should succeed with mocked storage
                assert response.status_code == 200, \
                    f"Recording access should succeed with mocked storage, got {response.status_code}: {response.data}"
                
                # Verify signed URL generation was called
                mock_generate.assert_called_once_with(
                    session.s3_recording_key,
                    expiration_hours=24
                )
                
                # Verify response includes time limit information
                assert 'expires_in_hours' in response.data, \
                    "Response should include expiration information"
                
                assert response.data['expires_in_hours'] == 24, \
                    f"Response should indicate 24-hour expiration, but shows {response.data['expires_in_hours']}"
                
                assert 'storage_type' in response.data, \
                    "Response should indicate storage type"
                
                assert response.data['storage_type'] == 's3', \
                    f"Response should indicate S3 storage, but shows {response.data['storage_type']}"
                
                assert 'recording_url' in response.data, \
                    "Response should include the signed URL"
                
                assert response.data['recording_url'] == mock_signed_url, \
                    f"Response should include the mocked signed URL"
            
        finally:
            # Clean up
            Enrollment.objects.filter(course__title=course_title).delete()
            Session.objects.filter(title=session_title).delete()
            Course.objects.filter(title=course_title).delete()
            User.objects.filter(email__in=[instructor_email, student_email]).delete()
            User.objects.filter(username__in=[instructor_username, student_username]).delete()