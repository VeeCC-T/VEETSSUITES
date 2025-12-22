"""
Celery tasks for async processing and performance optimization.
"""

from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .caching import CachingService, CacheWarmer
from .performance import AsyncTaskOptimizer
import logging
import time

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def warm_cache_task(self):
    """
    Async task to warm up application caches.
    """
    try:
        logger.info("Starting cache warm-up task")
        CachingService.warm_cache()
        logger.info("Cache warm-up task completed successfully")
        return "Cache warmed successfully"
    except Exception as e:
        logger.error(f"Cache warm-up task failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_cv_upload(self, portfolio_id):
    """
    Async task to process CV upload and extract content.
    """
    try:
        from portfolios.models import Portfolio
        from portfolios.services import CVParsingService
        
        logger.info(f"Processing CV upload for portfolio {portfolio_id}")
        
        portfolio = Portfolio.objects.get(id=portfolio_id)
        
        # Extract CV content
        parsing_service = CVParsingService()
        extracted_content = parsing_service.extract_cv_content(portfolio.cv_file)
        
        # Update portfolio with extracted content
        portfolio.parsed_content = extracted_content
        portfolio.save()
        
        # Invalidate cache
        from .caching import CacheInvalidator
        CacheInvalidator.invalidate_for_model('Portfolio', portfolio.user_id)
        
        logger.info(f"CV processing completed for portfolio {portfolio_id}")
        return f"CV processed successfully for portfolio {portfolio_id}"
        
    except Exception as e:
        logger.error(f"CV processing failed for portfolio {portfolio_id}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, user_email, subject, message, template_name=None):
    """
    Async task to send notification emails.
    """
    try:
        logger.info(f"Sending notification email to {user_email}")
        
        if template_name:
            # Use HTML template if provided
            from django.template.loader import render_to_string
            html_message = render_to_string(template_name, {'message': message})
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False
            )
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False
            )
        
        logger.info(f"Notification email sent successfully to {user_email}")
        return f"Email sent to {user_email}"
        
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_exam_results(self, exam_attempt_id):
    """
    Async task to process exam results and generate analytics.
    """
    try:
        from exams.models import ExamAttempt
        from exams.services import ExamAnalyticsService
        
        logger.info(f"Processing exam results for attempt {exam_attempt_id}")
        
        exam_attempt = ExamAttempt.objects.get(id=exam_attempt_id)
        
        # Generate analytics
        analytics_service = ExamAnalyticsService()
        analytics_data = analytics_service.generate_analytics(exam_attempt)
        
        # Store analytics in cache for quick access
        cache_key = f"exam:analytics:{exam_attempt_id}"
        cache.set(cache_key, analytics_data, 3600)  # Cache for 1 hour
        
        logger.info(f"Exam results processed for attempt {exam_attempt_id}")
        return f"Exam results processed for attempt {exam_attempt_id}"
        
    except Exception as e:
        logger.error(f"Failed to process exam results for attempt {exam_attempt_id}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_zoom_recording(self, session_id, recording_url):
    """
    Async task to process Zoom recording and store in S3.
    """
    try:
        from hub3660.models import Session
        from hub3660.storage import RecordingStorageService
        
        logger.info(f"Processing Zoom recording for session {session_id}")
        
        session = Session.objects.get(id=session_id)
        
        # Download and store recording
        storage_service = RecordingStorageService()
        stored_url = storage_service.store_recording(recording_url, session)
        
        # Update session with recording URL
        session.recording_url = stored_url
        session.save()
        
        # Invalidate related cache
        from .caching import CacheInvalidator
        CacheInvalidator.invalidate_for_model('Session', session_id)
        
        logger.info(f"Zoom recording processed for session {session_id}")
        return f"Recording processed for session {session_id}"
        
    except Exception as e:
        logger.error(f"Failed to process recording for session {session_id}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_expired_tokens(self):
    """
    Async task to cleanup expired JWT tokens.
    """
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        from django.utils import timezone
        from datetime import timedelta
        
        logger.info("Starting expired token cleanup")
        
        # Delete tokens older than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count = OutstandingToken.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} expired tokens")
        return f"Cleaned up {deleted_count} expired tokens"
        
    except Exception as e:
        logger.error(f"Token cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def generate_analytics_report(self, report_type, date_range=None):
    """
    Async task to generate analytics reports.
    """
    try:
        logger.info(f"Generating {report_type} analytics report")
        
        if report_type == 'user_engagement':
            from accounts.models import User
            from django.db.models import Count
            
            # Generate user engagement analytics
            user_stats = User.objects.aggregate(
                total_users=Count('id'),
                active_users=Count('id', filter={'is_active': True}),
                students=Count('id', filter={'role': 'student'}),
                instructors=Count('id', filter={'role': 'instructor'}),
                admins=Count('id', filter={'role': 'admin'})
            )
            
            # Cache the report
            cache_key = f"analytics:user_engagement:{date_range or 'all_time'}"
            cache.set(cache_key, user_stats, 3600)
            
        elif report_type == 'course_performance':
            from hub3660.models import Course, Enrollment
            from django.db.models import Count, Avg
            
            # Generate course performance analytics
            course_stats = Course.objects.annotate(
                enrollment_count=Count('enrollments'),
                avg_rating=Avg('enrollments__rating')
            ).values('id', 'title', 'enrollment_count', 'avg_rating')
            
            # Cache the report
            cache_key = f"analytics:course_performance:{date_range or 'all_time'}"
            cache.set(cache_key, list(course_stats), 3600)
        
        logger.info(f"{report_type} analytics report generated successfully")
        return f"{report_type} report generated"
        
    except Exception as e:
        logger.error(f"Analytics report generation failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def batch_process_mcq_import(self, question_data_list):
    """
    Async task to batch process MCQ imports.
    """
    try:
        from exams.models import Question
        
        logger.info(f"Batch processing {len(question_data_list)} MCQ questions")
        
        # Process questions in batches
        batch_size = 100
        created_count = 0
        
        for batch in AsyncTaskOptimizer.batch_process(question_data_list, batch_size):
            questions_to_create = []
            
            for question_data in batch:
                question = Question(
                    text=question_data['text'],
                    option_a=question_data['option_a'],
                    option_b=question_data['option_b'],
                    option_c=question_data['option_c'],
                    option_d=question_data['option_d'],
                    correct_answer=question_data['correct_answer'],
                    explanation=question_data.get('explanation', ''),
                    category=question_data.get('category', 'general')
                )
                questions_to_create.append(question)
            
            # Bulk create for better performance
            Question.objects.bulk_create(questions_to_create)
            created_count += len(questions_to_create)
        
        # Invalidate exam questions cache
        from .caching import CacheInvalidator
        CacheInvalidator.invalidate_for_model('Question')
        
        logger.info(f"Successfully imported {created_count} MCQ questions")
        return f"Imported {created_count} questions"
        
    except Exception as e:
        logger.error(f"MCQ import failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def optimize_database_task(self):
    """
    Async task to run database optimization.
    """
    try:
        from .performance import DatabaseOptimizer
        
        logger.info("Starting database optimization task")
        
        # Create performance indexes
        DatabaseOptimizer.create_indexes()
        
        # Analyze slow queries
        slow_queries = DatabaseOptimizer.analyze_slow_queries()
        
        if slow_queries:
            logger.warning(f"Found {len(slow_queries)} slow queries")
            # Could send alert email to admins here
        
        logger.info("Database optimization task completed")
        return f"Database optimized, {len(slow_queries)} slow queries found"
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


# Periodic tasks (would be configured in Celery beat)
@shared_task
def daily_cache_warmup():
    """Daily cache warmup task."""
    return warm_cache_task.delay()


@shared_task
def weekly_token_cleanup():
    """Weekly token cleanup task."""
    return cleanup_expired_tokens.delay()


@shared_task
def daily_analytics_generation():
    """Daily analytics generation task."""
    generate_analytics_report.delay('user_engagement')
    generate_analytics_report.delay('course_performance')
    return "Daily analytics generation started"


@shared_task
def weekly_database_optimization():
    """Weekly database optimization task."""
    return optimize_database_task.delay()