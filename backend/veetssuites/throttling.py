"""
Custom throttling classes for rate limiting API endpoints.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

class LoginRateThrottle(UserRateThrottle):
    """
    Rate limiting for login attempts to prevent brute force attacks.
    """
    scope = 'login'
    rate = '5/min'  # 5 login attempts per minute per user

    def get_cache_key(self, request, view):
        """
        Use IP address for anonymous users, user ID for authenticated users.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Rate limiting for registration attempts.
    """
    scope = 'registration'
    rate = '3/hour'  # 3 registration attempts per hour per IP


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Rate limiting for password reset requests.
    """
    scope = 'password_reset'
    rate = '5/hour'  # 5 password reset requests per hour per IP


class FileUploadRateThrottle(UserRateThrottle):
    """
    Rate limiting for file uploads.
    """
    scope = 'file_upload'
    rate = '10/hour'  # 10 file uploads per hour per user


class PaymentRateThrottle(UserRateThrottle):
    """
    Rate limiting for payment attempts.
    """
    scope = 'payment'
    rate = '5/hour'  # 5 payment attempts per hour per user


class ExamRateThrottle(UserRateThrottle):
    """
    Rate limiting for exam attempts.
    """
    scope = 'exam'
    rate = '10/hour'  # 10 exam starts per hour per user


class ConsultationRateThrottle(UserRateThrottle):
    """
    Rate limiting for consultation requests.
    """
    scope = 'consultation'
    rate = '20/hour'  # 20 consultation messages per hour per user


class AdminRateThrottle(UserRateThrottle):
    """
    Rate limiting for admin operations.
    """
    scope = 'admin'
    rate = '100/hour'  # 100 admin operations per hour per admin user

    def allow_request(self, request, view):
        """
        Only apply throttling to admin users.
        """
        if not request.user.is_authenticated or request.user.role != 'admin':
            return True
        return super().allow_request(request, view)


class BurstRateThrottle(UserRateThrottle):
    """
    General burst rate limiting for API endpoints.
    """
    scope = 'burst'
    rate = '60/min'  # 60 requests per minute per user


class SustainedRateThrottle(UserRateThrottle):
    """
    Sustained rate limiting for API endpoints.
    """
    scope = 'sustained'
    rate = '1000/day'  # 1000 requests per day per user


class CustomThrottleException(Exception):
    """
    Custom exception for throttling with detailed information.
    """
    def __init__(self, message, retry_after=None, throttle_type=None):
        self.message = message
        self.retry_after = retry_after
        self.throttle_type = throttle_type
        super().__init__(message)


class EnhancedThrottleMixin:
    """
    Mixin to enhance throttling with better error messages and logging.
    """
    
    def throttle_failure(self):
        """
        Called when a request is throttled.
        """
        wait = self.wait()
        
        # Log the throttling event
        logger.warning(
            f"Rate limit exceeded for {self.scope}",
            extra={
                'throttle_scope': self.scope,
                'throttle_rate': self.rate,
                'wait_time': wait,
                'cache_key': getattr(self, 'key', 'unknown'),
            }
        )
        
        return False

    def wait(self):
        """
        Returns the recommended next request time in seconds.
        """
        if self.history:
            remaining_duration = self.duration - (self.now - self.history[-1])
        else:
            remaining_duration = self.duration

        available_requests = self.num_requests - len(self.history) + 1
        if available_requests <= 0:
            return remaining_duration

        return remaining_duration / float(available_requests)


# Enhanced throttle classes with better error handling
class EnhancedLoginRateThrottle(EnhancedThrottleMixin, LoginRateThrottle):
    pass

class EnhancedRegistrationRateThrottle(EnhancedThrottleMixin, RegistrationRateThrottle):
    pass

class EnhancedPasswordResetRateThrottle(EnhancedThrottleMixin, PasswordResetRateThrottle):
    pass

class EnhancedFileUploadRateThrottle(EnhancedThrottleMixin, FileUploadRateThrottle):
    pass

class EnhancedPaymentRateThrottle(EnhancedThrottleMixin, PaymentRateThrottle):
    pass

class EnhancedExamRateThrottle(EnhancedThrottleMixin, ExamRateThrottle):
    pass

class EnhancedConsultationRateThrottle(EnhancedThrottleMixin, ConsultationRateThrottle):
    pass

class EnhancedAdminRateThrottle(EnhancedThrottleMixin, AdminRateThrottle):
    pass

class EnhancedBurstRateThrottle(EnhancedThrottleMixin, BurstRateThrottle):
    pass

class EnhancedSustainedRateThrottle(EnhancedThrottleMixin, SustainedRateThrottle):
    pass