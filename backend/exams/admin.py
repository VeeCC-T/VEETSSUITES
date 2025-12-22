from django.contrib import admin
from django.utils.html import format_html
from .models import Question, ExamAttempt, ExamAnswer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'category', 'difficulty', 'correct_answer', 'created_at']
    list_filter = ['category', 'difficulty', 'created_at']
    search_fields = ['text', 'category']
    ordering = ['category', 'difficulty', '-created_at']
    
    fieldsets = (
        ('Question Content', {
            'fields': ('text', 'category', 'difficulty')
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
    )
    
    def text_preview(self, obj):
        """Show a preview of the question text."""
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Question Text"


class ExamAnswerInline(admin.TabularInline):
    model = ExamAnswer
    extra = 0
    readonly_fields = ['is_correct', 'answered_at']
    fields = ['question', 'selected_answer', 'is_correct', 'answered_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'status', 'score_display', 'total_questions', 'started_at', 'completed_at']
    list_filter = ['status', 'started_at', 'completed_at']
    search_fields = ['student__username', 'student__email']
    readonly_fields = ['started_at', 'percentage_score']
    ordering = ['-started_at']
    inlines = [ExamAnswerInline]
    
    fieldsets = (
        ('Exam Information', {
            'fields': ('student', 'status', 'total_questions')
        }),
        ('Results', {
            'fields': ('score', 'percentage_score')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at')
        }),
    )
    
    def score_display(self, obj):
        """Display score with percentage."""
        if obj.score is not None:
            percentage = obj.percentage_score
            if percentage is not None:
                color = 'green' if percentage >= 70 else 'orange' if percentage >= 50 else 'red'
                return format_html(
                    '<span style="color: {};">{}/{} ({}%)</span>',
                    color, obj.score, obj.total_questions, percentage
                )
            return f"{obj.score}/{obj.total_questions}"
        return "Not completed"
    score_display.short_description = "Score"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt_id', 'student', 'question_preview', 'selected_answer', 'correct_answer', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'selected_answer', 'answered_at']
    search_fields = ['attempt__student__username', 'question__text']
    readonly_fields = ['is_correct', 'answered_at']
    ordering = ['-answered_at']
    
    def attempt_id(self, obj):
        return obj.attempt.id
    attempt_id.short_description = "Attempt ID"
    
    def student(self, obj):
        return obj.attempt.student.username
    student.short_description = "Student"
    
    def question_preview(self, obj):
        """Show a preview of the question text."""
        return obj.question.text[:50] + "..." if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = "Question"
    
    def correct_answer(self, obj):
        return obj.question.correct_answer
    correct_answer.short_description = "Correct Answer"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'question')


# Custom admin actions
@admin.action(description='Mark selected exam attempts as completed')
def mark_completed(modeladmin, request, queryset):
    """Mark selected exam attempts as completed."""
    updated = queryset.update(status='completed')
    modeladmin.message_user(request, f'{updated} exam attempts marked as completed.')


@admin.action(description='Calculate scores for selected attempts')
def calculate_scores(modeladmin, request, queryset):
    """Calculate scores for selected exam attempts."""
    updated = 0
    for attempt in queryset:
        attempt.calculate_score()
        updated += 1
    modeladmin.message_user(request, f'Scores calculated for {updated} exam attempts.')


# Add actions to ExamAttemptAdmin
ExamAttemptAdmin.actions = [mark_completed, calculate_scores]