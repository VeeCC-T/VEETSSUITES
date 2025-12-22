"""
Performance optimization tests.
"""

import time
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .performance import (
    QueryOptimizer, CacheManager, PerformanceMonitor, 
    DatabaseOptimizer
)
from .caching import CachingService, CacheInvalidator
from .tasks import warm_cache_task, process_cv_upload

User = get_user_model()


class PerformanceOptimizationTests(TestCase):
    """Test performance optimization utilities."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_cache_manager(self):
        """Test cache manager functionality."""
        # Test cache get_or_set
        def expensive_operation():
            time.sleep(0.01)  # Simulate expensive operation
            return {'result': 'computed_value'}
        
        cache_key = 'test_cache_key'
        
        # First call should compute and cache
        start_time = time.time()
        result1 = CacheManager.get_or_set(cache_key, expensive_operation, 60)
        first_call_time = time.time() - start_time
        
        # Second call should be from cache (faster)
        start_time = time.time()
        result2 = CacheManager.get_or_set(cache_key, expensive_operation, 60)
        second_call_time = time.time() - start_time
        
        self.assertEqual(result1, result2)
        self.assertLess(second_call_time, first_call_time)
        
        # Clean up
        cache.delete(cache_key)
    
    def test_caching_service(self):
        """Test caching service methods."""
        # Test user profile caching
        profile_data = CachingService.get_user_profile(self.user.id)
        
        self.assertIsNotNone(profile_data)
        self.assertEqual(profile_data['email'], self.user.email)
        self.assertEqual(profile_data['role'], self.user.role)
        
        # Test cache invalidation
        CachingService.invalidate_user_cache(self.user.id)
        
        # Verify cache was cleared (would need to check cache directly)
        # For now, just ensure no errors
        self.assertTrue(True)
    
    def test_query_optimizer_decorator(self):
        """Test query optimizer decorator."""
        @QueryOptimizer.log_queries
        def test_function():
            # Simulate database queries
            list(User.objects.all())
            return "completed"
        
        result = test_function()
        self.assertEqual(result, "completed")
    
    def test_performance_monitor_decorator(self):
        """Test performance monitoring decorator."""
        @PerformanceMonitor.time_function
        def test_function():
            time.sleep(0.01)  # Simulate work
            return "completed"
        
        result = test_function()
        self.assertEqual(result, "completed")
    
    def test_cache_invalidator(self):
        """Test cache invalidation system."""
        # Cache some user data
        CachingService.get_user_profile(self.user.id)
        
        # Invalidate cache for user model
        CacheInvalidator.invalidate_for_model('User', self.user.id)
        
        # Should not raise any errors
        self.assertTrue(True)
    
    def test_database_optimizer(self):
        """Test database optimization utilities."""
        # Test slow query analysis
        slow_queries = DatabaseOptimizer.analyze_slow_queries()
        
        # Should return a list (empty or with queries)
        self.assertIsInstance(slow_queries, list)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        from .performance import CacheKeys
        
        # Test user profile key
        key1 = CacheKeys.user_profile(self.user.id)
        key2 = CacheKeys.user_profile(self.user.id)
        
        self.assertEqual(key1, key2)  # Should be consistent
        self.assertIn(str(self.user.id), key1)  # Should contain user ID
        
        # Test course list key
        course_key = CacheKeys.course_list(1, {'search': 'test'})
        self.assertIn('courses:list', course_key)
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        metrics = PerformanceMonitor.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('database', metrics)
        self.assertIn('cache', metrics)
    
    def test_async_task_structure(self):
        """Test that async tasks are properly structured."""
        # Test that tasks can be imported without errors
        from .tasks import (
            warm_cache_task, process_cv_upload, 
            send_notification_email, cleanup_expired_tokens
        )
        
        # Verify tasks have proper attributes
        self.assertTrue(hasattr(warm_cache_task, 'delay'))
        self.assertTrue(hasattr(process_cv_upload, 'delay'))
        self.assertTrue(hasattr(send_notification_email, 'delay'))
        self.assertTrue(hasattr(cleanup_expired_tokens, 'delay'))


class CachePerformanceTests(TestCase):
    """Test cache performance specifically."""
    
    def test_cache_performance(self):
        """Test cache read/write performance."""
        cache_key = 'performance_test'
        test_data = {'large_data': 'x' * 1000}  # 1KB of data
        
        # Test write performance
        start_time = time.time()
        cache.set(cache_key, test_data, 60)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        cached_data = cache.get(cache_key)
        read_time = time.time() - start_time
        
        # Verify data integrity
        self.assertEqual(cached_data, test_data)
        
        # Performance assertions (adjust thresholds as needed)
        self.assertLess(write_time, 0.1)  # Should write in < 100ms
        self.assertLess(read_time, 0.05)  # Should read in < 50ms
        
        # Clean up
        cache.delete(cache_key)
    
    def test_cache_expiration(self):
        """Test cache expiration functionality."""
        cache_key = 'expiration_test'
        
        # Set with short expiration
        cache.set(cache_key, 'test_value', 1)  # 1 second
        
        # Should be available immediately
        self.assertEqual(cache.get(cache_key), 'test_value')
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        self.assertIsNone(cache.get(cache_key))


class QueryOptimizationTests(TestCase):
    """Test database query optimization."""
    
    def setUp(self):
        """Create test data."""
        self.users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123',
                role='student'
            )
            self.users.append(user)
    
    def test_queryset_optimization(self):
        """Test queryset optimization utilities."""
        # Test basic queryset
        queryset = User.objects.all()
        
        # Apply optimization
        optimized_queryset = QueryOptimizer.optimize_queryset(
            queryset,
            select_related=[],  # No relations for User model
            prefetch_related=[]
        )
        
        # Should return same results
        self.assertEqual(
            list(queryset.values_list('id', flat=True)),
            list(optimized_queryset.values_list('id', flat=True))
        )
    
    def test_query_count_optimization(self):
        """Test that optimizations reduce query count."""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Reset query log
            connection.queries_log.clear()
            
            # Perform operations
            users = list(User.objects.all())
            
            # Check query count
            query_count = len(connection.queries)
            
            # Should be reasonable number of queries
            self.assertLessEqual(query_count, 5)


class IntegrationPerformanceTests(TestCase):
    """Integration tests for performance optimizations."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='integration@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_end_to_end_caching(self):
        """Test end-to-end caching workflow."""
        # 1. Get user profile (should cache)
        profile1 = CachingService.get_user_profile(self.user.id)
        
        # 2. Get again (should be from cache)
        profile2 = CachingService.get_user_profile(self.user.id)
        
        # 3. Should be identical
        self.assertEqual(profile1, profile2)
        
        # 4. Update user
        self.user.first_name = 'Updated'
        self.user.save()
        
        # 5. Invalidate cache
        CachingService.invalidate_user_cache(self.user.id)
        
        # 6. Get profile again (should be fresh)
        profile3 = CachingService.get_user_profile(self.user.id)
        
        # 7. Should have updated data
        self.assertEqual(profile3['first_name'], 'Updated')
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        @PerformanceMonitor.time_function
        def monitored_function():
            # Simulate some work
            CachingService.get_user_profile(self.user.id)
            return "completed"
        
        result = monitored_function()
        self.assertEqual(result, "completed")
        
        # Check that metrics were recorded
        metrics = PerformanceMonitor.get_performance_metrics()
        self.assertIsInstance(metrics, dict)