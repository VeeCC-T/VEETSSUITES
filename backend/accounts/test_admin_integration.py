"""
Integration tests for admin features.

Tests the complete admin workflows including:
- User role promotion
- MCQ import flow  
- Analytics data retrieval

Requirements: 2.2, 4.1
"""

import json
import tempfile
import csv
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from exams.models import Question, ExamAttempt, ExamAnswer
from hub3660.models import Course, Enrollment
from payments.models import Transaction

User = get_user_model()


class AdminUserManagementIntegrationTest(APITestCase):
    """Test complete user role promotion workflow."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test users with different roles
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            first_name='Student',
            last_name='User',
            role='student'
        )
        
        self.instructor_user = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass123',
            first_name='Instructor',
            last_name='User',
            role='instructor'
        )
        
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_role_promotion_complete_flow(self):
        """Test complete user role promotion workflow."""
        # Test 1: List all users (admin can see all users)
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)  # admin, student, instructor
        
        # Verify user data structure
        user_data = response.data['results'][0]
        expected_fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'last_login']
        for field in expected_fields:
            self.assertIn(field, user_data)
        
        # Test 2: Promote student to instructor
        student_id = self.student_user.id
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': student_id})
        promotion_data = {'role': 'instructor'}
        
        response = self.client.patch(url, promotion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'instructor')
        
        # Verify database was updated
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.role, 'instructor')
        
        # Test 3: Promote instructor to admin
        instructor_id = self.instructor_user.id
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': instructor_id})
        promotion_data = {'role': 'admin'}
        
        response = self.client.patch(url, promotion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        
        # Verify database was updated with admin privileges
        self.instructor_user.refresh_from_db()
        self.assertEqual(self.instructor_user.role, 'admin')
        self.assertTrue(self.instructor_user.is_staff)
        self.assertTrue(self.instructor_user.is_superuser)
        
        # Test 4: Demote admin back to student
        promotion_data = {'role': 'student'}
        response = self.client.patch(url, promotion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'student')
        
        # Verify admin privileges were removed
        self.instructor_user.refresh_from_db()
        self.assertEqual(self.instructor_user.role, 'student')
        self.assertFalse(self.instructor_user.is_staff)
        self.assertFalse(self.instructor_user.is_superuser)
        
        # Test 5: Deactivate user
        deactivation_data = {'is_active': False}
        response = self.client.patch(url, deactivation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        
        # Verify database was updated
        self.instructor_user.refresh_from_db()
        self.assertFalse(self.instructor_user.is_active)
        
        # Test 6: Reactivate user
        reactivation_data = {'is_active': True}
        response = self.client.patch(url, reactivation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])
        
        # Verify database was updated
        self.instructor_user.refresh_from_db()
        self.assertTrue(self.instructor_user.is_active)
    
    def test_user_management_filtering_and_search(self):
        """Test user management filtering and search functionality."""
        # Create additional test users
        User.objects.create_user(
            username='pharmacist1',
            email='pharmacist1@example.com',
            password='pass123',
            first_name='Pharmacist',
            last_name='One',
            role='pharmacist'
        )
        
        User.objects.create_user(
            username='inactive_user',
            email='inactive@example.com',
            password='pass123',
            first_name='Inactive',
            last_name='User',
            role='student',
            is_active=False
        )
        
        url = reverse('accounts:admin_users')
        
        # Test role filtering
        response = self.client.get(url, {'role': 'student'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['results']:
            self.assertEqual(user['role'], 'student')
        
        # Test active status filtering
        response = self.client.get(url, {'is_active': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['results']:
            self.assertFalse(user['is_active'])
        
        # Test search functionality
        response = self.client.get(url, {'search': 'pharmacist'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        
        # Test email search
        response = self.client.get(url, {'search': 'student@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'student@example.com')
    
    def test_admin_cannot_deactivate_self(self):
        """Test that admin cannot deactivate their own account."""
        admin_id = self.admin_user.id
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': admin_id})
        deactivation_data = {'is_active': False}
        
        response = self.client.patch(url, deactivation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot deactivate your own account', response.data['detail'])
        
        # Verify admin is still active
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
    
    def test_non_admin_cannot_access_user_management(self):
        """Test that non-admin users cannot access user management endpoints."""
        # Authenticate as student
        refresh = RefreshToken.for_user(self.student_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to access user list
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to update user role
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': self.instructor_user.id})
        response = self.client.patch(url, {'role': 'admin'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminMCQImportIntegrationTest(APITestCase):
    """Test complete MCQ import workflow."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create non-admin user for permission testing
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            first_name='Student',
            last_name='User',
            role='student'
        )
        
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_mcq_import_csv_complete_flow(self):
        """Test complete MCQ import workflow using CSV file."""
        # Create temporary CSV file with test questions
        csv_content = [
            ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'category', 'difficulty'],
            ['What is 2+2?', '3', '4', '5', '6', 'B', 'Mathematics', 'easy'],
            ['What is the capital of France?', 'London', 'Berlin', 'Paris', 'Madrid', 'C', 'Geography', 'medium'],
            ['Which element has symbol O?', 'Gold', 'Oxygen', 'Silver', 'Iron', 'B', 'Chemistry', 'easy'],
            ['What is 10*10?', '50', '100', '200', '1000', 'B', 'Mathematics', 'medium'],
            ['Who wrote Romeo and Juliet?', 'Shakespeare', 'Dickens', 'Austen', 'Tolkien', 'A', 'Literature', 'hard']
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerows(csv_content)
            temp_file_path = temp_file.name
        
        # Test 1: Import questions via API
        url = reverse('exams:question-import-questions')
        
        with open(temp_file_path, 'rb') as csv_file:
            response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('imported_count', response.data)
        self.assertEqual(response.data['imported_count'], 5)  # 5 questions imported
        
        # Test 2: Verify questions were created in database
        questions = Question.objects.all()
        self.assertEqual(questions.count(), 5)
        
        # Test 3: Verify question data integrity
        math_question = Question.objects.get(text='What is 2+2?')
        self.assertEqual(math_question.option_a, '3')
        self.assertEqual(math_question.option_b, '4')
        self.assertEqual(math_question.option_c, '5')
        self.assertEqual(math_question.option_d, '6')
        self.assertEqual(math_question.correct_answer, 'B')
        self.assertEqual(math_question.category, 'Mathematics')
        self.assertEqual(math_question.difficulty, 'easy')
        
        # Test 4: Verify questions can be retrieved
        url = reverse('exams:question-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        
        # Test 5: Verify filtering works
        response = self.client.get(url, {'category': 'Mathematics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 math questions
        
        response = self.client.get(url, {'difficulty': 'easy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 easy questions
        
        # Clean up
        import os
        os.unlink(temp_file_path)
    
    def test_mcq_import_json_complete_flow(self):
        """Test complete MCQ import workflow using JSON file."""
        # Create temporary JSON file with test questions
        json_content = [
            {
                'text': 'What is the largest planet?',
                'option_a': 'Earth',
                'option_b': 'Jupiter',
                'option_c': 'Saturn',
                'option_d': 'Mars',
                'correct_answer': 'B',
                'category': 'Astronomy',
                'difficulty': 'medium'
            },
            {
                'text': 'What is H2O?',
                'option_a': 'Hydrogen',
                'option_b': 'Oxygen',
                'option_c': 'Water',
                'option_d': 'Carbon dioxide',
                'correct_answer': 'C',
                'category': 'Chemistry',
                'difficulty': 'easy'
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(json_content, temp_file)
            temp_file_path = temp_file.name
        
        # Test import
        url = reverse('exams:question-import-questions')
        
        with open(temp_file_path, 'rb') as json_file:
            response = self.client.post(url, {'file': json_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['imported_count'], 2)
        
        # Verify questions were created
        questions = Question.objects.filter(category='Astronomy')
        self.assertEqual(questions.count(), 1)
        
        jupiter_question = questions.first()
        self.assertEqual(jupiter_question.text, 'What is the largest planet?')
        self.assertEqual(jupiter_question.correct_answer, 'B')
        
        # Clean up
        import os
        os.unlink(temp_file_path)
    
    def test_mcq_import_error_handling(self):
        """Test MCQ import error handling."""
        # Test 1: Invalid file format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write('Invalid content')
            temp_file_path = temp_file.name
        
        url = reverse('exams:question-import-questions')
        
        with open(temp_file_path, 'rb') as invalid_file:
            response = self.client.post(url, {'file': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for validation error in file field
        self.assertIn('file', response.data)
        
        # Test 2: Malformed CSV (missing required columns)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(['invalid', 'csv', 'content'])  # Missing required columns
            writer.writerow(['data1', 'data2', 'data3'])
            temp_file_path2 = temp_file.name
        
        with open(temp_file_path2, 'rb') as malformed_file:
            response = self.client.post(url, {'file': malformed_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Clean up
        import os
        os.unlink(temp_file_path)
        os.unlink(temp_file_path2)
    
    def test_non_admin_cannot_import_mcq(self):
        """Test that non-admin users cannot import MCQ."""
        # Authenticate as student
        refresh = RefreshToken.for_user(self.student_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to import questions
        url = reverse('exams:question-import-questions')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write('text,option_a,option_b,option_c,option_d,correct_answer\n')
            temp_file.write('Test question,A,B,C,D,A\n')
            temp_file_path = temp_file.name
        
        with open(temp_file_path, 'rb') as csv_file:
            response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no questions were created
        self.assertEqual(Question.objects.count(), 0)
        
        # Clean up
        import os
        os.unlink(temp_file_path)


class AdminAnalyticsIntegrationTest(APITestCase):
    """Test complete analytics data retrieval workflow."""
    
    def setUp(self):
        """Set up test data with comprehensive analytics scenario."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test users with different roles
        self.students = []
        for i in range(5):
            student = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@example.com',
                password='pass123',
                first_name=f'Student{i}',
                last_name='User',
                role='student'
            )
            self.students.append(student)
        
        self.instructors = []
        for i in range(2):
            instructor = User.objects.create_user(
                username=f'instructor{i}',
                email=f'instructor{i}@example.com',
                password='pass123',
                first_name=f'Instructor{i}',
                last_name='User',
                role='instructor'
            )
            self.instructors.append(instructor)
        
        self.pharmacist = User.objects.create_user(
            username='pharmacist',
            email='pharmacist@example.com',
            password='pass123',
            first_name='Pharmacist',
            last_name='User',
            role='pharmacist'
        )
        
        # Create test courses
        self.courses = []
        for i, instructor in enumerate(self.instructors):
            course = Course.objects.create(
                title=f'Test Course {i+1}',
                description=f'Description for course {i+1}',
                instructor=instructor,
                price=Decimal('99.99'),
                currency='USD',
                is_published=True
            )
            self.courses.append(course)
        
        # Create test enrollments
        for i, student in enumerate(self.students[:3]):  # 3 students enrolled
            Enrollment.objects.create(
                student=student,
                course=self.courses[0],
                payment_status='completed',
                payment_id=f'pay_{i}'
            )
        
        # Create test transactions
        for i, student in enumerate(self.students[:3]):
            Transaction.objects.create(
                user=student,
                amount=Decimal('99.99'),
                currency='USD',
                provider='stripe',
                provider_transaction_id=f'txn_{i}',
                status='completed',
                metadata={'course_id': self.courses[0].id}
            )
        
        # Create test questions and exam attempts
        self.questions = []
        for i in range(10):
            question = Question.objects.create(
                text=f'Test question {i+1}',
                option_a='Option A',
                option_b='Option B',
                option_c='Option C',
                option_d='Option D',
                correct_answer='A',
                category='Test Category' if i < 5 else 'Another Category',
                difficulty='easy' if i < 3 else 'medium' if i < 7 else 'hard'
            )
            self.questions.append(question)
        
        # Create exam attempts
        for i, student in enumerate(self.students[:2]):  # 2 students took exams
            attempt = ExamAttempt.objects.create(
                student=student,
                total_questions=5,
                score=4 if i == 0 else 3,  # Different scores
                status='completed',
                completed_at=timezone.now()
            )
            
            # Add questions to attempt
            for j in range(5):
                ExamAnswer.objects.create(
                    attempt=attempt,
                    question=self.questions[j],
                    selected_answer='A' if j < (4 if i == 0 else 3) else 'B',  # Some correct, some wrong
                    is_correct=j < (4 if i == 0 else 3)
                )
        
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_analytics_data_retrieval_complete_flow(self):
        """Test complete analytics data retrieval workflow."""
        url = reverse('accounts:admin_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test 1: Verify user statistics
        user_stats = response.data['users']
        self.assertEqual(user_stats['total'], 9)  # 5 students + 2 instructors + 1 pharmacist + 1 admin
        self.assertEqual(user_stats['active'], 9)  # All active
        
        # Verify role breakdown
        role_stats = user_stats['by_role']
        self.assertEqual(role_stats['student'], 5)
        self.assertEqual(role_stats['instructor'], 2)
        self.assertEqual(role_stats['pharmacist'], 1)
        self.assertEqual(role_stats['admin'], 1)
        
        # Verify user growth data structure
        self.assertIn('growth', user_stats)
        self.assertIsInstance(user_stats['growth'], list)
        self.assertEqual(len(user_stats['growth']), 30)  # 30 days of data
        
        # Test 2: Verify course statistics
        course_stats = response.data['courses']
        self.assertEqual(course_stats['total'], 2)
        self.assertEqual(course_stats['published'], 2)
        
        # Verify top courses data
        self.assertIn('top_courses', course_stats)
        self.assertIsInstance(course_stats['top_courses'], list)
        if course_stats['top_courses']:
            top_course = course_stats['top_courses'][0]
            expected_fields = ['id', 'title', 'instructor', 'enrollment_count', 'price', 'currency']
            for field in expected_fields:
                self.assertIn(field, top_course)
        
        # Test 3: Verify enrollment statistics
        enrollment_stats = response.data['enrollments']
        self.assertEqual(enrollment_stats['total'], 3)
        self.assertEqual(enrollment_stats['completed'], 3)
        self.assertEqual(enrollment_stats['pending'], 0)
        self.assertEqual(enrollment_stats['failed'], 0)
        
        # Test 4: Verify revenue statistics
        revenue_stats = response.data['revenue']
        self.assertEqual(float(revenue_stats['total']), 299.97)  # 3 * 99.99
        
        # Verify payment provider breakdown
        self.assertIn('by_provider', revenue_stats)
        self.assertIsInstance(revenue_stats['by_provider'], list)
        if revenue_stats['by_provider']:
            provider_data = revenue_stats['by_provider'][0]
            expected_fields = ['provider', 'count', 'revenue']
            for field in expected_fields:
                self.assertIn(field, provider_data)
        
        # Test 5: Verify exam statistics
        exam_stats = response.data['exams']
        self.assertEqual(exam_stats['total_attempts'], 2)
        self.assertEqual(exam_stats['completed'], 2)
    
    def test_analytics_with_no_data(self):
        """Test analytics endpoint with minimal data."""
        # Clear all test data except admin user
        User.objects.exclude(id=self.admin_user.id).delete()
        Course.objects.all().delete()
        Enrollment.objects.all().delete()
        Transaction.objects.all().delete()
        ExamAttempt.objects.all().delete()
        Question.objects.all().delete()
        
        url = reverse('accounts:admin_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify empty state handling
        user_stats = response.data['users']
        self.assertEqual(user_stats['total'], 1)  # Only admin
        self.assertEqual(user_stats['by_role']['admin'], 1)
        
        course_stats = response.data['courses']
        self.assertEqual(course_stats['total'], 0)
        
        enrollment_stats = response.data['enrollments']
        self.assertEqual(enrollment_stats['total'], 0)
        
        revenue_stats = response.data['revenue']
        self.assertEqual(float(revenue_stats['total']), 0.0)
    
    def test_system_health_monitoring(self):
        """Test system health monitoring endpoint."""
        url = reverse('accounts:admin_health')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify health data structure
        health_data = response.data
        expected_fields = ['status', 'timestamp', 'checks']
        for field in expected_fields:
            self.assertIn(field, health_data)
        
        # Verify checks structure
        checks = health_data['checks']
        expected_checks = ['database', 'error_rate', 'external_services']
        for check in expected_checks:
            self.assertIn(check, checks)
            self.assertIn('status', checks[check])
            self.assertIn('message', checks[check])
        
        # Database check should be healthy
        self.assertEqual(checks['database']['status'], 'healthy')
    
    def test_non_admin_cannot_access_analytics(self):
        """Test that non-admin users cannot access analytics endpoints."""
        # Authenticate as student
        refresh = RefreshToken.for_user(self.students[0])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to access analytics
        url = reverse('accounts:admin_analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to access system health
        url = reverse('accounts:admin_health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_analytics_performance_with_large_dataset(self):
        """Test analytics performance with larger dataset."""
        # Create additional test data
        additional_students = []
        for i in range(50):  # Create 50 more students
            student = User.objects.create_user(
                username=f'bulk_student{i}',
                email=f'bulk_student{i}@example.com',
                password='pass123',
                first_name=f'BulkStudent{i}',
                last_name='User',
                role='student'
            )
            additional_students.append(student)
        
        # Create enrollments for some of them
        for i, student in enumerate(additional_students[:25]):
            Enrollment.objects.create(
                student=student,
                course=self.courses[0],
                payment_status='completed',
                payment_id=f'bulk_pay_{i}'
            )
        
        # Test analytics still works efficiently
        url = reverse('accounts:admin_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updated counts
        user_stats = response.data['users']
        self.assertEqual(user_stats['total'], 59)  # Original 9 + 50 new
        
        enrollment_stats = response.data['enrollments']
        self.assertEqual(enrollment_stats['total'], 28)  # Original 3 + 25 new


class AdminIntegrationErrorHandlingTest(APITestCase):
    """Test error handling in admin integration workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_management_error_cases(self):
        """Test error handling in user management."""
        # Test 1: Update non-existent user
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': 99999})
        response = self.client.patch(url, {'role': 'instructor'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found', response.data['detail'])
        
        # Test 2: Invalid role
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            role='student'
        )
        
        url = reverse('accounts:admin_user_detail', kwargs={'user_id': student.id})
        response = self.client.patch(url, {'role': 'invalid_role'}, format='json')
        
        # Should not update role to invalid value
        student.refresh_from_db()
        self.assertEqual(student.role, 'student')  # Unchanged
    
    def test_mcq_import_validation_errors(self):
        """Test MCQ import validation and error handling."""
        url = reverse('exams:question-import-questions')
        
        # Test 1: No file provided
        response = self.client.post(url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test 2: Empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        with open(temp_file_path, 'rb') as empty_file:
            response = self.client.post(url, {'file': empty_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Clean up
        import os
        os.unlink(temp_file_path)
    
    def test_analytics_error_resilience(self):
        """Test analytics endpoint resilience to data inconsistencies."""
        # Create user with missing related data
        User.objects.create_user(
            username='orphan_user',
            email='orphan@example.com',
            password='pass123',
            role='student'
        )
        
        # Analytics should still work
        url = reverse('accounts:admin_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
        self.assertIn('courses', response.data)
        self.assertIn('enrollments', response.data)
        self.assertIn('revenue', response.data)
        self.assertIn('exams', response.data)