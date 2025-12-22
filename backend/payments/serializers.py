from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'amount', 'currency', 'provider',
            'provider_transaction_id', 'status', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PaymentSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating payment sessions."""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=3, default='USD')
    course_id = serializers.IntegerField(required=False)  # For course enrollment payments
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_currency(self, value):
        """Validate currency code."""
        allowed_currencies = ['USD', 'NGN', 'EUR', 'GBP']
        if value.upper() not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(allowed_currencies)}")
        return value.upper()


class PaymentProviderRoutingSerializer(serializers.Serializer):
    """Serializer for determining payment provider based on user location."""
    
    country_code = serializers.CharField(max_length=2, required=False)
    currency = serializers.CharField(max_length=3, default='USD')
    
    def validate_country_code(self, value):
        """Validate country code format."""
        if value and len(value) != 2:
            raise serializers.ValidationError("Country code must be 2 characters long")
        return value.upper() if value else None


class WebhookEventSerializer(serializers.Serializer):
    """Base serializer for webhook events."""
    
    event_type = serializers.CharField()
    data = serializers.JSONField()
    provider = serializers.CharField()
    signature = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(required=False)