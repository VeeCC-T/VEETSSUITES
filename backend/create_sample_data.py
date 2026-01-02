#!/usr/bin/env python
"""
Create sample data for VEETSSUITES platform
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')
django.setup()

from accounts.models import User
from hub3660.models import Course, Session
from healthee.models import Consultation
from portfolios.models import Portfolio
from datetime import datetime, timedelta
from django.utils import timezone

def create_sample_data():
    print("Creating sample data...")
    
    # Create test users
    admin_user, created = User.objects.get_or_create(
        email='admin@veetssuites.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Created admin user")
    else:
        print("✓ Admin user already exists")
    
    # Create instructor user
    instructor_user, created = User.objects.get_or_create(
        email='instructor@veetssuites.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Instructor',
            'role': 'instructor'
        }
    )
    if created:
        instructor_user.set_password('instructor123')
        instructor_user.save()
        print("✓ Created instructor user")
    else:
        print("✓ Instructor user already exists")
    
    # Create student user
    student_user, created = User.objects.get_or_create(
        email='student@veetssuites.com',
        defaults={
            'first_name': 'Jane',
            'last_name': 'Student',
            'role': 'student'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        print("✓ Created student user")
    else:
        print("✓ Student user already exists")
    
    # Create sample courses
    courses_data = [
        {
            'title': 'Introduction to Pharmacy Practice',
            'description': 'A comprehensive introduction to modern pharmacy practice, covering fundamental concepts, patient care, and professional responsibilities.',
            'price': 299.99,
            'max_students': 50,
            'is_active': True
        },
        {
            'title': 'Clinical Pharmacology Masterclass',
            'description': 'Advanced course covering drug interactions, pharmacokinetics, and clinical decision-making in pharmacy practice.',
            'price': 499.99,
            'max_students': 30,
            'is_active': True
        },
        {
            'title': 'Pharmaceutical Care and Counseling',
            'description': 'Learn effective patient counseling techniques and pharmaceutical care principles for optimal patient outcomes.',
            'price': 399.99,
            'max_students': 40,
            'is_active': True
        }
    ]
    
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                **course_data,
                'instructor': instructor_user
            }
        )
        if created:
            print(f"✓ Created course: {course.title}")
            
            # Create sample sessions for each course
            for i in range(3):
                session_date = timezone.now() + timedelta(days=7 + i*7)
                Session.objects.get_or_create(
                    course=course,
                    title=f"Session {i+1}: {course.title}",
                    defaults={
                        'description': f"Session {i+1} covering key topics in {course.title}",
                        'scheduled_time': session_date,
                        'duration_minutes': 90,
                        'zoom_meeting_id': f"123456789{i}",
                        'zoom_join_url': f"https://zoom.us/j/123456789{i}",
                        'zoom_password': f"pass{i+1}23"
                    }
                )
            print(f"  ✓ Created 3 sessions for {course.title}")
        else:
            print(f"✓ Course already exists: {course.title}")
    
    print("\n🎉 Sample data creation completed!")
    print("\nTest accounts created:")
    print("📧 Admin: admin@veetssuites.com / admin123")
    print("📧 Instructor: instructor@veetssuites.com / instructor123") 
    print("📧 Student: student@veetssuites.com / student123")
    print("\nYou can now test all subsites with these accounts!")

if __name__ == '__main__':
    create_sample_data()