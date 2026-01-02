from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from hub3660.models import Course, Session

class Command(BaseCommand):
    help = 'Create sample courses and sessions for HUB3660'

    def handle(self, *args, **options):
        # Get or create instructor
        instructor, created = User.objects.get_or_create(
            email='instructor@veetssuites.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Instructor',
                'role': 'instructor'
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS('Created instructor user'))

        # Sample courses data
        courses_data = [
            {
                'title': 'Introduction to Pharmacy Practice',
                'description': 'A comprehensive introduction to modern pharmacy practice, covering fundamental concepts, patient care, and professional responsibilities.',
                'price': 299.99,
                'is_published': True
            },
            {
                'title': 'Clinical Pharmacology Masterclass',
                'description': 'Advanced course covering drug interactions, pharmacokinetics, and clinical decision-making in pharmacy practice.',
                'price': 499.99,
                'is_published': True
            },
            {
                'title': 'Pharmaceutical Care and Counseling',
                'description': 'Learn effective patient counseling techniques and pharmaceutical care principles for optimal patient outcomes.',
                'price': 399.99,
                'is_published': True
            }
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    **course_data,
                    'instructor': instructor
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
                
                # Create sample sessions
                for i in range(3):
                    session_date = timezone.now() + timedelta(days=7 + i*7)
                    Session.objects.get_or_create(
                        course=course,
                        title=f"Session {i+1}: {course.title}",
                        defaults={
                            'scheduled_at': session_date,
                            'zoom_meeting_id': f"123456789{i}",
                            'zoom_join_url': f"https://zoom.us/j/123456789{i}"
                        }
                    )
                self.stdout.write(f'  Created 3 sessions for {course.title}')
            else:
                self.stdout.write(f'Course already exists: {course.title}')

        self.stdout.write(self.style.SUCCESS('Sample courses creation completed!'))