"""
Simple performance optimization tests without external dependencies.
"""

import time
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .performance import CacheManager, PerformanceMonitor

User = get_user_model()


class SimplePerformanceTests(TestCase):
    """Test basic performance optimization utilities."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.role = 'student'
        self.user.save()
    
    def test_cache_manager_basic(self):
        """Test basic cache manager functionality."""
        def expensive_operation():
            return {'result': 'computed_value'}
        
        cache_key = 'test_cache_key'
        
        # Test get_or_set
        result = CacheManager.get_or_set(cache_key, expensive_operation, 60)
        self.assertEqual(result['result'], 'computed_value')
        
        # Clean up
        cache.delete(cache_key)
    
    def test_performance_monitor_basic(self):
        """Test basic performance monitoring."""
        @PerformanceMonitor.time_function
        def test_function():
            return "completed"
        
        result = test_function()
        self.assertEqual(result, "completed")
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        from .performance import CacheKeys
        
        # Test user profile key
        key1 = CacheKeys.user_profile(self.user.id)
        key2 = CacheKeys.user_profile(self.user.id)
        
        self.assertEqual(key1, key2)  # Should be consistent
        self.assertIn(str(self.user.id), key1)  # Should contain user ID
    
    def test_basic_caching(self):
        """Test basic Django caching."""
        cache_key = 'simple_test'
        test_value = 'test_data'
        
        # Set cache
        cache.set(cache_key, test_value, 60)
        
        # Get from cache
        cached_value = cache.get(cache_key)
        
        self.assertEqual(cached_value, test_value)
        
        # Clean up
        cache.delete(cache_key)