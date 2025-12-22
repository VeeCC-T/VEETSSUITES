"""
Optimized views with caching and performance improvements.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .performance import (
    QueryOptimizer, PerformanceMonitor, 
    cached_view, optimized_queryset
)
from .caching import CachingService, CacheInvalidator
import logging

logger = logging.getLogger(__name__)


class OptimizedViewSetMixin:
    """
    Mixin to add performance optimizations to ViewSets.
    """
    
    # Cache timeouts for different operations
    list_cache_timeout = 300      # 5 minutes
    detail_cache_timeout = 600    # 10 minutes
    
    # Query optimizations
    select_related_fields = []
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Get optimized queryset with select_related and prefetch_related."""
        queryset = super().get_queryset()
        
        return QueryOptimizer.optimize_queryset(
            queryset,
            select_related=self.select_related_fields,
            prefetch_related=self.prefetch_related_fields
        )
    
    @method_decorator(PerformanceMonitor.time_function)
    def list(self, request, *args, **kwargs):
        """Optimized list view with caching."""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(PerformanceMonitor.time_function)
    def retrieve(self, request, *args, **kwargs):
        """Optimized detail view with caching."""
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Invalidate cache after creation."""
        instance = serializer.save()
        self.invalidate_related_cache(instance)
        return instance
    
    def perform_update(self, serializer):
        """Invalidate cache after update."""
        instance = serializer.save()
        self.invalidate_related_cache(instance)
        return instance
    
    def perform_destroy(self, instance):
        """Invalidate cache after deletion."""
        self.invalidate_related_cache(instance)
        super().perform_destroy(instance)
    
    def invalidate_related_cache(self, instance):
        """Invalidate cache entries related to this instance."""
        model_name = instance.__class__.__name__
        instance_id = getattr(instance, 'id', None)
        
        CacheInvalidator.invalidate_for_model(model_name, instance_id)


class OptimizedCourseViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    Optimized course viewset with caching and query optimization.
    """
    
    select_related_fields = ['instructor']
    prefetch_related_fields = ['enrollments']
    
    @method_decorator(cached_view(timeout=300, vary_on=['Authorization']))
    def list(self, request, *args, **kwargs):
        """Cached course list."""
        # Use caching service for better control
        page = int(request.GET.get('page', 1))
        filters = {
            'instructor': request.GET.get('instructor'),
            'search': request.GET.get('search'),
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        try:
            cached_data = CachingService.get_course_list(page, filters)
            return Response(cached_data)
        except Exception as e:
            logger.error(f"Cache error in course list: {e}")
            # Fallback to normal list view
            return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    @method_decorator(cached_view(timeout=600))
    def enrollments(self, request, pk=None):
        """Get course enrollments with caching."""
        course = self.get_object()
        
        cache_key = f"course:enrollments:{course.id}"
        
        def fetch_enrollments():
            from hub3660.serializers import EnrollmentSerializer
            enrollments = course.enrollments.select_related('user').all()
            return EnrollmentSerializer(enrollments, many=True).data
        
        enrollments_data = CachingService.get_or_set(
            cache_key, fetch_enrollments, 600
        )
        
        return Response(enrollments_data)


class OptimizedExamViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    Optimized exam viewset with question caching.
    """
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get exam questions with caching."""
        try:
            questions_data = CachingService.get_exam_questions(int(pk))
            return Response(questions_data)
        except Exception as e:
            logger.error(f"Cache error in exam questions: {e}")
            return Response(
                {'error': 'Failed to load exam questions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    @method_decorator(PerformanceMonitor.time_function)
    def submit_answers(self, request, pk=None):
        """Submit exam answers with performance monitoring."""
        # Implementation would go here
        # This is just a placeholder showing the decorator usage
        return Response({'message': 'Answers submitted successfully'})


class OptimizedUserViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    Optimized user viewset with profile caching.
    """
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile with caching."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            profile_data = CachingService.get_user_profile(request.user.id)
            if profile_data:
                return Response(profile_data)
            else:
                return Response(
                    {'error': 'Profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logger.error(f"Cache error in user profile: {e}")
            return Response(
                {'error': 'Failed to load profile'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def enrollments(self, request):
        """Get user enrollments with caching."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            enrollments_data = CachingService.get_user_enrollments(request.user.id)
            return Response(enrollments_data)
        except Exception as e:
            logger.error(f"Cache error in user enrollments: {e}")
            return Response(
                {'error': 'Failed to load enrollments'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OptimizedPortfolioViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    Optimized portfolio viewset with content caching.
    """
    
    @action(detail=False, methods=['get'])
    def my_portfolio(self, request):
        """Get current user's portfolio with caching."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            portfolio_data = CachingService.get_portfolio_content(request.user.id)
            if portfolio_data:
                return Response(portfolio_data)
            else:
                return Response(
                    {'error': 'Portfolio not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logger.error(f"Cache error in portfolio: {e}")
            return Response(
                {'error': 'Failed to load portfolio'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OptimizedConsultationViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    Optimized consultation viewset with history caching.
    """
    
    select_related_fields = ['user']
    prefetch_related_fields = ['messages']
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get consultation history with caching."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            history_data = CachingService.get_consultation_history(request.user.id)
            return Response(history_data)
        except Exception as e:
            logger.error(f"Cache error in consultation history: {e}")
            return Response(
                {'error': 'Failed to load consultation history'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Performance monitoring view
class PerformanceMetricsView:
    """
    View to expose performance metrics for monitoring.
    """
    
    @staticmethod
    @method_decorator(cached_view(timeout=60))  # Cache for 1 minute
    def get_metrics(request):
        """Get current performance metrics."""
        try:
            metrics = PerformanceMonitor.get_performance_metrics()
            return Response(metrics)
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return Response(
                {'error': 'Failed to get performance metrics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Cache management views
class CacheManagementView:
    """
    Views for cache management operations.
    """
    
    @staticmethod
    def warm_cache(request):
        """Warm up application caches."""
        try:
            CachingService.warm_cache()
            return Response({'message': 'Cache warmed successfully'})
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
            return Response(
                {'error': 'Failed to warm cache'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def clear_cache(request):
        """Clear application caches."""
        try:
            from django.core.cache import cache
            cache.clear()
            return Response({'message': 'Cache cleared successfully'})
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return Response(
                {'error': 'Failed to clear cache'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )