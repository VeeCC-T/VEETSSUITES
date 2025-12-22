"""
Custom middleware for error handling and logging.
"""

import logging
import json
import traceback
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, OperationalError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed, 
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
    NotFound,
    MethodNotAllowed,
    Throttled,
    ParseError,
    UnsupportedMediaType
)
from decouple import config

logger = logging.getLogger(__name__)

class GlobalErrorHandlerMiddleware:
    """
    Global middleware to catch and handle all unhandled exceptions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Process unhandled exceptions and return appropriate JSON responses.
        """
        # Log the exception with full context
        logger.error(
            f"Unhandled exception in {request.method} {request.path}",
            extra={
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'request_path': request.path,
                'request_method': request.method,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'stack_trace': traceback.format_exc(),
            },
            exc_info=True
        )

        # Handle specific exception types
        if isinstance(exception, (AuthenticationFailed, DRFPermissionDenied, PermissionDenied)):
            return JsonResponse({
                'error': 'Authentication or permission error',
                'message': str(exception),
                'code': 'AUTH_ERROR'
            }, status=status.HTTP_403_FORBIDDEN)

        elif isinstance(exception, (ValidationError, DRFValidationError)):
            return JsonResponse({
                'error': 'Validation error',
                'message': str(exception),
                'code': 'VALIDATION_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exception, NotFound):
            return JsonResponse({
                'error': 'Resource not found',
                'message': str(exception),
                'code': 'NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)

        elif isinstance(exception, IntegrityError):
            return JsonResponse({
                'error': 'Data integrity error',
                'message': 'The operation conflicts with existing data',
                'code': 'INTEGRITY_ERROR'
            }, status=status.HTTP_409_CONFLICT)

        elif isinstance(exception, OperationalError):
            logger.critical("Database operational error", exc_info=True)
            return JsonResponse({
                'error': 'Service temporarily unavailable',
                'message': 'Please try again later',
                'code': 'SERVICE_UNAVAILABLE'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # For all other exceptions, return a generic 500 error
        return JsonResponse({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Get request info for logging
        request = context.get('request')
        user_id = getattr(request.user, 'id', None) if request and hasattr(request, 'user') else None
        
        # Log the exception
        logger.warning(
            f"API exception in {request.method if request else 'Unknown'} {request.path if request else 'Unknown'}",
            extra={
                'user_id': user_id,
                'request_path': request.path if request else None,
                'request_method': request.method if request else None,
                'exception_type': type(exc).__name__,
                'exception_message': str(exc),
                'status_code': response.status_code,
            }
        )

        # Customize the response format
        custom_response_data = {
            'error': get_error_message(exc),
            'code': get_error_code(exc),
        }

        # Add specific handling for different exception types
        if isinstance(exc, DRFValidationError):
            custom_response_data['details'] = response.data
            custom_response_data['message'] = 'Please check the provided data and try again'
        elif isinstance(exc, AuthenticationFailed):
            custom_response_data['message'] = 'Authentication failed. Please login again.'
        elif isinstance(exc, DRFPermissionDenied):
            custom_response_data['message'] = 'You do not have permission to perform this action'
        elif isinstance(exc, NotFound):
            custom_response_data['message'] = 'The requested resource was not found'
        elif isinstance(exc, MethodNotAllowed):
            custom_response_data['message'] = f'Method {request.method if request else "Unknown"} not allowed'
        elif isinstance(exc, Throttled):
            custom_response_data['message'] = f'Too many requests. Please try again in {exc.wait} seconds'
            custom_response_data['retry_after'] = exc.wait
        elif isinstance(exc, ParseError):
            custom_response_data['message'] = 'Invalid request format'
        elif isinstance(exc, UnsupportedMediaType):
            custom_response_data['message'] = 'Unsupported media type'
        else:
            custom_response_data['message'] = str(exc)

        response.data = custom_response_data

    return response


def get_error_message(exc):
    """
    Get a user-friendly error message based on exception type.
    """
    error_messages = {
        AuthenticationFailed: 'Authentication failed',
        DRFPermissionDenied: 'Permission denied',
        DRFValidationError: 'Validation error',
        NotFound: 'Resource not found',
        MethodNotAllowed: 'Method not allowed',
        Throttled: 'Too many requests',
        ParseError: 'Invalid request format',
        UnsupportedMediaType: 'Unsupported media type',
    }
    
    return error_messages.get(type(exc), 'An error occurred')


def get_error_code(exc):
    """
    Get a consistent error code based on exception type.
    """
    error_codes = {
        AuthenticationFailed: 'AUTH_FAILED',
        DRFPermissionDenied: 'PERMISSION_DENIED',
        DRFValidationError: 'VALIDATION_ERROR',
        NotFound: 'NOT_FOUND',
        MethodNotAllowed: 'METHOD_NOT_ALLOWED',
        Throttled: 'RATE_LIMITED',
        ParseError: 'PARSE_ERROR',
        UnsupportedMediaType: 'UNSUPPORTED_MEDIA_TYPE',
    }
    
    return error_codes.get(type(exc), 'UNKNOWN_ERROR')