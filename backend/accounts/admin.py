"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """
    
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    actions = ['promote_to_instructor', 'promote_to_admin', 'demote_to_student']
    
    def promote_to_instructor(self, request, queryset):
        """Admin action to promote users to instructor."""
        count = 0
        for user in queryset:
            user.promote_to_instructor()
            count += 1
        self.message_user(request, f'{count} user(s) promoted to instructor.')
    promote_to_instructor.short_description = 'Promote selected users to Instructor'
    
    def promote_to_admin(self, request, queryset):
        """Admin action to promote users to admin."""
        count = 0
        for user in queryset:
            user.promote_to_admin()
            count += 1
        self.message_user(request, f'{count} user(s) promoted to admin.')
    promote_to_admin.short_description = 'Promote selected users to Admin'
    
    def demote_to_student(self, request, queryset):
        """Admin action to demote users to student."""
        count = 0
        for user in queryset:
            user.demote_to_student()
            count += 1
        self.message_user(request, f'{count} user(s) demoted to student.')
    demote_to_student.short_description = 'Demote selected users to Student'
