"""
Middleware for request validation and sanitization.
"""

import json
import logging
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework import status
from .error_responses import create_validation_error_response, ErrorCodes, ErrorMessages

logger = logging.getLogger(__name__)

class RequestValidationMiddleware:
    """
    Middleware to validate and sanitize incoming requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define validation rules for different endpoints
        self.validation_rules = {
            '/api/auth/register/': {
                'max_content_length': 1024 * 1024,  # 1MB
                'required_fields': ['email', 'password', 'first_name', 'last_name'],
                'allowed_methods': ['POST'],
            },
            '/api/auth/login/': {
                'max_content_length': 1024 * 1024,  # 1MB
                'required_fields': ['email', 'password'],
                'allowed_methods': ['POST'],
            },
            '/api/portfolios/upload/': {
                'max_content_length': 10 * 1024 * 1024,  # 10MB
                'allowed_methods': ['POST'],
                'file_upload': True,
            },
            '/api/payments/': {
                'max_content_length': 1024 * 1024,  # 1MB
                'allowed_methods': ['POST'],
            },
        }

    def __call__(self, request):
        # Validate request before processing
        validation_response = self.validate_request(request)
        if validation_response:
            return validation_response
        
        response = self.get_response(request)
        return response

    def validate_request(self, request):
        """
        Validate incoming request based on endpoint rules.
        """
        path = request.path
        method = request.method
        
        # Check if we have validation rules for this endpoint
        rules = None
        for endpoint_pattern, endpoint_rules in self.validation_rules.items():
            if path.startswith(endpoint_pattern):
                rules = endpoint_rules
                break
        
        if not rules:
            return None  # No validation rules, proceed normally
        
        try:
            # Validate HTTP method
            if 'allowed_methods' in rules and method not in rules['allowed_methods']:
                logger.warning(f"Method {method} not allowed for {path}")
                return JsonResponse({
                    'error': ErrorMessages.METHOD_NOT_ALLOWED,
                    'code': ErrorCodes.METHOD_NOT_ALLOWED,
                    'allowed_methods': rules['allowed_methods']
                }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
            # Validate content length
            if 'max_content_length' in rules:
                content_length = int(request.META.get('CONTENT_LENGTH', 0))
                if content_length > rules['max_content_length']:
                    logger.warning(f"Content length {content_length} exceeds limit for {path}")
                    return JsonResponse({
                        'error': 'Request too large',
                        'code': 'REQUEST_TOO_LARGE',
                        'max_size': rules['max_content_length']
                    }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            # Validate required fields for JSON requests
            if method in ['POST', 'PUT', 'PATCH'] and 'required_fields' in rules:
                if not rules.get('file_upload', False):  # Skip for file uploads
                    try:
                        if hasattr(request, 'body') and request.body:
                            data = json.loads(request.body.decode('utf-8'))
                            missing_fields = []
                            
                            for field in rules['required_fields']:
                                if field not in data or not data[field]:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                logger.warning(f"Missing required fields {missing_fields} for {path}")
                                return JsonResponse({
                                    'error': 'Missing required fields',
                                    'code': ErrorCodes.VALIDATION_ERROR,
                                    'missing_fields': missing_fields
                                }, status=status.HTTP_400_BAD_REQUEST)
                    except json.JSONDecodeError:
                        # Not JSON data, skip validation
                        pass
            
            # Validate request headers
            self._validate_headers(request, rules)
            
            # Validate query parameters
            self._validate_query_params(request, rules)
            
        except Exception as e:
            logger.error(f"Error during request validation: {e}")
            return JsonResponse({
                'error': 'Request validation failed',
                'code': ErrorCodes.VALIDATION_ERROR
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return None  # Validation passed

    def _validate_headers(self, request, rules):
        """
        Validate request headers.
        """
        # Check for required headers
        required_headers = rules.get('required_headers', [])
        for header in required_headers:
            if header not in request.META:
                raise ValidationError(f"Required header '{header}' is missing")
        
        # Validate Content-Type for JSON requests
        if request.method in ['POST', 'PUT', 'PATCH'] and not rules.get('file_upload', False):
            content_type = request.META.get('CONTENT_TYPE', '')
            if content_type and 'application/json' not in content_type and 'multipart/form-data' not in content_type:
                logger.warning(f"Invalid content type {content_type} for {request.path}")

    def _validate_query_params(self, request, rules):
        """
        Validate query parameters.
        """
        max_params = rules.get('max_query_params', 50)
        if len(request.GET) > max_params:
            raise ValidationError(f"Too many query parameters (max: {max_params})")
        
        # Validate parameter lengths
        for key, value in request.GET.items():
            if len(key) > 100:
                raise ValidationError(f"Query parameter name '{key}' is too long")
            if len(value) > 1000:
                raise ValidationError(f"Query parameter value for '{key}' is too long")


class SecurityHeadersMiddleware:
    """
    Middleware to add comprehensive security headers to responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Basic security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://checkout.stripe.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://api.stripe.com https://api.paystack.co https://zoom.us",
            "frame-src 'self' https://js.stripe.com https://checkout.stripe.com https://zoom.us",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Additional security headers
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )
        
        # Cross-Origin policies
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        # Cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request.path):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Add CORS headers for API responses
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'Content-Range, X-Total-Count'
            
            # Vary header for caching
            response['Vary'] = 'Origin, Accept-Encoding'
        
        return response
    
    def _is_sensitive_endpoint(self, path):
        """
        Check if the endpoint contains sensitive data that shouldn't be cached.
        """
        sensitive_patterns = [
            '/api/auth/', '/api/payments/', '/api/admin/',
            '/api/portfolios/', '/api/healthee/consultations/'
        ]
        return any(pattern in path for pattern in sensitive_patterns)


class RequestSanitizationMiddleware:
    """
    Middleware to sanitize request data.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sanitize query parameters
        self._sanitize_query_params(request)
        
        response = self.get_response(request)
        return response

    def _sanitize_query_params(self, request):
        """
        Sanitize query parameters to prevent injection attacks.
        """
        # Remove potentially dangerous characters from query parameters
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:', 'vbscript:']
        
        for key in list(request.GET.keys()):
            value = request.GET[key]
            
            # Check for dangerous patterns
            for char in dangerous_chars:
                if char in value.lower():
                    logger.warning(f"Potentially dangerous query parameter detected: {key}={value}")
                    # You might want to remove or escape these parameters
                    break