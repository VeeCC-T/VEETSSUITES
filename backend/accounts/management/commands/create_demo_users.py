from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        # Demo users data
        users_data = [
            {
                'email': 'demo@veetssuites.com',
                'username': 'demo_user',
                'first_name': 'Demo',
                'last_name': 'User',
                'role': 'student',
                'password': 'demo123'
            },
            {
                'email': 'student@veetssuites.com',
                'username': 'student_user',
                'first_name': 'Jane',
                'last_name': 'Student',
                'role': 'student',
                'password': 'student123'
            }
        ]

        for user_data in users_data:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
            else:
                self.stdout.write(f'User already exists: {user.email}')

        self.stdout.write(self.style.SUCCESS('Demo users creation completed!'))