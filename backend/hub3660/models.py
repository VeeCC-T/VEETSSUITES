"""
HUB3660 course management models.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Course(models.Model):
    """
    Course model for HUB3660 technology education platform.
    
    Represents a course that can be created by instructors and enrolled in by students.
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Course title"
    )
    description = models.TextField(
        help_text="Detailed course description"
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text="Instructor who created this course"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Course price"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code (USD, NGN, etc.)"
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Whether the course is published and visible to students"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the course was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the course was last updated"
    )
    
    class Meta:
        db_table = 'hub3660_courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor']),
            models.Index(fields=['is_published']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.instructor.get_full_name()}"
    
    @property
    def enrollment_count(self):
        """Get the number of completed enrollments for this course."""
        return self.enrollments.filter(payment_status='completed').count()
    
    @property
    def is_free(self):
        """Check if the course is free."""
        return self.price == 0


class Enrollment(models.Model):
    """
    Enrollment model representing a student's enrollment in a course.
    
    Links students to courses and tracks payment status.
    """
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Student enrolled in the course"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Course the student is enrolled in"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status for this enrollment"
    )
    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Payment provider transaction ID"
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the enrollment was created"
    )
    
    class Meta:
        db_table = 'hub3660_enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['enrolled_at']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} enrolled in {self.course.title}"
    
    @property
    def is_active(self):
        """Check if the enrollment is active (payment completed)."""
        return self.payment_status == 'completed'
    
    def complete_payment(self, payment_id):
        """Mark the enrollment as completed with payment ID."""
        self.payment_status = 'completed'
        self.payment_id = payment_id
        self.save(update_fields=['payment_status', 'payment_id'])
    
    def fail_payment(self):
        """Mark the enrollment payment as failed."""
        self.payment_status = 'failed'
        self.save(update_fields=['payment_status'])


class Session(models.Model):
    """
    Session model for live Zoom sessions within a course.
    """
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Course this session belongs to"
    )
    title = models.CharField(
        max_length=200,
        help_text="Session title"
    )
    scheduled_at = models.DateTimeField(
        help_text="When the session is scheduled to start"
    )
    zoom_meeting_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Zoom meeting ID"
    )
    zoom_join_url = models.URLField(
        blank=True,
        null=True,
        help_text="Zoom meeting join URL"
    )
    recording_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to session recording (deprecated - use s3_recording_key)"
    )
    s3_recording_key = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="S3 object key for the session recording"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session was created"
    )
    
    class Meta:
        db_table = 'hub3660_sessions'
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    @property
    def is_upcoming(self):
        """Check if the session is scheduled in the future."""
        from django.utils import timezone
        return self.scheduled_at > timezone.now()
    
    @property
    def has_recording(self):
        """Check if the session has a recording available."""
        return bool(self.s3_recording_key or self.recording_url)