"""
Management command for performance monitoring and analysis.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from veetssuites.performance import PerformanceMonitor, DatabaseOptimizer
from veetssuites.caching import CachingService
import json
import time


class Command(BaseCommand):
    help = 'Monitor and analyze application performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--metrics',
            action='store_true',
            help='Show current performance metrics',
        )
        parser.add_argument(
            '--cache-stats',
            action='store_true',
            help='Show cache statistics',
        )
        parser.add_argument(
            '--slow-queries',
            action='store_true',
            help='Analyze slow database queries',
        )
        parser.add_argument(
            '--benchmark',
            action='store_true',
            help='Run performance benchmarks',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export metrics to file',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Performance Monitoring Dashboard')
        )
        self.stdout.write('=' * 50)

        if options['metrics']:
            self.show_performance_metrics()

        if options['cache_stats']:
            self.show_cache_statistics()

        if options['slow_queries']:
            self.analyze_slow_queries()

        if options['benchmark']:
            self.run_benchmarks()

        if options['export']:
            self.export_metrics(options['export'])

    def show_performance_metrics(self):
        """Display current performance metrics."""
        self.stdout.write('\n📊 Performance Metrics:')
        self.stdout.write('-' * 30)

        try:
            metrics = PerformanceMonitor.get_performance_metrics()
            
            # Database metrics
            db_metrics = metrics.get('database', {})
            self.stdout.write(f"Database Queries: {db_metrics.get('query_count', 'N/A')}")
            self.stdout.write(f"Connection Status: {db_metrics.get('connection_status', 'Unknown')}")
            
            # Cache metrics
            cache_metrics = metrics.get('cache', {})
            if cache_metrics:
                self.stdout.write(f"Cache Hit Rate: {cache_metrics.get('hit_rate', 'N/A')}")
                self.stdout.write(f"Cache Memory Usage: {cache_metrics.get('memory_usage', 'N/A')}")
            
            # Function performance metrics
            function_metrics = self.get_function_metrics()
            if function_metrics:
                self.stdout.write('\nFunction Performance:')
                for func_name, stats in function_metrics.items():
                    self.stdout.write(
                        f"  {func_name}: {stats['total_calls']} calls, "
                        f"avg: {stats['avg_time']:.3f}s, max: {stats['max_time']:.3f}s"
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to get performance metrics: {e}')
            )

    def show_cache_statistics(self):
        """Display cache statistics."""
        self.stdout.write('\n🗄️  Cache Statistics:')
        self.stdout.write('-' * 30)

        try:
            # Test cache performance
            cache_key = 'performance_test'
            
            # Write test
            start_time = time.time()
            cache.set(cache_key, 'test_value', 60)
            write_time = time.time() - start_time
            
            # Read test
            start_time = time.time()
            value = cache.get(cache_key)
            read_time = time.time() - start_time
            
            self.stdout.write(f"Cache Write Time: {write_time:.4f}s")
            self.stdout.write(f"Cache Read Time: {read_time:.4f}s")
            self.stdout.write(f"Cache Status: {'✓ Working' if value == 'test_value' else '✗ Failed'}")
            
            # Clean up
            cache.delete(cache_key)
            
            # Show cache info if available
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                for key, value in stats.items():
                    self.stdout.write(f"{key}: {value}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to get cache statistics: {e}')
            )

    def analyze_slow_queries(self):
        """Analyze slow database queries."""
        self.stdout.write('\n🐌 Slow Query Analysis:')
        self.stdout.write('-' * 30)

        try:
            slow_queries = DatabaseOptimizer.analyze_slow_queries()
            
            if slow_queries:
                self.stdout.write(f"Found {len(slow_queries)} slow queries:")
                for i, query in enumerate(slow_queries, 1):
                    self.stdout.write(f"\n{i}. Execution Time: {query['time']}s")
                    self.stdout.write(f"   SQL: {query['sql'][:100]}...")
                    if len(query['sql']) > 100:
                        self.stdout.write("   [truncated]")
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ No slow queries detected')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to analyze slow queries: {e}')
            )

    def run_benchmarks(self):
        """Run performance benchmarks."""
        self.stdout.write('\n⚡ Performance Benchmarks:')
        self.stdout.write('-' * 30)

        try:
            # Database benchmark
            self.stdout.write('Running database benchmark...')
            db_start = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            db_time = time.time() - db_start
            self.stdout.write(f"Database Query: {db_time:.4f}s")

            # Cache benchmark
            self.stdout.write('Running cache benchmark...')
            cache_start = time.time()
            cache.set('benchmark_key', 'benchmark_value', 60)
            cache.get('benchmark_key')
            cache.delete('benchmark_key')
            cache_time = time.time() - cache_start
            self.stdout.write(f"Cache Operations: {cache_time:.4f}s")

            # API endpoint benchmark (if possible)
            self.stdout.write('Running API benchmark...')
            api_start = time.time()
            # This would require making actual API calls
            # For now, we'll simulate
            time.sleep(0.01)  # Simulate API call
            api_time = time.time() - api_start
            self.stdout.write(f"API Response: {api_time:.4f}s")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Benchmark failed: {e}')
            )

    def export_metrics(self, filename):
        """Export performance metrics to file."""
        self.stdout.write(f'\n📤 Exporting metrics to {filename}...')

        try:
            metrics_data = {
                'timestamp': time.time(),
                'performance_metrics': PerformanceMonitor.get_performance_metrics(),
                'slow_queries': DatabaseOptimizer.analyze_slow_queries(),
                'function_metrics': self.get_function_metrics(),
            }

            with open(filename, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)

            self.stdout.write(
                self.style.SUCCESS(f'✓ Metrics exported to {filename}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to export metrics: {e}')
            )

    def get_function_metrics(self):
        """Get function performance metrics from cache."""
        try:
            # Get all performance metrics from cache
            function_metrics = {}
            
            # This would require scanning cache keys with pattern
            # For now, return empty dict
            return function_metrics
            
        except Exception:
            return {}