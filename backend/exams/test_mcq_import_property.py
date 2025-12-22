"""
Property-based tests for MCQ import functionality.
"""
import json
import csv
import io
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase

from .models import Question

User = get_user_model()


class MCQImportPropertyTest(HypothesisTestCase):
    """Property-based tests for MCQ import functionality."""
    
    def setUp(self):
        """Set up test client and admin user."""
        self.client = APIClient()
        # Use unique email to avoid conflicts with other tests
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.admin_user = User.objects.create_user(
            username=f'admin_{unique_id}',
            email=f'admin_{unique_id}@example.com',
            password='adminpass123',
            role='admin'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_simple_csv_import(self):
        """Simple test to verify CSV import works."""
        # Clear existing questions
        Question.objects.all().delete()
        
        # Create simple test data
        questions = [
            {
                'text': 'What is aspirin used for?',
                'option_a': 'Pain relief',
                'option_b': 'Antibiotics',
                'option_c': 'Antiviral',
                'option_d': 'Antifungal',
                'correct_answer': 'A',
                'category': 'Pharmacology',
                'difficulty': 'easy'
            }
        ]
        
        # Create CSV content
        csv_content = self._create_csv_content(questions)
        csv_file = SimpleUploadedFile(
            "test_questions.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # Import questions via API
        response = self.client.post(
            '/api/pharmxam/questions/import_questions/',
            {'file': csv_file},
            format='multipart'
        )
        
        # Verify successful import
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['imported_count'], len(questions))
        
        # Verify question is stored correctly
        stored_question = Question.objects.first()
        self.assertIsNotNone(stored_question)
        self.assertEqual(stored_question.text, questions[0]['text'])
        self.assertEqual(stored_question.option_a, questions[0]['option_a'])
        self.assertEqual(stored_question.correct_answer, questions[0]['correct_answer'])
    
    # Feature: veetssuites-platform, Property 15: MCQ import parses and stores questions
    @given(st.lists(
        st.fixed_dictionaries({
            'text': st.text(min_size=10, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'option_a': st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'option_b': st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'option_c': st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'option_d': st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'correct_answer': st.sampled_from(['A', 'B', 'C', 'D']),
            'category': st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '),
            'difficulty': st.sampled_from(['easy', 'medium', 'hard'])
        }),
        min_size=1,
        max_size=5  # Keep small for testing
    ))
    @settings(max_examples=100, deadline=None)
    def test_csv_import_parses_and_stores_questions(self, questions):
        """
        Property: For any valid CSV dataset, when imported by an admin, 
        all questions should be parsed and stored with their options and correct answers intact.
        Validates: Requirements 4.1
        """
        # Create fresh client and authenticate for this test iteration
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        
        # Clear existing questions to ensure clean test
        Question.objects.all().delete()
        
        # Create CSV content
        csv_content = self._create_csv_content(questions)
        csv_file = SimpleUploadedFile(
            "test_questions.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # Import questions via API
        response = client.post(
            '/api/pharmxam/questions/import_questions/',
            {'file': csv_file},
            format='multipart'
        )
        
        # Verify successful import
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['imported_count'], len(questions))
        
        # Verify all questions are stored correctly
        stored_questions = Question.objects.all()
        self.assertEqual(stored_questions.count(), len(questions))
        
        # Verify each question's data integrity
        # Since questions might have duplicate texts, we need to match more precisely
        stored_questions_list = list(stored_questions)
        
        for original_question in questions:
            # Find a matching question that hasn't been matched yet
            matching_question = None
            for stored_q in stored_questions_list:
                if (stored_q.text == original_question['text'] and
                    stored_q.option_a == original_question['option_a'] and
                    stored_q.option_b == original_question['option_b'] and
                    stored_q.option_c == original_question['option_c'] and
                    stored_q.option_d == original_question['option_d'] and
                    stored_q.correct_answer == original_question['correct_answer'] and
                    stored_q.category == original_question['category'] and
                    stored_q.difficulty == original_question['difficulty']):
                    matching_question = stored_q
                    stored_questions_list.remove(stored_q)  # Remove to avoid double matching
                    break
            
            self.assertIsNotNone(matching_question, 
                f"Question with data '{original_question}' not found in database")
            
            # All fields should match (already verified in the search above)
            self.assertEqual(matching_question.text, original_question['text'])
            self.assertEqual(matching_question.option_a, original_question['option_a'])
            self.assertEqual(matching_question.option_b, original_question['option_b'])
            self.assertEqual(matching_question.option_c, original_question['option_c'])
            self.assertEqual(matching_question.option_d, original_question['option_d'])
            self.assertEqual(matching_question.correct_answer, original_question['correct_answer'])
            self.assertEqual(matching_question.category, original_question['category'])
            self.assertEqual(matching_question.difficulty, original_question['difficulty'])
    
    def _create_csv_content(self, questions):
        """Create CSV content from questions list."""
        output = io.StringIO()
        fieldnames = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 
                     'correct_answer', 'category', 'difficulty']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)
        return output.getvalue()