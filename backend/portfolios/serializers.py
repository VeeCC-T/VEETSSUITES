from rest_framework import serializers
from .models import Portfolio
from accounts.serializers import UserSerializer


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for Portfolio model.
    
    Handles serialization of portfolio data including file uploads.
    """
    user = UserSerializer(read_only=True)
    cv_file_url = serializers.SerializerMethodField()
    public_url = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'id',
            'user',
            'cv_file',
            'cv_file_url',
            'parsed_content',
            'is_public',
            'public_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'parsed_content', 'created_at', 'updated_at']

    def get_cv_file_url(self, obj):
        """Get the URL for the CV file"""
        if obj.cv_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cv_file.url)
            return obj.cv_file.url
        return None

    def get_public_url(self, obj):
        """Get the public URL for this portfolio"""
        return obj.get_public_url()

    def validate_cv_file(self, value):
        """
        Validate CV file upload.
        
        - Must be PDF format
        - Must be under 10MB
        """
        # Check file size (10MB = 10 * 1024 * 1024 bytes)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                "File size exceeds maximum allowed size of 10MB"
            )

        # Check file type
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError(
                "File type not supported. Please upload a PDF file"
            )

        return value


class PortfolioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new portfolio.
    
    Simplified serializer for portfolio creation.
    """
    class Meta:
        model = Portfolio
        fields = ['cv_file', 'is_public']

    def validate_cv_file(self, value):
        """
        Validate CV file upload.
        
        - Must be PDF format
        - Must be under 10MB
        """
        # Check file size (10MB = 10 * 1024 * 1024 bytes)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                "File size exceeds maximum allowed size of 10MB"
            )

        # Check file type
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError(
                "File type not supported. Please upload a PDF file"
            )

        return value


class PortfolioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing portfolio.
    """
    class Meta:
        model = Portfolio
        fields = ['cv_file', 'is_public']

    def validate_cv_file(self, value):
        """
        Validate CV file upload.
        
        - Must be PDF format
        - Must be under 10MB
        """
        if value:
            # Check file size (10MB = 10 * 1024 * 1024 bytes)
            max_size = 10 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError(
                    "File size exceeds maximum allowed size of 10MB"
                )

            # Check file type
            if not value.name.lower().endswith('.pdf'):
                raise serializers.ValidationError(
                    "File type not supported. Please upload a PDF file"
                )

        return value
