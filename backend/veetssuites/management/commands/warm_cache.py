"""
Management command to warm up application caches.
"""

from django.core.management.base import BaseCommand
from veetssuites.caching import CachingService, CacheWarmer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm up application caches for better performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Warm all caches',
        )
        parser.add_argument(
            '--courses',
            action='store_true',
            help='Warm course caches',
        )
        parser.add_argument(
            '--exams',
            action='store_true',
            help='Warm exam caches',
        )
        parser.add_argument(
            '--users',
            type=str,
            help='Comma-separated list of user IDs to warm',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='Number of course list pages to warm (default: 5)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting cache warm-up...')
        )

        if options['all']:
            self.warm_all_caches(options['pages'])
        else:
            if options['courses']:
                self.warm_course_caches(options['pages'])
            
            if options['exams']:
                self.warm_exam_caches()
            
            if options['users']:
                self.warm_user_caches(options['users'])

        self.stdout.write(
            self.style.SUCCESS('Cache warm-up completed!')
        )

    def warm_all_caches(self, pages: int):
        """Warm all application caches."""
        self.stdout.write('Warming all caches...')
        
        try:
            CachingService.warm_cache()
            self.stdout.write(
                self.style.SUCCESS('✓ All caches warmed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to warm all caches: {e}')
            )

    def warm_course_caches(self, pages: int):
        """Warm course-related caches."""
        self.stdout.write(f'Warming course caches for {pages} pages...')
        
        try:
            CacheWarmer.warm_course_caches(pages)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Course caches warmed for {pages} pages')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to warm course caches: {e}')
            )

    def warm_exam_caches(self):
        """Warm exam-related caches."""
        self.stdout.write('Warming exam caches...')
        
        try:
            CacheWarmer.warm_exam_caches()
            self.stdout.write(
                self.style.SUCCESS('✓ Exam caches warmed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to warm exam caches: {e}')
            )

    def warm_user_caches(self, user_ids_str: str):
        """Warm user-specific caches."""
        try:
            user_ids = [int(uid.strip()) for uid in user_ids_str.split(',')]
            self.stdout.write(f'Warming caches for {len(user_ids)} users...')
            
            CacheWarmer.warm_user_caches(user_ids)
            self.stdout.write(
                self.style.SUCCESS(f'✓ User caches warmed for {len(user_ids)} users')
            )
        except ValueError:
            self.stdout.write(
                self.style.ERROR('✗ Invalid user IDs format. Use comma-separated integers.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to warm user caches: {e}')
            )