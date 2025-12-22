"""
Management command to optimize database performance.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from veetssuites.performance import DatabaseOptimizer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize database performance by creating indexes and analyzing queries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create performance indexes',
        )
        parser.add_argument(
            '--analyze-queries',
            action='store_true',
            help='Analyze slow queries',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run database vacuum (PostgreSQL/SQLite)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting database optimization...')
        )

        if options['create_indexes']:
            self.create_indexes()

        if options['analyze_queries']:
            self.analyze_queries()

        if options['vacuum']:
            self.vacuum_database()

        self.stdout.write(
            self.style.SUCCESS('Database optimization completed!')
        )

    def create_indexes(self):
        """Create performance indexes."""
        self.stdout.write('Creating performance indexes...')
        
        try:
            DatabaseOptimizer.create_indexes()
            self.stdout.write(
                self.style.SUCCESS('✓ Performance indexes created successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create indexes: {e}')
            )

    def analyze_queries(self):
        """Analyze slow queries."""
        self.stdout.write('Analyzing slow queries...')
        
        try:
            slow_queries = DatabaseOptimizer.analyze_slow_queries()
            
            if slow_queries:
                self.stdout.write(
                    self.style.WARNING(f'Found {len(slow_queries)} slow queries:')
                )
                for i, query in enumerate(slow_queries, 1):
                    self.stdout.write(f"{i}. Time: {query['time']}s")
                    self.stdout.write(f"   SQL: {query['sql'][:100]}...")
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ No slow queries detected')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to analyze queries: {e}')
            )

    def vacuum_database(self):
        """Run database vacuum for cleanup."""
        self.stdout.write('Running database vacuum...')
        
        try:
            with connection.cursor() as cursor:
                # Check database engine
                engine = connection.settings_dict['ENGINE']
                
                if 'postgresql' in engine:
                    cursor.execute('VACUUM ANALYZE;')
                    self.stdout.write(
                        self.style.SUCCESS('✓ PostgreSQL vacuum completed')
                    )
                elif 'sqlite' in engine:
                    cursor.execute('VACUUM;')
                    self.stdout.write(
                        self.style.SUCCESS('✓ SQLite vacuum completed')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Vacuum not supported for {engine}')
                    )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to vacuum database: {e}')
            )