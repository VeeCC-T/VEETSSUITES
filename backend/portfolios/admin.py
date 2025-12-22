from django.contrib import admin
from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """
    Admin interface for Portfolio model.
    """
    list_display = ['user', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'parsed_content']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Portfolio Content', {
            'fields': ('cv_file', 'parsed_content', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Portfolios should be created through the API"""
        return False
