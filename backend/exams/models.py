from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Question(models.Model):
    """
    Model representing a multiple-choice question for pharmacy exams.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    
    text = models.TextField(help_text="The question text")
    option_a = models.CharField(max_length=500, help_text="Option A text")
    option_b = models.CharField(max_length=500, help_text="Option B text")
    option_c = models.CharField(max_length=500, help_text="Option C text")
    option_d = models.CharField(max_length=500, help_text="Option D text")
    correct_answer = models.CharField(
        max_length=1, 
        choices=ANSWER_CHOICES,
        help_text="The correct answer option"
    )
    category = models.CharField(
        max_length=100, 
        help_text="Question category (e.g., Pharmacology, Clinical Pharmacy)"
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        help_text="Question difficulty level"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'difficulty', 'created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"{self.category} - {self.text[:50]}..."
    
    def get_options(self):
        """Return all options as a dictionary."""
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }


class ExamAttempt(models.Model):
    """
    Model representing a student's attempt at taking an exam.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='exam_attempts',
        help_text="The student taking the exam"
    )
    questions = models.ManyToManyField(
        Question,
        through='ExamAnswer',
        help_text="Questions included in this exam attempt"
    )
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Number of correct answers"
    )
    total_questions = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of questions in the exam"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        help_text="Current status of the exam attempt"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['student', '-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - Exam {self.id} ({self.status})"
    
    @property
    def percentage_score(self):
        """Calculate percentage score."""
        if self.score is not None and self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 2)
        return None
    
    @property
    def is_completed(self):
        """Check if exam is completed."""
        return self.status == 'completed'
    
    def calculate_score(self):
        """Calculate and update the score based on correct answers."""
        correct_answers = self.exam_answers.filter(is_correct=True).count()
        self.score = correct_answers
        self.save(update_fields=['score'])
        return self.score


class ExamAnswer(models.Model):
    """
    Model representing a student's answer to a specific question in an exam attempt.
    This is the through model for the many-to-many relationship between ExamAttempt and Question.
    """
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='exam_answers',
        help_text="The exam attempt this answer belongs to"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='exam_answers',
        help_text="The question being answered"
    )
    selected_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        null=True,
        blank=True,
        help_text="The answer option selected by the student"
    )
    is_correct = models.BooleanField(
        default=False,
        help_text="Whether the selected answer is correct"
    )
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
        ordering = ['answered_at']
        indexes = [
            models.Index(fields=['attempt', 'question']),
            models.Index(fields=['is_correct']),
        ]
    
    def __str__(self):
        return f"Answer {self.selected_answer} for Question {self.question.id}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set is_correct based on the question's correct answer."""
        if self.selected_answer:
            self.is_correct = self.selected_answer == self.question.correct_answer
        else:
            self.is_correct = False
        super().save(*args, **kwargs)