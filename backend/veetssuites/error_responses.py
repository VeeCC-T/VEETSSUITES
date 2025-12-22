"""
Standardized error response utilities for the VEETSSUITES platform.
"""

from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class ErrorCodes:
    """
    Standardized error codes for the platform.
    """
    # Authentication errors
    AUTH_FAILED = 'AUTH_FAILED'
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    EXPIRED_TOKEN = 'EXPIRED_TOKEN'
    INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    
    # Validation errors
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
    INVALID_FORMAT = 'INVALID_FORMAT'
    FILE_TOO_LARGE = 'FILE_TOO_LARGE'
    UNSUPPORTED_FILE_TYPE = 'UNSUPPORTED_FILE_TYPE'
    
    # Payment errors
    PAYMENT_FAILED = 'PAYMENT_FAILED'
    PAYMENT_TIMEOUT = 'PAYMENT_TIMEOUT'
    WEBHOOK_VERIFICATION_FAILED = 'WEBHOOK_VERIFICATION_FAILED'
    DUPLICATE_PAYMENT = 'DUPLICATE_PAYMENT'
    
    # External service errors
    ZOOM_API_FAILURE = 'ZOOM_API_FAILURE'
    AI_API_TIMEOUT = 'AI_API_TIMEOUT'
    S3_UPLOAD_FAILURE = 'S3_UPLOAD_FAILURE'
    EMAIL_SERVICE_FAILURE = 'EMAIL_SERVICE_FAILURE'
    
    # Database errors
    DATABASE_CONNECTION_FAILURE = 'DATABASE_CONNECTION_FAILURE'
    CONSTRAINT_VIOLATION = 'CONSTRAINT_VIOLATION'
    TRANSACTION_ROLLBACK = 'TRANSACTION_ROLLBACK'
    
    # Rate limiting
    RATE_LIMITED = 'RATE_LIMITED'
    
    # Generic errors
    NOT_FOUND = 'NOT_FOUND'
    METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED'
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE'


class ErrorMessages:
    """
    User-friendly error messages.
    """
    # Authentication messages
    INVALID_CREDENTIALS = "Invalid email or password"
    EXPIRED_TOKEN = "Session expired, please login again"
    INSUFFICIENT_PERMISSIONS = "You do not have permission to access this resource"
    ACCOUNT_LOCKED = "Account temporarily locked due to multiple failed login attempts"
    
    # Validation messages
    MISSING_REQUIRED_FIELD = "This field is required"
    INVALID_EMAIL_FORMAT = "Email must be a valid email address"
    FILE_TOO_LARGE = "File size exceeds maximum allowed size of 10MB"
    UNSUPPORTED_FILE_TYPE = "File type not supported. Please upload a PDF file"
    
    # Payment messages
    PAYMENT_FAILED = "Payment could not be processed. Please check your payment details and try again"
    PAYMENT_TIMEOUT = "Payment session expired. Please try again"
    
    # External service messages
    ZOOM_API_FAILURE = "Unable to create meeting at this time. Please try again later"
    AI_API_TIMEOUT = "AI service temporarily unavailable. Please try again or request human pharmacist"
    S3_UPLOAD_FAILURE = "File upload failed. Please try again"
    EMAIL_SERVICE_FAILURE = "Unable to send email at this time. Please try again later"
    
    # Database messages
    DATABASE_CONNECTION_FAILURE = "Service temporarily unavailable. Please try again later"
    EMAIL_ALREADY_REGISTERED = "Email already registered"
    
    # Rate limiting messages
    RATE_LIMITED = "Too many requests. Please try again in {seconds} seconds"
    
    # Generic messages
    NOT_FOUND = "The requested resource was not found"
    METHOD_NOT_ALLOWED = "Method not allowed"
    INTERNAL_ERROR = "An unexpected error occurred. Please try again later"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: dict = None,
    retry_after: int = None
) -> Response:
    """
    Create a standardized error response.
    
    Args:
        error_code: Standardized error code
        message: User-friendly error message
        status_code: HTTP status code
        details: Additional error details (e.g., validation errors)
        retry_after: Seconds to wait before retrying (for rate limiting)
    
    Returns:
        DRF Response object with standardized error format
    """
    response_data = {
        'error': message,
        'code': error_code,
    }
    
    if details:
        response_data['details'] = details
    
    if retry_after:
        response_data['retry_after'] = retry_after
    
    return Response(response_data, status=status_code)


def create_validation_error_response(field_errors: dict) -> Response:
    """
    Create a validation error response with field-specific errors.
    
    Args:
        field_errors: Dictionary of field names and their error messages
    
    Returns:
        DRF Response object with validation error format
    """
    return create_error_response(
        error_code=ErrorCodes.VALIDATION_ERROR,
        message="Please check the provided data and try again",
        status_code=status.HTTP_400_BAD_REQUEST,
        details=field_errors
    )


def create_authentication_error_response(message: str = None) -> Response:
    """
    Create an authentication error response.
    
    Args:
        message: Custom error message (optional)
    
    Returns:
        DRF Response object with authentication error format
    """
    return create_error_response(
        error_code=ErrorCodes.AUTH_FAILED,
        message=message or ErrorMessages.INVALID_CREDENTIALS,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


def create_permission_error_response(message: str = None) -> Response:
    """
    Create a permission error response.
    
    Args:
        message: Custom error message (optional)
    
    Returns:
        DRF Response object with permission error format
    """
    return create_error_response(
        error_code=ErrorCodes.INSUFFICIENT_PERMISSIONS,
        message=message or ErrorMessages.INSUFFICIENT_PERMISSIONS,
        status_code=status.HTTP_403_FORBIDDEN
    )


def create_not_found_error_response(message: str = None) -> Response:
    """
    Create a not found error response.
    
    Args:
        message: Custom error message (optional)
    
    Returns:
        DRF Response object with not found error format
    """
    return create_error_response(
        error_code=ErrorCodes.NOT_FOUND,
        message=message or ErrorMessages.NOT_FOUND,
        status_code=status.HTTP_404_NOT_FOUND
    )


def create_rate_limit_error_response(retry_after: int) -> Response:
    """
    Create a rate limit error response.
    
    Args:
        retry_after: Seconds to wait before retrying
    
    Returns:
        DRF Response object with rate limit error format
    """
    return create_error_response(
        error_code=ErrorCodes.RATE_LIMITED,
        message=ErrorMessages.RATE_LIMITED.format(seconds=retry_after),
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        retry_after=retry_after
    )


def create_internal_error_response(message: str = None) -> Response:
    """
    Create an internal server error response.
    
    Args:
        message: Custom error message (optional)
    
    Returns:
        DRF Response object with internal error format
    """
    return create_error_response(
        error_code=ErrorCodes.INTERNAL_ERROR,
        message=message or ErrorMessages.INTERNAL_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def create_service_unavailable_response(message: str = None) -> Response:
    """
    Create a service unavailable error response.
    
    Args:
        message: Custom error message (optional)
    
    Returns:
        DRF Response object with service unavailable error format
    """
    return create_error_response(
        error_code=ErrorCodes.SERVICE_UNAVAILABLE,
        message=message or ErrorMessages.SERVICE_UNAVAILABLE,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )