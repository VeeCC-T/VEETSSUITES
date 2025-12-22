from django.urls import path
from . import views

app_name = 'healthee'

urlpatterns = [
    # Consultation management
    path('consultations/', views.ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<int:pk>/', views.ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/<int:consultation_id>/messages/', views.consultation_messages, name='consultation-messages'),
    path('consultations/<int:consultation_id>/send-message/', views.send_message, name='send-message'),
    path('consultations/<int:consultation_id>/request-pharmacist/', views.request_pharmacist, name='request-pharmacist'),
    path('consultations/<int:consultation_id>/complete/', views.complete_consultation, name='complete-consultation'),
    
    # Pharmacist endpoints
    path('pharmacist/queue/', views.pharmacist_queue, name='pharmacist-queue'),
    path('pharmacist/accept/<int:consultation_id>/', views.accept_consultation, name='accept-consultation'),
    
    # AI service endpoints
    path('ai/health-check/', views.ai_health_check, name='ai-health-check'),
]