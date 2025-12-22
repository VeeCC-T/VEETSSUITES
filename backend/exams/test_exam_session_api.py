"""
API tests for exam session logic.
Tests the four main exam session endpoints:
1. Start exam with question randomization
2. Submit answer with validation
3. Complete exam with score calculation
4. Exam history
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Question, ExamAttempt, ExamAnswer

User = get_user_model()


class ExamSessionAPITest(TestCase):
    """Test cases for exam session API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        
        # Create test questions
        self.questions = []
        for i in range(10):
            question = Question.objects.create(
                text=f'Test question {i+1}',
                option_a=f'Option A {i+1}',
                option_b=f'Option B {i+1}',
                option_c=f'Option C {i+1}',
                option_d=f'Option D {i+1}',
                correct_answer='A',  # All correct answers are A for simplicity
                category='Pharmacology',
                difficulty='medium'
            )
            self.questions.append(question)
        
        # Create questions with different categories and difficulties
        Question.objects.create(
            text='Clinical question',
            option_a='Clinical A',
            option_b='Clinical B',
            option_c='Clinical C',
            option_d='Clinical D',
            correct_answer='B',
            category='Clinical Pharmacy',
            difficulty='hard'
        )
        
        Question.objects.create(
            text='Easy question',
            option_a='Easy A',
            option_b='Easy B',
            option_c='Easy C',
            option_d='Easy D',
            correct_answer='C',
            category='Pharmacology',
            difficulty='easy'
        )
    
    def test_start_exam_success(self):
        """Test starting an exam successfully."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('exams:examattempt-start-exam')
        data = {
            'num_questions': 5,
            'category': 'Pharmacology',
            'difficulty': 'medium'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['total_questions'], 5)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['student'], self.student.id)
        
        # Verify exam attempt was created
        exam_attempt = ExamAttempt.objects.get(id=response.data['id'])
        self.assertEqual(exam_attempt.student, self.student)
        self.assertEqual(exam_attempt.total_questions, 5)
        self.assertEqual(exam_attempt.questions.count(), 5)
    
    def test_start_exam_insufficient_questions(self):
        """Test starting exam when not enough questions available."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('exams:examattempt-start-exam')
        data = {
            'num_questions': 50,  # More than available
            'category': 'Pharmacology',
            'difficulty': 'medium'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Not enough questions available', response.data['error'])
    
    def test_start_exam_unauthenticated(self):
        """Test starting exam without authentication."""
        url = reverse('exams:examattempt-start-exam')
        data = {'num_questions': 5}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_submit_answer_success(self):
        """Test submitting an answer successfully."""
        self.client.force_authenticate(user=self.student)
        
        # First start an exam
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=2,
            status='in_progress'
        )
        exam_attempt.questions.set([self.questions[0], self.questions[1]])
        
        # Submit answer
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt.id})
        data = {
            'question_id': self.questions[0].id,
            'selected_answer': 'A'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question_id'], self.questions[0].id)
        self.assertEqual(response.data['selected_answer'], 'A')
        self.assertTrue(response.data['is_correct'])  # Correct answer is A
        self.assertEqual(response.data['correct_answer'], 'A')
        
        # Verify answer was stored
        exam_answer = ExamAnswer.objects.get(
            attempt=exam_attempt,
            question=self.questions[0]
        )
        self.assertEqual(exam_answer.selected_answer, 'A')
        self.assertTrue(exam_answer.is_correct)
    
    def test_submit_answer_incorrect(self):
        """Test submitting an incorrect answer."""
        self.client.force_authenticate(user=self.student)
        
        # Start an exam
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=1,
            status='in_progress'
        )
        exam_attempt.questions.set([self.questions[0]])
        
        # Submit incorrect answer
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt.id})
        data = {
            'question_id': self.questions[0].id,
            'selected_answer': 'B'  # Incorrect, correct is A
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['selected_answer'], 'B')
        self.assertFalse(response.data['is_correct'])
        self.assertEqual(response.data['correct_answer'], 'A')
    
    def test_submit_answer_update_existing(self):
        """Test updating an existing answer."""
        self.client.force_authenticate(user=self.student)
        
        # Start an exam using the API to avoid the through model issue
        start_url = reverse('exams:examattempt-start-exam')
        start_data = {
            'num_questions': 1,
            'category': 'Pharmacology',
            'difficulty': 'medium'
        }
        start_response = self.client.post(start_url, start_data)
        self.assertEqual(start_response.status_code, status.HTTP_201_CREATED)
        
        exam_attempt_id = start_response.data['id']
        exam_attempt = ExamAttempt.objects.get(id=exam_attempt_id)
        
        # Get the first question from the exam
        first_question = exam_attempt.questions.first()
        
        # Submit first answer
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt_id})
        data = {
            'question_id': first_question.id,
            'selected_answer': 'B'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['created'])  # Should be created=True for first answer
        
        # Update answer
        data = {
            'question_id': first_question.id,
            'selected_answer': 'A'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['selected_answer'], 'A')
        self.assertTrue(response.data['is_correct'])
        self.assertFalse(response.data['created'])  # Should be False for update
        
        # Verify only one answer exists
        answers = ExamAnswer.objects.filter(
            attempt=exam_attempt,
            question=first_question
        )
        self.assertEqual(answers.count(), 1)
        self.assertEqual(answers.first().selected_answer, 'A')
    
    def test_submit_answer_exam_not_in_progress(self):
        """Test submitting answer to completed exam."""
        self.client.force_authenticate(user=self.student)
        
        # Create completed exam
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=1,
            status='completed'
        )
        exam_attempt.questions.set([self.questions[0]])
        
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt.id})
        data = {
            'question_id': self.questions[0].id,
            'selected_answer': 'A'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Exam is not in progress', response.data['error'])
    
    def test_submit_answer_wrong_user(self):
        """Test submitting answer to another user's exam."""
        # Create another student
        other_student = User.objects.create_user(
            username='other_student',
            email='other@example.com',
            password='testpass123',
            role='student'
        )
        
        self.client.force_authenticate(user=self.student)
        
        # Create exam for other student
        exam_attempt = ExamAttempt.objects.create(
            student=other_student,
            total_questions=1,
            status='in_progress'
        )
        exam_attempt.questions.set([self.questions[0]])
        
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt.id})
        data = {
            'question_id': self.questions[0].id,
            'selected_answer': 'A'
        }
        
        response = self.client.post(url, data)
        
        # Django REST Framework returns 404 when object is not in user's queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_submit_answer_question_not_in_exam(self):
        """Test submitting answer for question not in exam."""
        self.client.force_authenticate(user=self.student)
        
        # Create exam with only one question
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=1,
            status='in_progress'
        )
        exam_attempt.questions.set([self.questions[0]])
        
        url = reverse('exams:examattempt-submit-answer', kwargs={'pk': exam_attempt.id})
        data = {
            'question_id': self.questions[1].id,  # Different question
            'selected_answer': 'A'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Question is not part of this exam', response.data['error'])
    
    def test_complete_exam_success(self):
        """Test completing an exam successfully."""
        self.client.force_authenticate(user=self.student)
        
        # Create exam with answers
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=3,
            status='in_progress'
        )
        exam_attempt.questions.set([self.questions[0], self.questions[1], self.questions[2]])
        
        # Add some answers (2 correct, 1 incorrect)
        # Get the existing ExamAnswer records and update them
        answer1 = ExamAnswer.objects.get(attempt=exam_attempt, question=self.questions[0])
        answer1.selected_answer = 'A'  # Correct
        answer1.save()
        
        answer2 = ExamAnswer.objects.get(attempt=exam_attempt, question=self.questions[1])
        answer2.selected_answer = 'A'  # Correct
        answer2.save()
        
        answer3 = ExamAnswer.objects.get(attempt=exam_attempt, question=self.questions[2])
        answer3.selected_answer = 'B'  # Incorrect (correct is A)
        answer3.save()
        
        url = reverse('exams:examattempt-complete-exam', kwargs={'pk': exam_attempt.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['score'], 2)
        self.assertEqual(response.data['total_questions'], 3)
        self.assertEqual(response.data['percentage_score'], 66.67)
        self.assertIsNotNone(response.data['completed_at'])
        
        # Verify exam is marked as completed
        exam_attempt.refresh_from_db()
        self.assertEqual(exam_attempt.status, 'completed')
        self.assertEqual(exam_attempt.score, 2)
        self.assertIsNotNone(exam_attempt.completed_at)
    
    def test_complete_exam_already_completed(self):
        """Test completing an already completed exam."""
        self.client.force_authenticate(user=self.student)
        
        # Create completed exam
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=1,
            status='completed'
        )
        
        url = reverse('exams:examattempt-complete-exam', kwargs={'pk': exam_attempt.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Exam is not in progress', response.data['error'])
    
    def test_exam_history_success(self):
        """Test retrieving exam history."""
        self.client.force_authenticate(user=self.student)
        
        # Create completed exams
        exam1 = ExamAttempt.objects.create(
            student=self.student,
            total_questions=5,
            score=4,
            status='completed'
        )
        exam2 = ExamAttempt.objects.create(
            student=self.student,
            total_questions=10,
            score=8,
            status='completed'
        )
        
        # Create in-progress exam (should not appear in history)
        ExamAttempt.objects.create(
            student=self.student,
            total_questions=3,
            status='in_progress'
        )
        
        url = reverse('exams:examattempt-history')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only completed exams
        
        # Verify exam data
        exam_ids = [exam['id'] for exam in response.data]
        self.assertIn(exam1.id, exam_ids)
        self.assertIn(exam2.id, exam_ids)
        
        # Check that exams are ordered by completion date (most recent first)
        self.assertEqual(response.data[0]['id'], exam2.id)  # More recent
        self.assertEqual(response.data[1]['id'], exam1.id)
    
    def test_exam_history_empty(self):
        """Test exam history when no completed exams exist."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('exams:examattempt-history')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_exam_history_only_own_exams(self):
        """Test that exam history only shows user's own exams."""
        # Create another student with exams
        other_student = User.objects.create_user(
            username='other_student',
            email='other@example.com',
            password='testpass123',
            role='student'
        )
        
        ExamAttempt.objects.create(
            student=other_student,
            total_questions=5,
            score=3,
            status='completed'
        )
        
        # Create exam for current student
        ExamAttempt.objects.create(
            student=self.student,
            total_questions=10,
            score=7,
            status='completed'
        )
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('exams:examattempt-history')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own exam
        self.assertEqual(response.data[0]['student'], self.student.id)
    
    def test_exam_review_success(self):
        """Test reviewing a completed exam."""
        self.client.force_authenticate(user=self.student)
        
        # Create completed exam with answers
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=2,
            score=1,
            status='completed'
        )
        exam_attempt.questions.set([self.questions[0], self.questions[1]])
        
        # Add answers
        answer1 = ExamAnswer.objects.get(attempt=exam_attempt, question=self.questions[0])
        answer1.selected_answer = 'A'  # Correct
        answer1.save()
        
        answer2 = ExamAnswer.objects.get(attempt=exam_attempt, question=self.questions[1])
        answer2.selected_answer = 'B'  # Incorrect (correct is A)
        answer2.save()
        
        url = reverse('exams:examattempt-review', kwargs={'pk': exam_attempt.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], exam_attempt.id)
        self.assertEqual(response.data['score'], 1)
        self.assertEqual(len(response.data['exam_answers']), 2)
        
        # Check that correct answers are included in review
        for answer in response.data['exam_answers']:
            self.assertIn('question', answer)
            self.assertIn('correct_answer', answer['question'])
            self.assertIn('is_correct', answer)
    
    def test_exam_review_not_completed(self):
        """Test reviewing an exam that's not completed."""
        self.client.force_authenticate(user=self.student)
        
        # Create in-progress exam
        exam_attempt = ExamAttempt.objects.create(
            student=self.student,
            total_questions=1,
            status='in_progress'
        )
        
        url = reverse('exams:examattempt-review', kwargs={'pk': exam_attempt.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Exam must be completed to review', response.data['error'])