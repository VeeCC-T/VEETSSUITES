"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    
    list_display = [
        'id', 'user', 'amount', 'currency', 'provider', 
        'status', 'created_at', 'updated_at'
    ]
    list_filter = ['provider', 'status', 'currency', 'created_at']
    search_fields = ['user__email', 'provider_transaction_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'amount', 'currency', 'provider', 'status')
        }),
        ('Provider Information', {
            'fields': ('provider_transaction_id', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['user', 'provider', 'provider_transaction_id'])
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """Restrict deletion of completed transactions."""
        if obj and obj.status == 'completed':
            return False
        return super().has_delete_permission(request, obj)