"""
Performance optimization utilities for the VeetsSuites backend.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Database query optimization utilities.
    """
    
    @staticmethod
    def log_queries(func: Callable) -> Callable:
        """
        Decorator to log database queries for performance analysis.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.DEBUG:
                return func(*args, **kwargs)
            
            initial_queries = len(connection.queries)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            final_queries = len(connection.queries)
            
            query_count = final_queries - initial_queries
            execution_time = end_time - start_time
            
            if query_count > 10:  # Log if more than 10 queries
                logger.warning(
                    f"High query count in {func.__name__}: {query_count} queries "
                    f"in {execution_time:.2f}s"
                )
            
            return result
        return wrapper
    
    @staticmethod
    def optimize_queryset(queryset, select_related=None, prefetch_related=None):
        """
        Apply common query optimizations to a queryset.
        """
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset


class CacheManager:
    """
    Centralized cache management with performance monitoring.
    """
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    LONG_TIMEOUT = 3600   # 1 hour
    SHORT_TIMEOUT = 60    # 1 minute
    
    @classmethod
    def get_or_set(cls, key: str, callable_func: Callable, timeout: int = None) -> Any:
        """
        Get from cache or set if not exists with performance logging.
        """
        timeout = timeout or cls.DEFAULT_TIMEOUT
        
        # Try to get from cache first
        cached_value = cache.get(key)
        if cached_value is not None:
            logger.debug(f"Cache HIT for key: {key}")
            return cached_value
        
        # Cache miss - compute and store
        start_time = time.time()
        value = callable_func()
        computation_time = time.time() - start_time
        
        cache.set(key, value, timeout)
        logger.debug(f"Cache MISS for key: {key}, computed in {computation_time:.2f}s")
        
        return value
    
    @classmethod
    def invalidate_pattern(cls, pattern: str):
        """
        Invalidate cache keys matching a pattern.
        """
        # This would require Redis with pattern support
        # For now, we'll use a simple approach
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            logger.warning(f"Pattern invalidation not supported for pattern: {pattern}")
    
    @classmethod
    def get_cache_key(cls, prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key.
        """
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection.
    """
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """
        Decorator to time function execution.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Log slow functions
            if execution_time > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow function {func.__name__}: {execution_time:.2f}s"
                )
            
            # Store metrics in cache for monitoring
            metrics_key = f"performance:function:{func.__name__}"
            current_metrics = cache.get(metrics_key, {
                'total_calls': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0
            })
            
            current_metrics['total_calls'] += 1
            current_metrics['total_time'] += execution_time
            current_metrics['avg_time'] = current_metrics['total_time'] / current_metrics['total_calls']
            current_metrics['max_time'] = max(current_metrics['max_time'], execution_time)
            
            cache.set(metrics_key, current_metrics, 3600)  # Store for 1 hour
            
            return result
        return wrapper
    
    @staticmethod
    def get_performance_metrics() -> Dict[str, Any]:
        """
        Get performance metrics for monitoring dashboard.
        """
        # Get database connection info
        db_queries = len(connection.queries) if settings.DEBUG else 0
        
        # Get cache stats (if available)
        cache_stats = {}
        if hasattr(cache, 'get_stats'):
            cache_stats = cache.get_stats()
        
        return {
            'database': {
                'query_count': db_queries,
                'connection_status': 'connected' if connection.connection else 'disconnected'
            },
            'cache': cache_stats,
            'memory': {
                # Add memory usage if psutil is available
            }
        }


# Decorators for common performance optimizations
def cached_view(timeout: int = CacheManager.DEFAULT_TIMEOUT, vary_on: list = None):
    """
    Decorator for caching view responses.
    """
    def decorator(view_func):
        # Apply cache_page decorator
        cached_func = cache_page(timeout)(view_func)
        
        # Apply vary_on_headers if specified
        if vary_on:
            cached_func = vary_on_headers(*vary_on)(cached_func)
        
        return cached_func
    return decorator


def optimized_queryset(select_related: list = None, prefetch_related: list = None):
    """
    Decorator to automatically optimize querysets in view methods.
    """
    def decorator(view_method):
        @functools.wraps(view_method)
        def wrapper(self, *args, **kwargs):
            # Apply query optimizations if queryset exists
            if hasattr(self, 'get_queryset'):
                original_get_queryset = self.get_queryset
                
                def optimized_get_queryset():
                    queryset = original_get_queryset()
                    return QueryOptimizer.optimize_queryset(
                        queryset, select_related, prefetch_related
                    )
                
                self.get_queryset = optimized_get_queryset
            
            return view_method(self, *args, **kwargs)
        return wrapper
    return decorator


# Cache key generators for common patterns
class CacheKeys:
    """
    Centralized cache key management.
    """
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def course_list(page: int = 1, filters: dict = None) -> str:
        filter_str = ":".join(f"{k}:{v}" for k, v in (filters or {}).items())
        return f"courses:list:page:{page}:filters:{filter_str}"
    
    @staticmethod
    def exam_questions(exam_id: int) -> str:
        return f"exam:questions:{exam_id}"
    
    @staticmethod
    def user_enrollments(user_id: int) -> str:
        return f"user:enrollments:{user_id}"
    
    @staticmethod
    def portfolio_content(user_id: int) -> str:
        return f"portfolio:content:{user_id}"
    
    @staticmethod
    def consultation_history(user_id: int) -> str:
        return f"consultation:history:{user_id}"


# Database optimization utilities
class DatabaseOptimizer:
    """
    Database-specific optimization utilities.
    """
    
    @staticmethod
    def create_indexes():
        """
        Create database indexes for better query performance.
        This should be run as a management command.
        """
        from django.db import connection
        
        indexes = [
            # User model indexes
            "CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_user(email);",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON accounts_user(role);",
            "CREATE INDEX IF NOT EXISTS idx_user_active ON accounts_user(is_active);",
            
            # Course model indexes
            "CREATE INDEX IF NOT EXISTS idx_course_instructor ON hub3660_course(instructor_id);",
            "CREATE INDEX IF NOT EXISTS idx_course_created ON hub3660_course(created_at);",
            
            # Enrollment model indexes
            "CREATE INDEX IF NOT EXISTS idx_enrollment_user ON hub3660_enrollment(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_enrollment_course ON hub3660_enrollment(course_id);",
            "CREATE INDEX IF NOT EXISTS idx_enrollment_status ON hub3660_enrollment(payment_status);",
            
            # Exam model indexes
            "CREATE INDEX IF NOT EXISTS idx_exam_attempt_user ON exams_examattempt(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_exam_attempt_created ON exams_examattempt(created_at);",
            
            # Portfolio model indexes
            "CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolios_portfolio(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_updated ON portfolios_portfolio(updated_at);",
            
            # Consultation model indexes
            "CREATE INDEX IF NOT EXISTS idx_consultation_user ON healthee_consultation(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_consultation_status ON healthee_consultation(status);",
            "CREATE INDEX IF NOT EXISTS idx_consultation_created ON healthee_consultation(created_at);",
            
            # Transaction model indexes
            "CREATE INDEX IF NOT EXISTS idx_transaction_user ON payments_transaction(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_transaction_status ON payments_transaction(status);",
            "CREATE INDEX IF NOT EXISTS idx_transaction_created ON payments_transaction(created_at);",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    logger.info(f"Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"Failed to create index: {index_sql}, Error: {e}")
    
    @staticmethod
    def analyze_slow_queries():
        """
        Analyze slow queries for optimization opportunities.
        """
        if not settings.DEBUG:
            return []
        
        slow_queries = []
        for query in connection.queries:
            if float(query['time']) > 0.1:  # Queries taking more than 100ms
                slow_queries.append({
                    'sql': query['sql'],
                    'time': query['time']
                })
        
        return slow_queries


# Async task optimization
class AsyncTaskOptimizer:
    """
    Utilities for optimizing Celery tasks.
    """
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100, task_func: Callable = None):
        """
        Process items in batches to avoid overwhelming the system.
        """
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            if task_func:
                task_func.delay(batch)
            else:
                yield batch
    
    @staticmethod
    def priority_queue(task_func: Callable, priority: str = 'normal'):
        """
        Add tasks to priority queues for better resource management.
        """
        queue_map = {
            'high': 'high_priority',
            'normal': 'default',
            'low': 'low_priority'
        }
        
        queue = queue_map.get(priority, 'default')
        return task_func.apply_async(queue=queue)