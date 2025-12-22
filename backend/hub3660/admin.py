"""
HUB3660 admin configuration.
"""

from django.contrib import admin
from .models import Course, Enrollment, Session


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model."""
    
    list_display = [
        'title', 'instructor', 'price', 'currency', 
        'is_published', 'enrollment_count', 'created_at'
    ]
    list_filter = ['is_published', 'currency', 'created_at', 'instructor']
    search_fields = ['title', 'description', 'instructor__email', 'instructor__first_name', 'instructor__last_name']
    readonly_fields = ['created_at', 'updated_at', 'enrollment_count']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'enrollment_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('instructor')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment model."""
    
    list_display = [
        'student', 'course', 'payment_status', 
        'payment_id', 'enrolled_at'
    ]
    list_filter = ['payment_status', 'enrolled_at', 'course']
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'course__title', 'payment_id'
    ]
    readonly_fields = ['enrolled_at']
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_id')
        }),
        ('Metadata', {
            'fields': ('enrolled_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('student', 'course')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Session model."""
    
    list_display = [
        'title', 'course', 'scheduled_at', 
        'zoom_meeting_id', 'has_recording', 'created_at'
    ]
    list_filter = ['scheduled_at', 'course', 'created_at']
    search_fields = ['title', 'course__title', 'zoom_meeting_id']
    readonly_fields = ['created_at', 'is_upcoming', 'has_recording']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('title', 'course', 'scheduled_at')
        }),
        ('Zoom Integration', {
            'fields': ('zoom_meeting_id', 'zoom_join_url')
        }),
        ('Recording', {
            'fields': ('recording_url',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'is_upcoming', 'has_recording'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('course')