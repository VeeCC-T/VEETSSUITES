from rest_framework import serializers
from .models import Question, ExamAttempt, ExamAnswer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'text', 'options', 'category', 'difficulty', 'created_at'
        ]
        # Don't expose correct_answer in regular serialization for security
    
    def get_options(self, obj):
        """Return options as a dictionary."""
        return obj.get_options()


class QuestionWithAnswerSerializer(QuestionSerializer):
    """Serializer for Question model that includes the correct answer (for admin/results)."""
    
    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['correct_answer']


class ExamAnswerSerializer(serializers.ModelSerializer):
    """Serializer for ExamAnswer model."""
    question = QuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExamAnswer
        fields = [
            'id', 'question', 'question_id', 'selected_answer', 
            'is_correct', 'answered_at'
        ]
        read_only_fields = ['is_correct', 'answered_at']


class ExamAnswerWithCorrectAnswerSerializer(ExamAnswerSerializer):
    """Serializer for ExamAnswer that includes correct answer (for review)."""
    question = QuestionWithAnswerSerializer(read_only=True)


class ExamAttemptSerializer(serializers.ModelSerializer):
    """Serializer for ExamAttempt model."""
    student_username = serializers.CharField(source='student.username', read_only=True)
    percentage_score = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = ExamAttempt
        fields = [
            'id', 'student', 'student_username', 'score', 'total_questions',
            'percentage_score', 'status', 'is_completed', 'started_at', 'completed_at'
        ]
        read_only_fields = ['student', 'started_at']


class ExamAttemptDetailSerializer(ExamAttemptSerializer):
    """Detailed serializer for ExamAttempt with answers."""
    exam_answers = ExamAnswerSerializer(many=True, read_only=True)
    
    class Meta(ExamAttemptSerializer.Meta):
        fields = ExamAttemptSerializer.Meta.fields + ['exam_answers']


class ExamAttemptReviewSerializer(ExamAttemptSerializer):
    """Serializer for reviewing completed exams with correct answers."""
    exam_answers = ExamAnswerWithCorrectAnswerSerializer(many=True, read_only=True)
    
    class Meta(ExamAttemptSerializer.Meta):
        fields = ExamAttemptSerializer.Meta.fields + ['exam_answers']


class StartExamSerializer(serializers.Serializer):
    """Serializer for starting a new exam."""
    category = serializers.CharField(required=False, help_text="Filter questions by category")
    difficulty = serializers.ChoiceField(
        choices=Question.DIFFICULTY_CHOICES,
        required=False,
        help_text="Filter questions by difficulty"
    )
    num_questions = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=20,
        help_text="Number of questions for the exam"
    )


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer to a question."""
    question_id = serializers.IntegerField()
    selected_answer = serializers.ChoiceField(choices=ExamAnswer.ANSWER_CHOICES)
    
    def validate_question_id(self, value):
        """Validate that the question exists."""
        try:
            Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question does not exist.")
        return value


class CompleteExamSerializer(serializers.Serializer):
    """Serializer for completing an exam."""
    pass  # No additional fields needed, just triggers completion


class QuestionImportSerializer(serializers.Serializer):
    """Serializer for importing questions from CSV/JSON."""
    file = serializers.FileField(help_text="CSV or JSON file containing questions")
    
    def validate_file(self, value):
        """Validate file type and size."""
        if not value.name.endswith(('.csv', '.json')):
            raise serializers.ValidationError("File must be CSV or JSON format.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value


class ExamStatsSerializer(serializers.Serializer):
    """Serializer for exam statistics."""
    total_attempts = serializers.IntegerField()
    completed_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    highest_score = serializers.IntegerField()
    lowest_score = serializers.IntegerField()
    category_breakdown = serializers.DictField()
    difficulty_breakdown = serializers.DictField()