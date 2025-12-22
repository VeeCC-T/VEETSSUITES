"""
Property-based tests for exam functionality.
"""
import random
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.core.management import call_command

from .models import Question, ExamAttempt, ExamAnswer

User = get_user_model()


class ExamFunctionalityPropertyTest(HypothesisTestCase):
    """Property-based tests for exam functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests."""
        super().setUpClass()
        # Load sample questions once for all tests
        call_command('load_sample_questions')
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
    
    def test_simple_exam_start(self):
        """Simple test to verify exam start works."""
        # Create user for this test
        student_user = User.objects.create_user(
            username='student_simple',
            email='student_simple@example.com',
            password='studentpass123',
            role='student'
        )
        
        client = APIClient()
        client.force_authenticate(user=student_user)
        
        response = client.post('/api/pharmxam/attempts/start_exam/', {
            'num_questions': 5
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['total_questions'], 5)

    # Feature: veetssuites-platform, Property 16: Exam questions are randomized
    @given(
        num_questions=st.integers(min_value=5, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_exam_questions_are_randomized(self, num_questions):
        """
        Property: For any exam with multiple questions, when started by different students 
        or at different times, the question order should vary (not always the same sequence).
        Validates: Requirements 4.2
        """
        # Create user for this test iteration
        student_user = User.objects.create_user(
            username=f'student_rand_{random.randint(1000, 9999)}',
            email=f'student_rand_{random.randint(1000, 9999)}@example.com',
            password='studentpass123',
            role='student'
        )
        
        client = APIClient()
        client.force_authenticate(user=student_user)
        
        # Ensure we have enough questions - reload if needed
        total_questions = Question.objects.count()
        if total_questions < num_questions:
            call_command('load_sample_questions')
            total_questions = Question.objects.count()
            if total_questions < num_questions:
                self.skipTest(f"Not enough questions in database. Need {num_questions}, have {total_questions}")
        
        # Start multiple exams and collect question orders
        question_orders = []
        for i in range(5):  # Start 5 exams to check randomization
            response = client.post('/api/pharmxam/attempts/start_exam/', {
                'num_questions': num_questions
            })
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Extract question IDs in order
            exam_questions = response.data['exam_answers']
            question_ids = [answer['question']['id'] for answer in exam_questions]
            question_orders.append(tuple(question_ids))
            
            # Clean up the exam attempt for next iteration
            ExamAttempt.objects.filter(id=response.data['id']).delete()
        
        # Check that not all orders are identical (randomization working)
        unique_orders = set(question_orders)
        
        # With proper randomization, we should have some variation
        # Allow for small chance of identical orders with small question sets
        if num_questions >= 5:
            self.assertGreater(len(unique_orders), 1, 
                "Question orders should vary between exam attempts (randomization not working)")
    
    # Feature: veetssuites-platform, Property 17: Answer submission provides immediate feedback
    @given(
        selected_answer=st.sampled_from(['A', 'B', 'C', 'D'])
    )
    @settings(max_examples=100, deadline=None)
    def test_answer_submission_provides_immediate_feedback(self, selected_answer):
        """
        Property: For any answer submitted during an exam, the system should immediately 
        validate it against the correct answer and return feedback indicating correctness.
        Validates: Requirements 4.3
        """
        # Create user for this test iteration
        student_user = User.objects.create_user(
            username=f'student_feedback_{random.randint(1000, 9999)}',
            email=f'student_feedback_{random.randint(1000, 9999)}@example.com',
            password='studentpass123',
            role='student'
        )
        
        client = APIClient()
        client.force_authenticate(user=student_user)
        
        # Ensure we have questions
        if Question.objects.count() < 5:
            call_command('load_sample_questions')
        
        # Start an exam
        response = client.post('/api/pharmxam/attempts/start_exam/', {
            'num_questions': 5
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        exam_id = response.data['id']
        first_question = response.data['exam_answers'][0]['question']
        question_id = first_question['id']
        correct_answer = Question.objects.get(id=question_id).correct_answer
        
        # Submit answer
        response = client.post(f'/api/pharmxam/attempts/{exam_id}/submit_answer/', {
            'question_id': question_id,
            'selected_answer': selected_answer
        })
        
        # Verify immediate feedback is provided
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_correct', response.data)
        self.assertIn('correct_answer', response.data)
        self.assertIn('selected_answer', response.data)
        
        # Verify correctness is calculated properly
        expected_correctness = (selected_answer == correct_answer)
        self.assertEqual(response.data['is_correct'], expected_correctness)
        self.assertEqual(response.data['correct_answer'], correct_answer)
        self.assertEqual(response.data['selected_answer'], selected_answer)
    
    # Feature: veetssuites-platform, Property 18: Exam completion calculates accurate scores
    @given(
        answers=st.lists(
            st.sampled_from(['A', 'B', 'C', 'D']),
            min_size=5,
            max_size=10
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_exam_completion_calculates_accurate_scores(self, answers):
        """
        Property: For any completed exam, the displayed score should equal the count of 
        correct answers divided by total questions, and the performance breakdown should 
        accurately categorize questions by correctness.
        Validates: Requirements 4.4
        """
        # Create user for this test iteration
        student_user = User.objects.create_user(
            username=f'student_score_{random.randint(1000, 9999)}',
            email=f'student_score_{random.randint(1000, 9999)}@example.com',
            password='studentpass123',
            role='student'
        )
        
        client = APIClient()
        client.force_authenticate(user=student_user)
        
        num_questions = len(answers)
        
        # Ensure we have enough questions
        if Question.objects.count() < num_questions:
            call_command('load_sample_questions')
        
        # Start exam
        response = client.post('/api/pharmxam/attempts/start_exam/', {
            'num_questions': num_questions
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        exam_id = response.data['id']
        exam_questions = response.data['exam_answers']
        
        # Submit all answers and track expected correct count
        expected_correct_count = 0
        for i, selected_answer in enumerate(answers):
            question_data = exam_questions[i]['question']
            question_id = question_data['id']
            correct_answer = Question.objects.get(id=question_id).correct_answer
            
            if selected_answer == correct_answer:
                expected_correct_count += 1
            
            # Submit answer
            response = client.post(f'/api/pharmxam/attempts/{exam_id}/submit_answer/', {
                'question_id': question_id,
                'selected_answer': selected_answer
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Complete exam
        response = client.post(f'/api/pharmxam/attempts/{exam_id}/complete_exam/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify score calculation
        self.assertEqual(response.data['score'], expected_correct_count)
        self.assertEqual(response.data['total_questions'], num_questions)
        
        expected_percentage = round((expected_correct_count / num_questions) * 100, 2)
        self.assertEqual(response.data['percentage_score'], expected_percentage)
        
        # Verify performance breakdown in exam answers
        exam_answers = response.data['exam_answers']
        actual_correct_count = sum(1 for answer in exam_answers if answer['is_correct'])
        self.assertEqual(actual_correct_count, expected_correct_count)
    
    # Feature: veetssuites-platform, Property 19: Exam history shows marked answers
    @given(
        answers=st.lists(
            st.sampled_from(['A', 'B', 'C', 'D']),
            min_size=3,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_exam_history_shows_marked_answers(self, answers):
        """
        Property: For any past exam attempt, when reviewed, each question should display 
        the student's selected answer and the correct answer, with visual indicators 
        for correct/incorrect.
        Validates: Requirements 4.5
        """
        # Create user for this test iteration
        student_user = User.objects.create_user(
            username=f'student_history_{random.randint(1000, 9999)}',
            email=f'student_history_{random.randint(1000, 9999)}@example.com',
            password='studentpass123',
            role='student'
        )
        
        client = APIClient()
        client.force_authenticate(user=student_user)
        
        num_questions = len(answers)
        
        # Ensure we have enough questions
        if Question.objects.count() < num_questions:
            call_command('load_sample_questions')
        
        # Start and complete an exam
        response = client.post('/api/pharmxam/attempts/start_exam/', {
            'num_questions': num_questions
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        exam_id = response.data['id']
        exam_questions = response.data['exam_answers']
        
        # Track expected results for verification
        expected_results = []
        
        # Submit all answers
        for i, selected_answer in enumerate(answers):
            question_data = exam_questions[i]['question']
            question_id = question_data['id']
            correct_answer = Question.objects.get(id=question_id).correct_answer
            
            expected_results.append({
                'question_id': question_id,
                'selected_answer': selected_answer,
                'correct_answer': correct_answer,
                'is_correct': selected_answer == correct_answer
            })
            
            # Submit answer
            client.post(f'/api/pharmxam/attempts/{exam_id}/submit_answer/', {
                'question_id': question_id,
                'selected_answer': selected_answer
            })
        
        # Complete exam
        client.post(f'/api/pharmxam/attempts/{exam_id}/complete_exam/')
        
        # Review exam (check history)
        response = client.get(f'/api/pharmxam/attempts/{exam_id}/review/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all answers are shown with correct markings
        review_answers = response.data['exam_answers']
        self.assertEqual(len(review_answers), num_questions)
        
        for i, review_answer in enumerate(review_answers):
            expected = expected_results[i]
            
            # Verify question details are present
            self.assertEqual(review_answer['question']['id'], expected['question_id'])
            
            # Verify selected answer is preserved
            self.assertEqual(review_answer['selected_answer'], expected['selected_answer'])
            
            # Verify correct answer is shown
            self.assertEqual(review_answer['question']['correct_answer'], expected['correct_answer'])
            
            # Verify correctness marking
            self.assertEqual(review_answer['is_correct'], expected['is_correct'])
        
        # Also test history endpoint
        response = client.get('/api/pharmxam/attempts/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should find our completed exam in history
        history_exams = response.data
        completed_exam = next((exam for exam in history_exams if exam['id'] == exam_id), None)
        self.assertIsNotNone(completed_exam, "Completed exam should appear in history")
        self.assertEqual(completed_exam['status'], 'completed')