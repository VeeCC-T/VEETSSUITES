# Backend Performance Optimization

This document describes the performance optimization features implemented in the VeetsSuites backend.

## Overview

The backend includes comprehensive performance optimizations covering:

- **Database Query Optimization** - Efficient queries with proper indexing
- **Redis Caching** - Multi-level caching strategy for frequently accessed data
- **Async Task Processing** - Celery-based background task processing
- **Performance Monitoring** - Real-time performance metrics and analysis
- **Resource Management** - Optimized resource usage and cleanup

## Features

### 🗄️ Database Optimization

#### Query Optimization
- **Select Related & Prefetch Related**: Automatic optimization of database queries
- **Query Logging**: Development-time query analysis and optimization
- **Database Indexes**: Strategic indexes for improved query performance
- **Connection Pooling**: Efficient database connection management

#### Management Commands
```bash
# Create performance indexes
python manage.py optimize_database --create-indexes

# Analyze slow queries
python manage.py optimize_database --analyze-queries

# Run database vacuum (PostgreSQL/SQLite)
python manage.py optimize_database --vacuum
```

### 🚀 Caching Strategy

#### Multi-Level Caching
- **L1 Cache**: In-memory cache for frequently accessed data
- **L2 Cache**: Redis cache for shared data across instances
- **Query Result Caching**: Automatic caching of expensive database queries
- **API Response Caching**: HTTP response caching with proper invalidation

#### Cache Configuration
```python
# Redis Cache (Production)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Local Memory Cache (Development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
    }
}
```

#### Cache Management
```bash
# Warm up caches
python manage.py warm_cache --all

# Warm specific caches
python manage.py warm_cache --courses --pages 10
python manage.py warm_cache --users 1,2,3,4,5
```

### ⚡ Async Task Processing

#### Celery Configuration
- **Task Queues**: Separate queues for different task types
- **Priority Queues**: High, normal, and low priority task processing
- **Retry Logic**: Automatic retry with exponential backoff
- **Task Monitoring**: Real-time task monitoring and metrics

#### Available Tasks
```python
# Cache management
warm_cache_task.delay()

# File processing
process_cv_upload.delay(portfolio_id)
process_zoom_recording.delay(session_id, recording_url)

# Notifications
send_notification_email.delay(email, subject, message)

# Analytics
generate_analytics_report.delay('user_engagement')

# Maintenance
cleanup_expired_tokens.delay()
optimize_database_task.delay()
```

#### Queue Configuration
```python
CELERY_TASK_ROUTES = {
    'veetssuites.tasks.warm_cache_task': {'queue': 'cache'},
    'veetssuites.tasks.process_cv_upload': {'queue': 'file_processing'},
    'veetssuites.tasks.send_notification_email': {'queue': 'notifications'},
    'veetssuites.tasks.generate_analytics_report': {'queue': 'analytics'},
    'veetssuites.tasks.optimize_database_task': {'queue': 'maintenance'},
}
```

### 📊 Performance Monitoring

#### Real-Time Metrics
- **Database Performance**: Query count, connection status, slow queries
- **Cache Performance**: Hit rates, memory usage, operation timing
- **Function Performance**: Execution time tracking for critical functions
- **System Resources**: Memory usage, CPU utilization

#### Monitoring Commands
```bash
# Show performance metrics
python manage.py performance_monitor --metrics

# Show cache statistics
python manage.py performance_monitor --cache-stats

# Analyze slow queries
python manage.py performance_monitor --slow-queries

# Run performance benchmarks
python manage.py performance_monitor --benchmark

# Export metrics to file
python manage.py performance_monitor --export metrics.json
```

### 🔧 Optimization Utilities

#### Decorators
```python
from veetssuites.performance import (
    QueryOptimizer, PerformanceMonitor, cached_view
)

# Log database queries
@QueryOptimizer.log_queries
def my_view_function():
    # Function implementation
    pass

# Monitor execution time
@PerformanceMonitor.time_function
def expensive_operation():
    # Function implementation
    pass

# Cache view responses
@cached_view(timeout=300, vary_on=['Authorization'])
def api_endpoint(request):
    # View implementation
    pass
```

#### ViewSet Optimizations
```python
from veetssuites.optimized_views import OptimizedViewSetMixin

class MyViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    select_related_fields = ['related_model']
    prefetch_related_fields = ['many_to_many_field']
    list_cache_timeout = 300
    detail_cache_timeout = 600
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Performance Settings
DEBUG=false  # Disable query logging in production
```

### Production Settings

```python
# Cache configuration for production
if not DEBUG:
    # Use Redis for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    
    # Enable cache middleware
    MIDDLEWARE = [
        'django.middleware.cache.UpdateCacheMiddleware',
        # ... other middleware ...
        'django.middleware.cache.FetchFromCacheMiddleware',
    ]
    
    # Cache timeout settings
    CACHE_MIDDLEWARE_SECONDS = 300
    CACHE_MIDDLEWARE_KEY_PREFIX = 'veetssuites'
```

## Performance Best Practices

### 1. Database Optimization

#### Query Optimization
```python
# ❌ Bad: N+1 queries
for course in Course.objects.all():
    print(course.instructor.name)

# ✅ Good: Use select_related
for course in Course.objects.select_related('instructor'):
    print(course.instructor.name)

# ❌ Bad: Multiple queries for related objects
courses = Course.objects.all()
for course in courses:
    for enrollment in course.enrollments.all():
        print(enrollment.user.email)

# ✅ Good: Use prefetch_related
courses = Course.objects.prefetch_related(
    'enrollments__user'
).all()
for course in courses:
    for enrollment in course.enrollments.all():
        print(enrollment.user.email)
```

#### Index Usage
```python
# Ensure indexes exist for frequently queried fields
class Course(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['instructor', 'created_at']),
            models.Index(fields=['title', 'instructor']),
        ]
```

### 2. Caching Strategy

#### Cache Key Design
```python
# Use consistent, hierarchical cache keys
def get_cache_key(prefix, *args, **kwargs):
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

# Examples
user_profile_key = get_cache_key('user', 'profile', user_id)
course_list_key = get_cache_key('courses', 'list', page=1, instructor=5)
```

#### Cache Invalidation
```python
# Invalidate related caches when data changes
def update_course(course_id, **updates):
    course = Course.objects.get(id=course_id)
    course.update(**updates)
    
    # Invalidate related caches
    cache.delete(f"course:detail:{course_id}")
    cache.delete_pattern("courses:list:*")  # Requires Redis
    cache.delete(f"instructor:courses:{course.instructor_id}")
```

### 3. Async Task Usage

#### Task Design
```python
# ✅ Good: Idempotent tasks
@shared_task(bind=True, max_retries=3)
def process_file(self, file_id):
    try:
        file_obj = File.objects.get(id=file_id)
        if file_obj.status == 'processed':
            return "Already processed"
        
        # Process file
        result = process_file_content(file_obj)
        
        file_obj.status = 'processed'
        file_obj.save()
        
        return result
    except Exception as e:
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

# ✅ Good: Batch processing
@shared_task
def batch_process_items(item_ids):
    batch_size = 100
    for i in range(0, len(item_ids), batch_size):
        batch = item_ids[i:i + batch_size]
        process_item_batch(batch)
```

### 4. API Optimization

#### Response Caching
```python
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@cache_page(60 * 5)  # Cache for 5 minutes
@vary_on_headers('Authorization')  # Vary by user
def api_endpoint(request):
    # Expensive operation
    data = generate_expensive_data()
    return JsonResponse(data)
```

#### Pagination
```python
# Use efficient pagination
class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    page_size = 20
    
    def get_queryset(self):
        return Course.objects.select_related('instructor').all()
```

## Monitoring and Alerting

### Performance Metrics

The system tracks various performance metrics:

- **Response Times**: API endpoint response times
- **Database Queries**: Query count and execution time
- **Cache Performance**: Hit/miss ratios and operation times
- **Task Processing**: Task queue lengths and processing times
- **Resource Usage**: Memory and CPU utilization

### Alerting Thresholds

Configure alerts for:
- Response times > 2 seconds
- Database queries > 100ms
- Cache hit rate < 80%
- Task queue length > 1000
- Memory usage > 80%

### Health Checks

```python
# Health check endpoint
def health_check(request):
    checks = {
        'database': check_database_connection(),
        'cache': check_cache_connection(),
        'celery': check_celery_workers(),
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JsonResponse(checks, status=status_code)
```

## Deployment Considerations

### Production Setup

1. **Redis Configuration**
   ```bash
   # Install Redis
   sudo apt-get install redis-server
   
   # Configure Redis for production
   # /etc/redis/redis.conf
   maxmemory 2gb
   maxmemory-policy allkeys-lru
   save 900 1
   ```

2. **Celery Workers**
   ```bash
   # Start Celery workers
   celery -A veetssuites worker -l info --concurrency=4
   
   # Start Celery beat (scheduler)
   celery -A veetssuites beat -l info
   
   # Monitor with Flower
   celery -A veetssuites flower
   ```

3. **Database Optimization**
   ```sql
   -- PostgreSQL configuration
   shared_buffers = 256MB
   effective_cache_size = 1GB
   work_mem = 4MB
   maintenance_work_mem = 64MB
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple application instances with shared Redis cache
- **Database Scaling**: Read replicas for read-heavy workloads
- **Task Processing**: Multiple Celery workers across different machines
- **Cache Scaling**: Redis Cluster for large-scale caching needs

## Testing Performance

### Load Testing
```bash
# Use Apache Bench for simple load testing
ab -n 1000 -c 10 http://localhost:8000/api/courses/

# Use Locust for more complex scenarios
locust -f locustfile.py --host=http://localhost:8000
```

### Performance Regression Testing
```python
# Include performance tests in test suite
class PerformanceTests(TestCase):
    def test_api_response_time(self):
        start_time = time.time()
        response = self.client.get('/api/courses/')
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # < 1 second
        self.assertEqual(response.status_code, 200)
```

## Troubleshooting

### Common Issues

1. **High Database Query Count**
   - Check for N+1 queries
   - Add select_related/prefetch_related
   - Review database indexes

2. **Low Cache Hit Rate**
   - Review cache key patterns
   - Check cache expiration times
   - Verify cache invalidation logic

3. **Slow Task Processing**
   - Monitor Celery worker status
   - Check task queue lengths
   - Review task retry logic

4. **Memory Issues**
   - Monitor cache memory usage
   - Check for memory leaks in tasks
   - Review queryset usage

### Debug Commands
```bash
# Check database performance
python manage.py performance_monitor --slow-queries

# Monitor cache usage
python manage.py performance_monitor --cache-stats

# Check Celery status
celery -A veetssuites inspect active
celery -A veetssuites inspect stats
```

This performance optimization system provides a solid foundation for scaling the VeetsSuites platform while maintaining excellent user experience through efficient resource utilization and proactive monitoring.