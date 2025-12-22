"""
HUB3660 tests for course management functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Course, Enrollment, Session

User = get_user_model()


class CourseModelTest(TestCase):
    """Test Course model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            username='instructor',
            password='testpass123',
            role='instructor',
            first_name='John',
            last_name='Doe'
        )
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123',
            role='student',
            first_name='Jane',
            last_name='Smith'
        )
    
    def test_course_creation(self):
        """Test creating a course."""
        course = Course.objects.create(
            title='Python Programming',
            description='Learn Python from scratch',
            instructor=self.instructor,
            price=Decimal('99.99'),
            currency='USD',
            is_published=True
        )
        
        self.assertEqual(course.title, 'Python Programming')
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.price, Decimal('99.99'))
        self.assertTrue(course.is_published)
        self.assertEqual(course.enrollment_count, 0)
        self.assertFalse(course.is_free)
    
    def test_free_course(self):
        """Test free course detection."""
        course = Course.objects.create(
            title='Free Course',
            description='A free course',
            instructor=self.instructor,
            price=Decimal('0.00'),
            currency='USD'
        )
        
        self.assertTrue(course.is_free)
    
    def test_enrollment_creation(self):
        """Test creating an enrollment."""
        course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.instructor,
            price=Decimal('50.00'),
            currency='USD'
        )
        
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=course,
            payment_status='pending'
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, course)
        self.assertEqual(enrollment.payment_status, 'pending')
        self.assertFalse(enrollment.is_active)
    
    def test_enrollment_completion(self):
        """Test completing an enrollment."""
        course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.instructor,
            price=Decimal('50.00'),
            currency='USD'
        )
        
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=course,
            payment_status='pending'
        )
        
        enrollment.complete_payment('payment_123')
        
        self.assertEqual(enrollment.payment_status, 'completed')
        self.assertEqual(enrollment.payment_id, 'payment_123')
        self.assertTrue(enrollment.is_active)


class CourseAPITest(APITestCase):
    """Test Course API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            username='instructor',
            password='testpass123',
            role='instructor',
            first_name='John',
            last_name='Doe'
        )
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123',
            role='student',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python from scratch',
            instructor=self.instructor,
            price=Decimal('99.99'),
            currency='USD',
            is_published=True
        )
    
    def test_course_list_public(self):
        """Test public course list endpoint."""
        url = reverse('hub3660:course-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Programming')
    
    def test_course_detail_public(self):
        """Test public course detail endpoint."""
        url = reverse('hub3660:course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['instructor']['full_name'], 'John Doe')
    
    def test_course_creation_instructor(self):
        """Test course creation by instructor."""
        self.client.force_authenticate(user=self.instructor)
        
        url = reverse('hub3660:course-create')
        data = {
            'title': 'Django Web Development',
            'description': 'Build web apps with Django',
            'price': '149.99',
            'currency': 'USD',
            'is_published': True
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        
        new_course = Course.objects.get(title='Django Web Development')
        self.assertEqual(new_course.instructor, self.instructor)
    
    def test_course_creation_student_forbidden(self):
        """Test that students cannot create courses."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('hub3660:course-create')
        data = {
            'title': 'Unauthorized Course',
            'description': 'This should fail',
            'price': '99.99',
            'currency': 'USD'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_enrollment_creation(self):
        """Test course enrollment."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('hub3660:course-enroll', kwargs={'course_id': self.course.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['payment_required'])
        self.assertEqual(Enrollment.objects.count(), 1)
        
        enrollment = Enrollment.objects.first()
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.payment_status, 'pending')
    
    def test_free_course_enrollment(self):
        """Test enrollment in free course."""
        free_course = Course.objects.create(
            title='Free Course',
            description='A free course',
            instructor=self.instructor,
            price=Decimal('0.00'),
            currency='USD',
            is_published=True
        )
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('hub3660:course-enroll', kwargs={'course_id': free_course.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['payment_required'])
        
        enrollment = Enrollment.objects.get(course=free_course)
        self.assertEqual(enrollment.payment_status, 'completed')
    
    def test_duplicate_enrollment_prevention(self):
        """Test that duplicate enrollments are prevented."""
        # Create initial enrollment
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            payment_status='completed'
        )
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('hub3660:course-enroll', kwargs={'course_id': self.course.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already enrolled', response.data['error'])
    
    def test_enrollment_status_check(self):
        """Test enrollment status check endpoint."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            payment_status='completed'
        )
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('hub3660:enrollment-status', kwargs={'course_id': self.course.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_enrolled'])
        self.assertEqual(response.data['enrollment_status'], 'completed')