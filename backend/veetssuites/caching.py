"""
Caching service for VeetsSuites application.
"""

from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet
from typing import Any, Optional, List, Dict
import json
import hashlib
from .performance import CacheManager, CacheKeys
import logging

logger = logging.getLogger(__name__)


class CachingService:
    """
    High-level caching service for application data.
    """
    
    # Cache timeouts
    SHORT_CACHE = 300      # 5 minutes
    MEDIUM_CACHE = 1800    # 30 minutes  
    LONG_CACHE = 3600      # 1 hour
    VERY_LONG_CACHE = 86400  # 24 hours
    
    @classmethod
    def get_user_profile(cls, user_id: int) -> Optional[Dict]:
        """Cache user profile data."""
        cache_key = CacheKeys.user_profile(user_id)
        
        def fetch_user_profile():
            from accounts.models import User
            try:
                user = User.objects.get(id=user_id)
                return {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                }
            except User.DoesNotExist:
                return None
        
        return CacheManager.get_or_set(
            cache_key, fetch_user_profile, cls.MEDIUM_CACHE
        )
    
    @classmethod
    def get_course_list(cls, page: int = 1, filters: Dict = None) -> Dict:
        """Cache course list with pagination."""
        cache_key = CacheKeys.course_list(page, filters)
        
        def fetch_course_list():
            from hub3660.models import Course
            from hub3660.serializers import CourseSerializer
            from django.core.paginator import Paginator
            
            queryset = Course.objects.select_related('instructor').all()
            
            # Apply filters
            if filters:
                if filters.get('instructor'):
                    queryset = queryset.filter(instructor_id=filters['instructor'])
                if filters.get('search'):
                    queryset = queryset.filter(title__icontains=filters['search'])
            
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(page)
            
            return {
                'courses': CourseSerializer(page_obj.object_list, many=True).data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
        
        return CacheManager.get_or_set(
            cache_key, fetch_course_list, cls.SHORT_CACHE
        )
    
    @classmethod
    def get_exam_questions(cls, exam_id: int) -> List[Dict]:
        """Cache exam questions."""
        cache_key = CacheKeys.exam_questions(exam_id)
        
        def fetch_exam_questions():
            from exams.models import Question
            from exams.serializers import QuestionSerializer
            
            questions = Question.objects.filter(
                id__in=range(1, 101)  # Assuming we have questions 1-100
            ).order_by('?')[:20]  # Random 20 questions
            
            return QuestionSerializer(questions, many=True).data
        
        return CacheManager.get_or_set(
            cache_key, fetch_exam_questions, cls.LONG_CACHE
        )
    
    @classmethod
    def get_user_enrollments(cls, user_id: int) -> List[Dict]:
        """Cache user enrollments."""
        cache_key = CacheKeys.user_enrollments(user_id)
        
        def fetch_user_enrollments():
            from hub3660.models import Enrollment
            from hub3660.serializers import EnrollmentSerializer
            
            enrollments = Enrollment.objects.select_related(
                'course', 'course__instructor'
            ).filter(user_id=user_id)
            
            return EnrollmentSerializer(enrollments, many=True).data
        
        return CacheManager.get_or_set(
            cache_key, fetch_user_enrollments, cls.MEDIUM_CACHE
        )
    
    @classmethod
    def get_portfolio_content(cls, user_id: int) -> Optional[Dict]:
        """Cache portfolio content."""
        cache_key = CacheKeys.portfolio_content(user_id)
        
        def fetch_portfolio_content():
            from portfolios.models import Portfolio
            from portfolios.serializers import PortfolioSerializer
            
            try:
                portfolio = Portfolio.objects.get(user_id=user_id)
                return PortfolioSerializer(portfolio).data
            except Portfolio.DoesNotExist:
                return None
        
        return CacheManager.get_or_set(
            cache_key, fetch_portfolio_content, cls.LONG_CACHE
        )
    
    @classmethod
    def get_consultation_history(cls, user_id: int) -> List[Dict]:
        """Cache consultation history."""
        cache_key = CacheKeys.consultation_history(user_id)
        
        def fetch_consultation_history():
            from healthee.models import Consultation
            from healthee.serializers import ConsultationSerializer
            
            consultations = Consultation.objects.select_related(
                'user'
            ).prefetch_related(
                'messages'
            ).filter(user_id=user_id).order_by('-created_at')[:10]
            
            return ConsultationSerializer(consultations, many=True).data
        
        return CacheManager.get_or_set(
            cache_key, fetch_consultation_history, cls.MEDIUM_CACHE
        )
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int):
        """Invalidate all cache entries for a user."""
        keys_to_invalidate = [
            CacheKeys.user_profile(user_id),
            CacheKeys.user_enrollments(user_id),
            CacheKeys.portfolio_content(user_id),
            CacheKeys.consultation_history(user_id),
        ]
        
        for key in keys_to_invalidate:
            cache.delete(key)
            logger.debug(f"Invalidated cache key: {key}")
    
    @classmethod
    def invalidate_course_cache(cls):
        """Invalidate course-related cache entries."""
        # This would require pattern matching in Redis
        # For now, we'll use a simple approach
        cache.delete_many([
            'courses:list:*'  # This won't work with default cache backend
        ])
        logger.debug("Invalidated course cache")
    
    @classmethod
    def warm_cache(cls):
        """Warm up frequently accessed cache entries."""
        logger.info("Starting cache warm-up...")
        
        try:
            # Warm up course list (first page)
            cls.get_course_list(page=1)
            
            # Warm up exam questions for first few exams
            for exam_id in range(1, 6):
                cls.get_exam_questions(exam_id)
            
            logger.info("Cache warm-up completed successfully")
        except Exception as e:
            logger.error(f"Cache warm-up failed: {e}")


class QuerySetCache:
    """
    Caching utilities for Django QuerySets.
    """
    
    @staticmethod
    def cache_queryset(queryset: QuerySet, cache_key: str, timeout: int = 300) -> List:
        """
        Cache a queryset result.
        """
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Convert queryset to list and cache
        result = list(queryset)
        cache.set(cache_key, result, timeout)
        
        return result
    
    @staticmethod
    def cache_count(queryset: QuerySet, cache_key: str, timeout: int = 300) -> int:
        """
        Cache a queryset count.
        """
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count
        
        count = queryset.count()
        cache.set(cache_key, count, timeout)
        
        return count
    
    @staticmethod
    def generate_cache_key(model_name: str, method: str, **kwargs) -> str:
        """
        Generate a consistent cache key for querysets.
        """
        key_data = {
            'model': model_name,
            'method': method,
            **kwargs
        }
        
        # Create a hash of the key data for consistency
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"queryset:{model_name}:{method}:{key_hash}"


class CacheInvalidator:
    """
    Handles cache invalidation based on model changes.
    """
    
    # Define cache dependencies
    CACHE_DEPENDENCIES = {
        'User': ['user_profile', 'user_enrollments'],
        'Course': ['course_list', 'user_enrollments'],
        'Enrollment': ['user_enrollments', 'course_list'],
        'Portfolio': ['portfolio_content'],
        'Consultation': ['consultation_history'],
        'Question': ['exam_questions'],
    }
    
    @classmethod
    def invalidate_for_model(cls, model_name: str, instance_id: int = None):
        """
        Invalidate cache entries related to a model change.
        """
        dependencies = cls.CACHE_DEPENDENCIES.get(model_name, [])
        
        for dependency in dependencies:
            if dependency == 'user_profile' and instance_id:
                cache.delete(CacheKeys.user_profile(instance_id))
            elif dependency == 'user_enrollments' and instance_id:
                cache.delete(CacheKeys.user_enrollments(instance_id))
            elif dependency == 'portfolio_content' and instance_id:
                cache.delete(CacheKeys.portfolio_content(instance_id))
            elif dependency == 'consultation_history' and instance_id:
                cache.delete(CacheKeys.consultation_history(instance_id))
            elif dependency == 'course_list':
                # Invalidate all course list pages
                CachingService.invalidate_course_cache()
            elif dependency == 'exam_questions':
                # Invalidate exam questions cache
                cache.delete_many([f"exam:questions:{i}" for i in range(1, 101)])
        
        logger.debug(f"Invalidated cache for {model_name} (ID: {instance_id})")


# Cache warming management command helper
class CacheWarmer:
    """
    Utilities for warming up cache entries.
    """
    
    @staticmethod
    def warm_user_caches(user_ids: List[int]):
        """Warm cache for specific users."""
        for user_id in user_ids:
            CachingService.get_user_profile(user_id)
            CachingService.get_user_enrollments(user_id)
            CachingService.get_portfolio_content(user_id)
            CachingService.get_consultation_history(user_id)
    
    @staticmethod
    def warm_course_caches(pages: int = 5):
        """Warm course list cache for multiple pages."""
        for page in range(1, pages + 1):
            CachingService.get_course_list(page)
    
    @staticmethod
    def warm_exam_caches(exam_count: int = 10):
        """Warm exam question caches."""
        for exam_id in range(1, exam_count + 1):
            CachingService.get_exam_questions(exam_id)