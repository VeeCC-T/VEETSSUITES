import csv
import json
import random
from django.db import transaction
from django.db.models import Avg, Max, Min, Count, Q
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from accounts.permissions import IsAdmin, IsStudent

from .models import Question, ExamAttempt, ExamAnswer
from .serializers import (
    QuestionSerializer, QuestionWithAnswerSerializer,
    ExamAttemptSerializer, ExamAttemptDetailSerializer, ExamAttemptReviewSerializer,
    ExamAnswerSerializer, StartExamSerializer, SubmitAnswerSerializer,
    CompleteExamSerializer, QuestionImportSerializer, ExamStatsSerializer
)


class QuestionViewSet(ModelViewSet):
    """ViewSet for managing questions."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'import_questions']:
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on user role."""
        if hasattr(self.request.user, 'role') and self.request.user.role == 'admin':
            return QuestionWithAnswerSerializer
        return QuestionSerializer
    
    def get_queryset(self):
        """Filter questions based on query parameters."""
        queryset = Question.objects.all()
        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty')
        
        if category:
            queryset = queryset.filter(category__icontains=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset.order_by('category', 'difficulty', '?')  # Random order for exams
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def import_questions(self, request):
        """Import questions from CSV or JSON file."""
        serializer = QuestionImportSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            
            try:
                if file.name.endswith('.csv'):
                    imported_count = self._import_from_csv(file)
                else:  # JSON
                    imported_count = self._import_from_json(file)
                
                return Response({
                    'message': f'Successfully imported {imported_count} questions.',
                    'imported_count': imported_count
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to import questions: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _import_from_csv(self, file):
        """Import questions from CSV file."""
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        questions = []
        for row in reader:
            question = Question(
                text=row['text'],
                option_a=row['option_a'],
                option_b=row['option_b'],
                option_c=row['option_c'],
                option_d=row['option_d'],
                correct_answer=row['correct_answer'].upper(),
                category=row.get('category', 'General'),
                difficulty=row.get('difficulty', 'medium')
            )
            questions.append(question)
        
        Question.objects.bulk_create(questions)
        return len(questions)
    
    def _import_from_json(self, file):
        """Import questions from JSON file."""
        data = json.load(file)
        
        questions = []
        for item in data:
            question = Question(
                text=item['text'],
                option_a=item['option_a'],
                option_b=item['option_b'],
                option_c=item['option_c'],
                option_d=item['option_d'],
                correct_answer=item['correct_answer'].upper(),
                category=item.get('category', 'General'),
                difficulty=item.get('difficulty', 'medium')
            )
            questions.append(question)
        
        Question.objects.bulk_create(questions)
        return len(questions)


class ExamAttemptViewSet(ModelViewSet):
    """ViewSet for managing exam attempts."""
    serializer_class = ExamAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return user's exam attempts or all for admin."""
        if hasattr(self.request.user, 'role') and self.request.user.role == 'admin':
            return ExamAttempt.objects.all().select_related('student')
        return ExamAttempt.objects.filter(student=self.request.user).select_related('student')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ExamAttemptDetailSerializer
        elif self.action == 'review':
            return ExamAttemptReviewSerializer
        return ExamAttemptSerializer
    
    @action(detail=False, methods=['post'])
    def start_exam(self, request):
        """Start a new exam with randomized questions."""
        serializer = StartExamSerializer(data=request.data)
        if serializer.is_valid():
            # Get filter parameters
            category = serializer.validated_data.get('category')
            difficulty = serializer.validated_data.get('difficulty')
            num_questions = serializer.validated_data.get('num_questions', 20)
            
            # Filter questions
            questions_query = Question.objects.all()
            if category:
                questions_query = questions_query.filter(category__icontains=category)
            if difficulty:
                questions_query = questions_query.filter(difficulty=difficulty)
            
            # Get random questions
            available_questions = list(questions_query)
            if len(available_questions) < num_questions:
                return Response({
                    'error': f'Not enough questions available. Found {len(available_questions)}, requested {num_questions}.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            selected_questions = random.sample(available_questions, num_questions)
            
            # Create exam attempt
            with transaction.atomic():
                exam_attempt = ExamAttempt.objects.create(
                    student=request.user,
                    total_questions=num_questions,
                    status='in_progress'
                )
                
                # Add questions to the attempt (without creating answers yet)
                exam_attempt.questions.set(selected_questions)
            
            # Return exam details with questions (without correct answers)
            serializer = ExamAttemptDetailSerializer(exam_attempt)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit an answer for a question in the exam."""
        exam_attempt = self.get_object()
        
        # Check if exam is still in progress
        if exam_attempt.status != 'in_progress':
            return Response({
                'error': 'Exam is not in progress.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user owns this exam attempt
        if exam_attempt.student != request.user:
            return Response({
                'error': 'You can only submit answers to your own exams.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubmitAnswerSerializer(data=request.data)
        if serializer.is_valid():
            question_id = serializer.validated_data['question_id']
            selected_answer = serializer.validated_data['selected_answer']
            
            try:
                question = Question.objects.get(id=question_id)
                
                # Check if question is part of this exam
                if not exam_attempt.questions.filter(id=question_id).exists():
                    return Response({
                        'error': 'Question is not part of this exam.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get or create answer record
                try:
                    exam_answer = ExamAnswer.objects.get(
                        attempt=exam_attempt,
                        question=question
                    )
                    # Check if this is the first time answering (no selected_answer yet)
                    created = exam_answer.selected_answer is None
                    exam_answer.selected_answer = selected_answer
                    exam_answer.save()
                except ExamAnswer.DoesNotExist:
                    # Create new answer
                    exam_answer = ExamAnswer.objects.create(
                        attempt=exam_attempt,
                        question=question,
                        selected_answer=selected_answer
                    )
                    created = True
                
                # Return immediate feedback
                return Response({
                    'question_id': question_id,
                    'selected_answer': selected_answer,
                    'is_correct': exam_answer.is_correct,
                    'correct_answer': question.correct_answer,
                    'created': created
                }, status=status.HTTP_200_OK)
                
            except Question.DoesNotExist:
                return Response({
                    'error': 'Question not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete_exam(self, request, pk=None):
        """Complete the exam and calculate final score."""
        exam_attempt = self.get_object()
        
        # Check if exam is still in progress
        if exam_attempt.status != 'in_progress':
            return Response({
                'error': 'Exam is not in progress.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user owns this exam attempt
        if exam_attempt.student != request.user:
            return Response({
                'error': 'You can only complete your own exams.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate final score and mark as completed
        with transaction.atomic():
            exam_attempt.calculate_score()
            exam_attempt.status = 'completed'
            exam_attempt.completed_at = timezone.now()
            exam_attempt.save()
        
        # Return detailed results
        serializer = ExamAttemptReviewSerializer(exam_attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def review(self, request, pk=None):
        """Review a completed exam with correct answers."""
        exam_attempt = self.get_object()
        
        # Check if exam is completed
        if exam_attempt.status != 'completed':
            return Response({
                'error': 'Exam must be completed to review.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user owns this exam attempt or is admin
        if (exam_attempt.student != request.user and 
            not (hasattr(request.user, 'role') and request.user.role == 'admin')):
            return Response({
                'error': 'You can only review your own exams.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ExamAttemptReviewSerializer(exam_attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's exam history."""
        attempts = self.get_queryset().filter(status='completed').order_by('-completed_at')
        serializer = ExamAttemptSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def stats(self, request):
        """Get exam statistics (admin only)."""
        stats = ExamAttempt.objects.filter(status='completed').aggregate(
            total_attempts=Count('id'),
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )
        
        # Category breakdown
        category_stats = (ExamAnswer.objects
                         .filter(attempt__status='completed')
                         .values('question__category')
                         .annotate(
                             total=Count('id'),
                             correct=Count('id', filter=Q(is_correct=True))
                         ))
        
        category_breakdown = {
            item['question__category']: {
                'total': item['total'],
                'correct': item['correct'],
                'percentage': round((item['correct'] / item['total']) * 100, 2) if item['total'] > 0 else 0
            }
            for item in category_stats
        }
        
        # Difficulty breakdown
        difficulty_stats = (ExamAnswer.objects
                           .filter(attempt__status='completed')
                           .values('question__difficulty')
                           .annotate(
                               total=Count('id'),
                               correct=Count('id', filter=Q(is_correct=True))
                           ))
        
        difficulty_breakdown = {
            item['question__difficulty']: {
                'total': item['total'],
                'correct': item['correct'],
                'percentage': round((item['correct'] / item['total']) * 100, 2) if item['total'] > 0 else 0
            }
            for item in difficulty_stats
        }
        
        stats.update({
            'completed_attempts': stats['total_attempts'],  # All are completed in this query
            'category_breakdown': category_breakdown,
            'difficulty_breakdown': difficulty_breakdown
        })
        
        serializer = ExamStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)