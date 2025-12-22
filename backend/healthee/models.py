from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Consultation(models.Model):
    CONSULTATION_TYPES = [
        ('ai', 'AI Chatbot'),
        ('human', 'Human Pharmacist'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting', 'Waiting for Pharmacist'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_TYPES)
    pharmacist = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pharmacist_consultations'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation {self.id} - {self.user.email} ({self.consultation_type})"


class ConsultationMessage(models.Model):
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_ai_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender_type = "AI" if self.is_ai_response else self.sender.email
        return f"Message from {sender_type} in consultation {self.consultation.id}"