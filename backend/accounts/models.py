"""
User models for the VEETSSUITES platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Adds role-based access control with four roles:
    - student: Default role, can access courses and consultations
    - instructor: Can create and manage courses
    - pharmacist: Can accept and manage health consultations
    - admin: Full system access
    """
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.',
        }
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text='User role determines access permissions'
    )
    
    # Override username to make email the primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        """Check if user has student role."""
        return self.role == 'student'
    
    @property
    def is_instructor(self):
        """Check if user has instructor role."""
        return self.role == 'instructor'
    
    @property
    def is_pharmacist(self):
        """Check if user has pharmacist role."""
        return self.role == 'pharmacist'
    
    @property
    def is_admin_user(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def promote_to_instructor(self):
        """Promote user to instructor role."""
        self.role = 'instructor'
        self.save(update_fields=['role'])
    
    def promote_to_admin(self):
        """Promote user to admin role."""
        self.role = 'admin'
        self.is_staff = True
        self.is_superuser = True
        self.save(update_fields=['role', 'is_staff', 'is_superuser'])
    
    def demote_to_student(self):
        """Demote user to student role."""
        self.role = 'student'
        self.is_staff = False
        self.is_superuser = False
        self.save(update_fields=['role', 'is_staff', 'is_superuser'])
