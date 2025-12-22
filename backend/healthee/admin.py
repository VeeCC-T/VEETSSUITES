from django.contrib import admin
from .models import Consultation, ConsultationMessage


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'consultation_type', 'status', 'pharmacist', 'created_at']
    list_filter = ['consultation_type', 'status', 'created_at']
    search_fields = ['user__email', 'pharmacist__email']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'pharmacist')


@admin.register(ConsultationMessage)
class ConsultationMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'consultation', 'sender', 'is_ai_response', 'created_at']
    list_filter = ['is_ai_response', 'created_at']
    search_fields = ['consultation__id', 'sender__email', 'message']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consultation', 'sender')