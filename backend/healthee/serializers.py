from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Consultation, ConsultationMessage

User = get_user_model()


class ConsultationMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    
    class Meta:
        model = ConsultationMessage
        fields = [
            'id', 'message', 'is_ai_response', 'created_at',
            'sender_email', 'sender_name'
        ]
        read_only_fields = ['id', 'created_at', 'sender_email', 'sender_name']


class ConsultationSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    pharmacist_email = serializers.CharField(source='pharmacist.email', read_only=True)
    messages = ConsultationMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'consultation_type', 'status', 'created_at', 'completed_at',
            'user_email', 'pharmacist_email', 'messages', 'message_count'
        ]
        read_only_fields = ['id', 'created_at', 'user_email', 'pharmacist_email']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConsultationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['consultation_type']
    
    def validate_consultation_type(self, value):
        if value not in ['ai', 'human']:
            raise serializers.ValidationError("Consultation type must be 'ai' or 'human'")
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationMessage
        fields = ['message']
    
    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class PharmacistQueueSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    latest_message = serializers.SerializerMethodField()
    waiting_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'user_email', 'user_name', 'created_at',
            'latest_message', 'waiting_time'
        ]
    
    def get_latest_message(self, obj):
        latest = obj.messages.filter(is_ai_response=False).last()
        return latest.message[:100] + "..." if latest and len(latest.message) > 100 else latest.message if latest else None
    
    def get_waiting_time(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        return f"{int(minutes)}m"