from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Question, ExamAttempt, ExamAnswer

User = get_user_model()


class QuestionModelTest(TestCase):
    """Test cases for Question model."""
    
    def setUp(self):
        self.question_data = {
            'text': 'What is the primary mechanism of action of aspirin?',
            'option_a': 'COX-1 inhibition',
            'option_b': 'COX-2 inhibition',
            'option_c': 'Both COX-1 and COX-2 inhibition',
            'option_d': 'Prostaglandin synthesis',
            'correct_answer': 'C',
            'category': 'Pharmacology',
            'difficulty': 'medium'
        }
    
    def test_question_creation(self):
        """Test creating a question."""
        question = Question.objects.create(**self.question_data)
        self.assertEqual(question.text, self.question_data['text'])
        self.assertEqual(question.correct_answer, 'C')
        self.assertEqual(question.category, 'Pharmacology')
        self.assertEqual(question.difficulty, 'medium')
    
    def test_question_str_method(self):
        """Test question string representation."""
        question = Question.objects.create(**self.question_data)
        expected_str = f"Pharmacology - {self.question_data['text'][:50]}..."
        self.assertEqual(str(question), expected_str)
    
    def test_get_options_method(self):
        """Test get_options method returns correct dictionary."""
        question = Question.objects.create(**self.question_data)
        options = question.get_options()
        expected_options = {
            'A': self.question_data['option_a'],
            'B': self.question_data['option_b'],
            'C': self.question_data['option_c'],
            'D': self.question_data['option_d'],
        }
        self.assertEqual(options, expected_options)


class ExamAttemptModelTest(TestCase):
    """Test cases for ExamAttempt model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question1 = Question.objects.create(
            text='Test question 1',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            correct_answer='A',
            category='Test',
            difficulty='easy'
        )
        self.question2 = Question.objects.create(
            text='Test question 2',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            correct_answer='B',
            category='Test',
            difficulty='medium'
        )
    
    def test_exam_attempt_creation(self):
        """Test creating an exam attempt."""
        exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=2,
            status='in_progress'
        )
        self.assertEqual(exam_attempt.student, self.user)
        self.assertEqual(exam_attempt.total_questions, 2)
        self.assertEqual(exam_attempt.status, 'in_progress')
        self.assertIsNone(exam_attempt.score)
        self.assertFalse(exam_attempt.is_completed)
    
    def test_exam_attempt_str_method(self):
        """Test exam attempt string representation."""
        exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=2,
            status='in_progress'
        )
        expected_str = f"{self.user.username} - Exam {exam_attempt.id} (in_progress)"
        self.assertEqual(str(exam_attempt), expected_str)
    
    def test_percentage_score_calculation(self):
        """Test percentage score calculation."""
        exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=10,
            score=8,
            status='completed'
        )
        self.assertEqual(exam_attempt.percentage_score, 80.0)
    
    def test_percentage_score_none_when_no_score(self):
        """Test percentage score is None when score is None."""
        exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=10,
            status='in_progress'
        )
        self.assertIsNone(exam_attempt.percentage_score)
    
    def test_calculate_score_method(self):
        """Test calculate_score method."""
        exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=2,
            status='in_progress'
        )
        
        # Create answers - one correct, one incorrect
        ExamAnswer.objects.create(
            attempt=exam_attempt,
            question=self.question1,
            selected_answer='A'  # Correct
        )
        ExamAnswer.objects.create(
            attempt=exam_attempt,
            question=self.question2,
            selected_answer='A'  # Incorrect (correct is B)
        )
        
        score = exam_attempt.calculate_score()
        self.assertEqual(score, 1)
        self.assertEqual(exam_attempt.score, 1)


class ExamAnswerModelTest(TestCase):
    """Test cases for ExamAnswer model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question = Question.objects.create(
            text='Test question',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            correct_answer='B',
            category='Test',
            difficulty='easy'
        )
        self.exam_attempt = ExamAttempt.objects.create(
            student=self.user,
            total_questions=1,
            status='in_progress'
        )
    
    def test_exam_answer_creation_correct(self):
        """Test creating a correct exam answer."""
        exam_answer = ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=self.question,
            selected_answer='B'  # Correct answer
        )
        self.assertEqual(exam_answer.selected_answer, 'B')
        self.assertTrue(exam_answer.is_correct)
    
    def test_exam_answer_creation_incorrect(self):
        """Test creating an incorrect exam answer."""
        exam_answer = ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=self.question,
            selected_answer='A'  # Incorrect answer
        )
        self.assertEqual(exam_answer.selected_answer, 'A')
        self.assertFalse(exam_answer.is_correct)
    
    def test_exam_answer_str_method(self):
        """Test exam answer string representation."""
        exam_answer = ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=self.question,
            selected_answer='B'
        )
        expected_str = f"Answer B for Question {self.question.id}"
        self.assertEqual(str(exam_answer), expected_str)
    
    def test_unique_together_constraint(self):
        """Test that attempt and question combination is unique."""
        # Create first answer
        ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=self.question,
            selected_answer='A'
        )
        
        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(Exception):  # IntegrityError in real DB
            ExamAnswer.objects.create(
                attempt=self.exam_attempt,
                question=self.question,
                selected_answer='B'
            )
    
    def test_automatic_is_correct_setting(self):
        """Test that is_correct is automatically set based on correct answer."""
        # Test correct answer
        correct_answer = ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=self.question,
            selected_answer='B'  # Matches question.correct_answer
        )
        self.assertTrue(correct_answer.is_correct)
        
        # Create another question for incorrect answer test
        question2 = Question.objects.create(
            text='Test question 2',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            correct_answer='C',
            category='Test',
            difficulty='easy'
        )
        
        # Test incorrect answer
        incorrect_answer = ExamAnswer.objects.create(
            attempt=self.exam_attempt,
            question=question2,
            selected_answer='A'  # Does not match question.correct_answer (C)
        )
        self.assertFalse(incorrect_answer.is_correct)